# 2025-05-05 Meeting

### Meeting Agenda

**Time:** meeting #69, 9am Monday San Diego time
- company update
- get_rewrites_for_renderer
- MLPerf submissions
- scheduler (fusion)
- driver
- symbolic
- webgpu
- fast OLMoE
- other bounties

### Audio

[Youtube Link](https://www.youtube.com/watch?v=Xy3VCX7mi0o)

### Highlights

- **[Company Update](#geohot-000000)**: TinyBox Green V2s are shipping this or next week for early buyers. New orders placed soon will ship by the end of May. Two units sold the morning of the meeting.
- **[Get Rewrites for Renderer](#geohot-000055)**: All rewrites now go through `CodeGen init`; a pre-built list of graph rewrite rules acts like an LLVM-style pass manager. Old functions retained for tests but should be phased out.
- **[MLPerf Submissions](#geohot-000140)**: Three submissions (BERT on MI300x green and red, RetinaNet on green). Awaiting verification before bounty payout.
- **[Scheduler Fusion](#qazalin-000225)**: `fuse_arange` refactored into a rewrite rule. Plan to replace the scheduler's dictionary-based grouper with proper passes. DSP work may be prioritized first.
- **[Driver Status](#nimlgen-000402)**: PSP driver modifications ongoing. Kernel crashes mostly resolved. TLB flushing errors hint at missing GCE firmware. USB booting instructions provided for reflashing controller.
- **[Red CI Boxes Down](#geohot-000447)**: Geohot observes red CI boxes offline; possibility of AMD GPU-related issues discussed.
- **[USB GPU Performance](#geohot-000640)**: OpenPilot model runs correctly but slowly. Focus shifting to performance improvements. Post boot/startup times to AMD hardware as a metric.
- **[5090 NV Backend Support](#geohot-000700)**: Not yet supported; low urgency but should be added soon. Older open-source versions could be reverse-engineered for compatibility.
- **[Driver Priorities](#geohot-000750)**: Priority order defined — 1) USB GPU, 2) P2P, 3) 5090 NV support.
- **[Symbolic/Z3 Fuzzer Work](#sied-lykles-001031)**: Z3-based fuzzer reveals bugs in rewrite rules (esp. negative numerators in division/mod). $500 bounty offered to formalize testing of rewrite validity.
- **[Division Semantics](#geohot-001352)**: Discussion on symbolic division complexity and Z3 handling; symbolic divisor cases require slower non-linear solvers.
- **[FastMod PR](#geohot-001543)**: FastMod approved and merged.
- **[WebGPU Refactor](#hooved-001604)**: Restarted from scratch without JIT. New `GraphRenderer` modularizes logic for rendering kernel graphs in JS/C. Future work will integrate a true linearizer replacement.
- **[Fast OLMoE / Multi-level Graph](#geohot-001901)**: Discussion on hierarchical graph structure (kernel/block UOPs) and vision for unified multi-level representation. Bounty tied to performance goal of 76.9.
- **[Other Active Bounties]**: Includes unsigned firmware for 7900XTX, FlashAttention integration, Mnist Torch compile fixes, and GPTFast beating AMD backend. Speed remains a core focus.

### Transcript

##### **Geohot** [[00:00:00](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=0)]
Good morning.
So ChenYu's on vacation.
So we're going to do a quick meeting today.
I got a lot of comma stuff to deal with.
Yeah, I'm back in San Diego.
Meeting 69.
And Tinybox Green V2s are shipping this week.
Probably.
If you're one of the three who already got their money in, your TinyBox V2 is either going to ship this week or next week.
And if you get an order in soon, we sold two this morning, yours will ship by the end of the month.
So, that's company update.

##### **Geohot** [[00:00:55](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=55)]
Get Rewrites for Renderer.
Everything now goes through CodeGen init.
I have it pre-build all of the list of graph rewrite rules, kind of like a pass manager on LLVM.
And then it runs the rules.
I left all the old functions in because the tests still use them, but we should take them all out.
So if anyone's interested in picking up one of those PRs... do so.
Things like rewrite shape tracker with index, expand rewrite, full graph rewrite, all that stuff.
And yeah, that's get rewrite for renderer.

##### **Geohot** [[00:01:40](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=100)]
MLPerf submissions.
We got three MLPerf submissions.
They have not been verified yet.
And we will pay that bounty when they are.
We got BERT submitted on MI300x, green and red, and we got RetinaNet submitted on green.
Flata, I don't know if you have a few words about that.

##### **Flata** [[00:02:05](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=125)]
No, not a whole lot.
I think the next step is to just optimize that evaluation stage, and hopefully we can get better times in the next cycle.

##### **Geohot** [[00:02:13](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=133)]
Great.
Yeah, let's hope it sticks around.
We also got to fix it for red, but that's a whole different thing.
Cool.
Schedule a fusion stuff?

##### **Qazalin** [[00:02:25](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=145)]
I refactored fuse A range to be a rewrite rule.
I think for the rest of this stuff, I really got to rewrite the grouper to not be the dictionary, to be an actual insertion of contiguous as pass and then followed by kernelize.
I'm thinking it would be better to first work a little bit on the DSP and then come back to the scheduler.
What's your thoughts on that?

##### **Geohot** [[00:02:53](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=173)]
Yeah, that sounds good.
You're welcome to go back and forth between them.
I don't really like the way that I did fuse.
I talked about this.
Like, it shouldn't really be a pass like that.
It should just be one pass.
I agree that it should totally just become contiguous insertion.
But, um, how about multi-output?

##### **Qazalin** [[00:03:13](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=193)]
Uh, I just focused on fuse A range, and I don't really get to that.

##### **Geohot** [[00:03:19](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=199)]
Uh...
Yeah, I mean, you're welcome to work on DSP stuff if you feel like you can make more progress there.
I think the schedule is in an okay place.
Yeah, the big two things I'm going to work on the next two weeks are the rewrite of Multi to take everything from O(N) to O(1), and the warp upcast.
And neither of those are blocking on anything, so... Yeah.
Yeah, I like this.
We're doing a 15-minute stand-up today.
All right, driver?

##### **Nimlgen** [[00:04:02](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=242)]
Yeah, so you use BGP, merged.
So for the PSP, I tried to modify the driver.
Yeah, apart from the kernel crashes, I think I just almost fixed all of them.
So yeah, it's just still in direct mode.
It shows error with flushing TLB.
And that problem means that the GCE firmware isn't loaded.
So yeah, I will continue looking into that.
Yeah.

##### **Geohot** [[00:04:47](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=287)]
Wait, did something break?
Because both our red boxes are down right now.
Our red CI boxes.
I saw you.

##### **Nimlgen** [[00:05:05](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=305)]
Yeah, yeah.
I mean, yeah, yeah, I'll take a look at it.

##### **Geohot** [[00:05:11](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=311)]
Can we just...
I mean, can we just blacklist AMD GPU on these machines?

##### **Nimlgen** [[00:05:18](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=318)]
We're on HIP.

##### **Geohot** [[00:05:21](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=321)]
What do you mean, we're on HIP?

##### **Nimlgen** [[00:05:23](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=323)]
I mean, in benchmark, we have... Oh, yeah.

##### **Geohot** [[00:05:29](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=329)]
Because I feel like... I'm looking at dmessage now of Tiny12, and there's all this spam about, like... PCI stuff.
So I don't know.
I guess we do still have to maintain that.
How's boot time at the USB?
Oh, do you have instructions for me?
I'm going to test the USB today to reflash the controller.

##### **Nimlgen** [[00:05:57](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=357)]
Yeah, I mean, it's just to run one script, you just connect the controller, run the extra GPU USB patched up by, and after that, you can run anything on it.
Cool.

##### **Geohot** [[00:06:12](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=372)]
And yeah, do we have, I think it'd be cool to post in AMD hardware, post the startup time, and then just drive that number down.

##### **Nimlgen** [[00:06:23](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=383)]
Yeah, sure.

##### **Geohot** [[00:06:25](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=385)]
And do we have it working to run the Openpilot model?

##### **Nimlgen** [[00:06:29](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=389)]
Yeah, I mean, it's actually passing all the tests.
I mean, it's correct, but it's still slow to go up in the weights.
Got it.

##### **Geohot** [[00:06:40](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=400)]
Yeah, so we've got to just focus on speed.

##### **Nimlgen** [[00:06:44](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=404)]
Yeah, and actually, for NV, we still... We don't support 5090 for NV backend.
So do we want to support them before the launch?

##### **Geohot** [[00:07:00](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=420)]
I think we're not in a huge... Oh, wait, we don't even support it in the... Yeah.
I think...
Yeah, yeah, we should do it.
We should do it.
It's not gonna get any easier, is it?
Like, we're not, like, waiting on them still to open source something?

##### **Nimlgen** [[00:07:24](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=444)]
I mean, yeah.
I mean, we're still waiting for them, but I think, first of all, we can try the previous version.
Because actually, all GPUs support new version and the previous version.
It used to be like that.
And the V4 is open source, so we can just reverse that.
I think it should be close to the previous ones.

##### **Geohot** [[00:07:50](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=470)]
Yeah, if it's not too much work, if you think it's only going to be a day or two of work, then I think it's worth it.

##### **Nimlgen** [[00:07:58](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=478)]
yeah okay so yeah i can also look into the driver thing p2p 

##### **Geohot** [[00:07:50](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=470)]
oh the p2p thing uh yeah uh let's let's let's come up with a priority order for these uh so i think i think usb gpu stuff is still top priority but if you're uh
want something else to switch to, I think probably P2P is second priority, and then 5090 support is third priority.
5090 support and NV.

##### **Nimlgen** [[00:08:39](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=519)]
Okay, got it.

##### **Geohot** [[00:08:41](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=521)]
Yeah, the P2P thing will help us sell these boxes.
We have enough GPUs to build 11 boxes, 10 for sale, one for us, in addition to the one prototype we have, so we'll have two.
Yeah, I mean, our CUDA stuff's not bad, is it?

##### **Nimlgen** [[00:09:03](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=543)]
I mean, it is.

##### **Geohot** [[00:09:06](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=546)]
It's bad?

##### **Nimlgen** [[00:09:09](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=549)]
I mean, it's... Yeah, I mean, the CPU overhead is... Yeah.

##### **Geohot** [[00:09:17](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=557)]
Yeah.

##### **Nimlgen** [[00:09:18](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=558)]
Running Llama, it's just, yeah, significant.

##### **Geohot** [[00:09:21](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=561)]
How is GPT-Fast doing it better?

##### **Nimlgen** [[00:09:26](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=566)]
um yeah that's a good question i don't know and i'm just 

##### **Geohot** [[00:09:29](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=569)]
i'm interested i'm interested in that in general right because maybe there's things that we can take away for the nv as well like gpt fast is fast 

##### **Nimlgen** [[00:09:44](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=584)]
yeah 

##### **Geohot** [[00:09:47](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=587)]
um yeah so it sounds like yeah usb gpu stuff 5090 stuff uh.
The V2 box is up and we can get another one up soon.
Anything else?

##### **Nimlgen** [[00:10:11](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=611)]
No.

##### **Geohot** [[00:10:14](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=614)]
Cool.
Symbolic stuff?
Sied Lykles, I don't know if you have anything you want to say.

##### **Sied Lykles** [[00:10:31](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=631)]
Oh, yeah.
So I've just been looking at the some of the rewrites for I did and I wrote like the z3 fuzzer for it, and I was hitting a lot of cases and.
I mean, like currently the current fuzzer
it replaces the Python ALU with like Python div and Python mod for it to pass, which is, I mean, not correct.
So I found like, I think three separate places where like a rewrite rule is incorrect.
I mean, like they don't happen a lot because they're all incorrect if it's, if the numerator is negative.
which doesn't happen much.
Because, I mean, idiv is, like, in C, it's truncating the vision.
I just, I was trying to, like, I found, I have a PR for two of them.
The third one is in, like, the Div and Mod folding.
And it's a little bit more complicated to...
cleanly do it without regressions because there's some rules that require like the remainder like they require like the normal remainder like the python remainder or the floored remainder but yeah 

##### **Geohot** [[00:12:19](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=739)]
yeah no I think a z3 fuzzer is a really good idea
I'll throw a $500 bounty on that and lock it to you.
Z3 fuzzer, testing, validity of all rewrite rules.
Yeah, because I wasted a ton of time last week on that Arange thing, and it turned out to just be a bug in div and mod folding.
So.
OK.
Cool.
Yeah, no, I think we're 10 years back, too.
We're going to work on making the symbolic stuff, making the view merge stuff work when you have symbolic variables, which is another rabbit hole of Vmax and Vmin and stuff.

##### **Sied Lykles** [[00:13:18](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=798)]
Yeah, I think, though, with Z3, you have to be careful with
It can do division very efficiently if it's bi-constant, because it uses a particular solver.
But if you have a symbolic divisor, you get a non-linear solver.

##### **Geohot** [[00:13:52](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=832)]
Yeah, no.
I mean, when you're dividing by a constant, you have that rewrite in there now.
It's just a multiply.
Like a multiply and a shift.

##### **Sied Lykles** [[00:14:01](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=841)]
I mean, well, that's not how V3 does it.
It just, like, there's some integers.
I mean, division is, you can express it as two bounds.
Like, you introduce an auxiliary variable, and then
The division, you define it in terms of multiplication, and then it just solves for it, the brand simplex kind of stuff.

##### **Geohot** [[00:14:43](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=883)]
Yeah, no, I haven't thought fully about how you'd even do division by a constant.
I understand how to like have like a theory for it, but I don't really even understand how to do division by a non-constant.
So.

##### **Sied Lykles** [[00:14:58](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=898)]
Yeah, I think you're using z3 can handle it.
It's just you get like z3...
You can get you got to prove that it's or it can actually verify whether
It's correct for all integers, or within your bound, for all the variables.
But if it's I don't know.
I'll have to think about it.
You end up using non-linear solvers.
It's going to be slower, at least.

##### **Geohot** [[00:15:33](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=933)]
Yeah.

##### **Sied Lykles** [[00:15:38](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=938)]
It should be fine, I think.

##### **Geohot** [[00:15:43](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=943)]
Is FastMod good to merge?

##### **Sied Lykles** [[00:15:46](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=946)]
Yeah.

##### **Geohot** [[00:15:48](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=948)]
Great.
Merged.
OK, WebGPU?

##### **Hooved** [[00:16:04](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=964)]
Hey, so I restarted the refactor from scratch.
this time not using the JIT and
I made a new thing called a graph renderer, which I think it's pretty self-explanatory.
We're trying to render the kernel graph into a different language.
So what that does is it takes your function that returns a tensor as well as the arguments of that function, and it constructs the graph, the kernel graph, it linearizes it, and it renders the kernels and buffer names and marks which buffers have state.
And this is all common logic, whether you want to render into JavaScript or C. And then if you're rendering into JavaScript for WebGPU, you subclass that graph renderer with WebGPU graph renderer.
And within there, you implement the function for rendering the graph into JavaScript.
starting from scratch here, trying to, instead of having a giant F string like I did before, just trying to have everything broken up into little understandable pieces so you could see all the operations, hopefully, and understand how they map to the webgpu runtime.

##### **Geohot** [[00:17:29](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=1049)]
Cool.
Yeah, no, I'm looking at it here.
I think, yeah, render is definitely the way to go on this.
Yeah, just have it render the uops that are in there.
that are in the kernel graph once it's kernelized.

##### **Hooved** [[00:17:46](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=1066)]
Yeah, so I'm using the same.
Basically, I want it to behave identically to if you were to actually run this in TinyGrad.
So right now, for linearizing the kernel graph, I'm just using the scheduling infrastructure.
It's not a true graph rewrite on uops because when you make schedule items, those are schedule items, not graph nodes.

##### **Geohot** [[00:18:12](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=1092)]
Yeah, I mean, we'll get there.
We'll get there.
We basically want to replace the scheduler, the thing that outputs schedule items, that toposort, with something that looks a lot more like the linearizer.

##### **Hooved** [[00:18:22](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=1102)]
Yeah, that's exactly what you would want to do to make this a true graph rewrite, like you said.
And when that happens, you can refactor these few lines of code to use that.

##### **Geohot** [[00:18:38](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=1118)]
Cool.

##### **Hooved** [[00:18:40](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=1120)]
All right, so if that seems like the right direction, I'll try to get this passing tests within a couple of days, probably, and then review it there.

##### **Geohot** [[00:18:52](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=1132)]
Sounds good.

##### **Hooved** [[00:18:54](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=1134)]
All right, thanks.

##### **Geohot** [[00:19:01](https://www.youtube.com/watch?v=Xy3VCX7mi0o&t=1141)]
Great.
Yeah, no, I thought that Arange stuff would help you with fast OLMoE.
Um, so how fast are we doing?
Let's give it a try.
Uh...
I also want to talk for a minute.
I was realizing I did a stream this weekend, and you understand where the... I'm not sure if this is what the multi-level in MLIR means, but so many of these things look like... So the kernelizing collapses groups of UOPs into a kernel, and then the linearizer collapses groups into a block.
this concept of collapsing into... The linearizer should really be replaced with the new kind of reduced stuff.
And then you'll have... It's a multi-level graph.
I see everything kind of moving to this.
And we're already doing it.
It's not far off from what we have now.
But right now we have this kernel UOP, and the kernel UOP has a special data structure called kernel.
We have the...
It's a block UOP, and it has a special data structure called Basic Block 2.
That stuff should be replaced by whatever generic multilevel representation we eventually move to.
But...
Cool.
So let's... I can try the Fast OLMoE offline.
But yeah, that bounty's yours when we get to 76.9.
Hopefully we're there.
Other bounties to go over quickly.
If anyone could get unsigned firmware working on 7900XTX.
Flash attention.
Very doable now with the Fuse stuff.
I don't know if someone's gotten Beautiful Mnist Torch to work with.
Oh, that's the Compile stuff.
And then GPTFast outperforming the AMD backend.
So a lot of good bounties for people who want to sit and work on Speed stuff.
Speed is the main focus of the year.
And with that, unless someone has a question or a comment...
quick meeting today.
Did like a stand-up style meeting.
Great.
See you all next week.
Good work last week.
Great having USBGPU merged.
Fuse A-Range feels closer than ever.
Yeah.
Cool.
See you next week.
