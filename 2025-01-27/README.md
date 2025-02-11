# 2025-01-27 Meeting

### Meeting Agenda

**Time:** 6:00 AM San Diego time (PST) or 10pm Hong Kong time
- company update
- new multi, new gradient
- resnet, bert, rand_like, ones_like
- scheduler
- driver
- bounties (tensor cores, onnx, retinanet, graph rewrite 2.0, tinychat, windows ci, flatten add node, new bounties)

### Audio

[Youtube Link](https://www.youtube.com/watch?v=IEel2egz8pc)

### Highlights

- Multi and Gradient depend on UOps now (200 line reduction!!!)
- New VIZ coming soon (with gpu accelerated speed!)
- Need a good way of testing and tracking numerical stability issues (Ignaciosica working on a numerical precision framework)

### Transcript

**Chenyu** [[00:00:00](https://www.youtube.com/watch?v=IEel2egz8pc&t=0)]
Let's get started.
Any company update?

**Geohot** [[00:00:09](https://www.youtube.com/watch?v=IEel2egz8pc&t=9)]
Only red boxes are in stock.
We have a lot of red boxes.
We set up a little cloud.
We have five red boxes, five new red boxes for internal use.
*unintelligible*
Trying to get my hands on 5090's.
I have contacted all the vendors, see what we can get.
Yeah, not much else.

**Chenyu** [[00:00:48](https://www.youtube.com/watch?v=IEel2egz8pc&t=48)]
want to talk about new multi and new gradient 

**Geohot** [[00:00:51](https://www.youtube.com/watch?v=IEel2egz8pc&t=51)]
Sure
Had a pretty good week this week.
Finally got multi and Gradient merge that depend on UOPs and not on anything else.
So we had a separate class called multi-lazybuffer.
Multi-lazybuffer doesn't exist anymore.
It's constructed at schedule time now by pushing this ops multi down through the graph.
So it's pretty much the same logic, but instead of being a class, it's a graph rewrite.
And then once multi was done, I could finally merge gradient.
The problem with gradient with multi lazy buffer is you'd have to apply the gradient on the multi lazy buffer.
So you have to apply the gradient basically before you apply the multi.
But yeah, this is no problem now because the multi stuff is applied at schedule time and the gradient happens before schedule time.
So we got a big, we got like a 200 line reduction for that.
All the stuff in function's gone.
Function.py, the function class is gone.
And I think there's still quite a bit of cleanup left to do.
Just random stuff left around from old Gradient that could just go.
So yeah, I'm very happy with them.
And it seems like the UOP project that we started in October is finally coming to a close and it works.

**Chenyu** [[00:02:26](https://www.youtube.com/watch?v=IEel2egz8pc&t=146)]
Cool.
You mentioned some scheduler things that you were working on?

**Geohot** [[00:02:36](https://www.youtube.com/watch?v=IEel2egz8pc&t=156)]
Oh, so I merged this morning.
I merged just removing contiguous.
Everything is finally good enough that we can finally remove contiguous from SGD, which is cool.
And I added one more case that was OK for the assign.
Yeah, I think what I'm going to start working on is the kernel.
We have this thing break Schedule right now.
And we then break Schedule into these pieces.
And then we reconstruct a graph and do a BFS on that graph.
I think I can make something that looks a lot like linearize, but for the kernels.
And then you'll end up with the graph, and you'll also end up with the buffers pointing in.
So this would happen before bufferization.
It would just capture everything in a kernel, and then the inputs to that kernel are either other kernels or buffers.
And I think I can do that in the same way linearize works.
So something to start experimenting with.
I think I'll work on that for the rest of the week or...
I have that, or I can start working on the DSP stuff.

**Chenyu** [[00:03:49](https://www.youtube.com/watch?v=IEel2egz8pc&t=229)]
Speaking of block, in the bug reports channel, I think one of the previous linearizing compile error, now it's an infinite loop in block.
Maybe you would be interested in that.
Yes, error 53.

**Geohot** [[00:04:16](https://www.youtube.com/watch?v=IEel2egz8pc&t=256)]
53 is now an infinite loop in block.

**Chenyu** [[00:04:20](https://www.youtube.com/watch?v=IEel2egz8pc&t=260)]
I think previously it was an issue for some variable scope, and it probably became a different issue in block.

**Geohot** [[00:04:35](https://www.youtube.com/watch?v=IEel2egz8pc&t=275)]
Cool yeah, I'll look into it.

**Chenyu** [[00:04:37](https://www.youtube.com/watch?v=IEel2egz8pc&t=277)]
Great.
So with the new multi and new gradient, it has consequences to ResNet and BERT.
So I think for ResNet, the main issue is our old hyperparameters doesn't converge anymore.
I'm not sure why.
But so we have two separate issues.
One is the loss scalar on float16.
That needs to change.
Otherwise, I mean, float16 training was brittle with loss scalar.
Anyway, I think we just have some numerical issue.
Now I can update the loss scalar, so it converges similar to float32.
So I think that's fine.
But for float32 training,
It didn't converge.
I'm not sure if it's because it's very sensitive to some hyperparameters, or there's bugs.
It might be bugs before, and now it's fixed, or it's something that's fixed and now has a bug.
I'm not sure which way.
That's ResNet.
I'm sorry.
Go ahead.

**Geohot** [[00:05:58](https://www.youtube.com/watch?v=IEel2egz8pc&t=358)]
I'm curious what the change is, and we need to find a way to test and quantify this kind of stuff.
The only change I could find was the relu thing.
But the relu thing should change the number of kernels, but I don't think it should ever change the correctness.
It shouldn't even change it numerically.

**Chenyu** [[00:06:20](https://www.youtube.com/watch?v=IEel2egz8pc&t=380)]
Yeah, so my point is maybe there was a bug before.
You mean you cannot think of any other difference in terms of compute before and after?

**Geohot** [[00:06:29](https://www.youtube.com/watch?v=IEel2egz8pc&t=389)]
Well, the sigmoid one, but we dealt with that.
You know what it might be?
It might be the sigmoid.
I went through all the derivatives and was like, okay, what's different about the new derivatives and the old derivatives?
And ReLU has an obvious difference.
But other than that... 

**Chenyu** [[00:06:51](https://www.youtube.com/watch?v=IEel2egz8pc&t=411)]
We changed sigmoid to the new sigmoid a while ago and ResNet was fine after that change.

**Geohot** [[00:06:58](https://www.youtube.com/watch?v=IEel2egz8pc&t=418)]
We didn't, actually.
We changed sigmoid to the, oh, wait.
No, we did.
No, we did.
You're right.
We removed it.
Yeah, so I don't know.
I don't know what else it is.
Yeah, you did.
Totally.

**Chenyu** [[00:07:06](https://www.youtube.com/watch?v=IEel2egz8pc&t=426)]
So I was confused.
I think what I would do is probably, though I would run separate run in the background, but I would probably start to look into the CIFAR thing and see if there's diff.
I think CIFAR is faster to iterate.

**Geohot** [[00:07:26](https://www.youtube.com/watch?v=IEel2egz8pc&t=446)]
Yeah, I mean, CIFAR still seems to work.

**Chenyu** [[00:07:28](https://www.youtube.com/watch?v=IEel2egz8pc&t=448)]
Yeah, but last year when we were tweaking and improving ResNet, we also have similar moments that some change seems to be fine on CIFAR.
But because the hyperparameter and training epochs are pretty aggressive on ResNet, we are very likely to just on some edge of weird stuff.
So if at the end this is just some hyperparameter tuning, I won't be worrying too much.
But we will see on that.

**Geohot** [[00:07:58](https://www.youtube.com/watch?v=IEel2egz8pc&t=478)]
But I don't understand what changed.

**Chenyu** [[00:08:00](https://www.youtube.com/watch?v=IEel2egz8pc&t=480)]
Yeah, that too.

**Geohot** [[00:08:05](https://www.youtube.com/watch?v=IEel2egz8pc&t=485)]
Do you want to try to bisect it and see if you could find it?
I looked through all the scheduler tests.

**Chenyu** [[00:08:12](https://www.youtube.com/watch?v=IEel2egz8pc&t=492)]
Yeah, I can bisect it more.
I'm pretty sure it changed multi.

**Geohot** [[00:08:20](https://www.youtube.com/watch?v=IEel2egz8pc&t=500)]
Oh, it changed on multi, not gradient.

**Chenyu** [[00:08:22](https://www.youtube.com/watch?v=IEel2egz8pc&t=502)]
I need to separate, because I run several runs.
And I can bisect this.
I'm pretty sure it changed right after multi.
I don't know if it changed more after gradient.
But initially, I thought it might be because we changed behavior to the unsync batch norm.
I don't know if we really changed behavior.
There's a test change.

**Geohot** [[00:08:50](https://www.youtube.com/watch?v=IEel2egz8pc&t=530)]
Which I didn't change the behavior.
No, that test change with the strides thing, it's just because there's no more strides.
It should be the same behavior.

**Chenyu** [[00:08:59](https://www.youtube.com/watch?v=IEel2egz8pc&t=539)]
You changed something about the real...

**Geohot** [[00:09:06](https://www.youtube.com/watch?v=IEel2egz8pc&t=546)]
I didn't mean to.

**Chenyu** [[00:09:08](https://www.youtube.com/watch?v=IEel2egz8pc&t=548)]
At least you disabled one test that I don't fully understand.
I can look it up later.

**Geohot** [[00:09:14](https://www.youtube.com/watch?v=IEel2egz8pc&t=554)]
Oh, I disabled the test that used to assert.
That doesn't assert anymore.
Yeah, so that's, I don't understand really ever why that asserted.
Yeah, I did make a change.
I changed it so all things being not real are okay.

**Chenyu** [[00:09:35](https://www.youtube.com/watch?v=IEel2egz8pc&t=575)]
Oh, okay.
Then that's probably fine.
Then it's just empty, maybe, or zeros?

**Geohot** [[00:09:42](https://www.youtube.com/watch?v=IEel2egz8pc&t=582)]
Yeah, it should be all zeros, yeah.
So if that's...

**Chenyu** [[00:09:48](https://www.youtube.com/watch?v=IEel2egz8pc&t=588)]
I don't know.
I will bisect more and post the findings on the channel.
I think for ResNet, if I can understand this better, maybe do some CIFAR thing, I think it's fine.
When I say it's not converging, it's also not off by that much.
So it's not completely off.

**Geohot** [[00:10:12](https://www.youtube.com/watch?v=IEel2egz8pc&t=612)]
Yeah, I really doubt there's a bug.
But we just have to have a better way of talking about numerical stability.
Did we ever merge in the thing where we put the accumulator first?

**Chenyu** [[00:10:25](https://www.youtube.com/watch?v=IEel2egz8pc&t=625)]
Yes.
That was merged a while ago.

**Geohot** [[00:10:30](https://www.youtube.com/watch?v=IEel2egz8pc&t=630)]
That one, that should be helpful.
That definitely changes things, too.
But I would expect only the better.

**Chenyu** [[00:10:39](https://www.youtube.com/watch?v=IEel2egz8pc&t=639)]
Yeah, but that's before these.
And the ResNet was fine.
Pretty much everything that change kernel, after that, I run ResNet.
So I'm pretty familiar with what changed stuff and what didn't.
So for BERT, BERT has the issue with dropout.
Dropout has an issue with randlike.
randlike has an issue because we cannot have x-axis at the tensor level.
Do you have suggestions?
Similar to, I think for the 0-like or 4-like, there was a similar issue.
It might be less important, but it's still annoying.

**Geohot** [[00:11:32](https://www.youtube.com/watch?v=IEel2egz8pc&t=692)]
For the const, it's different.
No.

**Chenyu** [[00:11:39](https://www.youtube.com/watch?v=IEel2egz8pc&t=699)]
Because now you allocate a lot more memory than needed, right?

**Geohot** [[00:11:41](https://www.youtube.com/watch?v=IEel2egz8pc&t=701)]
If it's none, yeah, sure.
No, I don't have an obvious way to fix that.

**Chenyu** [[00:11:46](https://www.youtube.com/watch?v=IEel2egz8pc&t=706)]
OK, I'll think about this.
Yeah, because we need this for a complete BERT run.
So BERT is fine.
BERT, we kind of know dropout was not really needed.
It still runs now if we disable dropout, but we need that back.

**Geohot** [[00:12:08](https://www.youtube.com/watch?v=IEel2egz8pc&t=728)]
Yeah, and I guess I see why you want rand like in dropout.

**Chenyu & Geohot** [[00:12:16](https://www.youtube.com/watch?v=IEel2egz8pc&t=736)]
Yes, that was the proposed solution initially for dropout.
Yeah, you could multiply the seed by one.
So I think one way is probably instead of resolving everything, make it reuse
you up through fry and resolve it in ops or something.
Uh, I don't, I don't like that.
Why you want to, you want to,
Resolving it in Ops might be OK.
Oh, you mean resolve access in Ops.
Yeah, that's probably the way to do it.
Probably the way to do it is to move some of that multi logic into Ops.
I think that's what I suggested.
Yeah, move the multi logic into Ops and then.
Yeah, something like that.
I really want this to be similar to how we handle with the zero likes and ones like.
Yeah, yeah, no, I don't think this should be a one-off thing.
I think that moving the logic makes a lot of sense, just having my dot access actually work.
Yeah.
Yeah, so that's probably what I will be working on this week, fixing the MLPerf models and the drop-out and these const-like thing.
We can move on to schedule.
Qazalin are you there?
Move on to drivers first.

**Nimlgen** [[00:14:25](https://www.youtube.com/watch?v=IEel2egz8pc&t=865)]
Yeah so for the driver i think i fixed this problem so actually am driver can now just restore from all states and we don't leave the gpu in a bad state anymore so yeah also i fuzz it so yeah it works now 
And yeah we also have now we also can now uh collect some metrics from the gpu
So yeah, I'm just going to fix this idle power consumption.
So for some reason, GFX activity is at 100 right now all the time.
So memory is good now.
So maybe something with power gating.
So yeah, I'll double check that.

**Geohot** [[00:15:14](https://www.youtube.com/watch?v=IEel2egz8pc&t=914)]
Yeah, I think you have to manually turn the cores off.
I think it's just a simple thing.

**Nimlgen** [[00:15:22](https://www.youtube.com/watch?v=IEel2egz8pc&t=922)]
yeah i mean it's um yeah okay i'll take a look into that 

**Geohot** [[00:15:29](https://www.youtube.com/watch?v=IEel2egz8pc&t=929)]
yeah i like amsoi looks fine 

**Nimlgen** [[00:15:31](https://www.youtube.com/watch?v=IEel2egz8pc&t=931)]
yeah also can we just for several days replug uh 7600 as far as remembering to pci for me to test it and just after that switching back to usb yeah i think it will be just faster for me to test it that everything works

**Geohot** [[00:15:53](https://www.youtube.com/watch?v=IEel2egz8pc&t=953)]
Yeah, so I'm in Asia right now.
I can't plug it in somewhere else, but we can definitely get that set up.
But the other computer is still the same.
The first computer is still a 7900 XTX.
Yeah, yeah, yeah, I know.
I think the first thing to do is to get it working there and then also get it working on the other chip.

**Nimlgen** [[00:16:20](https://www.youtube.com/watch?v=IEel2egz8pc&t=980)]
Okay, yeah.

**Geohot** [[00:16:22](https://www.youtube.com/watch?v=IEel2egz8pc&t=982)]
But yeah, I will definitely get a computer with a 7900, with a 7600 PCI before it's time for that.
OK, cool.

**Chenyu** [[00:16:35](https://www.youtube.com/watch?v=IEel2egz8pc&t=995)]
I have a question.
So is AM good to use for, say, ResNet?
For some reasons, ResNet's now hangs on Tiny13, the red box.
And I can either try to use AM, see if we got better error message from that, or if you have any other suggestions.

**Nimlgen** [[00:17:09](https://www.youtube.com/watch?v=IEel2egz8pc&t=1029)]
What hang do you mean?
The one you shared in AMD Hardware?

**Chenyu** [[00:17:16](https://www.youtube.com/watch?v=IEel2egz8pc&t=1036)]
No, there are more.
It just crashed.
And the only error message I get is the runtime errors on the device hang.
So I just got that.
I had one run last night and one run this morning, both hangs after, I don't know, 20 minutes.
I can share more in the channel.
Just want to know if running with AM would give better error message.

**Nimlgen** [[00:17:55](https://www.youtube.com/watch?v=IEel2egz8pc&t=1075)]
OK.
No, I'm not sure that we have any better message.
But OK, it's interesting to see why it hangs.
I mean, you mean AMD, not AM.

**Chenyu** [[00:18:08](https://www.youtube.com/watch?v=IEel2egz8pc&t=1088)]
Yeah, so for now, it's AMD.

**Nimlgen** [[00:18:10](https://www.youtube.com/watch?v=IEel2egz8pc&t=1090)]
Yeah, I found it.
Yeah, go on.

**Chenyu** [[00:18:16](https://www.youtube.com/watch?v=IEel2egz8pc&t=1096)]
OK, I'll post more in the AMD channel, see if I can reproduce it.

**Nimlgen** [[00:18:24](https://www.youtube.com/watch?v=IEel2egz8pc&t=1104)]
Yeah, OK.
Actually, I also found, yeah.
So I think I found one bug I'm not really sure about.
And you posted it.
So that's page file to the address, like FF000.
So and actually, I think it's just from SDMA.
Like, you got it on the AM, and I just tried to... And actually, it's kind of reproducible, not only on AM, but also on AMD.
Actually, the same address.
I don't know.
I think maybe it's something hardware related.
I'm not sure.
So yeah, actually, it's reproducible running a lot of our...
I think how it's called, reduce benchmark or something like that.
Yeah, without JIT, without graph.
So yeah.
And also, yeah, also this week, I'm just going to see, I had to disable this bind method for SDMA.
It currently worked only for YAM.
And I see for SNETL, it also calls HANKS for some reason.
So without it, it works fine.
I've tested it with BERT, and with BERT it worked.
So I don't know.
It's just pretty reproducible on the ResNet.

**Chenyu** [[00:20:02](https://www.youtube.com/watch?v=IEel2egz8pc&t=1202)]
Something is different.
I don't get device hang for Redbox for training BERT.
It's really just ResNet, but I'm not sure why.
But since you are on this, I'll probably share one more about the ResNet hang, because that's different from the one I posted before.
But since you are already aware of the issue, I'll leave that to you.
We'll probably just use the green box.

**Geohot** [[00:20:33](https://www.youtube.com/watch?v=IEel2egz8pc&t=1233)]
My guess would be that it has something to do with local memory, because the ResNet stuff uses local memory a lot more than the BERT stuff.
Like a whole lot of the kernels use local memory.
I don't know.
It could be lots of other things, too.
It could be like the communication pattern or who knows.
But yeah, I mean, if it's happening in both drivers, then it's probably a bug in our runtime, not our driver.
I just ordered a 7600 too.
So we'll get that in the computer at some point.

**Chenyu** [[00:21:16](https://www.youtube.com/watch?v=IEel2egz8pc&t=1276)]
Great, sounds good.
OK, so as driver, let's go back to scheduler.
Hello?
I see you mute, but if you're talking, I cannot hear you.
Hi.
I can hear some background noise.

**Qazalin** [[00:22:26](https://www.youtube.com/watch?v=IEel2egz8pc&t=1346)]
Hello?
Is it good now?

**Chenyu** [[00:22:29](https://www.youtube.com/watch?v=IEel2egz8pc&t=1349)]
Yeah, it's good now.

**Qazalin** [[00:22:35](https://www.youtube.com/watch?v=IEel2egz8pc&t=1355)]
So I looked into the kernel stuff a bit.
I do think we need to move a bunch of these stuff to the new block style.
I think George is going to work on that, so I don't want to have conflicts and stuff.
Are you planning to do the kernel refactor?
I think you know this part best, like how block works and everything.

**Geohot** [[00:22:57](https://www.youtube.com/watch?v=IEel2egz8pc&t=1377)]
Yeah, so I think there's a few prerequisites that I'm not exactly sure.
Well, so I think definitely let's get do not construct unmasked valid merged.

**Qazalin** [[00:23:16](https://www.youtube.com/watch?v=IEel2egz8pc&t=1396)]
Sure, yeah.
I'll get that merged this week.
That ended up being more lower work than the actual scheduler.
Scheduler just merges the views.
So yeah.

**Geohot** [[00:23:27](https://www.youtube.com/watch?v=IEel2egz8pc&t=1407)]
The kernel thing, so right now we're doing bufferization.
Like, I think before we even think about changing break schedule, we have to stop creating buffers for things that we never realize.
Like, right now we create all of these buffers and then don't use a lot of them.

**Qazalin** [[00:24:04](https://www.youtube.com/watch?v=IEel2egz8pc&t=1444)]
So do you want to split the work as I do the refactor for removing all those bufferizations?

**Geohot** [[00:24:11](https://www.youtube.com/watch?v=IEel2egz8pc&t=1451)]
Yeah, well, I think I should probably work on the DSP stuff as well.
I don't exactly see how to, like, I can write the kernel thing, but the problem is I don't know where to, like, stop consuming with the kernels.
Like, we already have a lot of logic for that.
I don't want to...
rewrite the logic at the same time that I'm rewriting the style.
So I think maybe if you could first refactor bufferization to happen after choosing.

**Qazalin** [[00:24:51](https://www.youtube.com/watch?v=IEel2egz8pc&t=1491)]
After doing the reduce op stuff.

**Geohot** [[00:24:56](https://www.youtube.com/watch?v=IEel2egz8pc&t=1496)]
What reduce op stuff?

**Qazalin** [[00:24:58](https://www.youtube.com/watch?v=IEel2egz8pc&t=1498)]
The group realizes stuff that exists like...

**Geohot** [[00:25:01](https://www.youtube.com/watch?v=IEel2egz8pc&t=1501)]
After group realizes, yeah, yeah, yeah.
And it's okay for group realizes to be custom.
I mean, I think that, okay, like here's my proposal for how to do it.
So before bufferization, do group realizes.
Then after group realizes, insert contiguouses everywhere that you want there to actually be a buffer.
Then I can write kernel, which comes in and grabs everything up to a contiguous.
then do bufferization.
The thing that I imagine this eventually being is not something that really ever has a bufferization step.
It becomes the graph of the kernels with the kernels either pointing... Every source of a kernel is either another kernel or...
a buffer, a pre-created buffer.
Yeah, so do you think it's doable with what we currently have to move bufferization after group realizes?

**Qazalin** [[00:26:39](https://www.youtube.com/watch?v=IEel2egz8pc&t=1599)]
I mean, sure, but like this week I merged your add merge views to the ops folding.
And it's like, I upstream it and it works just, it's green and I merge it.
And it's like, because tensor map exists, right?
So I think like there's this step that we could take of just removing bufferization and going right away to the,
like style of doing the fusion stuff with graph rewrites and grabbing all the UOPs and gathering them?
That would just make this problem not exist.
Is that an option, or do we need to go this half step, dealing with the

**Geohot** [[00:27:27](https://www.youtube.com/watch?v=IEel2egz8pc&t=1647)]
We could try it.
OK.
You know what?
I will try it tomorrow.
I will take a shot at just writing the kernel thing and seeing how far it gets without the current logic.
And we'll see what we end up getting.
We'll see if I get something that's correct.
Yeah, kind of like toonygrad.
And then, yeah, we'll see.
If that's what you want to do, yeah, that seems reasonable.
Also, how's the moving of multi to tensor map going?

**Qazalin** [[00:28:08](https://www.youtube.com/watch?v=IEel2egz8pc&t=1688)]
Yeah, I close that.
There's this problem that bufferization has, which is that you can't track views, you can only track bases.
If you have a multi and then a reshape, and then you push that reshape over to the sources of the multi, you lose that multi.
So it's like,
It has to be fixed with some sort of more fundamental refactor.
I mean, I can try to redo this whole thing again if it's really annoying to have that multi-map step.

**Geohot** [[00:28:49](https://www.youtube.com/watch?v=IEel2egz8pc&t=1729)]
Well, yeah.
I think having the multi-map step exposes
Like, I don't understand, yeah, what is it about it that it can't be in the graphrewrite?
Did you say that if there's a reshape?
The reshape is...

**Qazalin** [[00:29:19](https://www.youtube.com/watch?v=IEel2egz8pc&t=1759)]
Yeah.
Views are just not tracked.
So views stay views.
Movement ops always stay movement ops.
We only track bases right now in the scheduler after bufferization because only bases have buffers, right?
So only bases are tracked.
I added that thing this week of like the const stuff.
So tensors can become const if you do a mul zero and you schedule it, it becomes a const.

**Geohot** [[00:29:45](https://www.youtube.com/watch?v=IEel2egz8pc&t=1785)]
Yeah, yeah.

**Qazalin** [[00:29:47](https://www.youtube.com/watch?v=IEel2egz8pc&t=1787)]
But you can't do the same with the reshape.
You can't make the reshape be a view after schedule.
It stays reshape.

**Geohot** [[00:29:59](https://www.youtube.com/watch?v=IEel2egz8pc&t=1799)]
Yeah, I mean, it has to stay reshape.

**Qazalin** [[00:30:03](https://www.youtube.com/watch?v=IEel2egz8pc&t=1803)]
And you lose that reshape.
I had the comment of the last thing before I close this.
Can we go from a view back to the movement hops?
I don't think we can.
But it's like you have to, you kind of have to do this, right?
You have to, if you want to realize a view afterwards or you want to map a tensor to a view from a base.
Like you can think about what cast before view is doing.
Cast before view is making a base tensor a view tensor.
And you can't stack a view on top of it.
You have to actually chain all the movements exactly the way that you did in the ops.

**Geohot** [[00:30:43](https://www.youtube.com/watch?v=IEel2egz8pc&t=1843)]
Well, yeah.
I mean, you should have to.
So the reason that you can't have views in the tensor stuff is you can't compute the gradient of a view.

**Qazalin** [[00:30:52](https://www.youtube.com/watch?v=IEel2egz8pc&t=1852)]
Exactly.
I got the error.

**Geohot** [[00:30:54](https://www.youtube.com/watch?v=IEel2egz8pc&t=1854)]
Yeah, yeah.
And there's no way to do it.
I spent like half a day on this.
But I don't understand why there should ever be views.

**Qazalin** [[00:31:16](https://www.youtube.com/watch?v=IEel2egz8pc&t=1876)]
Okay, thought experiment, cast before view.
What cast before view is this?

**Geohot** [[00:31:26](https://www.youtube.com/watch?v=IEel2egz8pc&t=1886)]
No, it's not.
I mean, cast before view is a misnomer.
It's cast before movement ops.
And yeah, you just move the cast before the movement ops and replay the same movement ops on top of the cast.

**Qazalin** [[00:31:39](https://www.youtube.com/watch?v=IEel2egz8pc&t=1899)]
How do you know what the movement ops are after graph rewrite map is done?
Like that's a problem, right?
You have to have some sort of way to look at a view and reconstruct the movement ops from that view.
You kind of know it, but you have to track it.

**Geohot** [[00:31:58](https://www.youtube.com/watch?v=IEel2egz8pc&t=1918)]
I see.
Yeah.
I mean, why does graph rewrite map have to collapse the views?
I guess there's a lot of stuff we want to do in that one.
Okay, I see the problem.
I don't have an obvious solution right now.
I'll start working on... I'll work on the kernel stuff tomorrow, and we'll see how far I get with it.
I'll probably, similar to toonygrad, get it to a point where it's kind of correct, and then hand it back to you.

**Qazalin** [[00:32:40](https://www.youtube.com/watch?v=IEel2egz8pc&t=1960)]
Okay.
I'm also working on Viz.
You can expect a new, new Viz coming soon.

**Geohot** [[00:32:48](https://www.youtube.com/watch?v=IEel2egz8pc&t=1968)]
Oh, with speed.

**Qazalin** [[00:32:50](https://www.youtube.com/watch?v=IEel2egz8pc&t=1970)]
With speed.
It's already working.
It's just ugly.
Very ugly, but it renders beautiful MNIST.
I'll make it pretty.

**Geohot** [[00:33:01](https://www.youtube.com/watch?v=IEel2egz8pc&t=1981)]
Oh, then the other thing that I want to talk about about Viz was a memory profiler.
I think...
This can wait for another time.
I like that this is going to be fast, though.

**Qazalin** [[00:33:15](https://www.youtube.com/watch?v=IEel2egz8pc&t=1995)]
Yeah, it's going to be fast.
GPU accelerates it.

**Chenyu** [[00:33:30](https://www.youtube.com/watch?v=IEel2egz8pc&t=2010)]
Let's move on to Bounties, starting with TensorCores.

**Ignaciosica** [[00:33:42](https://www.youtube.com/watch?v=IEel2egz8pc&t=2022)]
Hi.
Hello.
For search over shape, I'm implementing TIP 9 today.
There has been already a discussion on the pull request, but nothing new to add from my side.
I also started studying the new TensorCores.
From what I see, they introduced many things that may require incremental support.
There is a new TensorCore memory unit that it supports might also bring fast AMX.
And another thing is that they share some requirements with the H100 TensorCores.
So progress on any of those will benefit both.
Also, from my part, I started thinking about the new precision framework.
I imagine it's similar to how we count flops or memory, but quite more complicated.
I'll try to come up with a proof of concept in the incoming weeks.
But also, I need a lot of more research and studying from my part.

**Geohot** [[00:34:50](https://www.youtube.com/watch?v=IEel2egz8pc&t=2090)]
Wait, the new which framework?

**Ignaciosica** [[00:33:52](https://www.youtube.com/watch?v=IEel2egz8pc&t=2092)]
A precision numerical stability framework.

**Geohot** [[00:34:56](https://www.youtube.com/watch?v=IEel2egz8pc&t=2096)]
Oh, oh, cool.
Yeah, no.
Yeah, the 5090 stuff's interesting.
The new tensorcores, and I agree, it's very similar to AMX.
That's kind of where things have to end up.
Like you want to keep your stuff in basically more registered than GPUs have or AMX.
You know, the main reason GPUs have tensorcores and not FMA units is because tensorcores have symmetric inputs and outputs.
And this works nicely for DPU registers and warps, whereas the AMX doesn't.
The AMX has this accumulator that's the square.
That's like the accumulator is n squared and the registers are n. But it's interesting to see DPU starting to move toward something else.
Is 8767 good to merge?

**Ignaciosica** [[00:35:52](https://www.youtube.com/watch?v=IEel2egz8pc&t=2152)]
Sorry, I don't know the number.
I'm going to look.

**Geohot** [[00:35:55](https://www.youtube.com/watch?v=IEel2egz8pc&t=2155)]
Oh, tip nine.

**Ignaciosica** [[00:35:58](https://www.youtube.com/watch?v=IEel2egz8pc&t=2158)]
Yes, that's only the rename.
It's good to merge.

**Geohot** [[00:36:00](https://www.youtube.com/watch?v=IEel2egz8pc&t=2160)]
Yep.
Cool.
Great.

**Chenyu** [[00:36:15](https://www.youtube.com/watch?v=IEel2egz8pc&t=2175)]
OK.
Do you have any update on Onnx?
I think I merged several PR.
Oh, OK.
No worries.
It looks nice.
So no worries on your internet stuff.
I think I merged several things.
Just let me know if any review or PRs block on me.
I will review your stuff.
RetinaNet.

**Flata** [[00:37:01](https://www.youtube.com/watch?v=IEel2egz8pc&t=2221)]
Hey, guys.
So for the retinanet, I got the training loop done.
I'm working on the eval now.
I was initially thinking earlier to kind of optimize for the speed on the evaluation, but I just wanted to get the correctness done.
So I think what I'll do is I think the model eval had some sort of a runner on the ResNet side of things that kind of used the data loader.
So I'm going to just kind of try it on a separate branch to see
make that faster, and then see what kind of speeds I get.
But then get the full training and validation working first to get the full correctness.
And then, yeah, so that's kind of my goal this week, to get that working.

**Chenyu** [[00:37:44](https://www.youtube.com/watch?v=IEel2egz8pc&t=2264)]
I would suggest rebase to master, because as you know, there are some
issues or difference on ResNet.
So you might want to rebase on new things.
Another thing about data loader is I noticed, I'm not sure why, but for ResNet, most of the speed regression seems to come from data load.
Data fetch time is now very slow.
I think now our per step is 240 millisecond, and data fetch itself is like 160.
And that used to be, I don't know, like 50.
So just making sure when you migrate to the data loader, see if it's really faster and things like that.

**Flata** [[00:38:33](https://www.youtube.com/watch?v=IEel2egz8pc&t=2313)]
OK, sounds good.

**Chenyu** [[00:38:40](https://www.youtube.com/watch?v=IEel2egz8pc&t=2320)]
Cool.
And which machine will you be using?
I think we got a lot more red, so I can move to other machine.
If you are using red, you should have enough machine and not block by waiting on the machine or stuff.
So just post in the TinyBox access channel if you don't have a machine.

**Flata** [[00:38:59](https://www.youtube.com/watch?v=IEel2egz8pc&t=2339)]
Yeah, I was on a green box, I think, but just recently, just because I think Tiny 10 and Tiny 13 were getting used, I think, when I checked the activity.
So I can go to another machine if possible.

**Chenyu** [[00:39:17](https://www.youtube.com/watch?v=IEel2egz8pc&t=2357)]
We will figure something out.
I can move out of 13, and so you can have 13.

**Geohot** [[00:39:24](https://www.youtube.com/watch?v=IEel2egz8pc&t=2364)]
Yeah, we have 30, 31, and 32.
Should already be accessible to everyone at the company.
I think we can give them to external people, too.

**Chenyu** [[00:39:38](https://www.youtube.com/watch?v=IEel2egz8pc&t=2378)]
I think I can move off of 13, and 13 can be used for retinanet training.
OK.
Sounds good.
Tiny chat browser.
I don't know if you have permission to talk.
Who is that?
Is it Hooved?

**Geohot** [[00:40:06](https://www.youtube.com/watch?v=IEel2egz8pc&t=2406)]
What's their Discord name?
Hooved.
Yeah, you want to talk about it?
You are a speaker now.

**Hooved** [[00:40:33](https://www.youtube.com/watch?v=IEel2egz8pc&t=2433)]
Cool.
So it's been working on WebGPU for a couple of weeks.
I just got working on Wasm with Clang today, but it's not hosted yet.
So my priority has been to try to get it to work on a phone because
I think we'll get the most exposure and people will get the most value if they just see the tweet, they click on the link, and it just works without having to go and figure out what webGPU is.
Just think about the average person, right?
So that's the plan.
It's only taking up two gigabytes of memory with Clang, because I'm using quantized weights.
And I just want to get that hosted, see how fast it is, just see if it actually works on a phone.
I want to see if I can get the WebGPU memory, if I can shrink that using quantized weights, if possible.
And I'd like to have both WebGPU and Clang work from the same link, where it just kind of detects what you have enabled and just uses the fastest thing possible.
So that's what's going on now.
Let me know if you have any questions.

**Geohot & Chenyu** [[00:41:58](https://www.youtube.com/watch?v=IEel2egz8pc&t=2518)]
What's the initial scope of the bounty?
What's considered done?
Oh, the bounty specifies specifically both.
TinyChat browser supporting Clang and WebGPU.
And it's a $1,000 bounty.
Do you have a definition for support?
Like, how fast should it be?
Work reasonably well.
Okay.
Yeah, I made you a blue so you can talk in the channel, too.

**Hooved** [[00:42:31](https://www.youtube.com/watch?v=IEel2egz8pc&t=2551)]
Cool, thanks.
It's roughly 15 to 20 tokens per second on WebGPU.
Yeah, I'm on a 3080, so that's probably why.
Yeah, but that seems pretty decent.
Maybe we can get it better.
But clang is like less than a token per second, which is kind of sketch.
But if that's what it takes to make it work on a phone, I'm still interested in it.
But maybe we can get it faster.
I just need to play with it.

**Geohot** [[00:43:10](https://www.youtube.com/watch?v=IEel2egz8pc&t=2590)]
Yeah, I mean, I'd expect it to be more than a token per second, right?
You just take the RAM bandwidth of the system and divide it by the size of what you're accessing.
I would imagine Clang could find that no problem, unless something else is wrong.

**Hooved** [[00:43:26](https://www.youtube.com/watch?v=IEel2egz8pc&t=2606)]
Yeah, I barely played with it.
I just got it working.
I want to just tinker with it.

**Geohot** [[00:43:33](https://www.youtube.com/watch?v=IEel2egz8pc&t=2613)]
Oh, cool.
Yep, sounds like good progress.

**Hooved** [[00:43:35](https://www.youtube.com/watch?v=IEel2egz8pc&t=2615)]
Thanks.

**Chenyu & Geohot** [[00:43:35](https://www.youtube.com/watch?v=IEel2egz8pc&t=2615)]
I don't know if the person's here, or it's a different person.
But I saw we merged simple Windows CI.
Yeah, we merged Windows CI.
It turned out to be really simple, because the LLVM backend just kind of worked.
So yeah, I put another bounty up for Clang, and he put a PR up for it.
But I don't want to merge and maintain a cost loader.
Hopefully there's another way to do it.
OK.
Do we have any further plans for Windows or after let us done is kind of maintained?
I think it's maintained.
I think that if we can just do test time with as many backends as we can get, it seems pretty good.
OK.
CL backends would be cool if there's a way to get that one to work.
Yeah, that sounds reasonable.
OK, and edit, flatten, add mul, because I saw the person working on it was in a meeting, but I don't see him anymore.
So I don't know.
I'll probably read the new change and comment on the PR.
Oh, we missed graph rewrite 2.0.
Oh.
OK, sorry.
Graph rewrite 2.0.
Oh, I don't know.
Maybe the person in front of me.
I think he left and rejoined.
If you are trying to speak, I cannot hear you.
Oh, I got to revert.
I got to revert the rename.
It broke something.
shape, and then negative number.
Interesting.
Do you have any bounties or things?
What happened to LLVM float16 cast to rewrite rules in render?
Is it locked?
Oh, yeah.
It's locked.
I think it's closed.
I think I just don't like where the icon is on it.
I don't like where the function.
I see.
OK.
Yeah, I think that's pretty much it.
Someone asked, where can we watch the recording of these meetings?
It's in the recordings channel.
Yeah, I think that's everything on the agenda.

**Geohot** [[00:47:24](https://www.youtube.com/watch?v=IEel2egz8pc&t=2844)]
I'm super tired tonight.
I'm still adjusting to the time.

**Chenyu** [[00:47:33](https://www.youtube.com/watch?v=IEel2egz8pc&t=2853)]
Let me know if this time is too late for you and we can figure something out.

**Geohot** [[00:47:37](https://www.youtube.com/watch?v=IEel2egz8pc&t=2857)]
It should be fine once I adjust.

**Chenyu** [[00:47:40](https://www.youtube.com/watch?v=IEel2egz8pc&t=2860)]
Sounds good.
Cool.
I think that's it for this meeting.
Thanks, everyone.
See you next week.

**Chenyu** [[00:47:50](https://www.youtube.com/watch?v=IEel2egz8pc&t=2870)]
Bye.

