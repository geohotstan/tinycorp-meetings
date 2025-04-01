# 2025-03-31 Meeting

## Meeting Agenda

**Time:** 7am Monday San Diego time (10pm HK time)
- company update
- quantize DSP
- driver / graph runner
- bert, indexing
- scheduler / viz
- tensor core
- webgpu
- onnx
- torch frontend
- retinanet
- other bounties

## Audio

[Youtube Link](https://www.youtube.com/watch?v=7AhKAlaQWNo)

## Highlights

- **[Company Update](#geohot-000004)**: Tiny box V2 green with four 5090s is available for order, shipping in May, priced at $25,000; orders processed based on wire transfer receipt.
- **[AMD MI300X Support](#geohot-000337)**: First milestone achieved for MI300X support, with ongoing optimization efforts in collaboration with AMD.
- **[Quantize DSP](#geohot-000415)**: Achieved 10.54 ms inference time on Qualcomm DSP for MobileNet v2, matching SNPE performance, with delivery planned shortly after April 1st.
- **[Bounties Update](#nimlgen-000809)**: New bounties added: CPU Graph with Clang ($200) and 5090 support in NV backend ($300), listed at bounties.tinygraph.org.
- **[DSP Graph and Memory Planner](#nimlgen-000809)**: DSP graph implemented with TLSF allocator-based memory planner; potential for further refinement.
- **[USB GPU Bounty](#nimlgen-001019)**: $300 bounty for PPC90 support, with initial branch work underway.
- **[CI Stability](#chenyu-001230)**: Addressing AM backend CI hangs by resetting machines and killing Python processes; proposing pre-run Python cleanup.
- **[BERT Optimization](#chenyu-001523)**: BERT training time reduced to 3-3.5 hours, targeting 2 hours; identified 8% slowdown from dropout randomness for optimization.
- **[Memory Planner Enhancements](#qazalin-002614)**: Fused conv backwards to cut memory usage, with visible improvements in scheduler channel updates.
- **[Python Speed Optimization](#geohot-002726)**: Urgent focus on reducing Python execution time, with beautiful MNIST taking 3 seconds on null backend—aiming for 0.1 seconds.
- **[Indexing and ALU Optimization](#geohot-002029)**: Simplifying indexing and ALU operations for faster, cleaner code, with potential Z3 solver integration.
- **[Constraint Solver for Optimization](#geohot-002150)**: Suggested using Z3 constraint solver to optimize kernel performance, starting with index checks.
- **[Scheduler Improvements](#qazalin-002302)**: Added null backend for faster testing (NULL=1) and fixed toposort memory leaks, with regression tests planned.
- **[Tensor Core Support](#ignaciosica-003030)**: Local memory support added for Tensor Cores; working on rewrite patterns and fixing PTX bugs.
- **[WebGPU Progress](#hooved-003253)**: Implemented WebGPU GraphRunner, boosting tiny chat performance by 40%; refining export logic for stateful buffers.
- **[Kernel Graph Renderer](#geohot-004452)**: Proposed JavaScript renderer for kernel graphs to improve visualization, aligning with WebGPU export goals.
- **[ONNX Float16 Handling](#chenyu-004733)**: Addressing float16 casting inconsistencies to ensure compatibility with key models like comma and top hogging face.
- **[Torch Frontend Fixes](#chenyu-004900)**: Resolved stride issues and path test failures, nearing completion of Torch frontend integration.
- **[RetinaNet Training](#flata-005011)**: Achieved 0.3396 accuracy (target 0.34) with batch size increased to 102; eval slowdowns noted for future optimization.
- **[Multi-GPU Training Progress](#geohot-005511)**: Advancements in multi-GPU training, focusing on test ops and Torch backend integration.
- **[Cloud=1 Intern](#geohot-005822)**: Cloud=1 intern starting in May to accelerate development efforts.
- **[Tensor Core Bounty for 9700 XTX](#geohot-005922)**: $150 bounty to fix Tensor Cores on 9700 XTX, deemed an approachable task.
- **[Linearizer Fixes](#geohot-010013)**: Merged linearizer fixes, but test failures persist; further review needed.
- **[F8 Support PR](#geohot-010242)**: PR for F8 support (adding two new Dtypes) is ready for merge after review.
- **[Viz Feature Reversion](#geohot-010351)**: Reverted copy button in Viz to maintain minimalism, favoring intuitive behaviors over added features.

## Transcript

##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=0)]
Let's start with company update.

##### **Geohot** [[00:00:04](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=4)]
So the biggest thing, yes, yes, we have our first tiny box V2 green.
It has four 5090s in it.
The 5090s are really incredible.
Uh, we're taking, so we're not going to do pre-orders this time.
It's always such a hassle to like track people down and then people want refunds for their pre-orders.
None of that this time, but the order link is live on the website.
Um, if you send a wire, you're in line.
Uh, I'm not gonna, I'm not gonna rug you.
Uh, tiny corp has over $5 million in the bank.
We've actually made money, uh,
Comma finally paid us for the servers, so we actually have more money right now in our banks than what we raised.
And if you want a tiny box V2, I have all the 5090s in pre-order.
You can buy one, send me a 25K wire, and then the orders that the wires come in is the orders that they will ship.
We're looking at shipping the first ones in May.
I feel comfortable doing that now that we have one.
It has a 32-core Genoa chip, 192 gigs of RAM, four 5090s, two nice power supplies, the same four terabyte RAID array, a one terabyte boot drive.
It's a great computer.
And if you're looking for the best way to do machine learning at home for the best price for $25,000, you can buy a tiny box green V2.
So you can order now and you can send the wire whenever, but the shipping order is the orders that the wires are received.
If you place an order now and don't send the wire, I'm not going to cancel your order.
I will just send you an email saying, hey, your box is in stock.
Send a wire.
And then whatever order I get the wires in is whatever order I'll ship the boxes in.
So yeah, exciting stuff.
We have a TinyBox V2 Green.
I think this is going to be by far our best-selling TinyBox.
I think we're ahead of all the curves on this.
I've been testing it.
No AERs between the GPUs.
No AERs to the drives.
The motherboard seems to be more solid than the motherboard in the TinyBox.
So I'm happy about that.
Yeah.
Tiny box, green V2s, $25,000, place your order today.
No pre-orders, no money, just order it, send the money.
Whatever order people send the money in is the order they'll ship in.

##### **Chenyu** [[00:02:45](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=165)]
Sounds good.
Okay.
Uh, that's it for company update?

##### **Geohot** [[00:02:59](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=179)]
I think so.
Yeah.
Oh, and
Our back end now works with the MI300X.
There's still some work to do, but congrats to UUVN for claiming that bounty.
There's still some work to do on making it fast.
We're in contact with AMD, but you guys all know that we got two, eight MI300X machines from AMD, and we're going to work hard to make sure TinyGrad supports them well.
So yeah, that's the first milestone has been achieved for that.
So I guess that's kind of a company update.

##### **Chenyu** [[00:03:37](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=217)]
Sounds good.
OK.
For people who's new to this meeting, we will go through a bunch of active projects.
And people who are working on these will share the progress on this stuff.
And at the end we would have like some discussion for other open bounties or another related topics that you may have questions, since we @everyone, we will accept like problem, like questions, problems, and some discussion at the end.
With that, let's move on to Quantize DSP.

##### **Geohot** [[00:04:15](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=255)]
So another very exciting thing, uh, we got a contract, uh, from a startup.
Right at the beginning of the year, so about three months ago, if we could get MobileNet v2 to run on the Qualcomm DSP in under 13.5 milliseconds by April 1st, and today we just got our first 10.54 millisecond time.
which is very similar to SNPE, and with all the generic flexibility of TinyGrad.
There's a little bit of hand-coded stuff, but not really that much.
The DSP fits into the Qualcomm paradigm so well.
It fits into the TinyGrad paradigm so well, just making sure that you lay your memory out correctly, because if the DSP is bad, it is swizzling.
But the DSP represents really the...
GPUs burn a lot of power on hardware managed caches and on warp scheduling.
The DSP really has a software managed cache and no warp scheduling.
So it's kind of the ultimate machine for machine learning if you want to target something.
The chip that we're eventually going to build is going to look a lot like the Qualcomm DSP or the Google TPU and a lot less like a GPU.
And the beauty of TinyGrad's flexibility is that we can support anything generic at a TinyGrad abstraction layer
compiled down to a machine that has very little friendly power burning stuff in hardware, right?
The warp scheduler, the memory coalescer, all of this stuff is just burning power in your GPU.
And if you are very clever with your software, you don't need it.
But also this architecture doesn't have to be crazy like Tenstorrent's architecture.
We don't need a new architecture.
We can make stuff that looks like a simple VLIW machine
that operates on long vector words and has some matrix extensions and can do everything.
So the Qualcomm DSP really represents a
I now also see all the ways to make GPUs fast.
If you can make things fast on the Qualcomm DSP, you can make things fast on GPUs.
The Qualcomm DSP is a SIMD machine.
GPUs are SIMT machines.
They're similar, but GPUs have really good memory coalescers and really good... I mean, you have warp scheduling, so you have high memory latency.
So GPUs are just DSPs with extra stuff that's totally optional to use, but it does always sit there burning power.
So Qualcomm DSP in a branch.
But it's a testament to the quality of what TinyGrad can do that you can get speed on that chip at all.

##### **Chenyu** [[00:07:09](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=429)]
What time zone is that, April 1st or whatever?

##### **Geohot** [[00:07:15](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=435)]
They said we could be a few days late.
I baked in a few days late is fine.
But yeah, I think we'll try to deliver it tomorrow.
And that would be yeah, definitely.
So we actually have two days because we are we're in the future.
We have an office, by the way, in Hong Kong, a whole bunch of people are here right now.

##### **Geohot** [[00:07:35](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=455)]
So if you start contributing to Tinygrad, claim a bunch of bounties, we'll invite you out to the next one of these.
So if you want to come to Hong Kong, and work with Tinygrad team, you know, start solving bounties.

##### **Chenyu** [[00:07:53](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=473)]
Cool.
And since it's semi-related, I just put Nimlgen's stuff next.

##### **Nimlgen** [[00:08:09](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=489)]
Uh, yeah, so yeah, so yeah, I've been working mostly on the base previously.
So yeah, we got base big graph and, uh,
So yeah, we've got DSP graph, we've got new memory planner.
And let's try the DSP now.
So still, I mean, still we might... Yeah, so actually for the memory planner, I can...
So we use, like, an inline solution using TLSF allocator instead of, like, to solve offline problems.
So potentially, if somebody wants, this could be improved.
Yes.
And also for... I don't know we want to consider this as bounty, but... So the CPU graph should actually potentially work with the Clang runtime.
But it doesn't right now, because of some relocations which we're missing.
So probably maybe that's a good bounty for someone.

##### **Geohot** [[00:09:23](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=563)]
Yeah, I mean, we should be able to make it like a slab of x86 code and jump around in it.
I think that's a good bounty.
Yeah, I'd put 200 bucks on that with tests, if someone wants to get CPU Graph working on Clang.

##### **Nimlgen** [[00:09:42](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=582)]
Basically, we need to pass in CI and test it out, and that should be fine.

##### **Geohot** [[00:09:49](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=589)]
Cool.
Yeah, no, good work on the DSP stuff.

##### **Nimlgen** [[00:09:52](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=592)]
Yeah, we also got RDNA in merged this weekend, RDNA4.
Supporting to AM, yeah, I think our AMs, it's pretty refactored before MI300 for UUVN to work.
So yeah.

##### **Geohot** [[00:10:08](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=608)]
Great.
Back to the USB GPU next week?

##### **Nimlgen** [[00:10:19](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=619)]
Oh, yeah, I think.
Would we consider PPC90 as bounty as well?

##### **Geohot** [[00:10:28](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=628)]
Oh, yeah.
I'd put a bounty on that.
How hard do you think it is?

##### **Nimlgen** [[00:10:34](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=634)]
I don't know.
I think if there is access to 5090, that's not really part.
I mean, I definitely can see like the same things like but yeah, they're a bit shuffled compared to the previous QMD we have right now.
But yeah, it should be similar.
Should be similar.

##### **Geohot** [[00:10:54](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=654)]
$300?

##### **Nimlgen** [[00:10:55](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=655)]
Yeah, I think so, yes.
Sounds good.
Yeah, and I have a branch which implements some of the initial support for 5990.
Yeah.

##### **Geohot** [[00:11:11](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=671)]
Great.
All right, we got two new bounties out of that.
CPU graph working with Clang and LLVM.
I think you got to do both.
$200.
And then 5090 support in NV backend. $300.
If you guys don't know, you can go to bounties.tinygraph.org and you can see all the open bounties.
They're a little bit of a mess right now.
I should probably sit and reorder these.
But I just added the two new ones right there at the top.
And I think that's what we'll do from now on.
They won't be ordered by money anymore.
They'll just kind of scroll in from the top like an infinite feed.
So yeah, CPU Graph working with CLANG LLVM, $200, 5090 support NV backend.
And then, yeah, we're back to the...
How many more weeks do you think for the USB GPU stuff?

##### **Nimlgen** [[00:12:10](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=730)]
I don't know.
I think maybe a week or two next year.
If that is available.

##### **Geohot** [[00:12:23](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=743)]
Sounds good.

##### **Chenyu** [[00:12:30](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=750)]
We also really want some stable solutions for our CI machine with AM backend.
Because it's quite, at least it happened a few times today or in past week, that it just hang during the BEAM job or some other jobs, then the subsequent CI run will fail.
Then I need to reset the machine.
find a PID to kill it.

##### **Geohot** [[00:12:59](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=779)]
Do we know why this is happening?
I mean, we should probably just fix CI by killing all the Pythons in the beginning.
Like, let's just kill all Python except for the current running one.

##### **Chenyu** [[00:13:15](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=795)]
I'm not sure.

##### **Geohot** [[00:13:17](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=797)]
But that fixes CI.
We can definitely fix CI with that, but we should also.

##### **Chenyu** [[00:13:23](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=803)]
We want to make sure it's not.
We want to handle this better, basically.

##### **Geohot** [[00:13:34](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=814)]
Yeah, I mean, we should figure out what's causing it to hang.
I think that that toposort thing changes things, points to use after freeze and stuff.
But I think we should add something to CI that kills the Python jobs in the beginning.

##### **Chenyu** [[00:14:04](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=844)]
That makes sense.
OK, I'll check that.
Next time we see it hang, I just reset both machine.
Hopefully it's good now.

##### **Chenyu** [[00:14:16](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=856)]
Okay.
Moving on.
The next one is for BERT, for MLPerf.
We have about one month left.
Our current time is somewhere between three hours and three hours and 30 minutes.
We don't have any quick fix or big win now.
We need to improve.
If we want to hit two hours, which is pretty aggressive, then we need 50% faster, in which case a lot of it really needs to come from layers
has 24 identical layers, which is basically just attention and normalization, which is just basically GEMM and softmax and normalization.

##### **Geohot** [[00:15:23](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=923)]
How much are we wasting still on the dropout randomness?

##### **Chenyu** [[00:15:30](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=930)]
So if we remove dropout, it's like 8% faster.
So I don't know about wasting.

##### **Geohot** [[00:15:39](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=939)]
I mean, that's all wasted pretty much.
That should be free.

##### **Chenyu** [[00:15:44](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=944)]
Why is that free?

##### **Geohot** [[00:15:47](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=947)]
That should take no time.
It's an element-wise multiply with a threefry.

##### **Chenyu** [[00:15:58](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=958)]
And you also need to generate those kernels.

##### **Geohot** [[00:16:04](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=964)]
What do you mean generate the kernels?
They should be in the JIT.

##### **Chenyu** [[00:16:08](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=968)]
No, generates the threefry kernels.

##### **Geohot** [[00:16:13](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=973)]
No, but I mean, that should be so fast on a GPU.

##### **Chenyu** [[00:16:20](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=980)]
Yeah, the problem is it's not fast.

##### **Geohot** [[00:16:24](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=984)]
Yeah, I mean, we got to look into that.
That 8% is like all waste.
It should be 1% at max.

##### **Chenyu** [[00:16:30](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=990)]
Yeah, sounds about right.

##### **Geohot** [[00:16:32](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=992)]
I think that's a good place to look this week.
I think we should look into that.
And see what we can do for embedding.

##### **Chenyu** [[00:16:45](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=1005)]
Oh, yeah.
So fuse embedding saves 7 milliseconds, which is another 2% or forward.
It's just relatively small, so probably
Yeah, we'll looking to threefry randoms.
Our forward is also, I think our forward is about 400 TFlops.
Oh, 40% utilization rates.
Our layer per layer forward and backward is 320ish TFlops.
So it's not too bad, but also kind of not fast enough.

##### **Geohot** [[00:17:43](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=1063)]
Can we get TinyGrad to export a pie chart?
Just use all the metadata.

##### **Chenyu** [[00:17:55](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=1075)]
Pie chart?
Of What?

##### **Geohot** [[00:17:56](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=1076)]
Yeah, like a pie chart that shows the breakdown of the model and where time is being spent.

##### **Chenyu** [[00:18:10](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=1090)]
Yeah probably.
I'll look into that.
I got the number by ablate stuff.

##### **Geohot** [[00:18:18](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=1098)]
Yeah, we should make this easier.
We should almost add a panel to Viz that just shows you a pie chart of where your model's spending time.

##### **Chenyu** [[00:18:25](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=1105)]
Yeah, but a lot of stuff are fused together.

##### **Geohot** [[00:18:30](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=1110)]
Well, I mean, what do you mean by that?
It's not like Softmax is just one.
It'll say Softmax in the metadata.

##### **Chenyu** [[00:18:41](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=1121)]
Yes, and your softmax backward is fused with some other backward.

##### **Geohot** [[00:18:47](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=1127)]
Yeah, I don't know.
Some good way to express this, maybe on the profiler window.
We should definitely work on tooling around this.
Also, we need to make it faster.

##### **Chenyu** [[00:18:59](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=1139)]
OK, sounds good.
Also spend some time with indexing because the DSP project also have a lot interesting use case, the upcast of 128 and the split for stuff.
So fix something.
There are more stuff that can be fixed.
A lot of lists is similar to other optimization.
Like if we have a range and we do upcast or like
And on that, we also want the output to be fused properly.
And in this case, there are valid case and optimization cases, which might long-term eventually be merged into the Z3 solver.
Basically, we want a better way to write this constraint on indexing.
So for the kernels and the indexing, we spend a lot of ALUs are computing what's the index that we are accessing.
And if we are masking, because if you do a pad or if you do a conv, those are a lot of it really boils down to the mask and the index.
So being able to simplify those will make your code simpler and faster.

##### **Geohot** [[00:20:29](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=1229)]
So to get at your question from before about what simpler means, I mean, you really don't want to do this in isolation.
You really want to ask the question for the entire kernel, what's the simplest expression of all the ALUs jointly?

##### **Chenyu** [[00:20:47](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=1247)]
Yeah, but there are cases for do you want
It's similar to a question for padding for multi-GPU.
I think we said, OK, if we want to pad to the multiple of, that would be simpler, because now every GPU is running the same set of kernels.
That's simpler in that sense, but not, say, for ALU, right?

##### **Geohot** [[00:21:23](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=1283)]
No, I mean, so here's kind of how I think about all of these things in general.
Imagine taking a GPU cycle-accurate simulator and then putting the cycle-accurate simulator in a constraint solver and saying, find the thing that accomplishes this math in the lowest number of cycles.

##### **Chenyu** [[00:21:45](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=1305)]
Yeah, so that would be the fastest, but not the simplest.

##### **Geohot** [[00:21:50](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=1310)]
Well, yeah, but that's what we really want.
We don't want the simplest.
We want the fastest.

##### **Chenyu** [[00:21:57](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=1317)]
Yeah, that I agree.
But a lot of what's fastest might not have a universal form or a fixed order of rules to apply.

##### **Geohot** [[00:22:11](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=1331)]
No, I agree.
And that's why I think we need a constraint solver.
I think we should just start moving to it.
I know it sucks to add Z3 as a dependency.
maybe the first thing to put in Z3 is the... So you said today there was a bug with the Vmin and the Vmax getting the out-of-band stuff.
I mean, we should be able to very easily put that index check in Z3.
And it should also work with masks, too.

##### **Chenyu** [[00:22:47](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=1367)]
Yeah, okay.
We'll look into it.
Cool.
OK.
Moving on to scheduler.

##### **Qazalin** [[00:23:02](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=1382)]
Right.
So a bunch of new tooling in Viz, mostly in the background.
You can now recenter the Viz graph.
So it will scale things correctly.
And I also added the null backend.
This was George's idea.
The null backend, if you put null equals 1, you can run anything.
And this will just compile.
So you don't need a heavyweight processor to run BERT and stuff.
It really lets you see things quickly.
It's also a nice test for how slow our Python time is.
Beautiful Mnist takes 3 seconds on the null backend, which is a lot.
So yeah.
We have that one too.
We merged the toposort fix.
It was causing some memory leaks.
I haven't seen it be reflected in the CI yet.
Maybe it will reveal some stuff that we were doing that was wrong.
So yeah, that was last week.

##### **Chenyu** [[00:24:24](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=1464)]
So is the memory leak fixed with that?

##### **Qazalin** [[00:24:27](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=1467)]
Yeah.

##### **Chenyu** [[00:24:29](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=1469)]
Should we respond to the issue or saying it's good for them to do a release or something?

##### **Qazalin** [[00:24:37](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=1477)]
Yeah, I'll post on the issue as well,
and test it with his repro.

##### **Geohot** [[00:24:46](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=1486)]
Great.
Do we have a regression test?
We should write a regression test, too.

##### **Qazalin** [[00:24:54](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=1494)]
Yeah, I think we talked about this today.
Probably something in test_gc to test it explicitly, count the number of alive UOPs.

##### **Geohot** [[00:25:03](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=1503)]
I mean, almost if we can just take commas thing exactly.
However you verified it, just take exactly that and put it in CI if we can do that.

##### **Qazalin** [[00:25:13](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=1513)]
I'll look into it.
The fix is a bit two staged.
You have to pickle first, and then unpickle.

##### **Geohot** [[00:25:21](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=1521)]
Yeah, OK.
Maybe not that test.

##### **Qazalin** [[00:25:23](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=1523)]
Yeah, not that test, but something that's approximated.
Long term, we would want to almost have a graph of the alive Python objects as anything in Tinygrad is running.
And we also talked about disabling gc.collate and see what happens.
Ideally, you wouldn't want TinyGrad to have any cycle references, which require the GC to function.

##### **Geohot** [[00:25:53](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=1553)]
Yeah.
I think this and the null thing is a good segway into the other thing that I wanted to call everybody to this meeting for.
You got anything else?

##### **Qazalin** [[00:26:08](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=1568)]
Please go ahead, yeah.

##### **Geohot** [[00:26:10](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=1570)]
Oh, you want to talk about the memory too?

##### **Qazalin** [[00:26:14](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=1574)]
Oh, the memory graph, yeah.
In the scheduler channel, if you look into it, there is a before and after of beautiful MNIST if we fuse conv backwards.
I'm going to look into that.
This is going to be a fun project just to segway into the grouper.
We are wasting a ton of memory on storing the output of a conv backward expanded.
when we could actually just use it.

##### **Geohot** [[00:26:47](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=1607)]
Did we have this problem for ResNet?
Could our ResNet be, like, way better?

##### **Qazalin** [[00:26:56](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=1616)]
If it uses conv, I would expect.
I can visit and show it later.
But yeah, you can actually see this now.

##### **Chenyu** [[00:27:05](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=1625)]
I think the memory planner already saved, like, 30% of memory.
20%, 30%.
And I imagine more was this.

##### **Geohot** [[00:27:20](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=1640)]
Maybe the memory planner can just hide this.
But yeah, so my segway into why I called everyone here.
So tinygrad has a bit of a crisis right now.
So you can go to stats.tinygrad.org.
Stats.tinygrad.org is where we track
time and you can take a look at llama uh 7b unjitted i'll post i'll post a quick screenshot of it and you can see that that time has gone one direction and not the good direction so unjitted means it's just like actually running all the python and tinygrad and you can see that it's become egregiously slow
Like we went from like, yeah.
It's like now two seconds a token.
Down from it used to be 100 milliseconds a token, even when it was like 500, not that long ago.
But it's just getting so slow to run the Python in TinyGrad.
So what we need is people who are good at making Python fast.
I'm sure we have tons of absolutely stupid things like the toposort thing where we're just doing just really suboptimal things.
So if people want to come work on Python speed, it's a great thing to work on.
We need to make the Python faster.
I think it's an addictive loop.
Run beautiful MNIST with null equals one.
It should not take three seconds.
It should take 0.1 seconds.
It should be 30 times faster than it is now.
And don't tell me Python's slow, because it's not Python that's slow.
It's our usage of Python that's slow.
Yeah, no, that's the wrong rocket.
We wanted to go the other way.

##### **Chenyu** [[00:29:26](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=1766)]
Okay.

##### **Geohot** [[00:29:27](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=1767)]
These all look pretty bleak.
No, I mean like stable diffusion.
Stable diffusion looks good.
It's moving in a good direction, but yeah.
Yeah, we need help with Python speed.
No ML knowledge required, just make the Python good.
Nope, I don't know where the milliseconds are going.
That's what I need you for.

##### **Chenyu** [[00:30:05](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=1805)]
It's similar to GPT-2 unJITted.
It's probably rewrite.
OK, anyway, let's move on.
Next, Tensor Core.

##### **Ignaciosica** [[00:30:30](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=1830)]
Hi.
Well, last week I've been mainly working on adding support for LDS that it's basically being able to cache into local memory.
I think the naive support for that is almost done.
Now I'm trying to fix one bug with PTX that it's currently broken local for PTX.
And once that is solved, I'll improve a little bit more the test.
And I will get support merge and then start working on the search.
And over the weekend, I've been starting to think how to make the TensorCores into a rewrite pattern.
And I think I got it in a PR today still needs a lot of cleanup.
But I think it's the first step into making the kernel.py way more simpler.

##### **Geohot** [[00:31:41](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=1901)]
Cool.
One of the things I was thinking about with the GPU stuff is potentially what we could do is take the warp and make it an unroll.
We could unroll the warp, and then the tensorcore pattern would be a lot simpler to express if you actually have access to all the multiplies.
So if the thing's unrolled, the tensorcore gets put in there with permutes, and then those permutes are basically GEPs, and then you push those GEPs back to the load, and that's how it has to do the load differently.
So we don't actually have to do it at the shape tracker level then.
We could do it one level lower than the shapetracker.
But it's probably basically the same stuff.
It's just a question of whether we want to do it in kernel.py, in the lower, in the expander.
The LDS stuff is very exciting, and I'm excited to have that merge.

##### **Ignaciosica** [[00:32:39](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=1959)]
Cool.

##### **Chenyu** [[00:32:45](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=1965)]
Next, WebGPU.
I see Hooved here.

##### **Hooved** [[00:32:53](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=1973)]
yeah so in the web gpu export refactor I got rid of the redundant data the data classes that were redundant with capture jet and exec item and I.
implemented WebGPU GraphRunner.
And I refactored OpsWebGPU so that the GraphRunner as well as just the non-graph execitems are basically using mostly the same logic.
So it's not that many lines to add the GraphRunner.
And I wasn't really expecting this, but it's tiny chat and browser is now 40% more tokens per second using the graph runners.
So that's nice.
But so I did those things, and I added a helper function to captureJIT so that captureJIT can tell you which of its internal buffers are stateful in terms of having state that we want to export.
So I did those things.
I'm still cleaning some things up.
I annotated.
There's still an export.py in TinyGrad with stuff that doesn't seem to fit well in the JIT or elsewhere.
So I put some notes at the top of that file with what those things are.
I'm still thinking about it, seeing if I can try to integrate stuff into TinyGrad better.

##### **Geohot** [[00:34:37](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=2077)]
Cool.
I'm looking at the PR now.
Are there small PRs of pieces of this?

##### **Hooved** [[00:34:44](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=2084)]
Oh, no.
I mean, that would be the next step.
Yeah, that's what we would do before anything's ready for review.
But if I could just get any feedback that this is the right direction, that would be very helpful.

##### **Geohot** [[00:35:03](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=2103)]
Well, I see a function called sort buffs in the JIT.
I don't understand that.

##### **Hooved** [[00:35:08](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=2108)]
Yeah, maybe I should rename it.
That's the logic that tells us which of the buffers in the JIT have state that should be exported from TinyGrad.

##### **Geohot** [[00:35:23](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=2123)]
So I totally agree with a function that does that, but be careful with your names.
So in TinyGrad, there's no such thing as a weight.
There's nothing that makes a weight a weight.
So they shouldn't be named that.
They should be named explicitly what they are, which is stateful buffers.
That's a much better name.
Like buffers that have persistent state across multiple runs of the JIT.
And then there's persistent ones that get updated, persistent ones that don't get updated.
But I would think about how less to like treat it like like I see this comment here that says for model export, instead of treating it like a function that you're going to call into, think about how you can expose that property on the JIT and think about what that property really means.
But I agree with you that the weight buffer should definitely expose that, or the buffers in the JIT should definitely have a way to expose that property, which is, is this something that I'm going to have to save when I export?
I mean, that's simply...

##### **Hooved** [[00:36:36](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=2196)]
I could refactor that so it's not a helper function and it's just an attribute of the captureJIT.
Or I could maybe even add properties to buffer and device.py.
Maybe not.
But yeah, we can make it not a helper function and something that just gets run.

##### **Geohot** [[00:37:00](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=2220)]
I don't think you could know it on the buffer.
The specific way that you detect this is, in a JIT, is the buffer read from before it's written to?
If the buffer is read from before it's written to, then it has state.
If the buffer is written to before it's read from, then it doesn't.

##### **Hoove** [[00:37:21](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=2241)]
Right, that's the logic in the helper function right now.

##### **Geohot** [[00:37:25](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=2245)]
Well, yeah, but so one of the things that makes TinyGrad different from frameworks like PyTorch is we always try to really get at the root of what things are.
So PyTorch might have something called a convolution.
TinyGrad has nothing called a convolution.
We have something in our front end called convolution, but it's really just a bunch of movement ops, a binary op, and a reduce op.
So the same sort of thing applies here, right?
TinyGrad has no concepts of, Torch calls them weights and parameters and all of these things.
We don't have anything like that.
I mean, the question is really like, given a capture JIT and a buffer, is this buffer read to before it's written?
So yeah, I would think about how to express things like that and how to use the terminology that is generic from all specifically what is this to what is the underlying concept.

##### **Hooved** [[00:38:30](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=2310)]
OK, yeah, I mean, I'll try to think about that and maybe
It's pretty abstract, so why don't I, in the next few days, just post some ideas in the WebGPU channel if I feel like I make progress on that.

##### **Geohot** [[00:38:47](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=2327)]
Sounds good.

##### **Chenyu** [[00:38:49](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=2329)]
And also, I think you can check how the memory planner is working.
Because it has a very similar level of abstraction.
Memory Planner basically concerned about can you reuse a buffer because it's no longer needed or it has a similar property on this.
And you can check how it's done and what kind of helper function or basically the way to think through that problem.
might find some similar ideas.

##### **Hooved** [[00:39:27](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=2367)]
So I think I remember seeing the memory planner either in the JIT or the scheduler.
Is there a specific schedule.py?
Or is there a specific thing I should look at in the code?

##### **Chenyu** [[00:39:45](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=2385)]
I think it's in some memory, memory.py or something.
But it's more of a...
So in memory planner, I think the idea is more clearly expressed in terms of here is your graph for the kernels you are going to run and the buffers attached to that.
And the problem memory planner is trying to solve is given that's the case, what's the minimum memory we need to allocate to such that this can run.
And I think for your case, given this capture JIT, what are the states that you need to export, the state for buffers that you want to export?
It might help you to think about expressing the problems and understand what it really is.

##### **Hooved** [[00:40:43](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=2443)]
OK, I'll look into that.
Thank you.

##### **Geohot** [[00:40:45](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=2445)]
Also, I generally like the direction with graph.
I think that's pretty much the right way to do it.
Instead of that being a function called render JS, I think a method on web GPU graph that exports the JavaScript to run the graph.
I think that's probably the right place to put that.
And then when you have, I see these helper functions, copy buffer to buffer and execute commands.
These need types.
Device, divine, compute, and wait.
I need to know what those things are.

##### **Hooved** [[00:41:16](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=2476)]
For sure, I need to clean that up.
But one thing that, so like, yeah, I can try to factor stuff into the WebGPU graph class.
But most, or I would say almost all, of that render JS stuff is at a level of abstraction above the graph.
It's just like, it includes allocations.
I think you might have mentioned that.
But it includes just like everything
that you would use to run WebGPU in JavaScript.
And the graph runner really maps to the command encoder, which is like some small, like a few lines of that code, honestly, out of...

##### **Geohot** [[00:41:57](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=2517)]
Yeah.
Yeah, so you probably want to, yeah, maybe you do want this more on a captured JIT.
And there's some method.
But either way, I think using the graph abstraction is a good idea.

##### **Hooved** [[00:42:12](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=2532)]
I agree, for the command encoder.
And yeah, it's a nice speed increase as well.
So are you suggesting that maybe I can move the rendered JavaScript stuff to the JIT and make it a function on the captured JIT?

##### **Geohot** [[00:42:28](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=2548)]
Well, maybe.
The idea with this is to think about how you want to like, like, I understand that it's exporting it to a different programming language.
But yeah, I mean, it probably shouldn't exactly be one function, right?
It should be like, oh, this supports conversion, like, like, I have some converter, which can convert buffers to JavaScript, which can convert command queues to JavaScript or graphs to JavaScript.
And then all that stuff lives somewhere.

##### **Hooved** [[00:43:01](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=2581)]
Yeah, the problem I've been facing, and it just feels like all that stuff, all this JavaScript stuff, doesn't have a good place to live because there's nothing else in TinyGrad as far as I can immediately think of that does that.
So I've sort of been struggling with where all this ugly JavaScript stuff should live.

##### **Geohot** [[00:43:22](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=2602)]
I mean, actually, there sort of is.
So like, okay, the abstractions totally aren't ready for this yet.
But really what I think this is, is if you have a, so everything in TinyGrad is UOps.
And the closest thing that this JavaScript thing is, is a renderer.

##### **Hooved** [[00:43:41](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=2621)]
Right, I understand that.
But we're not really rendering kernel code.
This is just rendering an external runtime.

##### **Geohot** [[00:43:52](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=2632)]
What's the difference?
So go run with VIZ=1, and look at Beautiful MNIST, and look at the kernel graph.
This is the right abstraction for this.
So do VIZ=1, and run examples/beautiful_mnist.py.
and then look at the kernel graph.
Really what this should be is a renderer on that.
It includes the buffers.
It includes the property of the buffers that you're talking about.
I mean, this is a big refactor, but I think this is the direction these things kind of have to go.
So if you click Schedule 121 Kernel, I'll post a screenshot in a minute, and then you click View Kernel Graph.

##### **Hooved** [[00:44:49](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=2689)]
Are you posting this in general?

##### **Geohot** [[00:44:52](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=2692)]
Yeah, I'll post it in general.
I think this is good for everybody, too.
It's kind of exciting.

##### **Hooved** [[00:44:59](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=2699)]
Yeah, I don't quite understand what you're saying, but I just need to actually see it and play with it.

##### **Geohot** [[00:45:04](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=2704)]
So this is a kernel graph.
This is the beginning of an MNIST kernel graph.
You see how it includes the buffers, the kernels, and then assign?
So really, I think what you want to do, and this is a new thing that doesn't quite exist in TinyGrad yet, but I think what you want to do is write a JavaScript renderer on the kernel graph.
It's different from the other abstractions, but you're right, there's no place for it, but I think this is the right place.
Eventually, I want everything to become graph rewrite.
Eventually, I want the entire TinyGrad to take it all the way from a model all the way to the command queues that actually execute on the GPUs to the malloc functions put into a compiled C runtime or something.
But yeah, something to think about.
Maybe we're not ready for it yet.
But I think there's definitely intermediate refactors that can be done in the meantime.

##### **Hooved** [[00:46:17](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=2777)]
Yeah, I mean, a lot of the stuff in, sorry, I know we're going long, but a lot of this JavaScript boilerplate stuff still does map to the stuff in ops_webgpu, like allocations and stuff like that.
I mean, I could try to put it next to that.
like factor stuff so that you can see the Python and JavaScript side by side.
And as for the ambitious topic you just outlined of the kernel graph, it's pretty intriguing.
But it would really help if I, maybe even from another project, saw an example of that.

##### **Geohot** [[00:46:56](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=2816)]
I don't think anything like this exists anywhere.
But I think this is the direction this stuff is going in.
But yeah, no, I think this is probably too much to bite off.
And I think there's definitely a way to get the export stuff in that won't be disrupted for the rest of TinyGrad in a simpler way.
And then hopefully, we can keep the test consistent while we refactor into this.

##### **Hooved** [[00:47:14](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=2834)]
All right, thank you.

##### **Geohot** [[00:47:16](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=2836)]
Cool.

##### **Chenyu** [[00:47:19](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=2839)]
Cool.
OK, ONNX.

##### **Geohot** [[00:47:19](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=2839)]
Still stuck on float16.

##### **Chenyu** [[00:47:33](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=2853)]
Yeah, apparently everyone is doing different things for float16.
So I think the bottom line is
I think bottom line is the comma model should run correctly, and the top hogging face model should run correctly.
Adding a flag for now is probably fine.
I think the issue is we still don't understand this in the sense that what are other runtime, what are they doing?
Are they all use this same casting thing?
If that's the case, we just should be fine if we do that.
So the models we care should run correctly.
And otherwise, we understand what other people are doing.
And we either match them, or if we don't match them, we have a good reason not to match them.

##### **Geohot** [[00:48:39](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=2919)]
I like that.

##### **Chenyu** [[00:48:44](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=2924)]
An unusual join activity detected in TinyGrad.

##### **Geohot** [[00:48:49](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=2929)]
Yeah, we got a lot of Twitter people in here for the meeting.
OK.

##### **Geohot** [[00:48:56](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=2936)]
I'm sure that's the problem.

##### **Chenyu** [[00:49:00](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=2940)]
Torch frontend.
So tocubed helps solving.
So for the test ops PR, there's one lasting issue with one path test and fix some stride issue because apparently for torch frontend you need to keep track of strides.
So hopefully that fix the last thing the last thing and we can merge that.
Don't know if anyone
Working on that is in this meeting.

##### **Geohot** [[00:49:48](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=2988)]
And tocubed has been doing most of the work on it.

##### **Chenyu** [[00:49:54](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=2994)]
Anyway, if anyone in this meeting was or is working on Torch frontend and stuff, and I cannot see you, just post in general, and you can talk.
Otherwise, let's move on to RetinaNet.

##### **Flata** [[00:50:11](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3011)]
Hello.
So finally fixed the loss explosion on the FP16 training.
I think I posted an update on the retinanet channel.
So we've been able to achieve the required metric of 0.34.
So I think my goal now is to just clean up the main PR.
So it's just going to be mainly the training loop.
So I'm going to hopefully put up one more PR on the model eval changes.
And I think that's about it.
And then I think maybe, Chenyu, you can start reproducing it, hopefully, later this week, once I clean up the PR.
I think I probably still need to add the MLPerf logger, but I want to see that you're able to reproduce the training runner first.

##### **Chenyu** [[00:50:57](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3057)]
Yeah sure, the MLPerf specific thing can happen after this is merged.
It's not required for your first part of the bounty.
But I would say 0.3396 definitely doesn't count as 0.34.

##### **Flata** [[00:51:16](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3076)]
Yeah, it was very conflicted with the .. 

##### **Chenyu** [[00:51:21](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3081)]
It's probably some noise.
And it's very likely that if you run it again, it would pass.
But generally, we don't round up for accuracy.

##### **Flata** [[00:51:33](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3093)]
Okay, sounds good.
I do think it's in the right direction for sure.

##### **Chenyu** [[00:51:37](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3097)]
Yeah, for sure.

##### **Flata** [[00:51:40](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3100)]
Oh, yeah.
Also, one thing I wanted to call out was when I tried to BEAM on the eval, for some reason, I think it's returning values.
Even I did some sanity checking by just kind of preloading the existing retinanet pre-trained models.
And for some reason, it's not really kind of returning the correct values.
I guess, outputs for some reason, because there's some post-processing detections function that gets run.
And what ends up eventually happening is that every output gets filtered out.
So it kind of counts as nothing, basically.
So something that needs to be investigated, but I don't think it's a blocker right now.
But I do kind of want to do that as definitely follow-ups to optimize the eval step to make it faster.
Because I do want to rewrite that post-processing portion as well in its own as a JITed tinygrad version of it.
So I do want to call that out still.

##### **Geohot** [[00:52:36](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3156)]
I'm looking at your MLPerf here, and I'm looking at the GPU fan graphs.
The eval is taking forever.

##### **Flata** [[00:52:44](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3164)]
Yeah.

##### **Geohot** [[00:52:45](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3165)]
You're spending half your time on eval.

##### **Chenyu** [[00:52:48](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3168)]
Yes.
Eval is very slow.
Uh, so for the beam stuff, usually how this works is if you can distill it down to like a single kernel and say, okay, this action on this kernel has issue, then, uh, we can take a look.
Otherwise it's very hard to say, okay, this eval script can not be beam and some, something will go wrong.
That's very hard to help.

##### **Flata** [[00:53:15](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3195)]
Okay.
Sounds good.
I'll definitely filter that down.

##### **Chenyu** [[00:53:18](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3198)]
Now there's also some beam debug-related flags that you can try.

##### **Flata** [[00:53:25](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3205)]
OK, sounds good.

##### **Chenyu** [[00:53:26](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3206)]
It will print more stuff for the kernel that is beaming and the action it's trying to apply.
So hopefully those will be useful.
Yeah, I will review your model eval change once it's ready.
Then I will try to reproduce.
Just let me know when you are ready, and I will set up the run.

##### **Flata** [[00:53:52](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3232)]
OK, sounds good.
Sorry, one more thing.
I was actually also able to fit more batches, which is good.
I think I went up from 72 to, I think, 102 batch size.
Hopefully, I can probably fit more, but I do want to reset it.

##### **Chenyu** [[00:54:08](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3248)]
Yeah, if it's after the memory planning, it's probably because it's similar to ResNet to help you to save memory so it can fit more.

##### **Flata** [[00:54:16](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3256)]
Oh, OK.
I see.

##### **Geohot** [[00:54:19](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3259)]
I bet you 96 is going to be faster than 102 also.
GPUs like when things are multiples of like 16 or 32.
I see.

##### **Flata** [[00:54:31](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3271)]
I see, OK.
Yeah, I did find that definitely faster on my benchmark runs for sure.

##### **Geohot** [[00:54:36](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3276)]
Wait, you found 102?
I believe 102 is faster than 72.
But I bet you 96 is going to be faster than 102.

##### **Flata** [[00:54:42](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3282)]
Oh, I meant 96.

##### **Geohot** [[00:54:42](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3282)]
Yeah, 96.
Yeah, 96 is good.

##### **Chenyu** [[00:54:50](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3290)]
Cool, excited.
OK, other bounties.

##### **Geohot** [[00:55:11](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3311)]
else we got?
Do I have anything I got the AMD LLVM tensor core support, I think looks good.
I think I can just merge that.
Yeah, I'm merging after the meeting.
What else we got?
I think there's been some progress on multi-GPU training.
I think we're getting there.
Oh, he's shifted to test ops.
Those are torch backend things.

##### **Chenyu** [[00:55:46](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3346)]
Yeah, he helped with the one test that had some issue.

##### **Geohot** [[00:55:52](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3352)]
CPU graph is the new bounty.
It's doable by everyone here.
Pretty easy.
I really got to go through the bounties and just see what's reasonable and stuff.
And I'll lock the OlMoE bounty, the speed up.
It's almost there.
Zibokapi's OlMoE speed up.

##### **Chenyu** [[00:56:44](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3404)]
I was reading that paper, that 1.3.
I know they claim 1.3 in the abstract, but do we know if it's really 1.3?

##### **Geohot** [[00:56:56](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3416)]
I think I was pretty generous already, saying 50% of theoretical.
So even if it's more than 1.3
I think that it should definitely be doable to get.
to go from 53 to 77.
Does anyone have any questions?
This is a good time for generally asking questions.
Ask them in general and we'll answer them here.
The charts have no units.
Well, the units on the y-axis are times, and the units on the x-axis are also times, but there are different kinds of times.
The x-axis is a commit number, and the y-axis is milliseconds.
Any progress on the, no, is that a bounty?
I think.
Did I make that a bounty, or did I just say someone should do it?
Oh, here we go.
Yeah, $150.
If someone could fix the tensor cores for 9700 XTX.
That's a good bounty for somebody.
That should be easy.

##### **Chenyu** [[00:58:20](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3500)]
Isn't that already a bounty?

##### **Geohot** [[00:58:22](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3502)]
Yeah, it's already a bounty, yeah.
So I just moved it to the top.
Any updates on Cloud=1?
Well, our Cloud=1 intern is joining us starting in May.
And then there will be lots of updates for Cloud=1.
No, so no one's picked that up yet.
If you have a 9700 XTX, Ignaciosica has made it really easy for anybody to add new Tensor Core, new types of Tensor Cores.
So I think that should be a pretty easy bounty.
Anyone attends Tenstorrent Dev Day?
I would have come, but I'm far away.
And did I want to offload any of my excess stock of motherboards?
Not at a good price.
At a high price?
Sure, I could hook you up at a high price.

##### **Chenyu** [[00:59:53](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3593)]
You merged your linearizer fix, right?

##### **Geohot** [[00:59:59](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3599)]
Which?
Oh, my linearizer fix.
I merged two linearizer fixes, but they didn't seem to fix any of the linearizer failures.

##### **Chenyu** [[01:00:13](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3613)]
So 53 is still failing.
Yeah.
Have you reviewed any of the

##### **Geohot** [[01:00:27](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3627)]
those ones are never good 

##### **Chenyu** [[01:00:32](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3632)]
there's one that fix almost it 

##### **Geohot** [[01:00:37](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3637)]
yeah we just don't have nearly enough tests for this

##### **Chenyu** [[01:00:44](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3644)]
Yeah, but that's also a case for the whole blocks.

##### **Geohot** [[01:00:50](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3650)]
Oh, I know.
But like, no, like I haven't seen anyone that like passes all the tests even.
Like, OK, there's the one that like has failing tests.
Let me know if other changes are required, like it has failing tests.

##### **Chenyu** [[01:01:06](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3666)]
Oh, you have 9616.

##### **Geohot** [[01:01:10](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3670)]
Oh, 9616 looks interesting.
Oh, interesting.
OK, I see this one.
OK, I'll lock this bounty.
I'll lock this bounty just because I see someone's ASCII art, and it seems like they've thought about the problem.
No, I'm talking about 9637, which I'm just going to close.
I don't know why the NOOPT test was removed.

##### **Chenyu** [[01:02:07](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3727)]
Because noop was initially added because it only fails in that case.

##### **Geohot** [[01:02:18](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3738)]
Tests as is and remove expected failure.
In general, it's bad form to update both the tests and the thing you're correcting the test for and the same thing if you don't have to.

##### **Chenyu** [[01:02:39](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3759)]
How's the F8 support one?

##### **Geohot** [[01:02:42](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3762)]
Oh, that one, I want to merge that one too.
That one, did they respond to me?
They responded.
Yeah, we should merge this.
Cool.
Yeah, I think.
All right.
I'll review PRs tomorrow.
I wish GitHub had a way for me to star them.
I think this one's pretty good.
Kind of as good as it can be.
I don't know.
It's only 2 Dtypes.
I think it's worth it.

##### **Chenyu** [[01:03:37](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3817)]
OK, anyway.
So that's it for review.
Made a PR for add copy in VIZ to copy render code.

##### **Geohot** [[01:03:51](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3831)]
Yeah, I reverted that.
I don't think we should have features like that in Viz.
I think we should also start counting the JavaScript lines.
I think we really want our visualizer to be as absolutely minimal as possible.
You know, you just start adding features, and then, well, now I need design, and now this feature doesn't appear correctly in this browser.
So what the feature was was something that was a button to copy the code, but why can't you just highlight the code and Control-C, right?
So that's why I reverted that.
Or if anything, the other thing to do there would be to do something like... I don't know if there's a way to do this, but to make it so you can click and then Ctrl-A and then Ctrl-C.
Make intuitive behaviors work.
Don't add buttons.
That's my UI philosophy.
I really hate whenever they have a...
click this button to use my file explorer to upload a file.
I'd much rather drag and drop a file there, and it works.
But yeah, no, we should be counting the lines in the JavaScript, too.

##### **Chenyu** [[01:05:11](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3911)]
It usually works, right?
But what if you're on your phone?

##### **Geohot** [[01:05:17](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3917)]
Well, if you're using Viz on your phone, I don't know what to tell you.

##### **Chenyu** [[01:05:26](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3926)]
OK.
Yeah.
OK.
I think that's it for this meeting.

##### **Geohot** [[01:05:36](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3936)]
Cool.
Thanks, everyone.

##### **Chenyu** [[01:05:39](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3939)]
Thank you, everyone.
See you next week.

##### **Geohot** [[01:05:42](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3942)]
Same time.

##### **Chenyu** [[01:05:44](https://www.youtube.com/watch?v=7AhKAlaQWNo&t=3944)]
Bye-bye.

