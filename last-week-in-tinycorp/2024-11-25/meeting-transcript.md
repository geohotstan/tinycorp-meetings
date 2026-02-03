# 2024-11-25 Meeting

### Meeting Agenda

**Time:** 8 PM Hong Kong Time
- Company update
- Big graph and delete lazy.py
- Block
- Stable Diffusion speed, pad fusion, block const
- AM driver, QCOM speed
- bounties: WebGPU, tensor cores, simpler PTX, onnx, tar_extract

### Audio

[Recording](https://drive.google.com/file/d/14WEs5oEBdVluENSZBsasMesFwN7KF80m/view?usp=sharing)

### Chapters

- **00:00:00 Introductions and TinyBox Sales Update** Updates on TinyBox sales, inventory, and future hardware plans.

- **00:01:51 Pro V1 Shipping Updates** Progress on Pro V1 production and December pre-order delivery.

- **00:02:53 Big Graph and Lazy Deletion** Work on replacing LazyBuffer and addressing simplifications.

- **00:07:28 Scheduler and Kernel Testing** Optimizing scheduler tests and handling kernel regression.

- **00:10:12 Subbuffer Handling** Adjusting subbuffer logic and rewrite rules in the scheduler.

- **00:13:42 Constants and Devices** Debating device assignments for const tensors and potential fixes.

- **00:16:31 Block Linearization** Updates on block linearization with simpler rewrite rules.

- **00:21:33 Kernel Optimization** Enforcing optimization order for pad, unroll, and upcast actions.

- **00:27:56 Stable Diffusion Speed** Fixes for dtype handling and Winograd optimization.

- **00:33:05 Expand and Fusion** Improving fusion strategies for const and expanded tensors.

- **00:35:38 VFIO and Copy Speed** Using VFIO to speed up memory copies.

- **00:39:00 Qualcomm and Lazy Rewrite** Scheduler and graph rewrite improvements tied to Lazy deletion.

- **00:42:32 OpenPilot Optimizations** Validhack mod updates for OpenPilot kernel speed-ups.

- **00:43:12 WebGPU Progress** WebGPU support, F16 decompression, and performance on M3 Max.

- **00:49:56 WebGPU Mobile Testing** Exploring WebGPU compatibility on mobile.

- **00:50:50 TensorCore Swizzle Rewrite** Updates on TensorCore swizzle and AMD reshape handling.

- **00:54:15 Turing and TF32 TensorCore** Plans for TF32 and Turing TensorCore support and H100 work.

- **00:58:31 PTX Cleanup** Simplifying PTX dtype handling and reducing special cases.

- **01:02:53 ONNX Discussion** Discussion about ONNX and fixing casting behavior.

### Transcript

**Chenyu** [00:00:00]
We can start.
Any company update?
Saw you post our revenue line on Twitter?

**Geohot** [00:00:11]
Yeah.
Pretty good for a first year of revenue.

**Chenyu** [00:00:20]
For selling hardware?

**Geohot** [00:00:24]
Yeah.
Yeah.
No, I don't know.
I'm hoping for rapid growth next year.
I think that if the 5090 is good, we have a chance to sell a lot of 5090 TinyBox pros.
Or if the 5090 is bad, we have a chance to sell a lot of 4090 TinyBox pros.

**Chenyu** [00:00:50]
I heard it's hard to buy 4090 these days, or more expensive.

**Geohot** [00:00:55]
I mean, it is.
And we're sitting on a lot of them, too.
I don't know.
Should we raise the price for tiny boxes?

**Chenyu** [00:01:02]
Should we lower the price for red?
I also saw that 7900 XTX is on sale.

**Geohot** [00:01:08]
How much?

**Chenyu** [00:01:11]
It's like 800 each or something.

**Geohot** [00:01:16]
Yeah.
Actually, that's less than what we got them for.

**Chenyu** [00:01:22]
Yeah, that's the inventory risk.
You gain some, you lose some.

**Geohot** [00:01:27]
You gain some, you lose some.
All right.
The greens went up and reds went down.

**Chenyu** [00:01:34]
OK, no, that's great.
No sounds good.
Yeah, I think this here is pretty nice.
How's, are we still delivering Pro V1 in December?

**Geohot** [00:01:51]
Yeah, Pro V1s are being built.
Let's see, maybe I have a picture I can share with the class.
Yeah, we're just going through a few minor little things.
Some of the CPU heatsinks are a little out of spec.
They don't fit in the hole right.
Maybe I'll share this image.
So yeah, they're going together and we'll have all the pre-orders in December.

**Chenyu** [00:02:40]
Great.
OK.
So I keep the same order from last week.
So we can start with Big Graph and Lazy.

**Qazalin** [00:02:53]
All right.
So for Lazy Deletion, I have to diff up
I'm going to start with the requirement being that LazyBuffer is equal to UOP and everything else exactly stays the same.
The challenges with that is that Lazy has a bunch of instance simplification rules with the const folding stuff and also with the view stuff.
So I'm wondering if we should move those simplifications to UOP while making everything like instance versus actually pattern measures in the scheduler.

**Geohot** [00:03:30]
We definitely don't want UOP to be instant.
If you're trying to make them the same, what I would even do maybe is just delete them initially.
Like you can delete them from the current lazy.

**Qazalin** [00:03:42]
Oh, it will break.
It will totally break everything.

**Chenyu** [00:03:46]
Break as in how?

**Qazalin** [00:03:50]
I had one PR for removing two lines from view and OpenPilot just created three times the kernels.
So I have stuff to do in the scheduler, I think, for that to work.
So that's going to be really hard.
But yeah, I think if you want to do that, though, that's what I was focused on this week then, just removing those from lazy and moving them to pattern matchers.
That's what you're saying, right?

**Geohot** [00:04:19]
Yeah, we definitely don't. Go ahead.

**Chenyu** [00:04:22]
I think the point was it's probably fine for a few days of minor regression.
I don't know anything about the OpenPilot kernel count thing.
But say, if you worry about counts folding in lazy, I think those you can just delete first, edit back.
Realistically, load const faulting in lazy is really minor.
Even if you create a buffer, you create a buffer kind of situation.
You are saying there are more things that you worry you won't be back soon, then it's a different case.

**Geohot** [00:05:07]
No, I don't even think it's that.
What I'm hearing is that if you delete those const folders from lazy, the OpenPilot kernel cap blows up.

**Qazalin** [00:05:16]
And no test failed, and that really scared me.
Like, everything passed, and then I counted the kernels, and it was three times more.
And somehow they changed parts.
No.

**Chenyu** [00:05:26]
So that cannot be confolding, right?

**Qazalin** [00:05:29]
It wasn't.
It was view.
It was specifically const folding.

**Chenyu** [00:05:32]
OK, so it's something else.

**Qazalin** [00:05:34]
Yeah.

**Geohot** [00:05:37]
Yeah.
The confolding should be OK to remove.
I wouldn't worry about putting that.
And you shouldn't be able to straight up delete that.
It might make the Python a little slower, but it shouldn't change kernels at all.
If it's changing kernels, there's a bug in the scheduler.

**Qazalin** [00:05:52]
Oh, because the elements-wise ops fuse?
Yeah, yeah, yeah.

**Geohot** [00:05:56]
Yeah, they should.

**Qazalin** [00:05:58]
Yeah, yeah, yeah.
That makes sense.
That makes sense.
I think that would work.
So I guess one thing that we could focus on is just making all those ALU stuff one line.
There are maybe 10 lines right now, each.
and making those one line.
The lazy stuff, so it has a bunch of if else's just removing all of those.

**Geohot** [00:06:27]
Yeah, just straight up delete that.
I see that big chunk in the ALU function called const-folding.
You can just delete that.

**Qazalin** [00:06:34]
So one thing I'm struggling with is testing infra for this stuff, because lazy buffer isn't process replayable.
I mean, you can pickle it.
It's really flaky if you pickle it.
How would you want to test this?
Because now if the test failed, the last time I broke everything on my PR.

**Geohot** [00:06:58]
How do you break everything?
Yeah, process replay shouldn't.. You shouldn't need process replay.
We have a lot of explicit tests for the scheduler and stuff that should test the number of kernels and stuff.
So I would think that if you get a regression of the number of kernels, you should add a new test to test schedule.
And then not worry about trying to, like, process replay is never going to handle this.
But what will handle this is, yeah, just test schedule explicitly.

**Qazalin** [00:07:28]
Yeah, like I exported the ASDs, the big graphs, into a text file and diffed it.
Like, that was my process replay scrappy version that showed the actual errors.
So yeah, I think maybe I'll move this to explicit unit test in the scheduler.
So yeah, that is one of the challenges.
Of course, there's also stuff with subbuffer.
I don't yet know how to solve that existing in the scheduler.
It exists already in the lazy code.
But yeah, other than those instant rules and the subbuffer stuff,
Everything else is pretty much passing.
All the tiny tests are passing in the DeleteLazy branch, which is pretty nice because we can just iterate on the rest.
That's the status.
Of course, buffers are the weak value dictionary, as we discussed.
And everything's being tracked like that.

**Chenyu** [00:08:42]
Are you saying something, George?

**Geohot** [00:08:53]
Yeah, yeah.
I'm just thinking, I'm just thinking if there's anything else on Big Graph.
Yeah, I'm thinking about like the const folding stuff.
So like, I see there's const folding in ALU and that can just go away.
the const folding in this logic should remove to the move to the scheduler.
Maybe that should move to the scheduler to handling the zeros.
But oh, I remember what I was gonna say.
What sub buffer is, okay, so sub buffer, whenever you have like a buffer pointing to a view, there's a special kind of view that's contiguous except for having an offset.
And that's what sub buffer would become.
Like I think you can use a graph rewrite rule to find valid of buffers and then not have to do a, yeah, like not have to do a kernel.

**Geohot** [00:09:49]
It also mutates the buffer object as a reference.

**Geohot** [00:09:57]
It shouldn't mutate the buffer object.
It should create a new buffer object with the other buffer as a base.

**Qazalin** [00:10:05]
Uh huh.
So different from how lazy does it.
Cause lazy right now does self.buffer.ref and then tracks the contiguous child.

**Geohot** [00:10:16]
Yeah.
I don't really know how lazy does it.
I'm also, I'm okay with like, if all the tests are passing, including process, including benchmark, obviously, like including the open pilot ones on benchmark, then
If there's a few minor regressions, there's a few minor regressions.
We're going to change so much here.

**Chenyu** [00:10:35]
This is the same thing as old lazy rewrite, lowerer rewrite.
It's not the first time we do things like this.
I think it has a new S-curve.
And initially, it might have small regression, as long as the direction is good and the new thing is cleaner than the old thing.
We can bring the speed back or the feature parity back.

**Qazalin** [00:11:06]
One minor thing that's just really off with everything being UOP is that UOP const can have a device.
at the lazy level, like lazy UOP, versus the UOP at the lower codegen level doesn't have a device for the const.
And function.py calls const like.
I'm gonna see how I can fix that.

**Geohot** [00:11:35]
It shouldn't.
Const should never have devices.

**Qazalin** [00:11:43]
Tensor definitely accesses device if your backward returns zero.

**Geohot** [00:11:51]
Yeah, I think that would be common.
I don't know.
I don't know.
Fix that however you want.
I don't know.
You're right.
It is kind of annoying, because we do say that all tensors have devices.

**Qazalin** [00:12:01]
Yeah, I think what you had is non-none devices.
And const just has none.
And you take the one that doesn't have none.

**Geohot** [00:12:11]
Yeah, I mean, if you have two branches, and one of them is coming in and has a none device, and one of them is coming in and has a device, you just ignore the none.

**Qazalin** [00:12:28]
Yes, like const is having different meanings.
I was slightly considering doing device const, but I don't think I'm going to do that.
Okay, device.

**Geohot** [00:12:40]
You definitely don't want to do device const.
What you might want to do potentially is create a UOP that just like injects device.

**Qazalin** [00:12:53]
And parent it.

**Geohot** [00:12:56]
I don't know.
Yeah, I don't even really like that either.

**Chenyu** [00:12:59]
Yeah, you don't want to inject device right.

**Geohot** [00:13:04]
Yeah, no, it really just shouldn't.
Like, why does a const have device?
If it's a const Tensor, it just doesn't have device.
That's OK.

**Qazalin** [00:13:11]
I mean, like, it needs to have some device.

**Chenyu** [00:13:16]
Then you need to start to check your sources either from the same device or it's a const.
Then you have all these is a const.

**Geohot** [00:13:25]
No, you don't check that it is a const.
You check that the device is none.

**Chenyu** [00:13:30]
Uh, yeah.
I don't know.
It's like, you really don't want to check that.

**Geohot** [00:13:42]
Well, I don't know, but I mean, I kind of like it, right?
Because that's actually the real, like, that's the real fundamental thing here, right?
If I create a tensor from a const, that tensor doesn't have a device.

**Chenyu** [00:13:58]
then if I do certain thing, like if I pad this const, or I do a sum on this const, then suddenly it has a device.

**Geohot** [00:14:06]
Yeah.
Why would you ever need it?
Hm.
OK, this is a question.

**Chenyu** [00:14:12]
Like creating a block const that I'm going to talk later?

**Geohot** [00:14:16]
How did I do this in Toonygrad?

**Chenyu** [00:14:25]
I don't know.
I feel we can move on now.
This is better.

**Geohot** [00:14:38]
We can move on.
But OK, fine.
Const needs a device.
I don't know.
Device const.
You opt device const or whatever.

**Qazalin** [00:14:45]
Yeah.
I'll just inject it.
And we'll rethink this later if it's right.
Now, Tensor does expect it.
The first requirement is to not change Tensor and stuff.
Just focus on changing lazy.

**Geohot** [00:14:58]
Let's move on.
Tensor needs a device.

**Qazalin** [00:14:55]
Yeah, that's all.
Thanks a lot.

**Chenyu** [00:14:55]
Great.
Okay.
Block?

**Geohot** [00:15:11]
Yeah, no, I think I finally made progress today.
I have new co-working space.
Nice place to sit down, drink a lot of coffee.
And yeah, so I have something now.
It's not passing all the tests quite yet, but it passes tiny and it passes ops.
That there's no longer a linearization step.
It just uses a set of rewrite rules to group things together in blocks.
And then another set of rewrite rules to stack the blocks on top of each other in a valid order.
And it's fairly local, which is nice.
So yeah, no more, no more linearization, no more tuple-izing the UOPs, no more comparison, no more hacks where we, you know, minus a thousand for low penalty or whatever.
Yeah, none of that stuff makes sense.
So yeah, this is probably still going to be, this is going to be the rest of my week.
But it's not, once you start, okay, so the basic thing is that you like, you have block ends, which is like the end of a for loop.
Then you have to combine those into one because you can only end the loop in one place.
And then you start pulling in things that have to be in the for loop.
Then eventually you close the loop as soon as you can.
So.

**Chenyu** [00:16:31]
I see.
I see if UOP const something minus 10.

**Geohot** [00:16:37]
Uh, yeah.
Yeah.
All that shit needs to go.
That's all going to be deleted.
You can look at the, you can look at the new one, second try at block linearize.
Oh, it doesn't have any const like that.
And I would say that, uh, most of this, oh yeah.
Yeah.
No, it's the output.
If you read second try block linearize, the output is a single block node.
Like the output of that graph rewrite is a single block node that has everything you need.
That has like a list.
So there's a few.

**Chenyu** [00:17:15]
Do you want to make this like whole rewrite rule base or do you eventually want to search some of these?

**Geohot** [00:17:24]
So.
Yeah, eventually you're going to want to search some of these.
So most of the decisions that you can make, and this makes the decisions a lot more clear too.
So most of the decisions you can make have to do with the ordering of the sources.
So for example, if I have a block and I test two parent blocks and those two parent blocks are in the same context, you can insert them in either order.
Um,
So yeah, that's eventually like where you're going to want to search, right?
You can, at each one of these, at each one of these points, you could try flipping it the other way.
I don't, we're not there yet, but this makes it a whole lot easier to think about than all that random priority stuff.
Because the problem with the old one was that there were invalid cases, right?
Not every topological sort was valid.
And making every topological sort valid is actually really hard.
You can imagine two loops that have nothing to do with each other and you're halfway into placement of both of them.
There's just no way to do it.
But now we can make it clear like here are the things you can change.
And maybe I'll even write a fuzzer before I get this merged that actually just, or maybe not a fuzzer, but I'll have like a mode where it just randomly permutes the things that can be randomly permuted.
and then tries recompiling the complex kernel thousands of times, making sure there's no bugs.

**Chenyu** [00:18:46]
Yeah, that sounds good.
I think we still have some cases that, for now, the generated source is invalid because of some scope issue.

**Geohot** [00:18:56]
Oh, yeah, there's tons, actually.
There's also, we're doing something really stupid in some of our kernels.
Sometimes loads will not get pushed out of loops that they can be pushed out of.
But that's the main thing that got me to start working on this.
Because yeah, you're doing loads multiple times when you just don't have to.
And yeah.

**Chenyu** [00:19:16]
Great.
It's good to have a principal framework to think about this that enables more optimization.

**Geohot** [00:19:31]
Yeah.
And the linearize was bad.
The linearize is going to be good.
Lazy is bad.
And then kernel.py, which I thought about a lot last week.

**Chenyu** [00:19:39]
Anything you want to say?
Kernel.py?

**Geohot** [00:19:49]
Um, well, just basically the, like right now we have this, and this is what we need for, uh, hand coded optimizations, right?
So right now we have this list of optimizations, but some of it doesn't make any sense, right?
Like you can call upcast four on an axis and then like upcast four again on the same axis.
This is just equivalent to upcast 16 on the axis.
So what I'm imagining is instead of moving to the current, like optimization, like we can probably still have the same action space, but the internal representation should be like for each axis, how much we're casting the axis.
And then what that actually upcasting or rolling and then what that actually becomes is a rewrite where we rewrite the range into the range time, something plus an expand.
If that makes sense.
Um, but I'm reluctant to change any of this stuff because of hand code and optimizations.
It's not the action space that's wrong.
See, basically what I never want to have to do is like hand coded optimizations will check a whole lot of weird properties about the shape.
And I never want to create those shapes.
Like I'm finally taking the current string of actions and applying it.
But the problem is that it looks at stuff that like, like I should never generate the intermediates is what I'm saying.
Um, this will also fix how slow everything's gotten.
Like, I just want to like apply all the optimizations and then figure out what the rewrite rules are in order to do those optimizations.

**Chenyu** [00:21:33]
I see.
Oh, I think I can think about that.
I think the first step, I think the first step is we have a bunch of tests that implicitly depends on hand coded optimization.
And if you put say NOOPT=1, those will fail.
I would probably start from there.

**Geohot** [00:21:59]
Yeah, there's also the
Pad is different.
So unrolls and like pad changes the loads.
Whereas unrolls and upcasts don't.
So you're going to want to apply pads beforehand.

**Chenyu** [00:22:23]
Add or pad?
Pad 2?

**Geohot** [00:22:24]
Pad.
Pad 2, yeah.
You're going to want to apply pad 2s before you apply any upcasts and unrolls basically.
Uh, because pad two actually changes the computation where the other ones just change like the iteration.
But is there any time we need to pad?
Is there any time pad can't be the first action basically?

**Chenyu** [00:23:03]
Uh, like TensorCores.
Pad usually is the first action, right?

**Geohot** [00:23:16]
Yeah, as long as we can enforce that, it's fine.

**Chenyu** [00:23:18]
As long as we can enforce that.

**Geohot** [00:23:24]
Because I want to apply the paths to the shape tracker, but then I don't want to apply the upcasts to the unknowns to the shape tracker.

**Chenyu** [00:23:36]
Yeah, this is like,
I think not just pad2.
We've probably discussed this about locals before.
It almost feels like for these optimizations, you have tiers, like orders you want to apply.
You have pad2 that changes the whole shape of thing.
Then you have local that splits global and local.
Then you have..

**Geohot** [00:23:47]
Local is easy.
Local is the same as unroll.

**Chenyu** [00:24:01]
and upcast.

**Geohot** [00:24:09]
Yeah, upcast, unroll, local, upcast, mid, are all the same thing.

**Chenyu** [00:24:14]
I guess I was meant to say group.

**Geohot** [00:24:20]
Group.
Okay, so what group is?
Group is a split of the reduce.
Group is just a rewrite rule on the reduce.
Yeah.
No, but yeah, this group is basically fine too.
Like it doesn't actually change the, uh, inserts, like it takes the reduced splits it into and insert some stuff.
Uh, you know, it's, it's PAD, PAD is the one that's fundamentally different.

**Chenyu** [00:24:49]
Yeah, we can, we can enforce PAD to be first, like there should be.
nothing, before pad, or something like that.

**Geohot** [00:25:09]
Because what I'm going to do is I'm going to rewrite.
So kernel.py is basically only going to do two things.
It's going to collapse all the axes as much as possible, because it's really easy to expand axes in rewrite rules, but it's really hard to collapse axes in rewrite rules, because collapsing requires you to deal with set of children.
It's expanding.
So yeah, that can be.
But pad two needs to be down on the shape tracker, because that's like changing the mask and changing everything.
Group and pad two are the only things done in kernel, and then everything else basically is done in lower.

**Chenyu** [00:25:47]
OK, that makes sense.
Cool.
Move on.
Oh, I got stable diffusion to be fast again.
I'm so happy.

**Geohot** [00:26:18]
It's amazing.
I love that tweet.
I love that tweet where it's like, we haven't really even focused on it, and it's faster and quicker.

**Chenyu** [00:26:27]
Yeah, we kind of did when we made conv fast.
But yes, it's pretty nice.
Yeah, what have I learned?
It also feels great that you don't need to check back to code base more than one year ago and apply all the diff to make it run again.
So I think for Mac, it really matters a lot if we store intermediate buffers in F versus float.
So I think two big speed regression.
One is from Winograd.
immediate output Dtype.
It was always created as float32.
I guess it was created to the default float.
Then when we use that for training, we always set default float to half.
But for stable diffusion, we only change the model to be half.
So that's one speed regression.
Another is the attention middle
intermediate thing that we used to store in floats when it can be half.
Those two are the biggest regressions and I think those two can all be fused eventually, so it's no longer a problem, but it's nice that we have this speed parity.

**Geohot** [00:27:56]
What I'll say about what that is, it's not the storing, it's all the loading.
What half gets you is your cache is effectively double the size.
That is why half is so much faster.
Like your L2 cache is effectively double the size.
You can fit twice as many items.
And sometimes memory bandwidth, memory bandwidth is doubled as well.

**Chenyu** [00:28:09]
I see, okay.
So I will also put attention to the speed versus theoretical later.
And I'll probably look into pad fusion, the one I talked about last week.
So pad fusion is basically, can we merge the conditions of two fusions?
Say if I have a where,
And another where, and I say add them together, then it can be, if it has the same gate, then you can merge the gate and push ALU down to its children.
And apparently, it's not always faster.
I need to look into in what condition is good.
But if we can do this, then I think we can have the pad
with non-zero thing to be cleaner.
And it also connects to the block const that I'm interested.
Because when looking at the Winograd, so for now, the old hack that made Winograd fast is not the most straightforward way you would write it.
If you have an tensor and you do a matmul on block const or like
padded, and concat const, because that's the only way you can write it now.
Ideally, you want all these to fuse element-wise into each one.
So if you have const that is 1, 2, 3, then you want your render kernel to be x multiplied by 1 plus y multiplied by 2 plus z multiplied by 3, something like that.
And for now, if you just write it this way, we will realize and create that 123 and just treat it as a loaded buffer.
I think this can improve and should make Winograd faster.

**Geohot** [00:30:36]
Yeah, I know we had some hacks where we were concatenating counsts together to get this behavior.

**Chenyu** [00:30:43]
Oh, no.
So for now, even if you do that, that creates a block const, but it doesn't fuse as you will want.

**Geohot** [00:30:50]
I see.
I mean, one of the biggest generic things that you always run into with Winograd is when, like, a lot of times now we will break on expands, but you don't always want to do this.

**Chenyu** [00:31:10]
Oh, yes.
Sorry, go ahead.

**Geohot** [00:31:16]
All right, just that.

**Chenyu** [00:31:18]
Yeah, so I was looking.
So because of this, I started to read scheduler.
I think this is also similar, but different from fuse arange.
It's similar in the sense that you have a tensor, or I guess for now it's a lazy that always parents its const, and you just apply some movement or ALU on top of that.
In a lot of these cases, you don't want this thing to be materialized.
Because if you do a matmul, then you do expand.
And if you do expand, then for now, we force realize this tensor.
So I think trying to read scheduler, I don't know.
I mean, I really want this delete lazy to finish so it can start to clean up scheduler.
I think a lot of schedulers still look pretty complicated.

**Geohot** [00:32:09]
we're all very excited about delete lazy.
You see I have gradient, it's ready to go as soon as we delete lazy, it was so easy.

**Chenyu** [00:32:15]
Oh yeah, I saw that.
Yeah, that's nice.

**Geohot** [00:32:19]
It's beautiful.
Yeah.
Yeah, but once lazy is deleted.
No, but it's not just for const.
I mean, the const case is the easy one.
The const case, you could just say like never realize const, that's the same as arange.
But there's also even the case of like, you have like,
tensor and then you have an expand on that tensor let's say the tensor is a megabyte and you expand it to 10 megabytes and then you multiply it by two right like do you really want to realize that first one or do you just want to do the multiply by two 10x more you probably just want to do the multiply by two it's probably way faster than going all the way to memory

**Chenyu** [00:33:05]
Yeah
This is like a general version of just const, because const we know is always faster to just apply the const.

**Geohot** [00:33:14]
Const we know is always faster.
And then I think the other thing is we probably need to take that ratio of the number of times it's accessed and jack it way up.
GPUs have a ratio of like, what's the actual ratio of like compute to memory?
It's like 1,000 to 1.
So anything that's expanded less than 1,000x, I think we probably don't want to.
That way, you just want to fuse.

**Chenyu** [00:33:37]
Yeah, that sounds good.
We will definitely explore this later.
OK, let's move on for Nimlgen.

**Nimlgen** [00:33:57]
Yeah, so this week, I just focused on cleaning up
AM, it's now readable without all these constants.
So yeah, it's pretty readable and compact.
So we also fix some several speed issues.
So yeah, I mean, still, like the main problem right now is the copy speed.
I mean, currently we're just right into VRAM.
and it's a lot slower than AMD.
So, and potentially for this, I'll double check some flags.
So, but basically it's like uncacheable memory and basically because we do some.. So yeah, I'll just check the flags, but

**Geohot** [00:34:56]
Um, are you using the GPU to copy it or the CPU?

**Nimlgen** [00:35:00]
No CPU.
Yeah.

**Geohot** [00:35:02]
Well, that's why it's slow.
Yeah.
How can we get the GPU to pull instead of getting the CPU to push?

**Nimlgen** [00:35:07]
So, yeah, that's, um, that's, that's the next point.
So actually I found that Linux has a thing called BF IO.
So that basically allows to like write user space drivers.
So.
And we can get interrupts, and we also can program IOMMU with it.
So actually, we have access to IOMMU.
We can just make the GPU read in this memory, like from CPU.

**Geohot** [00:35:38]
Wait, VFIO supports interrupts?
I know what it does with the IOMMU, but oh, that's great.

**Nimlgen** [00:35:47]
Yeah.

**Geohot** [00:35:47]
Yeah.
Yeah, I just thought it was just that it was just that you can map memory devices from user space.

**Nimlgen** [00:35:56]
So, yeah, it seems like it supports all these things.
I just skimmed through an NBME user space driver by someone.
So, yeah, I mean, we can get interrupts, I think, working as well.
So, and I think potentially if we think about cloud using this thing, so we definitely need interrupts because currently we're spinning, waiting for a queue to finish.

**Geohot** [00:36:27]
Yeah, it's great if we can get it in our apps.
I mean, yeah, what I really want to avoid is writing a device tracker, but if we can get interrupts from user space, that's great.

**Nimlgen** [00:36:40]
Yeah.
So this week, yeah, I'll focus on the HCQ removing update APIs and replacement with sint.
And yeah, also, I just looked at Ops_AMD and I think a lot of things to clean up there.
I don't really like how the packet trace, like they're really complex and looks not really readable.
I think, yeah, I can make them more readable and simpler to read.

**Geohot** [00:37:12]
Cool.
Yeah, no, I think the, I think the sint is a pretty high priority.
You know, you can just delete all those functions and every one of those functions has the potential for bug.
Um, and then like, there's actually a lot of code from the JIT that can be cleaned up too, because the sint thing is basically also the thing that does the, uh, dimensionizing, like dimensionizing.
Like there's this, there's this stuff to, yeah.
Um, so you could just have like one symbolize cache, run the symbolize for it.
Um, it also like when symbolize gets faster, everything gets faster.
Uh, but yeah, I'm excited about that.
You see what I mean?
You can make the device, the buffer addresses can be sint as well.
Do the shift, do the end, do the cast, do whatever.
It's all just UOPs.

**Chenyu** [00:38:38]
Okay, can we move on?

**Geohot** [00:38:42]
Well, I think that Qualcomm speed thing its the scheduler and most of it's going to wait for delete lazy.

**Chenyu** [00:38:47]
Okay, we will check Qualcomm later.

**Geohot** [00:38:50]
I think Qazalin push something this week to make it faster true or false.

**Qazalin** [00:39:00]
Yeah, it's like maybe 11% faster.
So there was like overhead from non graph rewrite right stuff.
I was saying with like verification.
checking cycles and stuff.
I got those to be much faster now.
But I love that it's just like graph rewrite?
There's like two paths here.
One path is like making graph rewrite faster and waiting for like the fast pattern measure stuff.
Another path is having a different graph rewrite for different runners.
Like copy doesn't need a bunch of those passes, but it's going through those passes because like the issue right is generic.
And it's meant to rewrite the kernel, not the copy stuff.
So maybe we'll just have a fast path for a simple, dead simple rewrite that's for the copy kernel.

**Geohot** [00:39:54]
Yeah, I don't know how I feel about that.
That's trading loss.
That's adding more code for exchange for speed.
I don't know.
I don't understand why it's five milliseconds.
I feel like if someone just sits down with a profiler and just looks at it, did you look at it with a profiler and say, what is it?

**Qazalin** [00:40:12]
It's definitely graph rewrite?
Because what you can do is you can baseline it.
You can remove those patterns that you know don't actually need to run on the copy.
And that's the baseline.
And then you, it's fast.

**Geohot** [00:40:25]
That's strange.

**Qazalin** [00:40:29]
That's like trading off complexity, right?
So it's like doing less, but sure.

**Geohot** [00:40:41]
But just because the patterns are in there, even if they're not actually being rewritten itself?

**Qazalin** [00:40:46]
Well, you're calling graph rewrites.
Well, the graph rewrites isn't like one pattern matcher added multiple times.
It's multiple graph rewrites, like the screenshot that you shared.

**Geohot** [00:40:58]
Oh, OK, I see.
You're removing entire calls to graph rewrites.
You're removing perversions in the graph.

**Qazalin** [00:41:04]
Yeah.

**Geohot** [00:41:05]
Yeah, I don't know.
Lets move on.
Let's revisit this after lazy is deleted.
And then we'll see what we can do.

**Qazalin** [00:41:11]
Yeah, I'm pausing it.
That's it.

**Chenyu** [00:41:16]
Oh, speaking of OpenPilot, Slyco improved my validhack mod.
So that's another 0.5 millisecond faster for OpenPilot.

**Geohot** [00:41:17]
What did he change?

**Chenyu** [00:41:19]
Just improved them.
There are some cases that I didn't handle initially.
So you can remove even more mods.

**Chenyu** [00:41:30]
That's great.

**Geohot** [00:41:36]
Yeah, that's great.
Yeah, that's a nice PR, too.

**Chenyu** [00:41:41]
Yeah.
And yeah, he also raised the issue initially.
There are some diff cases that he's looking now.
So I imagine those would also make that faster.
I'm just happy that someone else can also iterate on that part.

**Geohot** [00:42:32]
Yeah, happy someone else.
Yeah, that's awesome that someone else read this.
And I think that's a great PR.
It has tests, and the code is readable.
Yep.
OK, let's move on to Bounties.

**Chenyu** [00:42:49]
Are we merging WebGPU?
Have you tested the stable diffusion?

**Geohot** [00:42:52]
Is there a link?

**Wpmed** [00:42:52]
Yeah, I posted a link in WebGPU channel.

**Geohot** [00:42:52]
Oh, got it.
Cool.
WebGPU is not supported in this browser.

**Wpmed** [00:43:12]
I think you're opening in Safari, right?
If you're trying Chrome.
Yeah, it downloads the weights, then it catches the weight.
So next time it just decompresses because, you know,
VGPU doesn't yet have F16 extension.
So if you remember from last year, there is this F16 decompression to F32.
So when you open it again after weight download, only the decompression happens.
And that's fast.
So you don't have to wait for weight download again.

**Geohot** [00:43:24]
You're decompressing it in storage, right?

**Wpmed** [00:43:30]
Yeah.

**Geohot** [00:43:32]
Are you doing that in JavaScript or on the GPU?

**Wpmed** [00:43:37]
On the GPU.

**Geohot** [00:44:02]
Oh, cool.
Yeah, I mean, that should be doable.
Because it used to be in JavaScript, but I think you deleted that code.
I think I saw it on the PR.

**Wpmed** [00:44:09]
Yes, so yeah.
Yeah, I think last year you posted a snippet which was tinygrad, but I think the issue was that it generated more kernels, and I could do it in one kernel writing VGSL, so writing the decompression kernel code by hand.
And yeah, I deleted that code because last year I published it as a small lib, so I just used that lib.
It's basically the same stuff.

**Geohot** [00:44:42]
Wait, why can't we do this in TinyGrad now?

**Wpmed** [00:44:45]
I think now we can.
It's just that now we sure can.
Should I change the decompression to TinyGrad?

**Geohot** [00:44:59]
Yes, but I don't think this is a blocker on merging this.
Okay.
But yeah, no, the decompression should definitely be should definitely be Tinygrad that I think probably stuff that I want to work.
Yeah.
Go ahead.

**Wpmed** [00:45:15]
Good.
It's just that I think last year maybe it was pre D-type ALU or something like that.
So I can't remember exactly why it didn't work in TinyGrad, but I think some features were missing.
Yeah, but now we can do it for sure.

**Geohot** [00:45:35]
Great.
Yeah, no, that's.. I definitely would prefer things like that to be in TinyGrad because actually you might even realize.. it might even be faster to do the fusion.
right, to never even unpack the things, to just load them as packed uint16s and then upcast them to float32 in the same kernel or access element.

**Wpmed** [00:45:54]
Yeah.
Yeah, that's right.

**Geohot** [00:45:57]
Yeah, no, it's much better if you're trying to read kernels.
I mean, I think that's going to be a lot of the challenge in getting LLMs to be fast in the browser.

**Wpmed** [00:46:09]
Yeah.

**Geohot** [00:46:12]
OK.
OK, click and run.
It's going.
600 milliseconds.
700 milliseconds a step.
Great.
Cool.
This is awesome.

**Chenyu** [00:46:12]
Does it show us the time now?

**Wpmed** [00:46:29]
It's still in console.
So if you open the console,
Yeah, I will update the UI.
I didn't yet do it, but yeah.

**Chenyu** [00:46:29]
Oh, yeah, because I was using the console, and I saw you call the same timer function.
So yes, it shows the time, but it also mix with other times.
I think it's nice to show a step time, because people compare this.
If you load tinychat, we also show how many tokens per second it is.
It's a good way to know where we are and if we want to improve it, how fast it is.

**Wpmed** [00:46:52]
OK.

**Geohot** [00:46:59]
Yeah, I agree with that, but also not a blocker.

**Chenyu** [00:47:19]
Not a huge blocker on any of these, just small.

**Geohot** [00:47:22]
This is super usable.
This is amazing.

**Wpmed** [00:47:25]
And you're running on what hardware?
So what are you running on currently?
You're getting 600 milliseconds?

**Geohot** [00:47:35]
I'm getting 671 on M3 Max.

**Wpmed** [00:47:39]
Cool.

**Geohot** [00:47:41]
On M3 Max.
So I have a nice GPU, but.
I mean, this is probably a similar computer that most developers have.
Probably like a second on M1 Max or something.

**Chenyu** [00:47:57]
For M1 Max, I think it's 1700.

**Geohot** [00:47:57]
Oh, really?
It's that bad?

**Chenyu** [00:48:09]
So there's many things that's weird with my M1 Max.
There's always this JIT issue.
I don't know what's happening.
I wonder if it's similar things.
So I would test M4.

**Geohot** [00:48:19]
WebGPU is a completely different pipeline than the JIT.

**Chenyu** [00:48:24]
Yeah, but if it's a driver issue, it still goes to same.
I don't know.
It's just weird sometimes on M1 Max.

**Wpmed** [00:48:27]
Oh, and one thing I'm thinking of, but it's for later, is that maybe we could use OM WebGPU Engine.
So the one that Google Chrome uses, because now we use this WGPU lib.
And so the thing is that F16 is already supported in Chrome.
So if we switch to DOM, then we already can do F16.
WGPU, the library that we're currently using is not, there is a PR for that, but it's not yet merged.
So yeah, maybe we could switch to DOM.

**Geohot** [00:49:13]
Yeah, no, I think, I mean, the real, the real, we discussed this event and talk more about it offline.
tinygrad.org could be able to use WebGPU or your CPU.
could get you an LLM really fast.
And I think we can make, basically, a ChatGPT competitor that's completely local.
This stable diffusion is super usable.
This is awesome.
I think that this is, if we do this right, this can be the way that most people actually end up running AI.
If we can get decent performance on these models people care about in browsers, because no one installs apps.
Installing apps and computers is such a pain.
But does it work on my phone?

**Wpmed** [00:49:56]
I haven't tried it on a phone.
It might OOM, but you can try.

**Geohot** [00:50:06]
No blocker on that.
I'll give the code one last read and hopefully get it merged tonight.

**Wpmed** [00:50:11]
Okay, cool.
Thank you.

**Geohot** [00:50:18]
Great one.

**Chenyu** [00:50:19]
Oh, have we removed the limited of buffer count increased to 32?
Or is that default now?

**Wpmed** [00:50:37]
I think there's no buffer count limit now.
Sounds good.

**Chenyu** [00:50:46]
OK, let's move on to TensorCores.
Hello.

**Ignaciosica** [00:50:50]
This week I've been working on the first step into a true swizzle for the TensorCores and it's removing the expanded shape and the hidden reshapes that were within the FixShapeTracker function.
And I managed to remove that from Intel, CUDA and Metal, but I'm still having a little bit of trouble with AMD.
That's, I think, the first step towards the true swizzle.
Nonetheless, with some things you talked about here, about ops and what I was thinking before, I kind of
confused to how the truth swizzle will work because all other
shapetracker transformations that are performed in kernel are performed over the shapetracker.
But with a swizzled TensorCore, it not only performs a permute over that shape tracker but also adds the last shapetracker, messing the resulting view.
I kind of explained it in the PR I opened.
like an hour ago, showing progress.
But maybe I need to unpack what you talked here about kernel ops and it will be more clear.

**Geohot** [00:52:21]
Let me see this PR.
Remove tensor cores, expanded shapes and reshapes.
How do you do that?
Don't you need an expanded shape?

**Ignaciosica** [00:52:50]
No, the thing, the expanded shape was like reshaping the reduced dimension.
So what I did was actually using that expanded shape as the actual reduced shape and it worked.
But the thing with AMD is that it's not reshaping the reduced dimension, but reshaping the upcasted axis.
So it's different.
I'm trying to understand AMD TensorCores before a little bit more.

**Geohot** [00:53:27]
This stuff's always been confusing.
This stuff's never been that clear.
The way that I got a lot of those patterns was just trial and error.

**Ignaciosica** [00:53:34]
Yeah.
One question I had is, for Intel, for example, I can only rely on CI.
The tests are passing, but I can't test it anywhere else.
I don't think that's enough.
Good enough?
OK.

**Geohot** [00:53:49]
That's fine.
The Intel ones are kinda meh.
If it's broken, it's OK.
I mean, I want to keep it.
I wanted to pass CI, but otherwise, it's fine.
How's progress on deterring and TF32 tensor core support?

**Ignaciosica** [00:54:15]
I can retake work on that.
I kind of leave it aside and focus on this, but if you find it more prominent, not more priority, I can work on those.

**Geohot** [00:54:31]
Yeah, I mean, it's up to you.
It's up to you for which bounties you want to claim.
They're all locked to you.
And I have another bounty after the turing and TF32s are added, which is we've got to support the tensor cores in the H100.
Raj on Twitter was making fun of us.
He's like, it's so slow on H100s.
Because the H100 is a piece of crap if you don't use tensor cores.
They're different.
Yeah, yeah.
I'll add that one for you too.

**Ignaciosica** [00:55:15]
All the other reshapes and permutes are performed over the shape tracker itself.
And that's how it's done now.
It's the tensor core swizzle, it's performed over the shape tracker.
But with a true swizzle, it's not only performed over that shape tracker, but also adding the previous shape tracker.
It's like..

**Geohot** [00:55:49]
I don't, I don't exactly know what it is.
Like I don't exactly know why, but why, why it's different.
I don't think it should be a different thing, but like I merged your other one.
If we can't do it, then we can't do it.
There's a chance tensor cores are going to get like rethought again.
Once we read you the lower stuff and be made into like a rewrite rule.

**Ignaciosica** [00:56:08]
Okay.

**Geohot** [00:56:12]
But I still see expanded shape in the AMD one.
So you need it in the AMD ones, you just don't need it in the others.

**Ignaciosica** [00:56:17]
No, no, that's what I say.
I still can't figure it out at the AMD tensor core yet.
But that's why it's a draft.


**Geohot** [00:56:43]
Yeah, I mean, you're welcome to change all this stuff to be like, whatever you think, like, makes more sense.
It's not the best stuff.
Like we have ST1 pattern and ST2 pattern and they were just, I mean, like, I kind of know what they are, but yeah, they're kind of terrible.

**Chenyu** [00:56:54]
And if you remove all those and try to rewrite it again, you'd need to take the same path to trial and error again.
There's no principle way to understand.

**Geohot** [00:57:04]
Oh, I see why the reduce thing works now.
This works because of a bug I fixed.
You used to only be able to have one reduce axis, but now I've done the expands and the contracts good enough that that works.

**Ignaciosica** [00:57:17]
Yes, I think I realized that this one works even if I remove the contract from the WMMA operation.
Like it's no longer needed to fix that.
Maybe that's what you said.

**Geohot** [00:57:38]
Oh, well, be careful if you're removing the contract entirely.

**Ignaciosica** [00:57:42]
No, not removing.
I tested it and it worked, but yeah.

**Geohot** [00:57:48]
Yeah, I think we're exercising all the paths, but there is a bunch of hacks in UOPgraph to deal with WMMA.
There's something to deal with vectorized WMMA.
So there's a chance that it's just working because of that.
I don't love the vectorized WMMA thing in UOP graph either, but I did fix the multiple reduce access thing that used to not work.
I think that's why now that's not going to be deleted, so great.
If you feel like you're making good progress on it, keep at it.
If you get frustrated with it and want to make some quick money, get the TensorCore support ones.

**Chenyu** [00:58:30]
OK, thank you.
OK.
PTX?

**Alveoli** [00:58:31]
Hello?
Oh, yeah.
There is, I think I'm quite close, but there is an additional variable for the data type that's not needed.
And on top of that, just in general, spending more time on the actual instruction to see if they are really needed.
There might be more things I can shape up.
But I think I'm pretty close.
And thanks for reviewing.

**Geohot** [00:59:12]
Sure.
I think you're close too.
But really think about what that DType thing is doing and why you need it.

**Alveoli** [00:59:21]
Yeah, it's probably not necessary.
I just didn't look closely enough before.

**Geohot** [00:59:28]
Yeah, if that's gone, then I mean, eventually I'd really like to unify the for loop with the for loop and C style, but we don't have to do that right now.
I think that if you figure out how to get rid of those last few DTypes, I think it's good.
And I think that can all be deleted.
And if you have to, you can use like rewrite rules that apply to the graph instead of rewrite, instead of like hacking around the DTypes at the end there.

**Alveoli** [00:59:54]
Oh, that's true.
Yeah, I can try that.

**Geohot** [00:59:57]
there's pros and cons to that.
You know, then type verify might fail.
But yeah, I really like for each one of those, each one of those is like a special case to hack around something.
The general philosophy of tinygrad is every time you write a hack like that, you like something else, there's just something that isn't being understood correctly.
And if you think about really what it's doing, you can, you know, remove this stuff entirely and things become a lot simpler.

**Alveoli** [01:00:28]
I see.
Got it.

**Geohot** [01:00:49]
You're close.
It's the 20 lines I promised, right?

**Alveoli** [01:00:54]
Yeah, that's literally 20 lines.

**Geohot** [01:00:55]
Cool.

**Chenyu** [01:01:05]
Great.
Next is ONNX.
I'll speak for ONNX, I think.
Oh.
More.
Yeah, so.
Okay.
My point was there are like more stuff moving from on next to tensor.
I think it's.
Still not too complicated.
The pad looks pretty big now.
And generally, it's probably fine.
I saw a bunch of cast issues.
So we have different cast behavior because casting from
say a float that is very big into integer that is out of bound, it's not defined.
So NumPy and Jax does a slightly different thing.
I would say if we can match easily, that's good.
If we cannot, then it's not that big a priority.
We don't guarantee some of these undefined behavior.
But if we see things that should be truncated but that is not truncated, like the integer max minus 1 case, I think those we want to fix.
So cast behavior, I think that's important.
But some of the wrapping behaviors, especially if you don't apply any ops to it, we want those to match.
And tar extract, I think that one is.
George, do you have any comment on that?

**Geohot** [01:02:53]
I think it's pretty close to ready to merge.
Yeah, I think it looks pretty good.
The general, I'm just going to, I don't know.
Some of these instructions look a little weird, but maybe that is the right way to do it.
Like this one that's like checking to see if it's all zeros, the count.
It's like this point, I guess.
Yeah.
But yeah, the basic philosophy behind that stuff is we shouldn't be using files.
We should be using tensors.
So you can run these things in arbitrary places.
You can run these things on the GPU if you want, which is cool.
like you can extract a ton on your GPU.
You're going to have to do one transfer per file just to get the metadata, but that's OK.

**Chenyu** [01:03:56]
Cool.
OK, I'll leave that to you.
Yeah, I think that's all the things on agenda.
Well, next week we still do the same time and the one after we move back.

**Geohot** [01:04:20]
Sounds good.

**Chenyu** [01:04:21]
Yeah, I think we will both be in San Diego for that.

**Geohot** [01:04:24]
Yup, yup, I'll be back.

**Chenyu** [01:04:24]
On your phone.
Probably out of memory.

**Geohot** [01:04:32]
Yeah, I wish it gave an error.
I don't know how to bring up the console on my phone.
Oh, this phone has 12 gigs of RAM.
Why should it be out of memory?

**Chenyu** [01:04:48]
OK, we can discuss that offline.
I think that's it for this meeting.
Again, thanks, everyone, and see you next week.

**Geohot** [01:04:55]
Bye.
