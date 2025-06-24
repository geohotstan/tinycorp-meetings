# 2025-06-23 Meeting

### Meeting Agenda

**Time:** 9am Monday San Diego time
- company update
- testgrad / scheduler
- mlperf llama 405b, bert grad accumulation, llama 405b inference, bf16 adam
- viz tooling
- drivers
- cloud, hash, tinyfs
- z3 symbolic
- onnx
- local
- other bounties (retinanet, lm_eval, AMD_LLVM, cloud sync stuff)

### Audio

[Youtube Link](https://www.youtube.com/watch?v=nNXwJ320Dww)

### Highlights

- **[Company Update](#geohot-or-chenyu-000000)**: Signed $2M AMD contract for MLPerf submission on Lama 405B. Initial down payment is $400K, with milestones based on single and multi-node performance against NVIDIA.
- **[Company Update](#geohot-or-chenyu-000209)**: Tinybox Green V2 shipments underway; current orders shipping within approximately two weeks.
- **[Scheduler/TestGrad](#geohot-or-chenyu-000312)**: Kernel.py optimization isolated into a new directory (`opt`). Cleaner pipeline now consists of kernelization, optimization, and code generation.
- **[Halide Backend](#geohot-or-chenyu-000515)**: Plans to experiment with Halide's backend for improved optimization language. Halide provides a potentially better framework for double buffering needed in fast GEMMs.
- **[Gradient Accumulation for BERT](#geohot-or-chenyu-000756)**: Successfully implemented basic gradient accumulation; minor JIT input handling issues identified and to be fixed.
- **[Llama 405B Inference](#geohot-or-chenyu-001032)**: Model loads slowly but runs correctly on MI300X hardware; FP16 Adam optimizer tested and considered suitable.
- **[Fused Optimizer Memory Issue](#geohot-or-chenyu-001424)**: Memory overflow detected in the fused optimizer implementation; visualization tooling proposed to help diagnose buffer usage.
- **[Visualization Tooling](#qazalin-001545)**: Merged `TimeVis` tool for non-blocking UOP tracking. Memory allocation and kernel execution profiling being enhanced to debug memory issues effectively.
- **[Drivers Stability Issue](#nimlgen-002933)**: Red machine GPU reset instability traced potentially to `AMSMI` GPU probing service; plan to disable probing temporarily for stability tests.
- **[GPU Memory Transfer Optimization](#geohot-or-chenyu-003818)**: Priority set for optimizing CPU-GPU memory transfers, especially critical for Lama 405B due to optimizer states stored on CPU.
- **[Disk to GPU Direct Transfer](#nimlgen-003958)**: Exploring direct disk-to-GPU data transfer solutions using NVMe or DMA buffer mechanisms.
- **[Z3 Symbolic Bit Vector](#geohot-or-chenyu-004722)**: Flaky CI behavior suspected due to temporary files and multiprocessing conflicts; further debugging planned.
- **[Local Memory and Upcast Optimization](#ignaciosica-005005)**: Continued work on local memory optimization (`locals`) and `upcast` improvements; issues identified with masking and memory aliasing.
- **[RetinaNet Rewrite](#wozeparrot-005808)**: Rewrite completed and being tested against NumPy implementation prior to Tinygrad integration.
- **[LinAlg SVD Implementation](#geohot-or-chenyu-010312)**: Pending merge; concerns raised about usage of `.realize()` and `.clone()` calls, but likely to be merged after additional performance validation.


### Transcript
##### **Geohot or Chenyu** [[00:00:00](https://www.youtube.com/watch?v=nNXwJ320Dww&t=0)]
Okay, great.
Let's get started.
Star Wars company update.
Okay, we had a great week for the company last week.
We got the AMD contract signed.
So we have a $2 million contract on the table to get AMD's new chip on MLPerf for Lama 405B.
Okay.
So yeah, we have a $400K down payment, and then there's four milestones, $400K each, using single node, multi node, and whether we can beat NVIDIA on performance or not.
And we have an ace up our sleeves if we really want to beat NVIDIA, which is that those numbers are pegged to BF16 numbers.
So if we could get FP8 to work.
We basically get the performance free.
So kind of what I'm hoping is that we do a BF16 submission for the first MLPerf, and then we try to do FP8 for the second one, and then we get it all.
Is there an ETA for the new chips?
Yeah, so I was emailing with Inertia this weekend.
He says he's going to send them like this week or next, but...
To be fair, we have a lot to figure out on the old chips.

##### **Geohot or Chenyu** [[00:01:23](https://www.youtube.com/watch?v=nNXwJ320Dww&t=83)]
Fair enough.

##### **Geohot or Chenyu** [[00:01:25](https://www.youtube.com/watch?v=nNXwJ320Dww&t=85)]
Yeah, we got a lot, but they'll be here.
They'll be here.
Everything's good on that.
Yeah, they're going to be MI350s, and then they want us to do the final run on the 355s, but it's optional.
We could use our cloud for that, so we could have a bunch of machines to do cloud runs.
Oh, they are not going to send us 355?
We don't want them.
The 355, I believe, is water-cooled only.
I see.
Okay.
I'm happier to take the air-cooled 350s.
It's the same chip.
It's the same chip.
It's just clocking.

##### **Geohot or Chenyu** [[00:02:03](https://www.youtube.com/watch?v=nNXwJ320Dww&t=123)]
That's good.
No problem.
Yeah, no, I don't want to deal with it.
It's the same CDNA4.

##### **Geohot or Chenyu** [[00:02:09](https://www.youtube.com/watch?v=nNXwJ320Dww&t=129)]
We can make everything work.
I'm just trying a little faster.
Uh-huh.
Yeah, and also we got Tinybox V2s are now shipping.
Two shipped last week.
There's two that look ready in the room now.
So they'll ship today, probably.
Yeah, and if you order a Tinybox, not Pro, just Tinybox Green V2s.
If you order a Tinybox Green V2, it will ship in like probably two weeks.

##### **Geohot or Chenyu** [[00:02:44](https://www.youtube.com/watch?v=nNXwJ320Dww&t=164)]
So yeah, the tiny boxes are flowing.
We're making money on every front.
Yeah, things are good about that.
Great.
OK.
Sounds good.
Let's move on to...
That's great, scheduler.

##### **Geohot or Chenyu** [[00:03:12](https://www.youtube.com/watch?v=nNXwJ320Dww&t=192)]
Or the thing you post in the channel, that channel.
I forgot which one.
Yeah, no, I was thinking about stuff yesterday morning.
But no, what I did last week was, it's still not completely finished.
I got to finish it this week.
But if you look at that new docs I linked, that layout MD,
I've isolated all of kernel.py to be in one folder called opt.
We don't use kernel as an abstraction anywhere.
All kernel does is transforms the AST into an optimized AST, which is an AST that basically just the shapes are swizzled and there's tensor cores, and that's it.
But it's still just a UOP to UOP transformation.
It fits in the normal paradigm.
And all of that legacy code is shoved into a directory.
And we can replace it, not replace it.
We can do whatever we want.
It's a lot easier to reason about now.
Yeah, so the whole flow is basically like kernelize, turn things into kernels.
Opt, turn them into optimized kernels.
Cogen.
Generate the linearized code renderer, actually output the string, and then turn it into a program.
So it's a pretty straightforward flow now, and I think that it's a lot easier to reason about, and a lot easier to replace or not replace some of these pieces.
What I realized with TestGrad was I was thinking, oh, to replace the whole thing, but like, eh.
Not really.
I just found myself re-implementing parts of kernel.py.
And I'm like, kernel.py is mostly fine.
The problem is that it's not being used as a library.
It's being used as a subtraction in this class and other places, which is a lot of complexity to reason about.

##### **Geohot or Chenyu** [[00:05:06](https://www.youtube.com/watch?v=nNXwJ320Dww&t=306)]
But once you put it in, then it's just its own thing.
So it's pretty good.

##### **Geohot or Chenyu** [[00:05:15](https://www.youtube.com/watch?v=nNXwJ320Dww&t=315)]
Yeah, so this week I'm going to work on, I'm going to try writing a Halide backend.
It seems like that paper is really good, too.
It seems like they've put a lot more thought than we have into what makes... It's sad that what they're doing is the state of the art.
It just looks like it's very similar to our heuristics, but thought about for a few more years.
So it's not like we're missing... Are people using this now?
Not really.
Halide is mostly used for image pipelines.
There's some academic stuff using it for neural networks, but no, for actual neural networks, it's much more MLIR.
I mean, Triton's the big one.
I think Triton now is MLIR.
They're just using the MLIR infrastructure.
Triton is the big one they're using, and Triton gets you this basically... Triton solves one part of the problem.
And that's kind of what things are moving to.
But it doesn't seem like a very clean and generic solution to me.
And every time I've tried to use Triton, it's clear that there's paths they optimize for.
I mean, it's open AI.
I'm sure they use it internally.
It's clear that there's paths they optimize for.
And if you're on one of those paths, it's good.

##### **Geohot or Chenyu** [[00:06:39](https://www.youtube.com/watch?v=nNXwJ320Dww&t=399)]
The minute you step off that path a little, it's not like it was reasoned about in a principled way.

##### **Geohot or Chenyu** [[00:06:51](https://www.youtube.com/watch?v=nNXwJ320Dww&t=411)]
Yeah, I'm going to just try Halide and see if they have, they're good at specifying, like they have a really good language for talking about optimizations.
That I think is a lot better than our language with like upcast and unroll and stuff.
So I at least want to fully understand their language if we're going to rewrite part of that.
If we are missing anything, or maybe something can be expressed a lot.
Yeah, yeah, yeah.
There is something we're missing, which is the double buffering.
We don't have any way to express that now, like the double buffering.
You need this for fast gems.

##### **Geohot or Chenyu** [[00:07:33](https://www.youtube.com/watch?v=nNXwJ320Dww&t=453)]
And Halide has a way to express that, so if we could just steal it.
That sounds good.
OK.
Anything else?
No.
OK, cool.
Moving on.

##### **Geohot or Chenyu** [[00:07:56](https://www.youtube.com/watch?v=nNXwJ320Dww&t=476)]
OK, so now we have a contract.
Great.
Implement GradAccumulation for BERT.
Seems fine if you only do accumulated for four.
We tried to accumulate more.
There's memory overhead, and also scheduling time seems to be much longer.
I didn't look into this too much.
I just wanted to make sure the idea could work.
Yeah, what we really want gradient accumulation to be is a reduce on the overgraph.
It's also a range.
No, it's not the same as an RNN, because they're not sequentially dependent.
It's a range.
It's a range, yeah.
There's no reason.
And RNN looks a lot more like training, like training because your outputs depend on it.
So ideally, it becomes that.
Yeah, I think a good part is also one annoying thing is related to JIT that JIT doesn't take a list or sequence of tensor as input.
It would silently drop it.
Oh, yeah, we should fix that.
So the way I did it is I create a keyword R dictionary for
Each of the accumulation runs and kind of work.
It's just a little bit bad.
And I think I opened an issue on this.
I think silently drop some list of tensor seems to be something people would actually use and then their JIT would just silently fail.
I don't think that's a good experience.
No, we should change it to do, we should use get state on the args and the KW args of the JITed function.

##### **Geohot or Chenyu** [[00:10:02](https://www.youtube.com/watch?v=nNXwJ320Dww&t=602)]
I see.
OK.
Well, that sounds easy enough.
OK.
I can do that.
Cool.
Yeah.

##### **Geohot or Chenyu** [[00:10:15](https://www.youtube.com/watch?v=nNXwJ320Dww&t=615)]
So I think the good part is other than that, it's pretty easy to write this.

##### **Geohot or Chenyu** [[00:10:21](https://www.youtube.com/watch?v=nNXwJ320Dww&t=621)]
It's very intuitive for how to put it and overall easier than I thought.
So that was great.

##### **Geohot or Chenyu** [[00:10:32](https://www.youtube.com/watch?v=nNXwJ320Dww&t=632)]
And also, you see the LAMA 405B inference.
Loading model is slow.
Also, generally, it's not fast, but it runs on MI300x.
So what I would do, coming back to the grad accumulation, what I would do is I'd not try to put, like, I don't know if you're trying to put all the grad accumulations in the JIT, but for now, if you just JIT one step of the grad accumulation and then do the outer loop in Python, that should work pretty well.

##### **Geohot or Chenyu** [[00:11:04](https://www.youtube.com/watch?v=nNXwJ320Dww&t=664)]
Oh, that's how I did.
Oh, well, that shouldn't have memory overhead.

##### **Geohot or Chenyu** [[00:11:11](https://www.youtube.com/watch?v=nNXwJ320Dww&t=671)]
No, but now you're...
Maybe I misunderstand what you are saying.
So we should JIT the, say, if it's accumulated over 16 steps, then 016 will happen in the JITed.
Is that what you mean?
You should do the micro step JITed.
Yeah, I'm saying the other thing.
I'm saying that actually that should be 16 calls to the JITed function.
Then your update part is not no longer JITed?
You can update separately, I think.
I think you have two separate JITs.
I think you have one JIT for the step and one JIT for the update.
I mean, again, when you're talking about an actual timescale of these things, a step is going to be seconds.
The accumulation of 100 steps is going to be minutes.
And then the update is going to take 30 seconds.
So these things are massive already.
There are just some parts.
I am not sure if you realize something in the middle or break gradient.
I can double check.
I mean, yeah, it should work like this.
And this is good because it stress tests these annoying parts of the JIT.
But what I would expect to be the way to write this is each microstep of the gradient accumulation is one JIT.
And then you recall that in the outer Python.
And again, we're on the order of seconds here.

##### **Geohot or Chenyu** [[00:12:32](https://www.youtube.com/watch?v=nNXwJ320Dww&t=752)]
So this will be zero overhead.
OK, I mean, I'll think about it.
Cool.

##### **Geohot or Chenyu** [[00:12:50](https://www.youtube.com/watch?v=nNXwJ320Dww&t=770)]
Yeah, then last thing.
So I test Adam flow 16, beef flow 16.
You should see that in the LAMA 4 or 5B channel.
Beef flow seems fine.
I mean, fine for birds.
I don't know, 4 or 5B would require as much
I don't know if it's much bigger, but different kinds of range probably should also work.
O16, I'm pretty sure if we find a way to scale that number to the correct range, it might be also possible to work.
But if BF16 just worked, we probably would just use that.
BF16 is totally fine.
I mean, the CPU can, it's actually so much easier to transform from BF16 to Float32 anyway, if we're doing the optimizer on the CPU.
Yeah, just chunk it.
Also, the power thing should be fine.
The compute is still down in flow 32.
It's just the store.
At least it's not affected by the 0.99.
Yeah, if it's one number, it should be fine.
Yeah.
Finally, I just tested Fuse Optim.
For some reason, it caused auto-memory.
I didn't get a chance to investigate.
Was that a known behavior?
It's very unclear.
It's very untested.
That doesn't surprise me that it's out of memory.
And that's something we're going to have to fix.
I don't really know what it is, though.
Yeah, because it must be something else.

##### **Geohot or Chenyu** [[00:14:24](https://www.youtube.com/watch?v=nNXwJ320Dww&t=864)]
The parameter itself should be the same.
It's not like we reuse these.

##### **Geohot or Chenyu** [[00:14:35](https://www.youtube.com/watch?v=nNXwJ320Dww&t=875)]
Well, yeah, like you really want the scheduler to put really like all the gradients in one tensor.
And I don't know if it's going to do that now.
You see, like, like, like, it's really it's really when you start thinking in these like massive scales, it's really kind of like you have like this one tensor for one
Your wait.
It's just one tensor for the gradient, one tensor for RAM, and one tensor for V. And then, yeah, that's the whole optimizer.
It's simple.
Four big tensors.
Yeah.
So no, I don't know.
If that's running out of memory, it's probably because it's doubly allocating some stuff.
And yeah, we have to look into it.
Yeah, we also have to think about.
If this is something that I can use the visualization tools to figure out, that would be nice.
Yeah.

##### **Geohot or Chenyu** [[00:15:31](https://www.youtube.com/watch?v=nNXwJ320Dww&t=931)]
And I think that's a good dissect to this tooling.
Great.
George, did you want to finish your sentence?
No, that's it.
I have this tooling.

##### **Qazalin** [[00:15:45](https://www.youtube.com/watch?v=nNXwJ320Dww&t=945)]
Yeah, this tooling.
I merged TimeVis.
And I have a diff I posted to this channel for non-blocking UOP tracking.
The basic idea is to track the actual fields of the UOP data class and then reconstruct the UOP graph.
And that's going to solve Mickey.
I saw a bunch of the diffs where the bounties were like weak refs and stuff.
You need none of that.
I wasted time pickling weak refs and it was just...
Pick up the fields and reconstruct the graph.
So yeah.

##### **Geohot or Chenyu** [[00:16:21](https://www.youtube.com/watch?v=nNXwJ320Dww&t=981)]
Yeah, I think that's a reasonable way to do it.

##### **Qazalin** [[00:16:24](https://www.youtube.com/watch?v=nNXwJ320Dww&t=984)]
This is going to get us to 20% overhead on Lama.

##### **Geohot or Chenyu** [[00:16:28](https://www.youtube.com/watch?v=nNXwJ320Dww&t=988)]
Sweet.

##### **Qazalin** [[00:16:30](https://www.youtube.com/watch?v=nNXwJ320Dww&t=990)]
And yeah, I saw you posted that we are not using screen real estate.
I completely agree.
I'm going to add the buffer profiler soon.
Take it from there.

##### **Geohot or Chenyu** [[00:16:45](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1005)]
Yeah, I mean, it would be great if we could like debug FuseOptim.
I mean, that's kind of a first use case of it, like figure out why FuseOptim is using more memory than not FuseOptim.
And so that's Lama inference.
How is it working on BERT training?

##### **Qazalin** [[00:17:06](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1026)]
It's fast across the board.
Great.
It's just training for us.

##### **Geohot or Chenyu** [[00:17:10](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1030)]
Yeah, I mean, we're going to really need this for Lama405b.
I don't know how long the schedule is right now to schedule the step.
Yeah, that would be brutal.
I think this thing has how many layers again?
I have no idea.

##### **Geohot or Chenyu** [[00:17:31](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1051)]
It's layers that's different?

##### **Geohot or Chenyu** [[00:17:34](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1054)]
So definitely, layer is a problem.
That's why bird-sized layer 2 is a lot faster than 24.
Let me check.
Yeah.
I think it's 192, maybe.

##### **Geohot or Chenyu** [[00:17:51](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1071)]
192 layers?
No, it's 126.
It's very deep.
126.
Yeah, I put a parameter in Lama3.py.
I see.
Well, I guess one last thing from my part.

##### **Geohot or Chenyu** [[00:18:21](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1101)]
I'm writing the training Lama3AB this week.
Hopefully, I can get it done before next meeting.
I think it's essentially downloading the C4 data sets that they are using.
Then I should be able to import the model from Lambda 3 and just add an optimizer on top of that.
That's what I'm hoping.
Cool.
Yeah, I really want to get the 8B training with the MLPerf target.
Also, maybe I should prioritize work on the transformer layers are arranged.
So like, yeah, yeah, I mean, 126 is always going to be super brutal to schedule, unless we can use a range.
But you also just need that for even if it's scheduled for 20 minutes, that's probably fine.
No, but no one wants to deal with that.
I want this to I want this to schedule in 10 seconds.
As long as you can do it in a generic, fine way, I think that's fine.
Yeah, I mean, so you could imagine what it would be, right?
Your transformer weights would become, would have another parameter called layer.
And it would be a loop.
OK.
And your backward would be the reverse of that range?
Is that how it works?
Yeah.
Yeah, that's no problem.

##### **Geohot or Chenyu** [[00:19:52](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1192)]
That should actually all just work.
There's no reason you can't take a derivative of a range.
It's literally just the reverse of the range?
Yeah, right?
It's just doing the opposite order.

##### **Geohot or Chenyu** [[00:20:13](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1213)]
OK.
Yeah, it's a chain rule.
There's no reason that if you just take a range and go forward, and you just go the other way.
And it's like a no-op in the thing.
It's just put the ranges in the same thing, just swap the end range and the range.
Anyway, so that thing should also
The AB training should also work with 7TB, which 7TB by itself should fit on MI300X, I believe, without any model sharding.
Wait, no way.
No, no.
And if you put the MMV inference on CPU.
No, no.
You can put the MMV on CPU.
What's MMV?
You can't fit both the gradients and the weights in BF16 in a single thing for a 70B.
OK, never mind.
Well, we should think about sharding, too, and how we want to shard, right?
We have a bunch of options here, and it looks like the NVIDIA thing does all of them.
OK, so we can think about that next week.

##### **Geohot or Chenyu** [[00:21:21](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1281)]
Cool.
After we have the AD training.

##### **Geohot or Chenyu** [[00:21:25](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1285)]
Yeah, AP will totally fit on one.

##### **Geohot or Chenyu** [[00:21:29](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1289)]
Sounds good.
Anything else for Viz?

##### **Qazalin** [[00:21:34](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1294)]
I'm going to add the memory graph and a bunch of other stuff.
I'm going to upstream everything, so feel free to pull from master and test on your stuff.
And if it doesn't work, just complain.

##### **Geohot or Chenyu** [[00:21:48](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1308)]
Yeah, so you can also try with the FUSE opting.
I don't know if it reproduces on any of the tests.
But if so, that's a smaller place to start with.
Yeah, even in beautiful MNIST, we should just see, is it using more RAM?
I think debugging that is a really good use case for this.
We could see how these assignment things are actually becoming copies.
And if the visualizer can show that in a really good way, that's a great use case for this.
That justifies the entire investment into the project.
Because it's super hard to understand otherwise where buffers are actually being allocated, especially after they go through the memory planner.

##### **Qazalin** [[00:22:41](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1361)]
I'm going to literally put tracing in the buffer class.
I can de-allocate and allocate.
And that way, we can use the IDs to backtrack to whatever kernels use that buffer.

##### **Geohot or Chenyu** [[00:22:57](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1377)]
Cool.
Do you want the per device memory counter?

##### **Geohot or Chenyu** [[00:23:05](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1385)]
Well, I'm not sure we want to put that in global counters.
I think that tracking in the buffer class is probably the right place to do it.

##### **Qazalin** [[00:23:14](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1394)]
Yeah, I think so too.
Open the buffer class and then process it.

##### **Geohot or Chenyu** [[00:23:21](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1401)]
Yeah, the problem with doing it in global counters is kind of like, OK, now we have some dictionary in global counters of the device names and of the .
One concrete issue I had was I was testing training birds on a red box, and the total mem was 148 gig.

##### **Geohot or Chenyu** [[00:23:42](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1422)]
And I was not sure what's happening.

##### **Geohot or Chenyu** [[00:23:49](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1429)]
So if your total memory exceeds your GPU memory, I mean, it could be on the CPU.
That's why the per device counter.
Yeah, but then it's like, how do you display it?
I think that it'll just be a lot nicer when we have per-device graphs in Viz.
Yeah, especially having the max of the device will also be useful.
Yeah, I mean, you'll be able to see that really easily in the graph.
It should just be like, on that timeline, you'll just be able to see, OK, what's the highest point?

##### **Qazalin** [[00:24:26](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1466)]
Maybe we could even go .

##### **Geohot or Chenyu** [[00:24:29](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1469)]
Add to what?

##### **Qazalin** [[00:24:31](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1471)]
The allocator of the device, so the spare device?

##### **Geohot or Chenyu** [[00:24:41](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1481)]
Oh, you mean like the global counters?

##### **Qazalin** [[00:24:45](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1485)]
I mean the allocator that goes into each device.

##### **Geohot or Chenyu** [[00:24:50](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1490)]
What do you want to add to the allocator?

##### **Qazalin** [[00:24:55](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1495)]
Tracking those events, the instance of the allocator.

##### **Geohot or Chenyu** [[00:24:59](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1499)]
I don't think the allocator really... I would just do it at the buffer layer, probably.
The allocator is kind of... We don't support things like multiple allocators.
I don't think we have to.
I think just that the buffers... The allocator also, then you're asking, we assume that the LRU cache is at a much lower level, and we should never really be thinking about that.
There just shouldn't be bugs in the LRU cache, and we should never have to think about it.
I want to know how many buffers are allocated right now for any given device, and what the sum of that is, and how they stack, and all that.

##### **Geohot or Chenyu** [[00:25:44](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1544)]
Yeah.

##### **Qazalin** [[00:25:44](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1544)]
I'm also working on tracking multiprocess for this.
So that's going to be another fun one.
It's just going to be per device have a different file.
The problem is that you can't really clean that up.

##### **Geohot or Chenyu** [[00:26:02](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1562)]
It doesn't seem to be a good solution for it.
Well, what?
You're worried about the temp files not being deleted?

##### **Geohot or Chenyu** [[00:26:11](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1571)]
When are they normally deleted?

##### **Qazalin** [[00:26:15](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1575)]
When you reboot.
So right now, it's very easy because this writes to the same file over and over again.
So it's just whatever this command that you run overrides whatever existed before it.
If you have a folder with a bunch of files, which one gets you rm-rfd folder when?

##### **Geohot or Chenyu** [[00:26:35](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1595)]
How big are the files?
How big are the files?
It depends on how big your model is.

##### **Qazalin** [[00:26:51](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1611)]
And how long are you capturing?

##### **Geohot or Chenyu** [[00:26:54](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1614)]
Yeah, but are we talking about a meg here or a gigabyte?

##### **Qazalin** [[00:27:00](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1620)]
Oh, a couple of megs.

##### **Geohot or Chenyu** [[00:27:01](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1621)]
Yeah, who cares?
Don't worry about it.
Temp is probably big enough.
A couple of megs, you just can leave them in temp.
It's not a big deal.
Should we have another scale?
Oh, how do you know they're stale and not to open them next time?
I don't know.

##### **Geohot or Chenyu** [[00:27:23](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1643)]
Put a timestamp in them.
Yeah, put like a timestamp.
So you have like your primary one, right?
And then put a timestamp in the primary one, and then you can check the secondary ones and see if the timestamp matches.

##### **Geohot or Chenyu** [[00:27:44](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1664)]
Some ID or something like that.

##### **Geohot or Chenyu** [[00:27:49](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1669)]
You could even do cleanup there if you want to, right?
So you check the, you have a primary file, which has some ID or some timestamp that's unique.
Timestamp's probably good.
Then you, in your viz loader, you iterate through all the child files.
If they have matching timestamps, you load them in.
If they have older timestamps, you delete them.

##### **Geohot or Chenyu** [[00:28:15](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1695)]
There's your solution.
Does that work?
Because it's the same problem.
If you know when they're stale, you can delete them when they're stale.
So you're going to be able to see the Beam stuff.
Yeah, that would be cool.

##### **Geohot or Chenyu** [[00:28:38](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1718)]
Yeah, I mean, it'd be good also as we eventually, I mean, I want to eventually expand that infrastructure and not just be for Beam.

##### **Geohot or Chenyu** [[00:28:47](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1727)]
And I want to be able to do kernel rendering in parallel.
We should just do the code gen.
Even if you're not beaming, it should do all the kernels in parallel.
It won't make scheduling faster, but it will make code gen faster.

##### **Geohot or Chenyu** [[00:29:17](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1757)]
Let's move on to drivers.
And also, Nimogen, can you comment on what's the state of CI Red Machine?
I think it's quite broken.

##### **Geohot or Chenyu** [[00:29:28](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1768)]
Yeah.

##### **Nimlgen** [[00:29:33](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1773)]
So for the CI red machines, we actually started to see some IR errors on the machines where this functionality was enabled.
So we have only two red machines in our fleet where IR was enabled.
And they were in CI.
So basically, from what I just reproduced,
This is reproducible, and that's happening during the reset of the GPU, during the mod1 reset.
So we see completion timeout, and sometimes we see unexpected completion received.
So basically that means that sometimes the GPU can't answer within the given time frame.
And when we see unexpected, it just actually answers after that.

##### **Geohot or Chenyu** [[00:30:31](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1831)]
Do you think it's hardware or do you think it's software?

##### **Nimlgen** [[00:30:34](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1834)]
No, I mean, I think it's software.
I mean, actually, because this happened during the reset, I mean, it looks like it's fine that the GPU is not responding to some requests and they can time out.
But I'm not actually sure.
What's sending these requests?
Because from what I can see from IRs, sometimes it's just reports, ETLPs, and they have different sizes of two bytes or eight bytes, and I'm not sure that doesn't look like our request, because what we can send is during this time period only memory mapped IR requests, which are four bytes.
So maybe it's Linux probing something?
I don't know.

##### **Geohot or Chenyu** [[00:31:26](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1886)]
I've noticed that ever since we moved to upstairs, maybe we re-imaged them to 22, 24.04.
It seems like it's become a lot more unstable.

##### **Nimlgen** [[00:31:39](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1899)]
Yeah, that's, yeah.

##### **Geohot or Chenyu** [[00:31:43](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1903)]
I've been using AM for a while, I think.

##### **Nimlgen** [[00:31:47](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1907)]
Yeah, that started to happen like a week ago, and it was really reproducible almost every run on TinyR3.
Before that, yeah, I haven't seen crashes.

##### **Geohot or Chenyu** [[00:32:01](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1921)]
TinyR3 is also new.
We added TinyR3, so maybe TinyR3 is broken.

##### **Nimlgen** [[00:32:08](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1928)]
No, I mean, it's not broken because enabling AR on Tiny R9, it's also reproducible there.

##### **Geohot or Chenyu** [[00:32:20](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1940)]
I see.

##### **Nimlgen** [[00:32:21](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1941)]
Yeah, yeah.
So actually, I think I also reproduced that on the AMD GPU driver.
But yeah, the rate is definitely different, a little different between AM and AMD GPU.

##### **Geohot or Chenyu** [[00:32:38](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1958)]
Yeah, I mean, I think it's very important we fix this.
Very frustrating to have the CI fail.

##### **Nimlgen** [[00:32:45](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1965)]
Yeah, so for now, yeah, just temporarily.

##### **Geohot or Chenyu** [[00:32:55](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1975)]
Because the screen is asking the GPU for stats, for metrics.
Oh.
I bet it's this.
Do you want to disable that?
Disable the AM screen service just in general?
Like do it globally?

##### **Geohot or Chenyu** [[00:33:19](https://www.youtube.com/watch?v=nNXwJ320Dww&t=1999)]
So for AMD, for non-AM, or when the AMD driver is loaded, I already had to throttle the screen to one second because there's an open Linux kernel issue where the 7900 XTX just crashes.

##### **Geohot or Chenyu** [[00:33:31](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2011)]
It just times out if you probe the SMU too fast.
Wait, so you're probing it through the direct PCI interface?
No.

##### **Geohot or Chenyu** [[00:33:43](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2023)]
Wait, how are you probing it if there's no AMD GPU driver?

##### **Geohot or Chenyu** [[00:33:47](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2027)]
AMSMI.

##### **Geohot or Chenyu** [[00:33:50](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2030)]
Or AMSMI.
But that's just using the PCI stuff.
Well, this is the problem!
I think this is the problem.
It probably is.
Yeah, let's just disable that.
Because that's a new thing that we added recently.
No, this has been there for a while.
No, we added AMScreen recently.
Around the same time we moved things upstairs.
Oh, yeah, but it's not within a week.
No, not within a week, but it's been unstable for like three weeks.
A week.

##### **Wozeparrot** [[00:34:18](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2058)]
AMSMI has existed for a long time.

##### **Geohot or Chenyu** [[00:34:20](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2060)]
Yeah, yeah, but we weren't always running AMSMI.
AMSMI has existed in Extra, safely far away from everything.
Yes, and then it's existed in the screen service.
Since when?
Basically since I got here.
That's about when the problem started.
I think we should definitely start by disabling that.
Yeah, try disabling that.

##### **Geohot or Chenyu** [[00:34:42](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2082)]
Yeah.
Or you should just disable it in the screen service.
Yeah.
Yeah, well, it could also be 24-4.
That's another thing we changed.

##### **Nimlgen** [[00:34:56](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2096)]
Yeah, actually, I think we should maybe probably fix AMSMI and add some log to node.
And yeah, if we prove that that's the AMSMI, I'll find a way to fix this.

##### **Geohot or Chenyu** [[00:35:09](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2109)]
Great.
But yeah, let's definitely start by disabling that.
And any progress?
You know the thing that I really care about?
On the copy out of the USB GPU.

##### **Nimlgen** [[00:35:24](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2124)]
So yeah, I started to work on this.
I'll focus this week only on the USB GPU.

##### **Geohot or Chenyu** [[00:35:29](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2129)]
So yeah.
And then are we getting?
Sorry, go ahead.

##### **Nimlgen** [[00:35:42](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2142)]
Yeah, just for me, actually, I just merged the old NSRF things we need to merge in V. So
We need lines for NV and still a lot of boilerplate to bring up the GSP.
Yeah, we can raise the line count.

##### **Geohot or Chenyu** [[00:36:02](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2162)]
Yeah.
Feel free to raise the line count to merge NV.
Is it good for me to try?

##### **Nimlgen** [[00:36:09](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2169)]
Yeah, you can try.
So actually, from the point of the stability, it should be fine.
We're still full speed.
I think we still really need huge pages to work fine.
And it's only ADA right now.

##### **Geohot or Chenyu** [[00:36:23](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2183)]
Oh, it's $40.90 now.
Yeah.
Cool.

##### **Geohot or Chenyu** [[00:36:32](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2192)]
Yeah, but yeah, feel free to raise the line count for that.
But yeah, Kama's asking about copy out.

##### **Nimlgen** [[00:36:40](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2200)]
Yeah, okay.
Yeah, so this week I'll just, NVIDIA goes to the ground after I merge it.
It should be good now.
And yeah, also about the MI300, do we want these IQL buckets?

##### **Geohot or Chenyu** [[00:36:57](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2217)]
Oh, yeah.
Yeah, but not the highest priority right now.
I think that we're going to have to move to AQL, but I don't think we have to do it right now.
I think we can do it in a few months.
Once we understand... Because we are still getting that 10 microsecond overhead to sync the kernels, which seems to be gone in AQL.
Yeah, I mean, it's not... I spent...
A day trying to reverse the mech and look for what it is.
It's deep in the AQL stuff.
So whether we actually use AQL or try to use AQL through the back door of the PM4, I kind of like the idea of just straight up using it because we can just copy HIP.
Yeah, we should just support it.
I don't know.
But again, definitely lower priority than... The highest priority is fixing the stability of the red boxes, then copy out on GPU, then getting NVIDIA merged, then NVIDIA 5090, then all the way at the bottom is AQL for AMD.
Even probably even higher priority than AQL for AMD is figuring out how we can increase the load speed of LAMA45B.

##### **Geohot or Chenyu** [[00:38:13](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2293)]
I'll check this.

##### **Geohot or Chenyu** [[00:38:18](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2298)]
Yeah, because we're going to need... So, a conversation that we had in the office a few weeks ago was... So, for the Lama 405B, we can't fit the optimizer state on the GPU.
So, the optimizer state is going to live in CPU RAM, and we're going to run the optimizer on the CPU.
So, we've got to make that copy-in-and-out path fast.

##### **Geohot or Chenyu** [[00:38:42](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2322)]
Mm-hmm.

##### **Geohot or Chenyu** [[00:38:43](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2323)]
Yeah, we're basically, so we're pulling down all the weights and all the gradients, running the optimizer, and then uploading them back.

##### **Geohot or Chenyu** [[00:38:55](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2335)]
Okay, yeah.
Yes, we got to be hitting massive full PCIe speed across this whole thing.
We should be able to get like 400 gigabytes a second.
Which is a bit separate from the disk.

##### **Geohot or Chenyu** [[00:39:12](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2352)]
I mean, the disk is kind of two things, because we don't have a way.
Is there any hope of going direct from the disk to the GPU?

##### **Nimlgen** [[00:39:21](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2361)]
Yeah, I think with the NVMe, we can do that.
It should be pretty simple.
Well, do we have to write a driver for the NVMe?
Yeah, I mean, like from the USBGPU stuff, it looks pretty simple, like the BME driver.
All these queues, so yeah, we can do that.

##### **Geohot or Chenyu** [[00:39:46](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2386)]
Okay, but that involves, is there any way we can use Linux's NVMe stuff and do this?

##### **Nimlgen** [[00:39:58](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2398)]
Oh, here.
Yeah, I need to investigate this.

##### **Geohot or Chenyu** [[00:40:01](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2401)]
UUVN's got a link to...

##### **Geohot or Chenyu** [[00:40:06](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2406)]
Oh, yeah, this is the DMA ref stuff, which we don't know how to get in AM.
Who wants to get something upstreamed into the kernel?

##### **Nimlgen** [[00:40:19](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2419)]
No, it's already patched.
They're just not merged yet.

##### **Geohot or Chenyu** [[00:40:21](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2421)]
Why not?
Yeah, I think I've... Let's rewrite them from rusted to C, and then we can get them merged fast.
VFIO has patches to export DMA ball.
Yeah.

##### **Geohot or Chenyu** [[00:40:34](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2434)]
And then there's another one as well for UDMA buff that can accept the PCI bar address.

##### **Wozeparrot** [[00:40:49](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2449)]
Uh... No, no, there's a patch for UDMA buff that lets it accept a PCI bar address.

##### **Geohot or Chenyu** [[00:40:55](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2455)]
It's on an Intel tree, I believe.
I see.

##### **Geohot or Chenyu** [[00:41:04](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2464)]
We should think about whatever the easiest way to do this is.
Ideally not with our own... Yeah, yeah, yeah, yeah, we don't want to.
Maintaining a kernel module is a lot.
I'd much rather, like, if we have to build a kernel with a flag, I'd much rather that than a separate kernel module.

##### **Geohot or Chenyu** [[00:41:34](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2494)]
Since this is lower priority, can we discuss it next time?

##### **Geohot or Chenyu** [[00:41:41](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2501)]
Yeah, we can share.
Or, I don't know, you want to make it a bounty so someone can work on it, that's also fine.
Well, it's not clear.
We have to investigate more what the solution is.
A public bounty can just be something.

##### **Geohot or Chenyu** [[00:41:57](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2517)]
Yeah, yeah, yeah.

##### **Geohot or Chenyu** [[00:42:05](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2525)]
I mean, we'll see.
UUVN, I definitely don't want this to block the networking bounty.
So I would be OK with this solution for the networking bounty, if that's what it takes.

##### **Geohot or Chenyu** [[00:42:19](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2539)]
Let's move on to the host power stuff.
This is just remote stuff.

##### **Geohot or Chenyu** [[00:42:28](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2548)]
I mean, do we want the kernel module?

##### **Geohot or Chenyu** [[00:42:30](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2550)]
I mean, do you have a better idea?

##### **Geohot or Chenyu** [[00:42:33](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2553)]
Not really.
Not right now.
This patch is in progress for the kernel, but it's not in yet.
I don't know when they will be in.
The kernel module is as good as anything.
I'm fine with that.

##### **Geohot or Chenyu** [[00:42:46](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2566)]
Fairly short.
I think it's okay.

##### **Geohot or Chenyu** [[00:42:50](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2570)]
If you are the one who will be maintaining it, then sure.

##### **Uuvn** [[00:42:54](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2574)]
One alternative to the kernel module is that there is a vendor specific extension on Mellanoxus that allows it to register any physical address, but it has been deprecated and removed.
So if you're okay with using like two or something year old Mellanox of head package, it can just be a single API call.

##### **Geohot or Chenyu** [[00:43:19](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2599)]
Well, but... No, we should use DMA buff.
Yeah, I mean, the problem with the Mellanox thing is it's not going to work for NVMEs, too.
Yeah, we should use DMA buff.

##### **Uuvn** [[00:43:29](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2609)]
Yeah, OK.
Yeah, I have rewritten this model multiple times.
I think this is the simplest generic thing.
And it's fine, I think.
I expect it to have less chances of crashing the kernel than the AMD kernel module.

##### **Geohot or Chenyu** [[00:43:50](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2630)]
Yeah, I'm fine with it for now, if this is how.
Well, you'll be the one maintaining it, so.
It looks simple enough.
I think the kernel will just be fine for now.

##### **Geohot or Chenyu** [[00:44:09](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2649)]
I think we do want to move to whatever thing lands in the kernel officially.

##### **Uuvn** [[00:44:14](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2654)]
Yeah, obviously.

##### **Geohot or Chenyu** [[00:44:15](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2655)]
Yeah.
Yeah.

##### **Uuvn** [[00:44:18](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2658)]
So the remote thing has been blocked on the P2P PR.
I addressed the last... Yeah, that's my bad.
...asked me to split a couple things.
I did, like, four days ago, waiting on, like, this being merged.

##### **Geohot or Chenyu** [[00:44:33](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2673)]
Yeah, that's my bad.
I'll get to it today.

##### **Uuvn** [[00:44:37](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2677)]
Yeah, fine.
So I'm in no rush.
I just don't know, like, have you seen this?
Should I, like, ping you in DM also?
Yeah, I have.

##### **Geohot or Chenyu** [[00:44:44](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2684)]
Yeah, yeah, yeah.
He said get to it, right?
Yeah.
OK, OK, thanks.
Sure.

##### **Geohot or Chenyu** [[00:44:53](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2693)]
Any update on hashing or TinyFS?

##### **Wozeparrot** [[00:44:58](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2698)]
TinyFS can store files now, sort of.
It's not deployed anywhere.
I'm just testing locally.
But at least I can put chunks in places.
It's a little, I'm trying to, so for actually storing files, I'm just trying to use disk, like disk tensor.

##### **Geohot or Chenyu** [[00:45:15](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2715)]
Ideally, the gateway machine would remote the remote device and open the disk.
Because right now we need a program running on all the nodes to actually do the storage.

##### **Geohot or Chenyu** [[00:45:28](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2728)]
No, I think we definitely want that.
Why can't I open the disk remotely?

##### **Geohot or Chenyu** [[00:45:33](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2733)]
So remote currently only uses one device.

##### **Wozeparrot** [[00:45:37](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2737)]
What?

##### **Geohot or Chenyu** [[00:45:37](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2737)]
It's pretty specific on that one device.
But remote can use all the devices, I thought.
Doesn't it work for...

##### **Geohot or Chenyu** [[00:45:45](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2745)]
Doesn't work for multi-GPU?

##### **Geohot or Chenyu** [[00:45:47](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2747)]
Yeah.
Oh, but it has to be the same device.
Yeah, it has to be the same device.

##### **Geohot or Chenyu** [[00:45:52](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2752)]
Oh, well, we'll fix that.
I mean, remote, ideally, like, in some ways, we almost want all of Tinygrad to be funneled through remote, even when it's on the same machine.
Yeah, I feel like, yeah.
Yeah.
So, I think that that's the way to do that.
I think we definitely do not want disk service running on each thing.
We want one Tinygrad server, and it's kind of a...
And then the Tinygrad server will eventually become a kernel and will eventually remove Linux from the computers.

##### **Geohot or Chenyu** [[00:46:23](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2783)]
Right.
OK.
Anything else?
Nope.
OK.
Let's move on to Z3 Symbolics.
Or anything else Slycos want to say?
Yeah.
We should be able to talk.
Or if you cannot talk, you can just type.
And then next would be Annex.
Working on bit vector ranger.
I saw the PR.

##### **Nimlgen** [[00:47:22](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2842)]
I don't know what that is for.

##### **Geohot or Chenyu** [[00:47:25](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2845)]
Yeah, why is it flaky?
What's going on?
Why is ignore OOB not catching it if it really is some out of bounds access?
Is it a use after free?
There's only so many ways to crash Python.

##### **Geohot or Chenyu** [[00:47:41](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2861)]
Something related to temp file and multi-processing.
Huh.

##### **Geohot or Chenyu** [[00:47:51](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2871)]
Yeah, so I think in one of the PR, the speculation was because the way the Python temp file thing was multi-process crash.
I don't know.
But I think specifically for that PR, it's definitely good to understand if there's a problem with temp file, then
A fix should be not using temp file and not directly jump into another serialization and serialization.
Why do we need this?
Why is there temp file in there?
I don't even understand.
Temp file was the old way to dump and load.

##### **Geohot or Chenyu** [[00:48:38](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2918)]
Yeah, why are we dumping and loading?
Uh.
Reasons, the reasons.

##### **Geohot or Chenyu** [[00:48:48](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2928)]
Anyway, I think we want to understand why is it crashing?
Can we reproduce it reliably?
Then if so, we can discuss a boss solution.

##### **Geohot or Chenyu** [[00:49:00](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2940)]
Yeah.
To be a memory.
OK.
Anyway, that.

##### **Geohot or Chenyu** [[00:49:19](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2959)]
And I think there are other things that's blocking was the dtype fallback.
Because for now, our parsing would convert some dtype to the incorrect dtype.
And I think that's what's blocking some other refactors.
Anyway, there are many things that we want for Annex.

##### **Geohot or Chenyu** [[00:49:49](https://www.youtube.com/watch?v=nNXwJ320Dww&t=2989)]
What else do we have?
Loco?
Hi.
Hello.

##### **Ignaciosica** [[00:50:05](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3005)]
Well, regarding Locos, I'm still going after the masking issue.
And one thing I did was I also tested something with locals.
This is after locals.
Basic locals is merged.
But before, the only way I had for setting up the thread
The local memory layout was by permuting the shape tracker after it was initialized.
And that had some constraints because of the axis, the size of the axis that had to be the same and so on so it doesn't break.
But I realized that if you initialize the shape tracker, for example, you initialize it column wise, column major, it will affect the
Local memory layout, and you don't need any permutation.
So that is a way forward for the next step.
And well, that's it for locals.
And I also added, I've been benchmarking the upcast is only for globals.
And I don't think right now it's going to be.
It's a good idea to merge because of the search algorithm.
Right now, it's not that fast.
That justifies some kernels that are really slower.
And so I think that's not going to be upstreamed.
And also, I added
I mean, a PR that enables group... Wait, so why?

##### **Geohot or Chenyu** [[00:51:59](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3119)]
Your examples seem fine, right?
Your examples don't show it be any slower with Upcast Globals or not Upcast Globals.

##### **Ignaciosica** [[00:52:05](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3125)]
The second one is really slower.

##### **Geohot or Chenyu** [[00:52:10](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3130)]
Oh, the simple Matmall one?
Yeah.
Oh, I see.

##### **Ignaciosica** [[00:52:18](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3138)]
I explained why I think it is my...
The second one is bad.
But the other ones are fine.
But yeah.

##### **Geohot or Chenyu** [[00:52:29](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3149)]
Why does this block locals anyway?
I mean, you can like, yeah.

##### **Ignaciosica** [[00:52:34](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3154)]
No, this doesn't block locals.
Are we ready to merge locals?
What's been going on with that?
It's the masking issue.

##### **Geohot or Chenyu** [[00:52:44](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3164)]
And if you think it's not
What's the masking issue?
Does it create wrong code?

##### **Ignaciosica** [[00:53:06](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3186)]
No, it fails.
It doesn't even compile.

##### **Geohot or Chenyu** [[00:53:09](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3189)]
Oh, that's probably fine.
I mean, it doesn't compile, but it doesn't break anything else.
No.
Yeah, that should be fine.
I mean, as long as things aren't wrong...
There are some optimizations that... I mean, at what point does it fail?
Can it throw an error in the kernel.py?

##### **Ignaciosica** [[00:53:29](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3209)]
Yeah, I'm asking.
I mean, I don't know how to address the aliasing dimension that you mentioned, but apart from that, I'm catching it.

##### **Geohot or Chenyu** [[00:53:39](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3219)]
Well, you have to.
I mean, the aliasing dimension, you have to actually get it to be the true...
You have to get it to be the true local size.
And that is the entire challenge of locals.
If you have aliasing dimensions and you're making too many copies in locals, then that ruins everything.

##### **Ignaciosica** [[00:54:00](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3240)]
Don't I get the real size of locals if I ask for the real size in the shape tracker?

##### **Geohot or Chenyu** [[00:54:08](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3248)]
Well, but I don't know how well real size works, right?
Like, if you're, just imagine in a convolution, right?
And a convolution is going to be like, you know, it's overlapped.
You have to make sure that your locals are the actual number of fetches from the memory.
Right, like think about what the cache would do.
It has to behave like the cache, which is going to put addresses that are in the same, addresses that are the same, always in the same bucket.
Whereas if you have an alias, it has to be on aliasing at the locals level.

##### **Geohot or Chenyu** [[00:54:41](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3281)]
Is it doing that or not?

##### **Ignaciosica** [[00:54:46](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3286)]
I think it is, but I have to check.

##### **Geohot or Chenyu** [[00:54:52](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3292)]
The way you can write a test for this is do a 3x3 convolution and then upcast the entire thing and then see what the size of your locals is.
And if somehow the size of your locals is ever larger than the size of your globals, there's a bug.

##### **Geohot or Chenyu** [[00:55:09](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3309)]
Okay.
Yeah, that's a good test.

##### **Ignaciosica** [[00:55:11](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3311)]
Thank you.

##### **Geohot or Chenyu** [[00:55:13](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3313)]
But yeah, no, let's get this merged.
If it can't render everything, if there's some cases in which it just says, sorry, you can't do that if it's masked, that's fine.
But what I'm very concerned about is if it's ever wrong.
Or if it's wrong or if it's using massively more memory because it's missing aliasing.

##### **Ignaciosica** [[00:55:39](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3339)]
One last thing is I added a PR that enables group with TensorFlow course.
I'm having the same problem with CI, that it's failing in the Metal CI, but I test passed locally on my computer and also Sibo tested locally and he passed the test for him too.

##### **Geohot or Chenyu** [[00:56:01](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3361)]
So I don't see a failure.
You're talking about 10.903?
I don't see a failure.

##### **Geohot or Chenyu** [[00:56:08](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3368)]
No, because I skipped for Metal and CI.
Yeah, that's fine.

##### **Geohot or Chenyu** [[00:56:19](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3379)]
If it passes with O0 and it doesn't pass with O2, it's probably a compiler bug.

##### **Geohot or Chenyu** [[00:56:27](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3387)]
Yeah, it's fine.
Cool.
Yeah, I'm fine with... Let me see.
What's this doing?
Yeah, I'm fine with merging this.
OK.
Cool.
Yeah.
That's it.
Great.

##### **Geohot or Chenyu** [[00:56:58](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3418)]
Yeah, no, Apple's driver is kind of meh.
And we have that bug on the M2.
I don't know.
Apple's going downhill.
It's not just their driver.
It's their whatever thing they use for .
Oh, oh, I mean, yeah, that thing's crappy, too.
They're like virtualized thing.
But yeah, OK, cool.
I'm just going to click merge on this.
I don't totally understand how it works, but it seems short, so.

##### **Ignaciosica** [[00:57:32](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3452)]
The idea behind this was that group should work with a sensor course equals two, then basically the same opts.
So if it didn't work, it was due to an implementation details on the actual sensor course.
But in theory, it should work.

##### **Geohot or Chenyu** [[00:57:51](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3471)]
Whenever I see a three line change that enables something with a test, I'm usually happy to merge it.
So cool.
That's merged.
OK.
Let's go through other Bonti's rapid fire style.
Let's start with RetinaNet.

##### **Wozeparrot** [[00:58:08](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3488)]
Hey, so quick update.
I think I finished the rewrite, I'm pretty sure, over the weekend.
So I'll be testing the correctness of it entirely.
So I'll just run the eval script of the old NumPy implementation versus the new one.
And then from there, I'll see if I can get the rewrite to Tinygrad.

##### **Geohot or Chenyu** [[00:58:31](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3511)]
Just let me know if you need me to review anything.

##### **Geohot or Chenyu** [[00:58:35](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3515)]
Sounds good.
Are we doing better than AMD?

##### **Wozeparrot** [[00:58:55](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3535)]
No, we're doing the same as AMD.

##### **Geohot or Chenyu** [[00:59:05](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3545)]
Well, isn't AMD the bad one?

##### **Wozeparrot** [[00:59:08](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3548)]
No, no.
For 8B, AMD is fine.
For 8B, like BF16 or whatever.

##### **Geohot or Chenyu** [[00:59:14](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3554)]
They had some issue with mostly FBA models, and I believe it's mostly fixed now.
Great.
We're doing the same as AMD.
That's okay.
And they do the same as NVIDIA.
Oh, yeah, yeah.
The same as NVIDIA.
That's what we really want.

##### **Geohot or Chenyu** [[00:59:32](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3572)]
Great.
AMD AOVM.

##### **Geohot or Chenyu** [[00:59:40](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3580)]
By the way, do we want a bounty for battery reorder or register pressure-based reordering?

##### **Geohot or Chenyu** [[00:59:48](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3588)]
Yeah, I see that PR.
It adds a lot of lines.

##### **Geohot or Chenyu** [[00:59:56](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3596)]
Even for your Haley thing, you would eventually need a cost model somewhere.
I know you're going to need a cost model.
Yeah, the problem with like just doing it at the reorder level is register pressure is the same problem as memory pressure.
It's almost like I don't even like that we have linearized separate from schedule because they're really all the same problem.
I think if there's one thing that's going to make Tinygrad win, it's going to be that
Each one of these places in the hierarchy, right?
Like you have like registers to L1, L1 to L2, L2 to GMEM, GMEM to all your GPUs.
Like it seems that every other system handles them all differently.
And there's no reason this should be true.
If we win, it's because we handle them all the same.
So I'm very reluctant to merge something that's like a improvement to their reorderer.
If it's blocking something, then I guess we can merge it.
But from a more fundamental perspective, I think we have to solve these problems in a more broadly applicable way.
I think the issue here is is slower with the current reordering.
How much slower?
Like 20%.
I don't know.
Yeah, so no, no.
So the solution is probably not something like that.
We just need a direction on this eventually.

##### **Geohot or Chenyu** [[01:01:36](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3696)]
The eventual direction is to figure out.
OK, not something we don't need to answer now.
That's fine.
Yeah.
Yeah.
OK.
Anyway.
So lastly, so the closing stuff, it's on today?
Mm-hmm.
OK.
Wait.

##### **Geohot or Chenyu** [[01:02:11](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3731)]
So basically, we can talk about this later.
But I'm seeing basically it runs two algorithms and then chooses them with a selector.

##### **Geohot or Chenyu** [[01:02:24](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3744)]
Oh, what was that?

##### **Geohot or Chenyu** [[01:02:27](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3747)]
I'm reading the register pressure aware, and it's like running two algorithms and then choosing them with a selector.
If there's one principled way to deal with this, ideally it's some optimizer.
Ideally it's some real optimizer that says, okay, how do we actually minimize register pressure here?

##### **Geohot or Chenyu** [[01:02:47](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3767)]
We know all the toposorts, we know all the, yeah.
Yeah.
Okay.
Sorry, that was kind of a tangent.
No, no, that was fine.
Cool.
How about the Linage SVD?

##### **Geohot or Chenyu** [[01:03:12](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3792)]
Oh, I thought you were reviewing that one.
I have one that I locked.
Did they remove the realizes, and did they remove the manual seed?
My manual seed is gone.

##### **Geohot or Chenyu** [[01:03:24](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3804)]
One realize is still there.
Without them, the tests fail.
Interesting.

##### **Geohot or Chenyu** [[01:03:42](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3822)]
Yeah, we really need realizes removed.
Okay.
I don't know, but this might be a bug beyond...
What the SVD thing is.

##### **Geohot or Chenyu** [[01:03:52](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3832)]
I'm tempted to merge this and pay out the bounty.
Okay.
I don't know.
You don't like it?
It looks pretty complicated.
I mean, but is the algorithm this complicated?
Yeah.
No.
No?
It's probably a sim algorithm, but it's just... I don't know.
It's probably fine.
It doesn't look clean.
It's similar to whatever.
Yeah, but read page 26 of the paper.
It doesn't look better.
I don't know.

##### **Geohot or Chenyu** [[01:04:39](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3879)]
I mean, every time there's things between reshape, expand, and gather, whatever, usually what happens is I will stare at it for
Some minutes and write more tests and clean it so that I make sure it's using minimal number of stuff.

##### **Geohot or Chenyu** [[01:05:04](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3904)]
Oh, yeah.
It's fine.
I think it's fine.

##### **Geohot or Chenyu** [[01:05:12](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3912)]
I think it can be cleaned up, but I'm not sure that's a reason not to merge yet clone in there.
Oh, there's a dot clone in there too.

##### **Wozeparrot** [[01:05:21](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3921)]
Yeah.

##### **Geohot or Chenyu** [[01:05:21](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3921)]
Oh, it's using clones and realizes.

##### **Wozeparrot** [[01:05:24](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3924)]
Where's the clone?
It's in QR.

##### **Geohot or Chenyu** [[01:05:30](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3930)]
Do you need this clone?
Oh, there's two dog clones.

##### **Geohot or Chenyu** [[01:05:33](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3933)]
Oh.

##### **Geohot or Chenyu** [[01:05:35](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3935)]
Oh, the issue was... Oh, is it assigned to?
Oh, yeah, it's assigned to there.
Yeah.

##### **Geohot or Chenyu** [[01:05:46](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3946)]
I mean, this is a good stress test for Tinygrad anyway.
Yeah.
Okay, I don't know.
That's probably fine.

##### **Geohot or Chenyu** [[01:05:59](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3959)]
If it's working and it's not terrible, it doesn't hang your machine, it's probably fine.
Worst case, you just don't use it.
Yeah, maybe I'll test it on a few big ones and we'll see if the speed is within 10x of Torch, I'll merge.
If the speed is within 1000x of Torch, I won't.

##### **Geohot or Chenyu** [[01:06:17](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3977)]
And, okay, what's the behavior if it doesn't have SV?
Does it hang?
Or does it just produce the wrong answer?

##### **Geohot or Chenyu** [[01:06:31](https://www.youtube.com/watch?v=nNXwJ320Dww&t=3991)]
I mean, nothing can hang.
It has a fixed number of iterations.
It probably just produces the wrong answer.
But yeah, no, the paper that he took it from, like, you could say the code looks complicated, but the paper that he took it from looks equally complicated, so...

##### **Geohot or Chenyu** [[01:06:47](https://www.youtube.com/watch?v=nNXwJ320Dww&t=4007)]
I don't know.

##### **Geohot or Chenyu** [[01:06:51](https://www.youtube.com/watch?v=nNXwJ320Dww&t=4011)]
I don't know.
It's the same as Transcendental.
It's also from a paper.
I read the paper.
I wrote a much simpler one.
Yeah.
It's fine.
It's fine.
I don't know.
I have like a high school when you're out there.
It's fine.
And you can always improve it later as long as it's not wrong in a bad way.
Yeah.

##### **Geohot or Chenyu** [[01:07:13](https://www.youtube.com/watch?v=nNXwJ320Dww&t=4033)]
Sounds good.
I'll leave that to you.
And I think that's it.

##### **Ignaciosica** [[01:07:19](https://www.youtube.com/watch?v=nNXwJ320Dww&t=4039)]
Also leave a CIFAR one to you.

##### **Geohot or Chenyu** [[01:07:23](https://www.youtube.com/watch?v=nNXwJ320Dww&t=4043)]
Yeah, yeah, yeah.
I mean, is everything in the JIT and are there still realizes?
If everything's in the JIT, I'll merge the CIFAR thing.
But every time I ask if everything's in the JIT, they're like, this one can't be in the JIT.
And I'm like, okay, well, it's not done.
OK, so we have LED, we have SVD, and we have the sub-buffer.
I think those are the active ones.
Oh, this looks better.
OK, it looks like maybe everything's in the JIT now.

##### **Geohot or Chenyu** [[01:07:57](https://www.youtube.com/watch?v=nNXwJ320Dww&t=4077)]
They put fusee range there.
Oh, context is decorated.
That's cute.
OK.

##### **Geohot or Chenyu** [[01:08:15](https://www.youtube.com/watch?v=nNXwJ320Dww&t=4095)]
Maybe if everyone can go through the working PR and close the bad ones or stale ones so that we don't have five pages of PR, that would also be great.

##### **Geohot or Chenyu** [[01:08:28](https://www.youtube.com/watch?v=nNXwJ320Dww&t=4108)]
We shouldn't have more PRs than number of issues.
And with that, I think we can conclude this meeting.
Sounds good.
Thanks, everyone.
Thank you, everyone.
See you next week.
