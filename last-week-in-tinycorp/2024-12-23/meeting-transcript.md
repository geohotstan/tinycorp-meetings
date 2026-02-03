# 2024-12-23 Meeting

### Meeting Agenda

**Time:** 9:30 AM San Diego time (PST)
- Company update
- Scheduler cleanup
- AM and usb gpu
- Comma openpilot new tinygrad runner, use tinygrad onnx for rollout
- Llm.c
- Whatever geohot wants to add
- Bounties (onnx, tensor cores, x86 backend, int64 indexing, OSX GPUOcelot, blake3)

### Audio

[Recording](https://drive.google.com/file/d/1dSJqEtORyHW1dEgGcsFd0jM9DUUN3FDl/view?usp=sharing)

### Chapters

- **00:00:00 Company Update**  
  Green boxes and TinyBox Pros are selling well; Comma's integration with TinyGrad is progressing.

- **00:02:19 Scheduler Cleanup**  
  Focus on reducing fragility in scheduling, handling UOp tracking, and improving rewrite rules.

- **00:09:07 AM and USB GPU**  
  Stability improvements for AMD GPUs and USB GPU optimizations; discussions on DMA and libUSB rewrites.

- **00:14:02 Comma ONNX and TinyGrad Rollout**  
  Importance of ONNX model support for broader adoption and TinyGrad's role in Comma's model training.

- **00:17:50 Kernel Performance and Tensor Core Integration**  
  Debugging performance for float32 matmul kernels and integrating tensor core support.

- **00:21:32 Active Bounties**  
  - **00:21:32 ONNX Top Models**:  
    Feedback: Prioritize testing and supporting the top 100 ONNX models for better adoption by companies like Comma. Ensure correctness when running these models and validate architecture compatibility.  
  - **00:22:07 TensorCores**:  
    Feedback: verify stability and ensure minimal controversy before merging.  
  - **00:27:30 x86 Backend**:  
    Feedback: Benchmark the backend against Clang and LLVM to identify missing optimizations. Avoid merging if the register allocator is excessively inefficient or stack spilling is excessive.  
  - **00:29:56 Int64 Indexing**:  
    Feedback: Address critical bug fixes to support int64 indexing in TinyGrad. Avoid defaulting all indices to int64 unless necessary; instead, target specific cases where it’s required.  
  - **00:30:49 OSX GPUOcelot**:  
    Feedback: Merge HTQ file prerequisites and upstream patches. Ensure dependencies like the KFD driver are merged first for compatibility.  
  - **00:31:24 Blake3**:  
    Feedback: Remove print statements, add a proper benchmark, and optimize code for production readiness. Current implementation is not yet ready for merging.  

- **00:33:40 Retinanet Training and PR Closures**  
  Progress on retinanet losses and plans to close stale PRs inactive for over 30 days.

- **00:35:43 Example Kernels and ClangJIT**  
  Updates on custom kernels for maximum speed examples and progress on ClangJIT optimizations.

- **00:36:52 Whisper Bounty and TinyCloud**  
  Whisper bounty for transcription examples and plans for reliable TinyCloud services.

- **00:37:46 End-of-Year Goals**  
  Final push to merge AM updates, new gradient APIs, and scheduler improvements before year-end.

### Transcript

**Chenyu** [00:00:00]
Welcome to meeting number 50.
George do you want to start with company update?
Do we have enough green box to sell?

**Geohot** [00:00:14]
We do.
Yeah, I know.
We sold three more this week.
So the green boxes are really flying off the shelves.
Yeah, I think we have.
That might have been the last one.
Well, nothing's going to ship until after the holidays anyway.
We have some parts to build some more also, so we are..
Good on that.
Yeah, green boxes are really flying off the shelves.
We delivered [27 TinyBox Pros](https://x.com/gregjhogan/status/1870712068644741287) to Comma.
We have a bunch for pre-orders ready to ship.
I'm not sure we've gotten any of the wires for those yet.
But yeah, if you want a [TinyBox Pro](https://tinycorp.myshopify.com/products/TinyBox-pro), I think we have one extra that we can ship right away, and then the rest will ship Q1 next year.
But yeah, 27 are up for Comma.
They all seem stable.
We had CPU issues with one, but it's about the CPUs.
Those are good.
Yeah.
Tiny boxes are moving.
And oh, Dylan Patel wrote a [scathing review](https://semianalysis.com/2024/12/22/mi300x-vs-h100-vs-h200-benchmark-part-1-training/) of the AMD ecosystem.
So, you know, if AMD is not going to listen to semi-analysis, it's pretty much.. 

**Chenyu** [00:01:30]
Yeah, Flammit may share a link in the AMD channel as well.

**Geohot** [00:01:36]
Yeah, they're the most respected reviewer of these things.
They speak at all the big companies, even all the hyperscalers.
And if you're not going to listen to them, well, yeah.

**Flammit** [00:01:50]
It's interesting how much their journey mirrored our own, right?
Down to the filing the bug report and custom build.

**Geohot** [00:02:00]
It's identical, and they don't understand how broken their process is.
Yeah, I think that's company update.

**Chenyu** [00:02:19]
Cool.
Let's move on to scheduler cleanup.

**Qazalin** [00:02:28]
Yeah about that um so i'm working on first getting the merge view stuff merged there are some like instant folding rules we have in the views and uh so far I could pass almost all the tests I have some problems with gradients that i need to solve
So that is PR number [8380](https://github.com/tinygrad/tinygrad/pull/8380).
And once that's merged, the fragility in the scheduler will go away.
Because a lot of this is like views getting merged early versus late.
So that's what I'm working on.
And then I'll transition to just deleting all the elements by symbolic folding rules and making everything work with the existing rules.
That's my plan.

**Geohot** [00:03:25]
I think a lot of the instability comes from whenever you're assuming things about the structure.
You want UOps to be as absolutely local as possible.
Whenever you're assuming what its parents are or what its children's going to be, or when the meaning of a UOp comes from its children, this is why we have the fragility.
The meaning of the UOp should only ever come from the UOp itself and its parents.
And ideally, its parents as close as possible.
Like the UOp, like, for example, copy not having a device is a problem because the copy UOp is no longer defining the copy.
It's only with the context of the buffer, which even worse as a child, that it gets the full context.
So, yeah, and, like, the other thing is, like, to even explicitly think about it shouldn't just be one construction that works.
Like, UOp should just have a meaning.
In the same way, like, words have a meaning.
And you can put words together in all sorts of orders.
You should be able to put UOps together in all sorts of orders.
And, like, they should all have a meaning.
You can't have, like, a UOp that's like, well, if you put that UOp next, it's invalid.
Like, that should really never be true.

**Qazalin** [00:04:44]
I think one thing I'm having challenges with right now is the question of how do you keep track of these UOps when you're const folding.
So even after all these things are getting done, there's still this problem of every single UOp having a buffer early on just because
we need a way to get back to the tensor.
I think you had a proposal for the tracking.

**Geohot** [00:05:19]
You have a proposal for the.. Okay, so the tracking is not obvious.
It's not.. It's going to require some new sort of innovation.
The concept of tracking a UOp through rewrite rules
is not something we've really fully explored yet.
So yeah, I mean, you want something that basically will maintain a dictionary if the UOps change.
Maintain maybe a dictionary that maps the pre-rewritten UOps to the rewritten UOps or the other way around.
Yeah, you want to map the rewritten UOps to the pre-written UOps.
So I think this is going to involve messing with the rewrite itself.
But I'll emphasize that the fragility I was experiencing has really nothing to do with this, the fact that it's buffers.
I'm not that upset about buffers.
I'm upset about when I delete some view folding rule that should be an optimization, the whole thing breaks, and it breaks in incomprehensible ways.
It breaks with errors that are.. I had one where I deleted the first pass at that other one where I did the UOp fusion.
The word through was appearing in rendered things.
And that only happens when you're taking args of sources that you have not type checked.
So I'm glad to see that stuff moving in the right direction.
But yeah, then there's two other problems to solve that are kind of..
orthogonal to the instability.
One is a tracking rewrite, and the other is UOp mutability.
And I think tracking rewrite is a prerequisite for UOp mutability.
And yeah, maybe when you feel that things are very, very stable, start thinking about tracking rewrite, and I think you need that for const folding.
But no, it's good to see things becoming more stable, and I want all the cast before view.
Anything that requires an instant rule in Ops.py should not be there.
Like, it needs to be a rewrite rule.
Cool.
I think things are moving in the right direction.
And yeah, the buffer thing was just, like, make sure that it's documented.
I totally understand why it's there.
You need to figure out which tensor is mapped to which UOps, and right now, buffer UOps need done to do that.
And it's not the worst solution, and it might even end up being some variant of what we end up with, so.
You can also imagine a rewrite that happens before scheduling that does things like constant folding and then reapplies those UOps to the tensors.
That's an option.
Like it doesn't do any realization.
It just does simplification and then sets the tensors to the simplified UOps.
But that's like a UOp tracking rewrite that you can then scatter them to all the tensors.
And I think I talked about this a little bit.
You also have to think about children on the graph too.
So you'll have to explore the whole graph, run the simplification rule, track them, put them back in the tensors.
And I think that's the plan for mutability as well.
But yeah, specs and keep going on it.

**Chenyu** [00:08:56]
OK.
Let's move on to AM and USB GPU.

**Nimlgen** [00:09:07]
Yeah, so I fixed, I think, the bug I mentioned last week.
I mean, AM bug.
So it's pretty stable.
I've been testing BERT BEAM a lot.
So we had problems with BERT BEAM.
previously, previous MLPerf.
So, actually, AM is stable, so I'm going to.. Are we good on lines?
I think we can.. George said that we can raise them.
So, yeah, I'm going to merge AM soon.
And.. So, yeah, it's still a bit slower.
I mean, I'll follow up with some fixes.
But, yeah, it's actually stable right now.

**Chenyu** [00:09:54]
How many lines are there?

**Nimlgen** [00:09:57]
So it's 650.

**Geohot** [00:10:02]
So I think the first thing to merge is the kernel interface.
Just make sure that abstraction's good.
Get that merged separately.
Yeah, it's definitely looking closer.
I saw you have an allocator.
Just a little bit of documentation about how the allocator works.

**Geohot** [00:10:25]
I googled it and it was a uh uh like a known thing but yeah it was just a couple of lines for how it works 

**Nimlgen** [00:10:34]
yeah so yeah I also had some tests uh and for USB GPU um so actually with the like
23rd chip it works I mean yeah as I said it's pretty slow I mean I started to rewrite with libusb I haven't finished that I think first of all I think that we can make it faster because we have like we sent like SCSI commands to different registers and I think because of the SCSI interface it's just they do the sequential I think we can just
So they send it sequentially.
I think we can just definitely optimize that.
And maybe it will be, like, I don't know.
I mean, 10x faster?
Because we sent, like, 19 comments each PCIe access.
And I think definitely 10 of them and 10 of them.
We can send them in batches of 10.
So yeah, maybe this can help.

**Geohot** [00:11:49]
I think this can make it a bit faster, but I think fundamentally there's not going to be a way around figuring out how the chip is doing DMA.
The chip is very, very fast when reading and writing to NVMe drives.
So there is some way to DMA onto the PCIe bus.
The question is, how much of it can we use individually?
Yeah, you know, in the absolute extreme, we changed the firmware that's running on the device.
It is flashable.
It looks pretty simple, but I'm hoping we don't have to do that.
I'm hoping we can just figure out what the fast interface is and use that.
But yeah, I think a libUSB rewrite is a good first step anyway, because if we want this to work on Mac, we're not going to have DevSG0, so..
The goal is Mac.
The goal is literal drop-in anywhere.
If you have a user-space USB, you get a GPU.
And I think that's a crazy accomplishment.
No one else has stacks that look like this.
And there's no fundamental reason.
There's no fundamental reason other stacks don't look like this.
It's enough for speed.
It's mostly just for legacy reasons.
But yeah, we are.. I think, yeah, a good first step is libUSB and batching requests.
But we're going to still have to figure out how the DMA works.
And with regards to line count for AM, let's get all the prerequisites merged first.
Maybe if the only prerequisite is just the refactor for the new interface, then let's get that one merged.
And then, yeah, if it's good, have you fixed the speed issues?

**Nimlgen** [00:13:24]
Not yet.

**Geohot** [00:13:27]
We've got to get those fixed before it's merged.
Do you know what it is?

**Nimlgen** [00:13:36]
Really not yet.
I think definitely there is one optimization to do to memory handling, but I'm not sure that's it.

**Geohot** [00:13:48]
Got it.
Yeah, well, let's get the prerequisites in either way.
And then if you think it's really ready to merge, maybe even if the speed thing isn't fixed, we can bump a line down and do it.
But yeah, good progress.

**Chenyu** [00:14:02]
Great.
Okay.
Moving on.
So the next one is about our biggest user Comma.
So Comma merge or update a newer version again on their runner.
It's a third attempt.
So far it's not reverted yet.
So hopefully it's good.
It's very important.
Or I think one main goal for TinyGrad is to suit Comma's use case because we want to empower other companies like Comma that builds, train, and run their own model.
So after this, the next step I really want to push is for Comma's rollout.
the, they have like models that they currently run on Torch or I guess on Onnxruntime or Torch, I'm not sure which one, but we want to see if we can, you, we can also ask them to use TinyGrad to run it.
So, so far I've heard good things.
The speed seems to be pretty fast.
So we'll see how that goes.
So that's kind of the reason we talk about like ONNX and supporting popular ONNX architecture and making sure everything is correct, because I think
For other companies, their very first project to use TinyGrad is very likely to be a project like this.
Like they have a train or already a model they are already using, and they can store it in ONNX format, and they can use TinyGrad, import the model, and run the model to start with.
is asking a lot for other companies to like totally migrate to TinyGrad and write everything from scratch using TinyGrad and it's a lot easier for them if ONNX is a it's a very uh popular format and if we can support this well i think that's a very good starting point for promoting TinyGrad yeah so that's why i put out a bounty for
Supporting like the top 100 models, making sure it's correct.
And if it's, we will be using this to prioritize every time we do a decision to say, okay, do we support this or not?
It's a lot easy to justify these decisions.
If we say, okay, this is important because everyone is using it.
Then we need to find a way to support it.
So that's about Comma ONNX.
And I was also looking into llm.c speed.
I think any box red, we are 20%, about 20% slower than
the torch nightly version or I was wrong.
I don't know, a few months ago, maybe, maybe like maybe torch got faster, but I think that's a good target anyway.
And now it seems to be the slower part is coming from two matmul kernels that because they think float32, it doesn't trigger tensor core.
But it's still quite slow than I believe it should be.
So I'll probably spend the next today or this week to look into why that is slow.
It might be something to do with the older reload stuff or non-tensor core stuff.

**Geohot** [00:17:50]
Why is it float32?
Why is it not float16?

**Chenyu** [00:17:54]
Oh, because it was in float32.
We were doing 32 to 32 comparison.

**Geohot** [00:18:04]
I see. Okay.

**Chenyu** [00:18:07]
I mean, of course, it would be faster if it's 16 because it triggers TensorFloat.
But I think this is a good opportunity to look into why certain things are surprisingly slow.
Yeah.

**Geohot** [00:18:13]
If Torch is faster running the same kernel, what do we do?

**Chenyu** [00:18:19]
We probably also need to double check that Torch is not doing something
like rewrites your matmul default into TF32 or something like that and triggers TensorCore.

**Geohot** [00:18:31]
But there's no TF32 on AMD.
Is this on AMD or on NVIDIA?

**Chenyu** [00:18:35]
Oh, AMD.

**Geohot** [00:18:40]
I don't know.
AMD Tensor Cores are only for float16.

**Chenyu** [00:18:42]
Yeah, that makes sense.
And my point is, even for float32, it seems very slow for
from just TinyGrad compared to other kernels in TinyGrad.
So yeah, my goal is to fix that.
And with that, we should be on par with the likely number we get.
So that number is without flash attention, without any crazy optimization and compile.
So we should at least beat that.
and there are definitely more things that we need to do if we want to improve that it's it's very similar to our BERT speed there are just uh we have like bad layer norms and just some current mostly a lot of like kernel fusion decisions that uh hopefully with the
New scheduler can be fixed.
FuseArange is another thing that improves another 10 milliseconds.
Leads or adds up to making the whole pipeline fast.

**Geohot** [00:19:55]
Yeah, I think it's a good thing to push on.
I think hopefully the scheduler should let us make those changes easily.

**Chenyu** [00:20:07]
Looking forward to that.
The next one is whatever Geohot wants to add.

**Geohot** [00:20:13]
Pretty much said most of what I wanted to say.
Yeah, really looking forward to the schedule getting better, getting new gradient merge.
I worked a lot last week on
There is a change to the API.
We still have.backwards, so we're not just pushing the new gradient API.
People from PyTorch talked me out of it.
But we won't be able to compute a backward pass if you've realized the forward tensor.
I don't think this is too much of a limitation, but it did require updating to a few tasks.
But most of those updates are done, and the biggest blocker on deleting gradient, the old gradient stuff, is cast before view, which should be fixed in the new scheduler.
The main thing I've been working on.

**Chenyu** [00:21:10]
Okay.
And some of the active bounties for ONNX.
ONNX, we just discussed why it's important.
And I think the person working on it was traveling.
So he will be back this week.
So let's move on to TensorCores.

**Ignaciosica** [00:21:32]
Hi.
I marked the PR as ready for review.
I think I tested on the Intel machine and it worked.
It had a bug in bfloat16, but I think it's because of the casting.
It was broken before with a straight bug.
I fixed that, but padded tensor cores are still failing.
But I think it's independent from the PR I'm working on.
So I mark it as ready for review and that's it.

**Chenyu** [00:22:07]
PR [8292](https://github.com/tinygrad/tinygrad/pull/8292)?
OK.

**Ignaciosica** [00:22:23]
I added a guide to how to reason over the of the tensor cores.
And as an example, I
I made a walkthrough in adding tensor cores for TF32, and also the shapes for all the other tensor cores that are supported.

**Geohot** [00:22:46]
Great.
So does this support TF32, or is that separate from this PR?

**Ignaciosica** [00:22:50]
No, no.
It's separate, but the changes are in the README from this PR.
It's like a standalone PR.

**Geohot** [00:23:01]
Yeah, how did you generate these pictures?

**Ignaciosica** [00:23:06]
I drew them in ScaliDraw.
It's an app.

**Geohot** [00:23:11]
Cool.
Yeah, I mean, it looks pretty good.
I'll do a better review of it later today or tomorrow.
But I think we're good to merge it and then..
Yeah, hopefully with these refactors, it could be easy for you to clean up all the bounties for the other Dtypes and stuff.
They're all locked to you.
So yeah, first refactor, then yeah, cool.
Looks good.

**Ignaciosica** [00:23:44]
OK, thank you.

**Chenyu** [00:23:38]
Cool.

**Ignaciosica** [00:23:41]
Sorry.
No, no, no.
I'm sorry.

**Chenyu** [00:23:47]
Go ahead.

**Ignaciosica** [00:23:49]
I think the main point to talk to is from the Swizzling the view right.
I changed one spec in how the view is pushed right.
And I think that's the most controversial change in the whole PR.

**Geohot** [00:24:16]
Yeah, I see it here.
Qazalin, I'm curious what your thoughts are on this.
I'm not that familiar with this code, or if this makes sense.
One of the problems I've seen with the scheduler, maybe it's the same one, if you have two views next to each other, the two views should be added together, which I feel like that doesn't always happen.
Is that the same thing as this, or..?

**Qazalin** [00:24:45]
That actually does always happen.
It just happens late.
I'll make sure it happens early, but there's nothing blocking that to happen.

**Geohot** [00:24:55]
Yeah, I mean, no, I agree.
This change is actually very controversial.
Push the permute from source to root if the shape is the same?
Hmmmmmmmmm..

**Qazalin** [00:25:06]
Like, I think a lot of these stuff, Ignaciosica, do you remember the PR that you had for True Swizzle?
It was one line and the ShapeTracker from shape.

**Ignaciosica** [00:25:17]
Yes.

**Qazalin** [00:25:18]
These stuff tend to be much more simpler.
The ShapeTracker is a very stable API.
If you need to do stuff to hack around it, there's something wrong upstream of this.

**Geohot** [00:25:32]
I don't think this is the ShapeTracker.
I think this is specifically saying we push per mutes if the shape is the same.
It's a scheduler decision.
I'm not exactly sure why you need it.
I'll have to sit down for an hour and really spend time with this to understand.

**Ignaciosica** [00:25:51]
Yes, the thing is that it didn't push the permutative because it created a ShapeTracker from a shape that it's contiguous.
So it doesn't swizzle right if this change isn't added.
So that's why it's the only way I found to push the view, the swizzle right.
But yes, as I said, it's the controversial thing.

**Geohot** [00:26:24]
Is there some part of this that's less controversial that we can merge as a prerequisite?

**Ignaciosica** [00:26:30]
No, because all the other changes depends on the output of the tensor core.

**Geohot** [00:26:39]
Yeah.
OK, I'll have to send some time and think this through.
But no, I mean, I definitely like the simplification to the tensor core class is great.

**Chenyu** [00:27:00]
Sounds good.
I don't think the person who's working on x86 is here.

**Geohot** [00:27:06]
Yeah, the main thing I asked for for that was I want to know how the speed compares to Clang and LLVM.
I'm okay with not all the optimization being in there.
If it's something like SIMD, yeah, whatever.
That's just something we have to add.
But if the register allocator is egregiously bad, I don't think we should merge it.
So that's the main thing I want to know.
If it's stack spilling everything, no, we got to do better than that.

**Chenyu** [00:27:37]
Okay, so benchmark that against LLVM, see how bad it is and understand what's, if it's like missing optimizations, fine, but if something fundamentally wrong, then that needs to be fixed.
Okay, int64 indexing.
I also don't know if the person is here.
So I comment this in the Bounty channel.
I think for now, it's a bug fix because we certainly have example code like training MLPerf or there are other people reporting issues like hit this.
And for now for TinyGrad, if you hit this, there's no way around it.
So that's the main reason we want this.
We definitely don't want to just convert every default index to int64 because that's very slow.
I think the question was around, OK, if you start with int64 and some intermediate variables or ALUs can be int32, do we want to downcast it or not?
And first, I don't think that's a very common use case because at least the two int64 kernels that we encounter
Doesn't have that.
So I think it's probably fine to start saying, OK, at your index to UOp upstage, check if they can be more than int64.
And if so, change or its source or any relevant parts to int64.
So at least that makes TinyGrad correct if that can be the case.
Then internally, for least like intermediate, do we want to do a smaller Dtype or not can be a separate optimization step.
So that's my view on this bounty.
OK.
Next is GPU Ocelot.
I see the GPU Ocelot author comment on the PR saying they would upstream the patches.

**Geohot** [00:29:56]
Yeah, no, I mean, the patterns look great.
Nimlgen, can we get HTQ file merged?
Because I see that that PR is targeting HTQ file.
So that's kind of a prerequisite for this.

**Nimlgen** [00:30:11]
Yeah, OK, we'll do that tomorrow.

**Geohot** [00:30:15]
Cool.
Yeah, no, HTQ file and the KFD driver thing should be merged before we think about merging AM.
Yeah, but I think once HTQ files merge, I'm okay with raising the line number for these things.
Once HTQ file is merged, then yeah, that should be good.
And the bounty is yours.

**Chenyu** [00:30:49]
No, no, no.
You finish first.

**Geohot** [00:30:51]
Oh, yeah, no, that's all I got.

**Chenyu** [00:30:53]
Okay, no, I ran the coverage thing.
And I just remove another 20 lines of like, unused and untriggered and untested stuff.

**Geohot** [00:31:04]
Oh, great.

**Chenyu** [00:31:08]
It's more compact.
Okay, blake3.
I think the main ask is just to benchmark and test how fast it is.
And I think it's also currently failed on one of the backend.

**Geohot** [00:31:24]
Yeah, I also see, like, I'm looking at this code.
Like, it's in extra.
It has tons of print statements, and it doesn't have a benchmark.
So those are, like, three things we kind of need before we can merge that.
Yeah, this doesn't look optimized.
There's literal print statements in the code.
So this is not ready to merge yet.
This is not supposed to be demo code.
This is supposed to be a production implementation of blake3.

**Chenyu** [00:32:24]
OK.
Do you want to say something about ClangJIT?

**Geohot** [00:32:28]
Oh, yeah.
ClangJIT.
There is one line in it that's quite sketchy.
which is this, I have to really understand more of what it is.
The fact that normal Clang can produce something that doesn't need it, but ClangJIT needs it, makes me very suspicious.
But yeah, no, otherwise it looks pretty clean.
I think we're making progress on that.
I locked the bounty.
We'll get it in, but we have to fully understand if we need that, if platform, machine, ARM64, and OSX align.
Yeah, and the ClangJIT program is.. Maybe it shouldn't even be named that.
I'm not that worried about the name for now.
But what it really is is just a raw assembly program.
And if we could move LLVM, Clang, and x86 Assembler all to this new thing, it runs very fast compared to CTLL, which is super slow for some reason I don't quite understand.
It's probably making tons of syscalls and something.
So, yeah, no, I think we're going to get it in, but we've got to really understand..
why it's different.
And we need a way to disassemble, which I don't see.

**Chenyu** [00:33:28]
OK, sounds good.
So I see flata is here.
I see is Sieds Lykles here.
If you want to talk on anything that you are working on, feel free.

**Flata** [00:33:40]
I guess I can go first.
I think I've figured out the losses for retinanet training.
So I think what I'm going to try to do now is for correctness.
I'm probably going to train on a very small batch size of the dataset.
And then once that looks good, I'll progress through an actual full training.
And then once I feel ready to go with that, I'll put up a PR.

**Chenyu** [00:34:02]
You can put a PR first.
I can lock that to you.

**Flata** [00:34:07]
Okay, sounds good.
Okay, I'll do that.
I'll obviously just put it on draft.

**Chenyu** [00:34:13]
Cool.
Speaking of PR, as I said earlier, I want to find a way to close the stale PR, stale defining as inactive for more than 30 days.
So I will probably do that this week.
Ideally, I want to find a bot to do that.
That's the plan.
So if you have things you want to still working on, just update it.
Or you can open a new one after I close the old one.
That's also fine.
Can't talk.
Really?
I thought you have the permission to talk.
Anyway, if you say it will be ready in next few days, great.
OK, I don't know.

**Flammit** [00:35:43]
Sorry, speaking of old PRs, the example within the max matmul, I mean, it's all extra.
It doesn't impact anything.
I can't remember what we were waiting for, or maybe it doesn't need to get merged to extra.

**Chenyu** [00:35:36]
Which one is it?

**Flammit** [00:35:38]
You know, the custom kernels showing how to get to max speed.

**Chenyu** [00:35:43]
Oh, sure.
I mean, if you want that to be merged, we can merge it.
It's more like an example, right?

**Flammit** [00:35:52]
Yeah, exactly, just what linear algebra.

**Chenyu** [00:35:57]
Just ping on the PR so that it got bumped up in the stack, and I will take a look, or someone can take a look and merge that.

**Flammit** [00:36:08]
Cool, thanks.

**Chenyu** [00:36:13]
Do you have anything you want to add?

**Geohot** [00:36:18]
Nope, I think that's good.

**Chenyu** [00:36:21]
Yeah, so that's all for meetings.
People in this meeting, if you have questions about TinyGrad, you can type in the general channel or the chat channel.
We also added, I also added the whisper bounty because it would be cool that we have a whisper examples that we can run these meeting recording through TinyGrad.

**Geohot** [00:36:52]
Yeah, I can't wait till we have TinyCloud up.
We can just put those things into TinyCloud.
TinyCloud is going to be super reliable, always up, very easy.

**Chenyu** [00:37:01]
Great.
Yes.
That would be cool.
Yeah, so next week's meeting is the last one of this year.
I'll probably put up a year in review for TinyGrad project for that one.
I don't have anything else for this one, so.

**Geohot** [00:37:30]
But yeah, some quick end of year goals.
Yeah, AM merged, new gradient merged.
And I think then we basically did everything we said we were going to do in Hong Kong for the end of the year.

**Chenyu** [00:37:46]
Sounds good.
OK, so that's it for this one.
Thank you everyone.
Happy holidays.

**Geohot** [00:37:54]
Happy holidays.
Bye.
