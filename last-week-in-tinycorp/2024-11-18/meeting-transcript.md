# 2024-11-18 Meeting

### Meeting Agenda

**Time:** 8 PM Hong Kong Time  
- Company update  
- 0.10 release  
- Big graph and LazyBuffer  
- Block, new style backward  
- Speed (simple ops vs. theoretical, mid-size kernel search, high-level math simplification)  
- AMD/QCOM driver issues  
- Active bounties (WebGPU, TensorCores, ONNX, Matcher speed, PTX renderer)

### Audio

[Recording](https://drive.google.com/file/d/1Rtqwh6nfymyqPkbnUjMOCspmSGWHy9VX/view?usp=sharing)

### Chapters

- **00:00:00 Introductions and TinyBox Updates**  TinyBox sales performance, pre-orders, and installation improvements.

- **00:01:56 Conda Installation Fixes**  Fixes for Conda compatibility on Mac.

- **00:03:15 Release Version Discussion**  Deciding between version 0.10 or 0.9.3.

- **00:03:40 Big Graph and LazyBuffer Updates**  Progress on Big Graph and lazy.py removal.

- **00:05:28 Global Cache Challenges**  Issues with global cache in scheduling.

- **00:10:22 LazyBuffer and UOp Integration**  Simplifying LazyBuffer with UOps.

- **00:18:19 Scheduler and Multi Buffer Handling**  Optimizing multi-buffer scheduling.

- **00:20:31 Backward Pass Redesign**  Plans for a new gradient computation approach.

- **00:25:13 Stable Diffusion Regression**  Investigating and fixing performance declines.

- **00:32:47 Driver Optimization**  Updates on AMD and QCOM drivers.

- **00:34:58 WebGPU Backend Progress**  WebGPU performance improvements and cleanup.

- **00:43:05 Data Type Handling in WebGPU**  Challenges with uint8/uint16 support.

- **00:50:07 TensorCore Refactor**  Updates on TensorCore swizzling logic.

- **00:58:22 ONNX Support Expansion**  Progress on ONNX integration and fixes.

- **01:00:32 Matcher Speed Optimization Bounties**  Bounties for faster matcher implementation.

- **01:02:37 PTX Renderer Cleanup**  Suggestions for reducing PTX renderer lines.

- **01:03:13 Release Preparation**  Final steps for version 0.10 release.

- **01:04:12 Meeting Wrap-Up**  Closing remarks and next steps.

### Transcript

**Chenyu** [00:00:00]
All right.
Let's start it.
Any company update?

**Geohot** [00:00:07]
Yeah.
Tinyboxes have still been selling well.
We got some press for the TinyBox Pro.
We got two more pre-orders in for TinyBox Pros.
So those are paid pre-orders, which is nice.
We actually have $2,000 for most people.
And they're non-cancelable.
So they're likely to actually convert unlike the first hundred pre-orders.
And yeah, I think a bunch of a bunch of good signals on Twitter too, where it's kind of like people know tinygrad is next, and it's kind of ours to lose.
People are talking about the PyTorch Conda thing.
Uh, PyTorch got removed from Conda and you know, people are just fed up with the complexity of installing any of this stuff.
Uh, so a few, like, this is why tinygrad's been a win.
Um, this is only accelerating the adoption of tinygrad.
So, you know, it really is ours to lose.

**Chenyu** [00:01:04]
Isn't one of the main point from Jeremy is that you can install without dependency and change different versions from conda.
Easily, that's why people use it.

**Geohot** [00:01:18]
Yeah.
So it's easy to install different versions of tinygrad, too.

**Chenyu** [00:01:22]
Yeah.
But isn't that part of a reason why Conda has the weirdest thing on Metal, presumably?

**Geohot** [00:01:30]
Well, it's fixed now.
It's fixed.
Now, this is not weird on Mac anymore.
It works great with Conda on Mac now.
We fixed that.

**Chenyu** [00:01:36]
Great.

**Geohot** [00:01:38]
Now, some guy pointed out on Twitter about the Conda on Mac thing.
It was actually our fault.
We were using a private API
once we didn't, it worked!

**Chenyu** [00:01:56]
Great.
OK, so we do a release this week? Soonish?

**Geohot** [00:02:05]
You want to call it 0.10?

**Chenyu** [00:02:09]
Oh, what else?
This is either 0.10 or 0.9.3.

**Geohot** [00:02:21]
Well, how much are we going to get rid of lazy.py?

**Chenyu** [00:02:29]
No.
That's the next point.
But how will that change your release number?

**Geohot** [00:02:36]
Oh, I don't know.
It doesn't really matter.
Whatever you want to call it.
If you're doing the release, whatever you want to call it.

**Chenyu** [00:02:42]
Oh, I'm doing a release.
OK.
I thought previously we say 0.10 because we remove the last dependency.

**Geohot** [00:02:54]
Oh, good point.
Yeah.
OK, 0.10 of this.
Do you want me to do it or do you want to do it?

**Chenyu** [00:03:00]
I don't know how to do it.
I never have done it.
Okay, you can do that.
You can write like a very simple three point release note or something.

**Geohot** [00:03:11]
Yeah, no, I'll wait up to some release notes.
I'll do the release tomorrow.

**Chenyu** [00:03:15]
Okay.
That sounds good.
I think we just caught.
I don't think we need to we don't have major blockers or just call whenever you like.

**Geohot** [00:03:28]
Cool.

**Chenyu** [00:03:32]
Okay.
Uh, I moved the big graph and LazyBuffer to the first point.
So, uh, Qazalin can you?

**Qazalin** [00:03:40]
Can you guys hear me well?

**Geohot** [00:03:42]
Yep.

**Qazalin** [00:03:44]
Cool.
Um, so last week I merged, uh, a diff that will basically make scheduler completely independent of lazy.py.
So, uh, we create the big graph and we do everything from UOp.
I also made the big graph smaller, ironically.
The big graph got smaller, got more readable and faster too.
That was a nice win.
So yeah, this week I am working on the lazy deletion.
This is the [complete milestone list](https://github.com/tinygrad/tinygrad/issues/7697).

**Geohot** [00:04:31]
Sorry, server muted.

**Qazalin** [00:04:34]
So I'm going through the milestone list of LazyBuffer one at a time.
It's a little challenging to merge everything in small points now that I'm at the point where I'm going to just make LazyBuffer equal UOp.
So I think I need to merge that like a big diff.
Then I want to, like, there is one thing I want to bring up in this meeting, which is that lazy cache right now is global.
If you create a LazyBuffer and an operation, it's globally across the entire runtime, not the dedupping of the schedule itself.
The dedupping of graph rewrite is a part of lazy cache, but it's not that important.
I'm not sure the performance will be, once we remove the global cache,
But that's one issue that we might face.

(network issue start)

**Geohot** [00:05:28]
The global cache is undesirable.
So I don't, what do you think anything to break if we remove global cache?
I actually think we basically don't want it.

**Qazalin** [00:05:39]
I think it's the face books.
Yeah, I agree.
Because of global cash.
So yeah.
I'm making progress.
I'm moving to your diff from the toonygrad and from the step that you have.

(network issue end)

**Geohot** [00:06:00]
Your signal's breaking up a bit.
Is that just for me or for everyone?

**Chenyu** [00:06:11]
So I have like 300 milliseconds of latency, so I don't know.

**Qazalin** [00:06:19]
If anything, I said is not clear, just let me know.
But yeah, that's what I am making progress on.
It's a little challenging to think about what the buffers are going to look like with this new structure.
But yeah, I think that's my only challenge right now.
At this point, it's all about memory management.
Once that is done, I think it will be ready for your new backwards style.

**Geohot** [00:06:47]
Cool.
I'm really looking forward to doing that.
It seems you're making great progress on deleting that stuff.
You should be able to just copy, paste all the stuff because I do have it working in toonygrad.
Toonygrad actually works to run things.
You should be able to just copy and paste everything out of PR.
Obviously, I didn't actually get the schedule working.

**Qazalin** [00:07:14]
Yeah, I tried really hard, but it's like there are subtleties in it that I haven't been able to debug.
So I spent two days.
I've been trying to get your stuff merged, but I might want to do like a just from scratch implementation myself and compared with yours just like for a couple of days.
See where that goes because like so far what I've been going on is like, it's been a little challenging to translate all this stuff.
But we'll see.

**Geohot** [00:07:50]
Yeah, you don't have to you don't have to stick with any of that stuff.
The only really important thing is that LazyBuffer equals UOp.

**Qazalin** [00:08:02]
And then I think multi, we need to do work on multi.

**Geohot** [00:08:09]
Why?

**Qazalin** [00:08:11]
Most just comes to UOp or list of UOp.

**Geohot** [00:08:19]
Yeah, it becomes list of UOp, but it should just work if you say you up equals LazyBuffer and it has all the same API, right?
The idea is that UOp should have all the same API as LazyBuffer.

**Qazalin** [00:08:30]
Yeah, sure.

**Geohot** [00:08:31]
Yeah, I think you should, if it works, you'll be able to leave multi alone, I think.

**Qazalin** [00:08:39]
Okay, I'll try.

**Chenyu** [00:08:52]
Delete all of multi or what part of multi?

**Geohot** [00:08:57]
Oh no, I don't think we delete any of Multi.
I think Multi stays completely as is.

**Chenyu** [00:09:01]
Yeah, I think it's under the hood.
It used to be a collection of LazyBuffer and some metadata along this collection.
Now it's a UOp.

**Geohot** [00:09:16]
Yeah, but it should be.
We should actually make a lazy.py that says LazyBuffer equals UOp.
And then we can work on refactoring that later.

**Chenyu** [00:09:24]
How do you?
So for now, you can create a tensor out of UOp.
And you can create a tensor out of a LazyBuffer.
UOp, I believe, is only for the variable case.
But after that, it needs some kind of checking what is a valid UOp you can create a tensor out of.

**Geohot** [00:09:50]
I mean, yeah, we could write a, we could write a checker if you want.
We could write a pattern match here if you want to check.
But I don't know.
I don't think it's that big a deal.
You could use the API wrong if you create bad UOps, but otherwise.
You shouldn't be importing UOps in user code anyway.

**Chenyu** [00:10:22]
I would probably want to check.
For now, we check out of, so in the tensor init function, we convert every types of different types of input into LazyBuffer or multi LazyBuffer and we check.
That's the case.
So we'll probably do the same thing for UOp.

**Geohot** [00:10:43]
Yeah.
All of this stuff just, the way that toonygrad just works, like all of this stuff just works.
Uh, yeah, no, it's great.
This is, uh, this was one of our big goals at the end of the year.
And it looks like we're totally on track to do it.

**Chenyu** [00:11:09]
Sounds good.
Okay.
Oh, I guess.
Oh, it's block.

**Geohot** [00:11:17]
Boy, block is block is infuriating.
And I, I've, I've put hours into it now, like,
It will eventually work.
It will eventually work.
What's difficult, ok.
The hardest thing to deal with is when you have graph nodes that have children, like a graph node that has two children.
Because if you have some rewrite rule for that graph node,
then if it's rewritten identically by both children, that's the only way that this will stay the same.
Like if both children reach the same, reach the same rewrite conclusion.
So I've been playing with, I have a bunch of tests that are playing with just dealing with this pattern.
Because I realized that like I've wasted so much time on block just like hacking around what needs to be a generic pattern, which is like dealing with.
Here's a simple, here's a simple like,
use case that like graph rewrite has to support, that's really annoying right now.
So you just want to do basically uop.substitute.
Okay, so uop.substitute is a dictionary, maps one set of uops to another set of uops.
If you do this and any of the uops that you're replacing exist in parents, like if one of the uops is like a parent, then the whole thing is rewritten before your child uop is ever even seen.
Even if it's the same UOp, right?
But it's like not the same UOp because it has parents.
So I don't know.
I've been like working through what the cases are.
And then that stuff will make block easy.
But yeah, I've been reading a bunch of different implementations of rewrite engines as well.
Seeing how LLVM does it.
Is there any major difference that you found?
Yeah, so LLVM or MLIR has a whole bunch of like, they specify in the rewrite rules that they let you access children, they let you access parents is extremely flexible, which has its limitations.
But I think I think I think I have the main thing that I want to do, but it's going to involve changes to the actual graph rewrite function.
before it doesn't touch the matcher, so any matcher speedups will be fine.
You just kind of need to like, you need to tag, you kind of need to maintain the children as well in the graph rewrite.
as you do the rewrite, which is fine.
And then you're like, oh, I've seen this node before.
This node has two children.
I've already done a rewrite for this node.
I'm going to do the same.
I'm going to do the same rewrite.

**Chenyu** [00:14:32]
Yeah, but isn't this cached?

**Geohot** [00:14:37]
No, no, because if you are, if it's the same,
well, if it's the same node, it's cached.
But if there's, like, I'll push my tests with the patterns.

**Chenyu** [00:15:02]
Oh, OK.
That sounds good.

**Geohot** [00:15:04]
Yeah, yeah, yeah.
I've been hung up on basically this.
And I went off on a big tangent of reading how different rewrite engines work.
because I want to solve this in a generic way and not just hack around it.
And I think the scheduler has all these same problems too.
Qazalin, is there anything in the scheduler that's not where the number of passes depends on the number of nodes?

**Qazalin** [00:16:47]
I guess, like, one thing that could fall into that is the grouping stuff is you do need to look up a children.

**Geohot** [00:17:07]
Yeah.
Okay.
You just avoid it.
How do you avoid it?

**Qazalin** [00:16:11]
I avoided rewriting that into UPats.
It's just pure Python at this point.
And it's just recursing in generic Python.

**Geohot** [00:16:19]
Got it.
Got it.
I mean, maybe the scheduler is further along.
And I should get these patterns.
Maybe I can rewrite that one part of the scheduler and get these patterns to work correctly before I try to write block.
Every time I try to write it, it's just like, again, it's slightly wrong.
Yeah.
I don't know.
I don't know if the scheduler is a better expression of what the problem is, but yeah, I feel like the same problem exists on the schedule too.

**Qazalin** [00:16:45]
It definitely does.
And I think it's going to be even harder because you have assign.
They say, um, yeah, you're dealing with assign and it's like, okay, sometimes if you group in assign and then you group the usage of the pre-assign, it might create a cycle.
But then one child, for example, isn't feasible.
Like it's exactly the same problem.
Two children don't come to the same conclusion.
If one is assigned to the other.
Like I have four lines in the schedule.
Thats dealing with this is completely like every time I look at it, it's like, yeah, I couldn't write it any better.
It's just.

**Geohot** [00:17:32]
Yeah, okay, we'll leave these for now.
But yeah, I mean, that's kind of been the block or unblock until this stuff is like understood and not just hacked around.
I did manage to get block working.
But the problem is it's not a fixed number of passes.
There's a there's a while loop that keeps checking if it ever does a child rewrite and then it has to retrigger the rewrite.
Like if it ever if it ever gets to like a point where it where it sees a fork and then I created like an op call block fork.
It's just like it's not it's not good.
It's just hacks.
I'll be a better way to express that.

**Chenyu** [00:18:19]
OK.
And I think the new style thing will start after the lazy is done.

**Geohot** [00:18:36]
Yep.
As soon as we have a graph of UOps to iterate over.
Great.
I'll say one thing about it.
For people listening,
What new style backward is going to be is we're no longer going to have a requires grad on the tensors.
We're going to have loss.gradient, and then you pass in a list of tensors.
And that will compute the gradient of those tensors with respect to the loss.
I haven't seen exactly this API in any other library.
JAX and MLX have value and grad, but you don't need this in TinyGrad because it's lazy.
I mean, we could just add it as a helper.
But I think that like loss.gradient is a cleaner way to express this and it'll work really well with our optimizer abstraction.

**Chenyu** [00:18:38]
How do we know what to store?
I guess that's a scheduler problem.
Like how to store for your backwards.
Which way is fast.

**Geohot** [00:19:49]
So, yeah, that's a scheduler problem, right?
Like the forward pass will be jointly scheduled with the backward pass.
If the forward pass is not jointly scheduled with the backward pass, then it's going to be slow.

**Chenyu** [00:20:15]
Yeah, but even that, right, if you have, say,
uh say x square very early in your graph that you have this derivative that's 2x that's very late i don't know we will see 

**Geohot** [00:20:31]
yeah we'll have to just look at the patterns i think it'll be better than what it is right now

**Chenyu** [00:20:39]
Yeah, I think for now it's less flexible, because for now we have the same thing pretty much for, we have this locally store your thing, and who knows if it ends up saving both your input and output for your forward or something like that.

**Geohot** [00:20:57]
Oh, yeah, I know it'll just be the ones that end up getting used.
Right, so right now nothing is saved on the floor, because nothing is computed.
Yeah, I can see the way the whole graph comes together, and it'll know only to keep around the buffers.
I mean, that's a really late schedule, I think, anyway.
It'll be broken up into kernels, and then decided which things to end buffers.

**Chenyu** [00:21:27]
It's not just that.
It's also the compute.
Maybe a lot of backward compute is the same as a forward compute.
And for now, we know to save.

**Geohot** [00:21:42]
Yeah.
So in new style backwards, you'll be able to access, like when you're computing the backwards for say, like, like a ReLU node, you'll be able to access both the input and the output of that ReLU.
when you're computing, when you're writing the backwards.
That node will give you, that node will give you access to everything.
That node will give you access to both like the gradient flowing up
the output that was previously computed of the UOp, and then any inputs to the UOp.
I mean, it gives you the whole UOp, right?
So you can either just, yeah, right?
Like you can either use the UOp, which will be the output, and it'll be duplicated, it'll be dedupped with the one above it.
Won't even be dedupped, it's the same UOp.
Or you can use.src, so it should be the inputs to that.

**Chenyu** [00:22:48]
Okay, let's move on to the next point.
I was writing this meeting agenda and I think this is the same thing we had last year around the same time, I remember.
I think late last year we also talked about three levels of speed and I think.
So I was, so I added some, I added
matmul and conv in the benchmark test versus theoretical.
I started this rabbit hole of a wide stable diffusion one year ago, much faster than now.
for majority of the network.
So we had the Res block or ResNet block that does the conv.
I think our conv with or without BEAM, it's a lot faster than before.
And I thought it's isolated into a transformer block.
I thought that was that, but that we can just increase the BEAM number.
turns out that's not all of the problem.
And also we have a lot more kernels now.
So I need to isolate it a bit better.
My problem for making the default hand optimization better is it needs to be based on a good BEAM search and the fact that our stable diffusion got a lot slower than before doesn't.
I think that's a much bigger problem.
So I'll probably continue with that this week, find out why it's slower.
And I don't really know why we have like 30% more kernels.
It might just be like some like recompute decisions, like, I know we have like some small patterns, we don't fuse anymore, like loads.
expand before the reduce of things like that.
But I want to fix stable diffusion this week.

**Geohot** [00:25:13]
Yeah, one of the that was shocking how much worse it's gotten.
We need better testing methodologies to make sure these things don't regress.

**Chenyu** [00:25:24]
Yeah, so that's what I've listed here.
I think we have so
or the VS, something like VS torch that we have the very like the minimalist thing like matmul or some of the element wise ops that we should.
I think this is more tied to the block thing or like how you reorder things like small things like these or even like the instructions that you use things like that.
Those we can individually test and we should have like
a good understanding versus what's possible and like why are we not hitting that then we have like mid-sized thing like maybe a ResNet block or like one single transformer block I think those we can have we BEAM test those and we say
uh like what's the also non-limit and this is like slightly tricky and like flaky right because if you it's like the current test I have I just saw it become like flaky this morning and I was like okay now is that does that mean we have a regression or does that because I previously leave like five to ten percent of the buffer so that it's not flaky so yeah anyway I'll think about that some more but
I think the point is here.

**Geohot** [00:26:53]
We can add those numbers to stats.tinygrad.org.

**Chenyu** [00:26:59]
Yeah, that we need a better logging API for that.
Yeah, OK.
And I think the high level math simplification, we just do unit tests like what we are doing now.
So because we can say, OK, something should be rendered or understood or computed in a certain way, and we can test that.

**Geohot** [00:27:24]
Yeah.
Yeah, I think the mid-size thing is really smart.
I think that that would probably, things like that would probably catch the stable diffusion regression, just like search one block or that.

**Chenyu** [00:27:33]
No, so I think stable diffusion is just special.
I think the whole time you go, it's definitely less mature back then.
So like, okay, you make a lazy change and then changes everything.
It's like, even if you know that the case is not clear, if you want to stop like up and figure that out at that point.
But I think now everything is more mature.
So, we keep a pretty nice speed on ResNet.
I think this past six months, it's slightly slower, but we kind of, at least I kind of understand why it's slower.
I think stable diffusion is interesting because we have a number one year ago that was pretty optimized.
For now, given the better conv and a lot of other improvements, I expect to like beat that number.
So I think this is the last examples that we know we kind of have fixed.
And after this is all new examples, like llm.c or BERT that we will optimize.

**Geohot** [00:28:55]
That's good.

**Chenyu** [00:29:01]
Uh, well, I really also find another, you just see my example of like padding, like change the, uh, do the pad with a value and those conditions can be merged together.

**Geohot** [00:29:16]
So, um, I mean, the normal pad and when padding is not zero.

**Chenyu** [00:29:25]
Uh, yeah, yes.
So that, that is just a PoC for that as possible, but it actually points out that you can do the condition merging or you can like push up or down the condition to simplify stuff further.
I think that's pretty cool.

**Geohot** [00:29:44]
Uh, yeah, I actually have something kind of like this in my hack that I wrote for, uh, for the THREEFRY thing to remove the uint64.
But yeah, no, you can totally push the condition.
And I didn't come up with a generic rule.
But yeah, I think maybe generically you want to push the condition to as late as possible or as early as possible.

**Chenyu** [00:30:09]
No, no, no.
I don't think we want to push.
It's just when you rewrite, if you go top down this UOp tree, you actually can carry all the conditions from your parent branch.
So if you know you are in, say, a true branch of a condition, then you can.
So we have this simplified given valid, right?
And you can also add your parent's last branch into your condition, because you know you are in this branch.
Anyway, so it's like a double condition is the same thing kind of case.
Anyway, I just find that pretty cool.
I think if we rewrite that and slightly not related, but also interested in how do we do argmax in one loop?

**Geohot** [00:31:14]
This isn't even like this is like
I'm reading this.
I'm reading this more carefully now.
It's like, you're getting a one and a zero to be the thing.
You can make this much simpler.

**Chenyu** [00:31:26]
Oh, I should.
If you read my notes, they're so like.

**Geohot** [00:31:32]
Yeah, what it should be.
Yeah.
Yeah.
Yeah.

**Chenyu** [00:31:37]
And the reason that is not because we have a double condition is actually the same thing.
Those two should merge together.

**Geohot** [00:31:57]
Why is it master that it's doing like ALU zero question mark one zero question mark zero four.
Why is that question mark one zero there?

**Chenyu** [00:32:05]
It's gone.
I remove it.

**Geohot** [00:32:07]
Okay.
Cool.

**Chenyu** [00:32:10]
Yeah.
So light one zero is the simple one to remove.
So I remove that first.

**Geohot** [00:32:14]
Yeah.
Yeah.
Yeah.
Just a rule that like if, if, if, you know, if condition then true, else false, that should not be a thing.
Yeah.

**Chenyu** [00:32:22]
Oh, yeah, that is in master already.
Yeah, no, I think I think there are a lot more interesting mathy stuff that we can do.
OK.
Move on to the driver.
Yeah, Nimlgen.

**Nimlgen** [00:32:47]
So, been working on optimizing and fixing speed in AM driver.
So fixed some TLB thrashing we had.
And yeah, also we now have fixed clocks as set in like high performance profile with ROCM SMI.
So we're still slower in some kernels.
I'm just investigating this.
Yeah, also,
I just removed mes_kiq completely.
We had mes_kiq previous week.
Now we just set up our queue directly without mes_kiq.

**Geohot** [00:33:30]
I see it's all commented out.

**Nimlgen** [00:33:35]
Yeah.
Yeah.
I mean, I would delete it.
It's just not needed.
We even don't need load this firmware, like mes firmware at all.
Yeah.
So yeah, I've seen I've seen your comments.
Yeah, I just need a lot of to clean up.
I'm just focusing on speed right now.
So yeah.

**Geohot** [00:34:01]
Well, you know, I think it's coming together great.

**Nimlgen** [00:34:07]
Yeah.
So I also documented what what I've learned about TLB be in cache and stuff.
So that was a part of the slowness.
We'll document this and
for QCOM.
Yeah, the problem of slow copies is actually because of the scheduler.
We have like five realises and the schedule of each of them takes about one millisecond.
So just five millisecond total.
So copies, like they're all copies are just pretty fast there.
So yeah, we
Yeah, it's mostly scheduler.
I've created an issue.
Maybe Qazalin, you want to take a look into this, if we can do anything with this.

**Geohot** [00:34:58]
Why are they not being jointly scheduled?
Why are they being scheduled one-by-one?
Yeah, no, if it's the scheduler, it's totally not on you.

**Qazalin** [00:35:15]
I was thinking, yeah, but this should be a copy scheduled at once.

**Geohot** [00:35:24]
We should have one call to schedule for the entire thing.
I don't know why those copy are being realized.
I don't know.
Probably got my wrong.
I can look into that one too.
Uh, I'll add that.
I'll add that's my list of the week.

**Nimlgen** [00:35:58]
Yeah.
So that's it for me.

**Geohot** [00:35:59]
Cool, uh, you know, I'm, uh, my comment, my main comment about the driver was, uh,
I want to be able to like, almost, I want to have like 95% code reuse between AM and AMD.
In fact, I almost think that our driver couldn't be Ops_AM.
It should be Ops_AMD with a flag that says going to the kernel.

**Nimlgen** [00:36:24]
Okay.
Yeah.
Yeah.
I mean, yeah, the user space should be totally the same.
Yeah.

**Geohot** [00:36:34]
The runtime should be should be 95% identical just instead of ioctl, your functions.
And what are we at now?
900 lines?

**Nimlgen** [00:36:51]
So yeah, I'm targeting I think, I mean 600 maybe.
I think after the full cleanup.

**Geohot** [00:36:57]
We've got to figure out what we're deleting.
And the lazy should be a loss of lines, multi will be a loss of lines.

**Chenyu** [00:37:32]
Not 600.

**Geohot** [00:36:57]
Where are all the lines?
Where are they all going?

**Chenyu** [00:37:42]
There are 171 in cloud.

**Geohot** [00:37:32]
Those are good lines!

**Chenyu** [00:37:54]
I think just I'm reading like in these 500 lines AMD currently is 365 QCOM is another 300 or hcq is another 300 that's a lot of lines in these runtimes.

**Geohot** [00:38:15]
I'm wondering if we can save save lines in these runtimes I think I think that might be a big a big place if we can tidy up the code

**Chenyu** [00:38:25]
How compact is all the expand and reduce thing you have for UOp?

**Geohot** [00:38:36]
Oh, you're talking about you are graph?
Yes.
UOp graph's pretty compact.
Yeah, I don't think I think that our best bet to save lines and Nimlgen this is going to be on you is in ops_NV ops_AMD and ops_QCOM.
I just think that we can like like almost make some syntactic wrappers that'll make these things nicer.

**Nimlgen** [00:39:12]
Maybe I'll think of this.

**Geohot** [00:39:17]
Yeah, like, okay, for example, like just just just in AMD, I see, uh, like you have this like, uh, self.qmd set adder, const buffer adder, upper size shifted.
Like I almost think that like there's some.
Thing to think about for a bit, right?
Like a really good helper.
And this could also be used in the, in the AMD driver as well.

**Nimlgen** [00:39:47]
Yeah.

**Geohot** [00:39:50]
Yeah, just for places where like registers are set.
Always a good time to potentially improve on these tests too.

**Chenyu** [00:40:11]
Okay, let's move on.
So for active bounties, WebGPU

**Geohot** [00:40:28]
Oh, yeah, like the QCOM, the QCOM one.
It's like, like there's these like Q reg things, like all the lines in QCOM from like 116 down to, uh, down to 123.
Like why else would you be constructing the Q reg if you weren't going to set it?
I don't know.
Maybe not.
I hope we can save lines.

**Chenyu** [00:41:06]
OK, let's move on.
Do you want to server unmute?
and talk now if you want.

**Wpmed** [00:41:32]
Yeah, thanks.
I made some refactors on the PR, like I had WebGPU specific stuff in C-style.
This pre-kernel stuff has been deleted, so now C-style is, so there's no modifications there.
I moved it to,
WGSL and I also, so there was a lot of test skips like because of the sign stuff like all unary test was skipped and I made that skip much narrower and there was also a couple of lines where
only because of different casting stuff and the const rendering was sort of duplicated and I made this render cast which made it possible to delete those four lines from the GPU.
I also made a new
I tested the new stable diffusion stuff, tested it with the latest, with the new WebGPU and compared it with the export from a year ago.
I found it a bit faster.
Yeah, I'm planning to deploy that.
I just tested it locally currently.
So I'm planning to deploy a new stable diffusion stuff today.
Yeah.
Clean up the PR a bit more.
It's 143 lines currently.
88 lines above the limit.

**Geohot** [00:43:05]
Cool.
Yeah, no, it's looking much better.
I think we're definitely getting close on that.
We can find you some lines.

**Chenyu** [00:43:26]
Delete PTX.

**Geohot** [00:43:29]
Well, we just got a beautiful refactor of PTX merged.
And there's clearly 20 lines that can go from that refactor.
He didn't delete them because he wanted to make process preplay match.
So you say there's still a bit more you want to do to clean up the PR for WebGPU?

**Wpmed** [00:43:59]
Yeah, I want to do a bit more like, so this PR can be smaller if, so how I added support for char, so like uint8, uint16, int8, int16 is sort of like a workaround because WebGPU itself doesn't have these data types.
And like if for the first version of the PR, like I don't, I just don't support those, then that could be a,
I think maybe 10 lines or something like that.
But if I want to keep that, I have to clean that up.

**Geohot** [00:44:38]
I don't understand why you're doing this scale size thing.

**Wpmed** [00:44:42]
so I think what you said is just to have them like tightly packed right so you have one yeah exactly and and you have like you can pack four bytes into a word but I also plan to do that but that also requires some rewrite rules for the indexing modifications you know because then when you index two bytes
You have to rewrite that to points to the first, let's say you want to index byte one and two in the first word done.
you have to sort of rewrite the indexing because you want to read from that word and shift out the bytes.
I think for that, you also have to do that in an automate way.
To avoid that, since we only had this scale size stuff for bool, I thought that in the same way, I can just make the
make it four byte aligned always, and that way you don't have to modify indexing and stuff.
And yeah, this is great.

**Geohot** [00:45:56]
I don't think modifying indexing is very hard.
I see the thing that is potentially annoying where if you want to only store one pack, what do you actually do?
You have to load the others.

**Wpmed** [00:46:09]
Yeah, exactly.

**Geohot** [00:46:12]
But that should still be fine.
I would do that.

**Wpmed** [00:46:15]
I proposed it a while ago.
So I proposed this, that we do this, but I think there was discussion that, okay, maybe we don't want to do that first, just keep the PR simple.
But yeah, then I still supported it, but with this other approach, but yeah, I can make it work with a type of fact and indexing modified way.
So yeah, if you want, I can make that change.

**Geohot** [00:46:45]
Yeah, the beauty of tightly packing it is then we don't have the modified buffer.

**Wpmed** [00:46:51]
Exactly.
Yeah.
Yeah, that would be no, there would be no modification in core tinegrad or other than the runtime change.
Yeah.
Okay, I can do that.

**Geohot** [00:47:07]
Excellent, yeah.
No, with no modification in Core TinyGrad, WebGPU will never, ever go away.
We did it.
We've succeeded.
Remember how many hacks were in the first one, where we had stuff all over the place?

**Wpmed** [00:47:18]
Yeah, a lot of hacks.

**Geohot** [00:47:20]
If this last one goes away, it's just completely just a runtime.
Again, even if it costs more lines, we will find you lines.
OK, yeah, sounds good.
Cool.
Yeah, it's great to see stable diffusion back.

**Wpmed** [00:47:48]
Yeah.
Maybe once it's completely fine, I can also update the UI and stuff so that if we share it again, that way we have a new stable diffusion graph GPU demo.
Now it's a bit faster.
It looks better, stuff like that.

**Chenyu** [00:48:04]
Mindful that the UI you put in the demo will accidentally be popular and show up in other big places.
Like a tiny chat UI.
So whatever you like, but just it might accidentally get popular.
And you might not feel good about it seeing another place.

**Geohot** [00:48:33]
Yeah, we have that nice EXO, EXO's tiny chat.
They're red in the green.
Showed up an EXO's tiny chat.

**Chenyu** [00:48:44]
It's nice to see WebGPU back.

**Geohot** [00:48:46]
Yeah, I think that the stable diffusion one is cool.
The YOLO one is cool to run on your phone.
We can even look and bring WebGL back.
Does iPhone support WebGPU yet?

**Wpmed** [00:49:00]
I think in new Safari, this is behind the toggle in the new Safari beta.
So it's closed.
So like WebGL will be irrelevant to it.
So last year, when I did WebGPU backend, it was irrelevant because it seemed like all mobile WebGPU is far away, but it's actually here.
So I think all the WebGL stuff, even in extra, can be gone.
And I think in easy type support, we still have WebGL.
We can just delete that.
And also from the test, there are some references to WebGL.
It will not be relevant, because WebGL doesn't have a compute API.
So I told it with this frame buffer rendering workaround, this hack.
But it was the graphics API.

**Geohot** [00:49:50]
Let's just get WebGPU in.
And then let's hope Apple actually got their act together.
OK.
Okay.
Moving on to TensorCores.

**Ignaciosica** [00:50:07]
Hello.
I think the big thing, the big refactor of the TensorCores, Swizzle is done.
But the problem now is that actually the Swizzle won't work for the patterns.
So the way you see it is that they are two possible pathways.
One is that there's something wrong in the lowering to index UOp, but I don't believe that.
So the other thing is that the patterns itself for fixing the things turns of course, shapes are wrong because they are not think to actually swizzle, but to replace the ShapeTracker.
So I'm now trying to fix the patterns alone to fix the output.
And that's it.

**Geohot** [00:50:59]
Wait, so I don't exactly follow.
The swizzle patterns are wrong?

**Qazalin** [00:51:17]
I can explain.
So the swizzling that you're doing isn't actually swizzle, it's replace.
It's doing a replacement of the ShapeTracker, which at the end of the day, like I think there might be a way or like every single ShapeTracker transformation is in addition is a merge view.
That merge view is happening way too early right now in the kernel or in the fixed SD, whatever function you have.
And that should happen later in the graph rewrite itself.
But when you're doing a load and then you're viewing the load, what happens is that the ShapeTracker should be added.
Right now, what you're doing is you're replacing that ShapeTracker, which is like, I want the swizzling to be a generic thing that's shared across both the schedule and the kernel.
Right now, you have something that you call swizzle, but it's actually replaced.

**Ignaciosica** [00:52:11]
No, no.
I discarded that, and I was talking using the same swizzle that in schedule.
That's why the thing I wrote.
I'm trying to fix that without replacing the ShapeTracker.

**Geohot** [00:52:28]
Yeah, I get it.
There was an existing bug, basically.
What I was doing wasn't swizzle.
You're right.
I was replacing it.
I know what I was replacing, too.
Do we think it's possible to do it with swizzle?

**Ignaciosica** [00:52:45]
I'm trying to fix the TensorCores for metal in order to prove that a swizzling TensorCores might fix that.
And it's not necessarily going to be a replacement.

**Geohot** [00:53:04]
Got it.
What you have now, I see all the tests passing.
What's wrong with just merging it?

**Ignaciosica** [00:53:12]
That's what Qazalin said, that it's replacing and not actually swissling.

**Qazalin** [00:53:21]
Oh, I mean.. Recall, just call it replace.

**Geohot** [00:53:27]
Yeah, well maybe we should change the name of it to replace and then merge it because it looks better than what's in there.
And it's a reduction of 14 lines.

**Qazalin** [00:53:39]
Yeah, the line reduction is good.
I was just thinking if there was something wrong with it, that's like, if we're okay with the replace, which was like a hack.

**Geohot** [00:53:49]
Well, where do you see the replace?

**Qazalin** [00:53:54]
The replace is in the UPat.
Like, if you look at the UPat on line 686, it says load of view and then it replaces v.r.
It's not like v.r.
I think it should be V2 plus V1, right?
That's Swizzle.

**Geohot** [00:54:15]
Yeah, yeah, I get it.

**Qazalin** [00:54:21]
That addition is happening somewhere in ShapeTracker right now.
You just got to pull it out of the kernel or whatever it is that's being done.

**Geohot** [00:54:31]
The old one used to be Replace.
But it can't replace it exactly because it still needs to keep the global dimensions.

**Qazalin** [00:54:47]
It's replacing it exactly.
It's basically referencing that ShapeTracker in the fixed ST or whatever the function was.
If you were to get the function, it's like it has, I think, two simplifiers in it and it's like doing something weird.

**Geohot** [00:55:06]
Yeah.

**Qazalin** [00:55:11]
He should all do all that addition.

**Geohot** [00:55:16]
Yeah.
Okay.
So what's the consensus?
Should we merge it or not?

**Chenyu** [00:55:23]
I think it's fine to merge it first, then do the more thing on it.
I mean, the PR looks pretty complete.
And it's not changing.
It was doing replace.
It's still doing replace.
If there's a better way to not do the replace and do the swizzle properly, then great.
But this as a clean up, I think, can be merged.
That's why I say it.

**Geohot** [00:56:00]
Cool, then let's merge it.

**Chenyu** [00:56:28]
If we want to change behavior from like a replace to not replace, then it probably could be like a step.

**Geohot** [00:56:36]
Oh, I see.
No, I actually wait, wait, wait.
I agree that this isn't right.
I see what this is doing now.
Okay, so on line 641, this is like the problem is it's referencing sources I dot ST.
Like the problem is the reason that the add isn't working is because it's like it's referencing the ShapeTracker.
This is the same function.
I don't even understand, like, somehow it deleted 14 lines.
This isn't what the bounty is.

**Ignaciosica** [00:57:32]
I agree.
The bounty isn't actually swizzling.

**Geohot** [00:57:38]
OK, Ignacio, I'll leave it up to you.
Do you want it merged or not?

**Ignaciosica** [00:57:44]
No, I agree with Qazalin that it's
It's not the right thing to do, but I might totally agree with you, Chenyu, that it might also be better to change behavior in another PR.
That's good.

**Geohot** [00:58:05]
If the test pass, let's merge it.
And then it's a good groundwork to approach the bounty.

**Chenyu** [00:58:22]
uh we're already at one hour mark so ONNX uh how do you give 

**Geohot** [00:58:33]
oh yeah yeah yeah uh i don't know if he's ever spoken before but now your speaker congratulations
Oh, recording.

**Chenyu** [00:58:50]
Oh, recording.

**Geohot** [00:58:50]
Can't talk.

**Chenyu** [00:58:52]
OK.
I think it's making progress.
I see many things being moved from ONNX to tinygrad proper.
And back to my reading tensor.py and re-write the things that I don't like.
So I think
Most of it, if it's just style, then I can merge those.
It's fine.
Some of it is more like a mis-case or there's a better way to do stuff.
I think it's making progress.
Yeah, I think we would have like some add.
And I saw there's like a new scatter and when like the bugs for the item and stuff are progress, I expect that's how this bounty will go, like maybe 10 PRs for 10 different functions, then that's pretty much it.
OK, let's move on.

**Chenyu** [01:00:19]
I think the matcher of speed, what I saw is something not known, correctness unknown, speed unknown.
That's my understanding.

**Geohot** [01:00:32]
Yeah.
I'll give a TJbecker a chance to put a PR up.
And if he doesn't, we'll unlock those bounties.
And then there's $2,500 in bounties available to anybody.
to write a matcher using a DFA.
Or I don't really care if it's DFA as long as it's fast.

**Chenyu** [01:00:59]
Yeah, the problem for DFA is variable length and it's very annoying.

**Geohot** [01:01:03]
Yeah, I just care that it's fast.
I mean, anyone who wants to claim those, there's three speed boundaries available.
I think I'll let TJbecker.

**Chenyu** [01:01:17]
I think we should probably should probably should do the speed on one of the TinyBox or something like that that's more easy to benchmark 

**Geohot** [01:01:26]
Uh yeah it just doesn't really matter what it is 

**Chenyu** [01:01:31]
How do people how do people know when they're up done kind of 

**Geohot** [01:01:37]
Yeah just compare to master 

**Chenyu** [01:01:42]
Yeah but on which machine

**Geohot** [01:01:47]
No, it's just this, I don't think it matters.
I think as long as you use the same machine for the master versus your branch, just look at the multiplier.
I've seen, I've seen like, I've tested across a bunch of different machines and it seems like, like pretty consistent.
If you get a 20% speed up on one machine, you get a 20% speed up on another machine.

**Chenyu** [01:02:16]
Yeah.
PTX renderer so I think the consensus is the bounty is to save the like obviously can be removed lines the ones that was kept because the process replaced things like that 

**Geohot** [01:02:37]
yeah yeah i think i think there's definitely there's definitely 20 obvious lines to remove there's 13 lines doing define_acc which should just be the same thing as const
uh, just keep process replay stuff the same?
And then there's like a bunch of stuff which names the variables things that it doesn't have to do.
So I think, uh, I think he knows what he has to do.
Okay.
Sounds good.

**Chenyu** [01:03:06]
Uh, that's it.
So, uh, when do you want to do release?
Like today, tomorrow?

**Geohot** [01:03:13]
uh yeah i'm tired i will do it tomorrow morning uh so in like 12 hours i'll do like i'll do it write up make it try to do a decent release

**Chenyu** [01:03:35]
OK, I would probably test, again, all the local tests locally, like Mac and TinyBox to making sure it looks good.

**Geohot** [01:03:49]
Yeah, I'd say release in 15 hours.

**Chenyu** [01:03:53]
OK, great.
Yeah, cleanups or bugfix always welcome.
Don't squeeze very big unstable feature before release.
That's all.

**Geohot** [01:04:09]
Yes, sounds good.

**Chenyu** [01:04:12]
Well, thanks, everyone.
See you next week.

**Geohot** [01:04:16]
Thanks.
Bye.
