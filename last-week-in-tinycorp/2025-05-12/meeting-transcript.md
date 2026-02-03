# 2025-05-12 Meeting

### Meeting Agenda

**Time:** 9am Monday San Diego time
- company update
- new ci machines, new release
- min rectified flow example
- amd LLVM changes (with b1tg)
- mlperf
- symbolic folding, divmod, validation (with S-Lykles)
- scheduler / DSP
- usb driver
- WebGPU
- LDS
- cloud remote stuff
- other bounties


### Audio

[Youtube Link](https://www.youtube.com/watch?v=_FVcMAtePJ4)

### Highlights

- **[Company Update](#geohot-000011)**: TinyBox V2s are shipping — 4 units this week, 4 more sold, and a 4-week lead time for new orders. Focus remains on fulfilling customer orders before using units for CI.

- **[CI Machines](#chenyu-000050)**: Discussion on whether TinyBox or Rainbow machines should be used for CI. Current CI setup remains until user demand clarifies use cases.

- **[Metrics and Performance](#geohot-000220)**: Emphasis on improving [stats.tinygrad.org](https://stats.tinygrad.org) and driving all development by measurable performance metrics, aiming to match or beat PyTorch.

- **[New Release Plans](#chenyu-000324)**: A release is planned this week. Key blocker is the FUSE arange bug; it's essential for MLPerf compatibility.

- **[Rectified Flow Example](#geohot-000408)**: A new MNIST rectified flow example works well and outputs generated digits to the terminal. Performance debugging revealed benefits from inserting `contiguous` ops.

- **[Metal Buffer Limit](#geohot-000454)**: Hitting a 32-buffer limit on Metal. Likely due to scheduling issues; some kernels may be keeping intermediates alive too long.

- **[Missing Features](#geohot-000613)**: Tinygrad is missing `randn_like`; a proposal was made to add it using existing `rand_like` as a base.

- **[Gradient Flow Debugging](#geohot-000750)**: Proposal to enhance the Viz graph with gradient-aware layouts showing forward and backward ops together for easier debugging.

- **[USB GPU Performance](#geohot-000931)**: Copy-out speed on USB GPU remains a bottleneck. Improvements are ongoing.

- **[AMD LLVM Backend](#geohot-001005)**: LLVM backend for AMD still has slow kernel compilation. Potential causes include poor parallelization or unoptimized LLVM passes.

- **[MLPerf Submission](#chenyu-001357)**: Submissions under review. Tinygrad’s MI300X BERT run appears clean. Official results expected in June.

- **[Symbolic Folding and Validation](#sied-lykkles-001755)**: Work on improving `divmod` folding correctness. Many rewrites are currently technically invalid but functionally correct due to gate constraints.

- **[Div/Mod Semantics](#geohot-002248)**: GPUs likely don't support hardware integer division. Proposal to switch to C-style division for compatibility and simplification.

- **[Scheduler and DSP](#qazalin-002628)**: Fuse arange bug prioritized. DSP backend progressing, but quantize remains broken in master. Plan to validate via CPU and DSP simulators.

- **[CI Benchmarking](#geohot-003024)**: Plan to add nightly CI jobs using cron for BERT and MLPerf benchmarks.

- **[USB Driver](#nimlgen-003122)**: Copy speed improved to 150 MB/s on some Macs. Work continues on improving copy-out and firmware stability.

- **[Large BAR Support](#geohot-003553)**: Investigating 64-bit TLP support and enabling large BAR. GPUs may lack advertised resizable BAR due to bridge limitations.

- **[WebGPU Refactor](#hooved-003923)**: Major WebGPU refactor close to completion. Outstanding issues: preventing `realize` during graph construction and improving developer experience.

- **[LDS and CI Failures](#ignaciosica-005003)**: LDS PR blocked by a test failure in Metal CI. The test fails but does not fail the CI job due to improper command configuration.

- **[CI Mac Access](#geohot-005432)**: CI Macs 18 and 19 were sold. Access will be restored on Mac 14. A new Mac will be purchased for debugging Metal issues.

- **[Cloud Remote](#geohot-005817)**: Merged PR simplifying the HTTP server unexpectedly led to performance improvements.

### Transcript

##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=0)]
Okay, let's get started.
Everyone, I think.
OK, let's start with company update.

##### **Geohot** [[00:00:11](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=11)]
Yeah, so on TinyBox 2s, did some optimizing of how the drives are going to go in and stuff.
We've had the demo machine up and working.
So yeah, we got four shipping this week, and then I think we have four more sold beyond that.
That'll ship in like three weeks, and then if you buy today, it'll ship in like four weeks.
So yeah, buy a TinyBox V2 today.
They look great.

##### **Chenyu** [[00:00:50](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=50)]
Will we get any for us?
I guess that's the next point.
Will we get any for CI?

##### **Geohot** [[00:00:57](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=57)]
For CI, we're still a ways away from that.
We have one.
Until we're caught up on orders, I don't feel we should take more than one.
Well, we have people's money.
We have people's money.
We've got to get these boxes out.
It's good that we keep one to make sure we can test any bugs with it.
I don't think this is going to happen for CI anytime soon.
I'm not going to take the two green ones down.
We'll keep those three green ones.
We'll ride them out.

##### **Chenyu** [[00:01:24](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=84)]
Okay, sounds good.
Okay.

##### **Geohot** [[00:01:31](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=91)]
Yeah, and then I don't know about the Rainbow CI machines.

##### **Chenyu** [[00:01:37](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=97)]
Why not?

##### **Geohot** [[00:01:39](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=99)]
I mean, I don't know.
It's just like, it's not something we sell.
It's like a custom order, and we'll have to maintain these.
I just kind of like the idea of just using whatever we have.

##### **Chenyu** [[00:01:52](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=112)]
Maybe if we have more evidence for more people using Tinygrad, we would know better what to put down CI.
It should be what people use it for and what we want to maintain.

##### **Geohot** [[00:02:04](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=124)]
Yeah.
I mean, I think more important than CI is just having much better stats.tinygrad.org.

##### **Chenyu** [[00:02:17](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=137)]
We can also discuss about that too.

##### **Geohot** [[00:02:20](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=140)]
Yeah, yeah, I think this is what I'm really, I'm really excited to just make it easy for anybody to add metrics and then we can all just have metrics and your job is to drive the metric down.
Yeah, no, we got a second half of the year is all just going to be, we just, everything needs to be tied to a number.
We just got to drive these numbers, make the speed on par with Torch.
We got to figure out where Torch is.
We got to put like Torch as a dash line and we just got to start matching and beating Torch.

##### **Chenyu** [[00:02:50](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=170)]
Oh, I was trying with the leet GPU stuff because they support Tinygrad and they also support Torch.
So I basically submit everything with Tinygrad.

##### **Geohot** [[00:03:01](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=181)]
Did you see my reply on Twitter to them?
You can just type pass and it passes.

##### **Chenyu** [[00:03:08](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=188)]
Oh, I think they fixed it.

##### **Geohot** [[00:03:10](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=190)]
Okay, good.

##### **Chenyu** [[00:03:12](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=192)]
Yeah, and I pay $5 because otherwise they limit how many you can submit every day.

##### **Geohot** [[00:03:17](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=197)]
Oh, good.
They have a business model.
Yeah, no, it's nice to support Tinygrad.

##### **Chenyu** [[00:03:24](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=204)]
Yeah, the funny thing, I don't know how it will work, because the way you time the function and benchmark stuff, but whatever.
OK.
I could digress.
Let's move on.
So we can do a new release this week.
I really want the FUSE Arange thing to be fixed, because we have MLPerf, and I really want the new release to work with MLPerf.

##### **Geohot** [[00:03:55](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=235)]
Yeah, let's make a list of the bugs that absolutely need to be fixed before release, and let's get them fixed.

##### **Chenyu** [[00:04:02](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=242)]
Otherwise, I think it's fine.
We can release this week.

##### **Geohot** [[00:04:08](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=248)]
Yeah, I was very happy doing the Rectifly flow stuff yesterday.
I had no real Tinygrad issues.
The only minor Tinygrad issue was I had to insert a contiguous contiguous backwards after each transformer layer, or training was really slow.

##### **Chenyu** [[00:04:27](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=267)]
And how did you realize this?

##### **Geohot** [[00:04:30](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=270)]
Accidentally, someone in chat said, oh, it works if you use the old transformer code.
And the old transformer code had a contiguous at the end, and that was faster.
And then contiguous backward made it even faster.

##### **Chenyu** [[00:04:44](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=284)]
Interesting..
So I think it's twofold.
One is a scheduler to be smart to do things like that.
Another is the debugging tools to show things like this.

##### **Geohot** [[00:04:54](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=294)]
Yeah, well, so it's also related.
The other issue I had, sorry, I have three comments from yesterday's thing, and I'm moving to the next point.
But yeah, one is the contiguous, contiguous backwards thing.
I mean, it's the kind of thing where if you don't understand Tinygrad, you'd never find that.
And you'd just be like, why is it slow?
The second thing is kind of related to that.
The 32 buffer limit on Metal.
So I had to use GPU equals 1 on Mac.
One, we should fix the buffer limit.
But two, I don't think any of the kernels should actually have more than 32 buffers.
I think that's the bug.
I think some scheduler thing is just scheduled way too far back, and there should be intermediates being realized.

##### **Chenyu** [[00:05:49](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=349)]
Okay.

##### **Geohot** [[00:05:52](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=352)]
Yeah, so the metal thing, the contiguous thing, and then just little niceties, RANDN-like.
I think Torch has RANDN-like.
That was the only Torch thing I felt that was missing.

##### **Chenyu** [[00:06:08](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=368)]
Oh, because it's also a NumPy.
Wait, what?
Oh, randn_like.

##### **Geohot** [[00:06:13](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=373)]
Just randn_like, yeah.
Maybe we should refactor tensor a little bit so we could make the like methods really easy to write.
I'm sure there's rand_like as well.

##### **Chenyu** [[00:06:26](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=386)]
No, we already have rand_like.

##### **Geohot** [[00:06:29](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=389)]
Oh, we have rand_like.
We just don't have randn_like.

##### **Chenyu** [[00:06:31](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=391)]
So something on top of rand_like should work.

##### **Geohot** [[00:06:35](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=395)]
Yeah, yeah, yeah.
randn_like would be.. That was the only thing I felt like we were missing.
But overall, I mean, overall, there's so much things in Tinygrad that are just so much better.
Like our handling of automatic casting of D-types and the fact that things all work with all D-types is so much nicer.

##### **Chenyu** [[00:06:52](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=412)]
Did your model train?

##### **Geohot** [[00:06:55](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=415)]
Oh, yeah.
Yeah, yeah, yeah.
We got rectified flow on MNIST working great.
It's nice.
The example is really nice.
In fact, try it.
Because it doesn't output.
I wrote an MNIST command line visualizer.
So by the end, it's just printing generated MNIST digits to the command line.
It's cool.
There's one bug that I never found.
I'm not sure if it's a model training bug or potentially a Tinygrad bug.
I'm pretty sure it's a model.
But I just worked around it.
Yeah, but no, I mean, it would be nice to have debugging tools that show where the gradients are flowing.
Like a gradient aware Viz, I don't know.

##### **Chenyu** [[00:07:36](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=456)]
I don't know, yeah.
What do you mean by that?

##### **Geohot** [[00:07:50](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=470)]
Like,
I don't know.
We have the model graph in Viz.
It'd be interesting to see where the gradients are flowing.

##### **Chenyu** [[00:08:00](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=480)]
Yeah, but I wonder if Viz has a loss in the middle and everything after that is gradient-flowing.

##### **Geohot** [[00:08:08](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=488)]
Well, yeah.
But I guess what I'm concretely asking for here is imagine a Viz layout.
That instead of going from left to right, puts the gradients next to their forward pass.

##### **Chenyu** [[00:08:25](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=505)]
I see.
So instead of reading a very long edge, it's kind of your forward goes from left to right, and your backward goes from right to left.

##### **Geohot** [[00:08:28](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=508)]
Yeah.
Yeah.
I'm curious if we could find a nice Viz layout where that just works.
And then also, like, in Viz, putting, like, dash lines around.
Just making sure metadata is clean and, like, putting dash lines around each.
Like, this is a conv.
Some way to, like, light that up in Viz with the metadata.
Yeah, no, I'll be more concrete about what I want.

##### **Chenyu** [[00:09:19](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=559)]
Cool.
Oh, that sounds good.
In fact, it doesn't have any Tinygrad issue.
Did you try using USB GPU to train your model?

##### **Geohot** [[00:09:31](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=571)]
No.
I was in the other room.
I didn't have my USB GPU.
Also, until we fix the copy in speed is getting better, but the copy out speed is just brutal.

##### **Chenyu** [[00:09:42](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=582)]
OK.

##### **Geohot** [[00:09:45](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=585)]
Yeah, there's a few bugs still, too.
I've been posting them.
But we'll get there.

##### **Chenyu** [[00:09:52](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=592)]
OK.
Because I'm unrelated between your work and B1TG's work, AMD LLVM?

##### **Geohot** [[00:10:05](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=605)]
Well, I don't see B1TG here.
Yeah, I think he's been working on a lot of the speed up things.
I didn't realize he already did.
The major one was that the reason the gemms were slow is because of that work group size thing, which just limits the locals.
I fixed that, but I think he's got a bunch of other things to fix.
I think as soon as it's faster for BERT, we should just set it to the default.

##### **Chenyu** [[00:10:30](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=630)]
Yeah, absolutely.
Yeah, I think I also posted in the channel, but the main issue now is beaming kernels with AMD LLVM is very slow.
I have one job that has been running for eight hours.
I don't know if it's hanging somewhere.
Because it's not hitting the C front end.

##### **Geohot** [[00:10:55](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=655)]
Yeah, I would expect it to be faster also.

##### **Chenyu** [[00:11:00](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=660)]
Is parallel not working?

##### **Chenyu** [[00:11:05](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=665)]
It really depends on the device.
I mean, I don't know.
It also failed for if I have a draft PR that enables AMD LLVM.
And for that, some other smaller single kernels with AMD LLVM also took forever and time out.

##### **Geohot** [[00:11:27](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=687)]
We should look at what options we're passing to LLVM.
But yeah, no, I would expect it to be faster, right?
Maybe we should look and see if we're passing any options to LLVM that AMD isn't also passing.
Maybe there's one pass in LLVM that's really slow.
Because yeah, I mean, we're skipping a whole step.
It should be faster.

##### **Chenyu** [[00:11:49](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=709)]
Yeah, I think that's probably the main issue for switching.

##### **Chenyu** [[00:11:56](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=716)]
I also posted another smaller one that's on MI300x.

##### **Geohot** [[00:12:02](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=722)]
Oh, the MI300x without AMD LLVM.
I don't know if we tested that.

##### **Chenyu** [[00:12:04](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=724)]
No, I tested it.
There's some intrinsic WMMA not found, probably because it needs a different one.

##### **Geohot** [[00:12:20](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=740)]
Yeah.
Yeah.
It's kind of annoying to maintain both.
I don't know.
I like moving to the LLVM one anyway.
Co-manager, AMD.
AMD updated to ROCm 6.4 and they broke binary compatibility for no reason except they wanted to delete, like they had enums, like 1, 2, 3, 4, and then they deleted option 3, which is fine, but then they renamed option 4 to option 3.
Why would you do this?

##### **Chenyu** [[00:12:55](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=775)]
Maybe they only have two bits for that enum?
I don't know.

##### **Geohot** [[00:12:58](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=778)]
What, they're going to run out of numbers?
Oh, well, just in case we had 4 billion more of these.
No, and now it's just incompatible.
So another project that I want to work on after Multi is dealing with, I want to rewrite the C-libs thing, the C-type lib thing, to be good.
And then we could actually support, like, because you basically need two different headers for two different versions.
We have some hacks for this in AMD GPU, but I'd like to just write this all in a clean way.
A project that we can start doing is right now we install all the things to get the headers.
We install all the packages.
We should just copy all the headers to Tinygrad runtime headers that are used for autogen.
Yeah, because that should all be in the repo.
That shouldn't be dependent on some hypothetical package version.

##### **Chenyu** [[00:13:57](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=837)]
Sounds good.
OK.
related as MLPerf.
Have you checked other people's submissions?

##### **Geohot** [[00:14:13](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=853)]
Yeah, yeah.
I don't know how much we should talk about them.
I mean, yeah, we're not the only person to do BERT for MI300x, but a bunch of other people did other ones.

##### **Chenyu** [[00:14:29](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=869)]
Yeah, that's the funny thing.
You would think other people with MI300x would do BERT.

##### **Geohot** [[00:14:39](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=879)]
I'm assuming people are doing the LLaMA one.
They're doing the LoRa, yeah.
Yeah, they're all into the LoRa.

##### **Chenyu** [[00:14:48](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=888)]
No, but the other submission for AMD, they did BERT.
They just didn't do that on AMD 300X.

##### **Geohot** [[00:14:53](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=893)]
Oh.
I don't know if I saw that.
I definitely saw all the LoRa ones.

##### **Chenyu** [[00:15:01](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=901)]
Yeah.
So our review deadline is, I think, 13?
So that's my work tomorrow.
I'm going to review Google's submission for their stuff.
It's a sad story.
Nvidia trying to poke Google because Google resides very good with their TPU and stuff.
So far, we haven't got any objection, but it's probably just because Google doesn't care enough to review our stuff.
I don't know.
We'll see.
But I don't expect anything major to come up.

##### **Geohot** [[00:15:37](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=937)]
I don't think we did anything wrong.
I think we're pretty careful about stuff.

##### **Chenyu** [[00:15:37](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=937)]
And we are definitely the most careful based on how many people changes their logs and left and right after submission.

##### **Geohot** [[00:15:54](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=954)]
Wait, even Google's doing that?

##### **Chenyu** [[00:15:56](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=956)]
Yeah, because for whatever reason, out of their 10 rounds, three use a different learning rate.

##### **Geohot** [[00:16:03](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=963)]
Wow.
Well, yeah, I guess we don't know who at Google is in charge of the MLPerf.

##### **Chenyu** [[00:16:14](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=974)]
Yeah, so it's whatever.

##### **Geohot** [[00:16:19](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=979)]
Yeah, no, I don't even know.
I think our stuff is very cleanly done compared to what I could imagine others doing.
So I would hope Google would be better.

##### **Chenyu** [[00:16:35](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=995)]
I think it's, yeah, they probably just, they also have like Google and Google2 for some reason.
They have like two organizations submitting like two sets of stuff.
Already the person in charge for TPU is different from the person in charge of GPU.

##### **Geohot** [[00:16:52](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1012)]
I mean, that kind of makes sense.

##### **Chenyu** [[00:16:56](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1016)]
Yeah.
Okay.
Anyway, so it's tomorrow.
I will wrap up, and that should probably it.
Result will come, official results, sometime in June.

##### **Geohot** [[00:17:10](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1030)]
Great.
I mean, we can officially say that an MI300 box is about twice as good as a TinyBox green, and about three times as good as a TinyBox red.

##### **Chenyu** [[00:17:21](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1041)]
And we have the fastest time for training BERT with MI300x.
Okay, anyway, let's move on.
Next is about, we have a lot of symbolic folding stuff, a lot of div mod, because floor div and C div are different, some validation stuff.
Sied Lykkles is here, do you want to say something?

##### **Sied Lykkles** [[00:17:55](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1075)]
Yeah, so yeah, I'm working a lot on the div mod stuff.
It's a bit annoying, like, right now there's some rewrites that are incorrect, technically.
And if I make them incorrect, then there's a lot of open, like, the created image reads goes up a lot, and they happen to be sort of like
Within a gate, sometimes the rewrite is correct, like you end up with sort of the right thing.
So there's a lot of games that are technically incorrectly simplified, but then they're not producing bugs because they're in a gate.
So, I'm trying to improve your given valid, because if that works, then the DevOps simplifying will work correctly for trunkdiv.

##### **Sied Lykkles** [[00:19:26](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1166)]
I can make the running correct without regressing OpenPilot.

##### **Chenyu** [[00:19:32](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1172)]
I think my two comments on this is, I think usually if you find something that's incorrect, add it as a test first.
If it's something just lucky and happened to be correct, it's also fine to add it as a test.
Probably don't have enough tests for behaviors, especially the cases that never happen outside of Openpilot, because a lot of these new up, given that the optimizations, a lot of these are for the image only.
And image has these specialties for how you can simplify stuff.
It's very likely that, yes, we got lucky because it's
It's only wrong if you are outside of the bond.
But it's also fine for the image, because if you go outside the bond, most likely it's zero anyway.
So the fact that your expression is not correctly filled is probably not a bug.
But we definitely want to have this as a test.
And so

##### **Geohot** [[00:20:55](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1255)]
Adding tests, adding test layers and add value, then I think the event for div and mod folding function is becoming pretty big and hard to reason about.
It has a lot of special cases that I don't know if it needs to be a special case.

##### **Chenyu** [[00:21:16](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1276)]
But I will only know after we are done with fixing all the bugs, and we know
Is this correct?
We can think about how to simplify the logic and see.

##### **Chenyu** [[00:21:31](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1291)]
So the branch where I have, it's called correct congruence folding.
I think I'm going to test a new symbolic test that I changed to, like,

##### **Sied Lykkles** [[00:21:50](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1310)]
That actually was simplified previously, but is not a valid simplification.

##### **Chenyu** [[00:22:00](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1320)]
Okay.

##### **Chenyu** [[00:22:01](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1321)]
I will review those.
That sounds good.
Yeah.
I mean, yeah, if I.. If I get some errors, then I can add a symbolic fuzzer as well.
And the other thing I posted was maybe arguing to make givenMods actually ProDev.

##### **Chenyu** [[00:22:32](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1352)]
I was checking the instruction.
I think they all implement the givenCmod, not the floor one, on the hardware.
Because we likely would only keep one, and we use the one that is on the hardware.

##### **Geohot** [[00:22:48](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1368)]
So I'm actually not sure the hardware implements any of them.
I don't know if there's any GPUs that support an integer divider.
Cool.
We should look into what the generated GPU assembly is.
I'm not sure.
Do you know for the x86 instruction?
No.
I mean, CPUs actually have integer dividers, but I'm not sure GPUs even have them.
So we should think about what the GPU is actually doing.
Yeah, like obviously if we're doing the stuff where we transform it into like a multiply or something, then that's all just up to us.
So I don't know what's easier with that.

##### **Chenyu** [[00:23:32](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1412)]
Yeah, so my argument is kind of that doing division by constant is easier if it's
Because shifting is for division.

##### **Sied Lykkles** [[00:23:53](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1433)]
The only time where it's kind of a little bit trickier is if you have division by a variable.

##### **Chenyu** [[00:24:04](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1444)]
You don't know ahead of time.
You can't compile it down to anything.
And then it would take two cycles extra to go from that.

##### **Chenyu** [[00:24:19](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1459)]
Yeah, I don't think we worry too much about divided by variable at this point.
Variable is most likely positive numbers because how we use it.
So the software already have a lot of constraints.
If the thing we come up with works with LLaMA, I think that's fine.

##### **Geohot** [[00:24:37](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1477)]
No, I mean, we do need general correctness on this, but I am okay with changing it, as long as you're aware of what this entails.
Like, I wouldn't worry about, I don't think any GPUs that I know of have an integer divider.
So I'm curious what algorithms they're using, and if we could, like, similar to the way that we did Transcendental, if we could move those algorithms into Tinygrad.

##### **Chenyu** [[00:25:01](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1501)]
So, at least like in PTX, we usually compile to this kind of fast
Like in this stuff, so multiplication and shifting.
But the way you do, so PTX will do like, it will add the device or minus one if it's negative.
Because the multiplication and shifting is four driven, the way PTX then implements it is
Yeah, no, I got it.

##### **Geohot** [[00:25:46](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1546)]
Yeah, again, I'm open to changing it.
If you put a PR up to do it, I'm not opposed.
But yeah, the only thing I insist on is that we do only keep one.

##### **Chenyu** [[00:25:58](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1558)]
Yeah.
Okay.
Cool.
And we can make that decision first.

##### **Geohot** [[00:26:06](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1566)]
Before making more refactor, because I imagine the one we pick would change how we write the div and mod footing.
Yeah.
Cool.

##### **Chenyu** [[00:26:18](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1578)]
Awesome.
OK.
Next, we have scheduler.

##### **Qazalin** [[00:26:28](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1588)]
So my highest priority for this week is going to be fixing fuse A range.
Then I'll let you guys know so that you can release.
There's a bug in Shrink, which should be pretty easy to fix, I think.
The reason why the bugs are coming up is because it's more generic, so it's ended up actually fusing more things than before.
So it's a good stretch, actually.
I also worked on the DSP a little bit.
I think we need..
Some more infrastructure in master for rendering the same intrinsics correctly.
Right now, the benchmark is 178 off target.

##### **Geohot** [[00:27:13](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1633)]
So I don't see the benchmark.
Is it in there?

##### **Qazalin** [[00:27:18](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1638)]
It's a branch.
I can merge it once we have the signature.
I can't get the signature for Tiny 2020.

##### **Geohot** [[00:27:25](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1645)]
Oh, yeah, I can deal with that.
Yeah, you have to go to this Qualcomm website and get them.
Yeah, you can't just move it.
Sorry, I saw your thing about that.
I'll fix that today.

##### **Qazalin** [[00:27:36](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1656)]
Thanks.

##### **Chenyu** [[00:27:38](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1658)]
So if you said that's good to merge, post that to the Qualcomm channel as well.
Cool.

##### **Geohot** [[00:27:50](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1670)]
Yeah, no, I mean, it's just going to be a..
It's going to be a grind to get things in.
What do you think we need that's not supported for the SIMD intrinsic?

##### **Chenyu** [[00:27:58](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1678)]
You don't think the custom thing is good?
No, it's going to be the custom thing.

##### **Qazalin** [[00:28:07](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1687)]
I think the way I'm going to approach it is make the stuff in test quantize honest fast.
And then incrementally, like naturally, then the mobile one becomes faster.
The problem I had with moving the handbook and stuff was that there were so many changes.
I ended up getting a bunch of bugs that it's just hard to make generic.
So I think the way it's going to be made generic is just, we're not using a bunch of the bishop stuff in master right now.
And the multiply instructions, I think we aren't using that at all.
It's just going to be ranger stuff, adding them to CodeGen, the defecturizer.
Quantize is completely broken in master.

##### **Geohot** [[00:28:53](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1733)]
Yeah, yeah, there's very little test for that.
We could see what's wrong with that.
But the other thing that I'd like to do is get, so I want the benchmark in CommaCI, and then if you can do a correctness test in GitHub Actions.

##### **Chenyu** [[00:29:15](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1755)]
Hopefully it'll be fast enough, like it probably should be.
The simulator's not too slow.

##### **Qazalin** [[00:29:22](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1762)]
CPU is very fast, yeah.

##### **Geohot** [[00:29:24](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1764)]
Wait, what do you mean CPU?

##### **Qazalin** [[00:29:28](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1768)]
Validating with CPU, right?
So one of the same kernels on CPU.

##### **Geohot** [[00:29:34](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1774)]
Oh, yeah, I mean, I guess you could use validate with CPU to actually validate the kernels.
I was even more just talking validation of the whole thing, just like running, because the DSP simulator seems correct.
So just running all the generated DSP code.
But yeah, if you just do validate with CPU, that's great.

##### **Chenyu** [[00:29:53](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1793)]
I don't know if we have tests for that.
I'll add it.
Cool.

##### **Chenyu** [[00:30:02](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1802)]
Yeah, for Fuse Air Range, I think as long as the CI benchmark won't work, it should work for the training.
I can do it for training after lab pass.

##### **Geohot** [[00:30:24](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1824)]
Oh, while we're talking about CI benchmark, I'd like to get, we should make cron jobs to do the beam search for BERT and stuff.
Yeah, I remember we discussed this probably exactly one year ago.
Well, now it's more serious.
It looks easy in GitHub Actions.
I think we could just make like cron.yaml and just say run every night.
We can use the same runner infrastructure, so we don't have to set up new runners or anything.
And just, OK, CI is slow at some random hour.
We'll pick an hour that no one is likely to be on.

##### **Chenyu** [[00:31:03](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1863)]
OK.
Uh, let's move to USB driver.

##### **Nimlgen** [[00:31:22](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1882)]
Um, yeah, so for, so yeah, actually now in master, we have copy speeds at about 150 megabytes a second.

##### **Chenyu** [[00:31:40](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1900)]
I only see 50 in the benchmark test.

##### **Nimlgen** [[00:31:43](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1903)]
Yeah.
I mean, on my Mac, it's faster.
I don't know why.
Why is that?
Actually, they had problems on M2 with old macOSes.
Oh, interesting.
But I'm not sure, yeah.

##### **Geohot** [[00:32:01](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1921)]
Yeah, no, I mean, 50 is definitely in the realm of usability.
But yeah, 1.50 is even better.
I saw your fast boot branch too.
It's nice having that 512K RAM.

##### **Chenyu** [[00:32:14](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1934)]
Yeah.
Yeah, I just need some more factors to do.

##### **Geohot** [[00:32:22](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1942)]
Did you ever post any of the notes on the firmware and stuff?

##### **Nimlgen** [[00:32:28](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1948)]
Yeah, I mean..
Yeah, I have a repo for some nodes, but I think not for the patch.
So I need to write this up.

##### **Geohot** [[00:32:39](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1959)]
Also, whenever you write patches like that, before you do the write, like right before you do the write, you should check the SHA hash of what you're about to write.
Because if something happened to be wrong there, you'll break the thing.

##### **Chenyu** [[00:32:54](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1974)]
Yeah.
Yeah.
Yeah.
And a SHA hash.
But basically, they just
Yeah, okay, yeah.

##### **Geohot** [[00:33:05](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1985)]
I mean, just say, like, imagine your download was corrupted, or that file got corrupted, or anything could happen that would lead to the device being bricked.

##### **Chenyu** [[00:33:17](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=1997)]
Yeah.

##### **Nimlgen** [[00:33:20](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2000)]
I mean, they have, like, the second flight, so it can boot if the.. Yeah, but.. Well.. Wait, wait, wait, wait, wait, wait.

##### **Chenyu** [[00:33:29](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2009)]
How does it know the boot from the second flash?

##### **Nimlgen** [[00:33:33](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2013)]
Yeah, I actually think my theory is that it will check the signature, but yeah.
What signature?
It's CRC32.
We recalculated.
Exactly.

##### **Geohot** [[00:33:49](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2029)]
You recalculate it, but if the CRC32 is correct, it's never going to run that other branch, even if the first thing your thing does is a dead loop.
So I agree with you that that CRC32 might check, might catch corruption of the actual write process.
It's not going to check, I recomputed a CRC32 on bad code.

##### **Nimlgen** [[00:34:14](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2054)]
Yeah, right.
That's, yeah, we'll let it.
Yeah, still, so for the copyouts, I think we, so currently we're much only writes.
So for the copyouts, it's just,
Yeah, probably.
Yeah, we need one more patch for copy-outs.
Yeah, we'll look into this.

##### **Geohot** [[00:34:38](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2078)]
You think we need another firmware patch to make it not halt on the NVMe read?

##### **Nimlgen** [[00:34:43](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2083)]
Definitely, yeah.
I mean, yeah, because that's patching the NVMe write branch.

##### **Geohot** [[00:34:49](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2089)]
Yeah, yeah, that makes sense.
Cool.
Yeah, good progress.
And then any luck with the large bar?

##### **Chenyu** [[00:35:01](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2101)]
No, I haven't.
I haven't started that.
Yeah, I mean, I can't imagine why it wouldn't work.

##### **Geohot** [[00:35:13](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2113)]
Is the register 64 or 32 bits?
32.
Oh, the address register is only 32?

##### **Nimlgen** [[00:35:28](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2128)]
You mean.. No, actually, I mean, we send currently like the TLP, like 32-bit TLPs.
I think we can change it.
I mean, there is some structure changes for 60-bit, 64-bit TLPs.
I don't know if they are supported, but yeah, we can try that.
But apart from that, we still need to enable large bar.

##### **Geohot** [[00:35:53](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2153)]
Yeah, so the TLP thing is the thing that I would be more concerned about working.
I think if you could send 64-bit TLPs, I see no reason why we can't poke the PCIe registers and get large bar.

##### **Nimlgen** [[00:36:12](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2172)]
Yeah, when I tried it last time, the GPU reported that
Yeah, it just doesn't report any resizable bar feature.
Maybe because of the bridges.
I don't know.

##### **Chenyu** [[00:36:32](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2192)]
Imagine the device should support large bar regardless of.. The bar is just entirely on the device.
It's just the PCIe controller registers.
Interesting.

##### **Geohot** [[00:36:55](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2215)]
I mean, it's pointless if we can't get 64-bit TLPs anyway.
But I mean, GPUs have definitely worked with small bars, too.
So there has to be some, like window registers or something like that.
I don't know.

##### **Nimlgen** [[00:37:09](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2229)]
I've never dealt with that.

##### **Geohot** [[00:37:12](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2232)]
Yeah, it makes it slower.
I mean, it'd be great to just enable a large bar if it's possible, but not that not.

##### **Nimlgen** [[00:37:19](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2239)]
No, I mean, we can just resolve some space.
It's, yeah.
And just for the page tables, that's the only way.

##### **Geohot** [[00:37:30](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2250)]
And you say you only want to put the page tables in first 256?

##### **Chenyu** [[00:37:37](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2257)]
Yeah.
Will the page tables always fit?

##### **Nimlgen** [[00:37:44](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2264)]
Yeah.
I mean, we need like two megabytes of page tables for a gig.

##### **Geohot** [[00:37:49](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2269)]
Oh.
Oh, well, I don't know.
Maybe just reserve the beginning for page tables if it's really that small.
I mean, I don't mind reserving two megs.

##### **Chenyu** [[00:38:00](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2280)]
Yeah, I mean, yeah.

##### **Nimlgen** [[00:38:05](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2285)]
Yeah, that should be simpler.
OK, yeah, I'll try to enable large bar.
That works.

##### **Geohot** [[00:38:15](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2295)]
Yeah, yeah, yeah.
But no, you're right.
If it really is just two megs of page tables, we could just stick them at the beginning.

##### **Nimlgen** [[00:38:21](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2301)]
No, I mean, two megs for one gigabyte.
I mean, the cards have like eight.
So yeah, 16 megabytes.

##### **Geohot** [[00:38:29](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2309)]
Yeah, 24 card and 48 megs of page tables.
I mean, I guess you're going to need them anyway.

##### **Chenyu** [[00:38:34](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2314)]
It doesn't matter where we put them.
Yeah.

##### **Geohot** [[00:38:41](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2321)]
Oh, apparently some people in LLaMA P2P were complaining the P2P driver doesn't work on the modded 4090s with the 48 gigs.
Because it only has a 32 gig bar.

##### **Chenyu** [[00:39:00](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2340)]
But, uh.. Yeah, cool.
Good progress.
Excited to see it get even faster.
8 second boot is pretty nice.
Cool.
Okay.
Next, we have web GPU.

##### **Hooved** [[00:39:23](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2363)]
So for WebGPU, I pushed a complete draft of the refactor that is passing all tests except for the line limit.
There's a couple of things I still have to do, even though it's passing tests, which is ensure that, first thing is to ensure that all the state is realized before we begin creating the graph.
So either we, the way the JIT solves this, not that I'm using the JIT, but the way the JIT solves it is by calling the function once before capture and then calling it a second time and capturing everything.
So either we could do that or we could just assert that all the state is realized
And basically, the developer has to do it.
So one of those things.
And the other thing I have to figure out is how to assert that no realizes happen during graph construction to ensure that we're capturing everything and that we don't have these hidden realizes that
are removing some of the compute from our capture.
So those are two things that remain to be done.
And also just testing and thinking about corner cases.
And also, I need to make sure this stuff works with ONNX and Torch and check out the developer experience there.
But I wrote about what some of the new stuff looks like in the web GPU channel.
So you can see some of the changes there.
And yeah, that's how it is.

##### **Geohot** [[00:41:07](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2467)]
I'm looking at your change here to LLaMA.
I mean, I don't like that assign change.

##### **Hooved** [[00:41:12](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2472)]
Oh, that's another problem I forgot to mention.
Yeah, that has to be fixed.
That can't stay as it is.
So the scheduler partial assign thing that we were chatting about a couple weeks ago, I don't think it's fixed yet.
That has to be fixed.

##### **Geohot** [[00:41:29](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2489)]
Yeah, I mean, I think that's the first thing.
Just reading this PR, the first thing to get merged is that fix.
I'm also okay with moving to banning use of realize inside JITs.

##### **Hooved** [[00:41:47](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2507)]
Yeah, I mean, that makes sense too, but we have to ban realize, you know, like even if you're not JITing anything, you have to ban realize, or you have to detect that realizes aren't happening somehow.

##### **Geohot** [[00:42:00](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2520)]
Wait, no, what do you mean?
What I want to add is if you're inside a JIT context, I mean, you can still use the, are you not using a JIT context?

##### **Hooved** [[00:42:09](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2529)]
Yeah, I'm not using the JIT at all.

##### **Chenyu** [[00:42:12](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2532)]
The JIT at all..

##### **Geohot** [[00:42:17](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2537)]
I mean, there should be some concept of like, I've specified, I mean, the JIT tells you what the inputs and outputs are to the function.
If you're not using the JIT, how do you get the inputs and outputs?

##### **Hooved** [[00:42:30](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2550)]
I mean, I'm pretty confident about that.

##### **Geohot** [[00:42:33](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2553)]
You know, I just, I have.. No, no, no, but I'm saying, how do I literally specify it, right?

##### **Hooved** [[00:42:40](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2560)]
So you have the arguments and the function, right?
And so the arguments, you basically, I'm doing the same thing the JIT does essentially, which is realizing- Oh, oh, I see what you're doing here with export web GPU.

##### **Geohot** [[00:42:57](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2577)]
Yeah, yeah, don't do this.
Just use the JIT, but you don't actually have to run, like use the JITed function.
Export should practically be a function call on the JIT.
Just from a syntactic perspective.

##### **Hooved** [[00:43:13](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2593)]
I mean, that was what I was doing before, and then a couple, I think a week ago or a couple weeks ago, we discussed that I would rewrite this, not using the JIT.

##### **Geohot** [[00:43:24](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2604)]
No, no, no.
Two different things here.
So I'm saying, don't use the JIT's internal structures, which is what the original thing was.
But from a semantic perspective, from just a..
Like, what the syntax should be.
Is you kind of just want it to be decorated with TinyJIT, and then it's like TinyJIT.export.
Even if it's a totally different code path that doesn't actually run the existing JIT stuff.
Right, because I see what you have now is you have this export web GPU function, and you're passing in a function, and then you're passing in a list of arguments, right?
You can instead just do that with the JIT.

##### **Hooved** [[00:44:05](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2645)]
Also, I'm not sure you're looking at the right thing.
I don't have an export web GPU function anymore.

##### **Geohot** [[00:44:09](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2649)]
Oh, I'm looking at 9424.

##### **Hooved** [[00:44:11](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2651)]
I guess I'm looking at A2DFE.

##### **Geohot** [[00:44:21](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2661)]
Wait, I'm looking at, no, that's the number of the PR, export model.

##### **Hooved** [[00:44:25](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2665)]
Yeah, 9424, the most recent commit, A2DFE.

##### **Geohot** [[00:44:33](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2673)]
So I'm looking at 9424.
I'm looking at compile.py.
And you have a call to a function exportWebGPU, where the first argument is model.forward.

##### **Hooved** [[00:44:42](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2682)]
Yeah, sorry.
Yeah, we're talking about different things.
I need to change that.
The TinyChat stuff is not in the test paths.
I'm talking about the compile efficient net tests.

##### **Geohot** [[00:45:00](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2700)]
That's what's in our CI.
Which one should I look at?

##### **Hooved** [[00:45:06](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2706)]
You should be looking at examples forward slash compile efficient net dot pi.

##### **Geohot** [[00:45:12](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2712)]
Compile efficient net, okay.
So yeah, okay.
You have a function called export model.
I don't know what mode is.

##### **Hooved** [[00:45:24](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2724)]
That's not being used.
That's the old thing.
That's the old thing.

##### **Geohot** [[00:45:29](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2729)]
OK.
So you have something called WebGPU JS renderer.
Yes.
But it's all the same, right?
We're looking at the same thing.

##### **Hooved** [[00:45:40](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2740)]
OK.

##### **Geohot** [[00:45:42](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2742)]
Oh, why do you have to pass in the model state deck?
You shouldn't have to do that either.

##### **Hooved** [[00:45:48](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2748)]
We don't have to do that.
There is importance for that.
In order for the exported buffers to have names for debugging and understanding the model, you want to be able to see, oh, this is the KV cache.
This is the attention weights or whatever.
So it's an optional parameter that lets you do that.
It lets you assign names to the state.

##### **Geohot** [[00:46:14](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2774)]
Okay, I think we should probably solve that problem more generically and support like name tensors, but regardless.
Okay, so what I'm basically saying is this is so close, but instead of making it a function where you pass in a function, it should still be decorated with TinyJet and then have a class method on TinyJet called something like render or export.

##### **Hooved** [[00:46:43](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2803)]
I need to just play with it.

##### **Geohot** [[00:46:48](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2808)]
It's the same exact thing.
But then the key thing is for the realizes, what you can do is use the same idea of the JIT context when you actually run that function.

##### **Hooved** [[00:46:59](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2819)]
Yeah, I mean, that's how you solve it.
I see what you're saying, because that can detect if realizes are happening.

##### **Geohot** [[00:47:06](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2826)]
Yeah, and there's not another way.
It's totally fine to have something like a context var, and then you run the thing, and if realizes happen, you just say, assert, sorry, can't realize in a JIT context.

##### **Hooved** [[00:47:18](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2838)]
Okay, yeah, I think I get it.
I'll try it, and then I can think about it.

##### **Geohot** [[00:47:24](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2844)]
The very notable thing, and I'm sure your call does this, the call to render, is it never actually executes those kernels.
It executes model.forward, but it never actually runs anything on the device.

##### **Hooved** [[00:47:34](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2854)]
Correct.
Yeah, correct.
Nothing is being run when it's actually doing the stuff.
The only thing is the state has to be realized before you do that stuff so that there's actual real buffers that you can.. Yes.
Yeah.

##### **Geohot** [[00:47:52](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2872)]
So how you should deal with that is just to gather up all the state and then do a big co-realize on all the state.

##### **Hooved** [[00:48:01](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2881)]
Yeah, that's fine, I think.

##### **Chenyu** [[00:48:04](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2884)]
Cool.
OK.
Great.

##### **Geohot** [[00:48:10](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2890)]
Yeah, no, looking good.
This is definitely the right path.
And I think everything is going to start to go down this sort of path, where it's like no longer, the JIT no longer runs anything.
The JIT doesn't capture run kernels.
The JIT just runs the function and gets the graph.
And it renders that or does whatever to it.

##### **Hooved** [[00:48:32](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2912)]
Cool.
And then one last thing, the WebGPU.py and renderer slash graph, is there anything about the style there that you hate?
I basically got rid of all the function.
I factored.
I had all the stuff in runtime, but then I took it out because it didn't really make sense.

##### **Geohot** [[00:48:54](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2934)]
No.
No, it looks.
Yeah, I mean, there's no way around just having something that's going to build strings.
This is actually outputting the JavaScript.
Yeah, I don't really see a better way to do this.

##### **Hooved** [[00:49:08](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2948)]
All right.
All right.
So this sounds good.
I think I'll try to get that stuff done within a day or two.

##### **Geohot** [[00:49:14](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2954)]
But yeah, no, I think this could be a bunch of different PRs.
I think the LLaMA thing needs to be its own PR.

##### **Hooved** [[00:49:20](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2960)]
That's a whole separate thing I have to figure out.
I don't understand the scheduler enough to quickly make that change.
I'd have to figure out how to do the partial assigned thing in the scheduler.

##### **Geohot** [[00:49:32](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2972)]
If you write failing tests, we can look into it.
If you write just the behavior that you want.
Understanding the scheduler is probably beyond the scope of what's expected of this.
If you write failing tests, someone can definitely look into that.
We should make sure we're supporting partial assigned.

##### **Chenyu** [[00:49:49](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=2989)]
But cool.
Yeah, good progress.
Thanks.
We have LDS.

##### **Ignaciosica** [[00:50:03](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=3003)]
Hi, hello.
Well, the LDS code has been basically done for the past two weeks.
But it has also been blocked by failing cases in CI.
Like, Metal benchmark CI fails, and I couldn't reproduce either on my PC, or also helped me test on his PC.
He couldn't reproduce on the failing case.
So as it's so slow to debug Metal, I couldn't figure out what is actually happening.
So it's blocked on that.

##### **Chenyu** [[00:50:51](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=3051)]
So it's 9771?
Yeah.
Did you disable it in Metal?

##### **Geohot** [[00:51:01](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=3061)]
No, no.
I don't see failure for Metal.
I only see failure for AMD.

##### **Ignaciosica** [[00:51:08](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=3068)]
Yeah, that's one thing.
I saw it many times, that on Benchmark, some test fails.
Depending on the command you use, like Python or PyTest or Python slash m don't die test, the CI doesn't fail, but the test too.
That was happening before with a test on Red Benchmark, that the test was failing, but it wasn't triggering the fail on the CI.
And here it's happening the same.
I linked the failing test in the last comment of the PR.

##### **Geohot** [[00:51:43](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=3103)]
So I think there's a bunch of things here that can be pulled out into their own PR.
Like I see that you're changing the alignment of all the SMEMs to 16.
Yeah, I think that's fine.
But I think that should definitely be done in its in its own PR.

##### **Chenyu** [[00:52:01](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=3121)]
Okay.
Um, yeah, then otherwise, what are you saying is the problem?

##### **Geohot** [[00:52:08](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=3128)]
I don't see the failure.

##### **Ignaciosica** [[00:52:13](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=3133)]
I have no idea what's happening.
No, but I don't even like.
No, I don't think he was trying to say it's flaky.
No, it's not flaky.
It's like failing every time.
It's not failing on this PR.
Yes, if you click the last link in the last comment that says benchmarks, Mac benchmark, it links to a test that is failing.
It's like an F right next to the 1206 line.
And that is the test that is failing.

##### **Geohot** [[00:52:51](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=3171)]
And if you go down to the- I just clicked it.
It has a green check mark.

##### **Ignaciosica** [[00:52:57](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=3177)]
Yes, that's what I told, that some tests, depending on the command, it is run, and some benchmarks, it doesn't fail the job, but the test itself, it does fail.

##### **Geohot** [[00:53:11](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=3191)]
Oh, I see.
I mean, I see the printout of the failing test.
Do we just have a bug there where failing tests aren't actually causing the job to fail?

##### **Ignaciosica** [[00:53:19](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=3199)]
Yes, some tests, I saw this happening in different cases, yes.

##### **Geohot** [[00:53:25](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=3205)]
Did we just forget the dash E or whatever it is?

##### **Chenyu** [[00:53:29](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=3209)]
Or pipe failure or something.

##### **Geohot** [[00:53:31](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=3211)]
Yeah, pipe fail.
Yeah.
Does pipe fail not work on Macs?
Did no one test us?

##### **Ignaciosica** [[00:53:36](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=3216)]
I don't know.
I saw it happening in red benchmarks as well for some tests.

##### **Geohot** [[00:53:45](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=3225)]
OK, next time you see this post in Discord too, so more people will be aware of the issue.
And we definitely should fix that.
Yeah, I see the failing test LDS TC test, which is probably a real failure.
But yeah, no, it shouldn't be showing up as a green checkmark.
I don't know why that is.

##### **Ignaciosica** [[00:54:04](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=3244)]
I don't know if there's a Mac, the same CI machine, but I could try to reproduce the bug there.
Because I tried on my machine and on Sivo's machine, and it worked.
The exact same kernel fails for
Yeah.
Otherwise, it's extremely slow to debug this.

##### **Geohot** [[00:54:32](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=3272)]
Oh, I get it.
Yeah, yeah.
If you're throwing it at CI.
I could just give you SSH into one of the CI Macs.
Just be very careful on it.

##### **Chenyu** [[00:54:40](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=3280)]
OK.
Or should we just buy?
Do you want to buy one more Mac?

##### **Chenyu** [[00:54:45](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=3285)]
Sure.
Buy one more.
We can also update the OS for the machine.

##### **Geohot** [[00:54:51](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=3291)]
We mean update the OS.

##### **Chenyu** [[00:54:54](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=3294)]
I saw someone mention the M2 has some issue with the old OS or something.

##### **Geohot** [[00:55:02](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=3302)]
All right.
Well, let's buy one more Mac so that we can have one.
Are there new Mac studios now?
Are there M4 Mac studios?

##### **Chenyu** [[00:55:18](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=3318)]
It's a different machine.

##### **Geohot** [[00:55:19](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=3319)]
Yeah, I know it's a different machine then, but do we want to upgrade our Macs?

##### **Chenyu** [[00:55:26](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=3326)]
Ooh, M4 Macs.
Ooh, that looks nice.
And you're going to buy three?

##### **Geohot** [[00:55:36](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=3336)]
Oh, that's so many.
Kind of expensive.
No, it's expensive.
No, OK, we'll just buy one more M2.
I bet those are cheap on eBay.

##### **Chenyu** [[00:55:50](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=3350)]
Okay.
Very cheap.

##### **Ignaciosica** [[00:55:56](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=3356)]
One more thing is that I don't know if the green boxes are down or replaced, but I was trying to.. I was profiling the continuation of this PR, like the swapping of the local memory, and I was using an inside compute for
Better metrics, but I lost access and I couldn't continue that work.

##### **Geohot** [[00:56:18](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=3378)]
Do you have access to 14?

##### **Ignaciosica** [[00:56:21](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=3381)]
No, I was having access to, I was working on 19.
14, I think, a long time I haven't had access.

##### **Geohot** [[00:56:29](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=3389)]
I'll add you to 14.
Yeah, yeah, yeah.
19 and 18 are gone.
They are sold.
We sold them.

##### **Chenyu** [[00:56:38](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=3398)]
Okay, thank you.

##### **Geohot** [[00:56:39](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=3399)]
Oh, yeah, I'll add you to 19 right now.
14, 14, sorry.

##### **Chenyu** [[00:56:40](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=3400)]
Yeah, yeah, yeah.

##### **Geohot** [[00:56:47](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=3407)]
Cool.
I'll add you to 14.
We'll buy another Mac and get you access to it.
OK.

##### **Ignaciosica** [[00:56:52](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=3412)]
One minor thing is that it's just a question.
If you have a quick benchmark for speed tweaks,
I think I come up with some minor tricks to the search algorithm, but I couldn't back it up with some benchmarks.
So if you haven't any benchmarks to use, I will try to come up with that first before posting the search tricks.

##### **Chenyu** [[00:57:25](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=3445)]
I think the one on CI.
So for inference, we have LAMA and those few kernels.
That's one off.
And you can also round the MLPerf.

##### **Chenyu** [[00:57:40](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=3460)]
OK.
That's it for me.
Thank you.

##### **Chenyu** [[00:57:46](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=3466)]
Yeah, so usually for speed stuff, for MLPerf, I just round one on master, wait about 14 minutes.
You will see the step time.
Then you can round on your new stuff.

##### **Chenyu** [[00:57:58](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=3478)]
OK.
OK, that's good.

##### **Chenyu** [[00:58:06](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=3486)]
Two minutes left.
There are some cloud remote stuff from you, Ian.
I think that's going well.

##### **Geohot** [[00:58:17](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=3497)]
Yeah, I merged in the HTTP server delete yesterday.
I don't know why it's faster, but whatever.

##### **Chenyu** [[00:58:33](https://www.youtube.com/watch?v=_FVcMAtePJ4&t=3513)]
OK, and I think that's it.
Anything else that's not mentioned?
I think that's pretty much it.
Cool.
OK.
Cool.
That was good.
That's it for this week.
Thank you, everyone.
See you next week.
Bye.
