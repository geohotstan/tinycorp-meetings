# 2025-03-10 Meeting

### Meeting Agenda

**Time:** 7am Monday San Diego time (10pm HK time) (daylight savings!)
- company update, business development
- moe, quantized mobile net
- gpu on usb, driver
- bert
- scheduler
- onnx
- webgpu
- torch frontend
- retinanet
- other bounties?

### Audio

[Youtube Link](https://www.youtube.com/watch?v=swYfv-dheuc)

### Highlights

- [Company & Business Update](#geohot-000007) MI300X boxes have been delivered, signaling strong AMD support. No news from Intel.
- [DeepSeek & MLPerf](#geohot-000135) Plans are underway to achieve 500 token/sec DeepSeek performance and outperform H100s on MLPerf.
- [MOE Integration](#geohot-000255) A state-of-the-art MOE model is now in TinyGrad with Top-K merging; bounty reduced to $300 for final integration.
- [MobileNet](#geohot-000600) Shift focus back to quantize-mobile-net next week.
- [HCQ Timeout](#nimlgen-000833) GPU command timeout is set to 30 seconds; discussion centers on accommodating longer BERT operations.
- [BERT Optimizations](#chenyu-001054) Float16 ACC kernel improvements yield 20% speedup with larger batch sizes and fused Arange enhancements.
- [Scheduler Refactoring](#qazalin-001736) Efforts to remove views and refactor the kernel graph are in progress, with multi-output support on the horizon.
- [ONNX Testing](#chenyu-002840) Dry run flag and true float16 support are being tested to ensure numerical consistency with model inputs.
- [WebGPU Export](#hooved-002945) The WebGPU export model is being refactored for better Torch frontend integration and competitive performance versus ONNX Runtime Web.
- [Torch Frontend Updates](#b1tg-003308) Bounties continue for test ops improvements, nanoGPT memory leak fixes, and COMGR PR refinements.
- [RetinaNet Optimization](#flata-003832) Transitioning RetinaNet to float16 aims to achieve sub-24-hour training runs alongside Top-K eval script enhancements.
- [x86 Backend](#chenyu-004503) The x86 backend currently lags (20% slower than O0, 3x slower than O1) and needs targeted performance improvements.
- [TC=3 Bug](#ignaciosica-004150) A bug with TC=3 causing failures on larger matrices due to local memory limits has a $200 bounty for a fix.


### Transcript

##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=swYfv-dheuc&t=0)]
Let's start with company update and slash business development.

##### **Geohot** [[00:00:07](https://www.youtube.com/watch?v=swYfv-dheuc&t=7)]
Yeah, so we did good business development.
We got two MI300X boxes.
They'll be set up in a few hours.
We got our guy back at the Comma headquarters flying in.
He's half remote.
He's going to fly in and get them racked and get them set up as tiny 42 and 43.

##### **Geohot** [[00:00:38](https://www.youtube.com/watch?v=swYfv-dheuc&t=38)]
Updates on the Intel business development.

##### **Geohot** [[00:00:42](https://www.youtube.com/watch?v=swYfv-dheuc&t=42)]
I haven't heard anything since my two requests where I need to be able to plug these things in and I need a, you want me to, I'm happy to buy a ton of them, but I need like a deal on paper.
I know how this is going to work at Intel.
There's going to be 27 legal things.
And, you know, you think you can do something.
But at Intel, there's thousands of people who can say no.
It is cool that, like, I mean, Lisa Su sent us those boxes.
And that is such a strong signal for AMD that they have leadership that's capable of doing that.
Like, I wasn't kidding about the cultural test.
So they passed the cultural test.
We got boxes, and I'm actually really bullish on AMD.

##### **Chenyu** [[00:01:29](https://www.youtube.com/watch?v=swYfv-dheuc&t=89)]
What's our plan for those boxes?
Anything tangible?

##### **Geohot** [[00:01:35](https://www.youtube.com/watch?v=swYfv-dheuc&t=95)]
Well, yeah, I want to get, so eventually I want to get MLPerf, but I don't want to give them a bad MLPerf score.
I want to make sure that if we get the MI300s on MLPerf, I want to beat the H100s.
But I also want to do deepseek really fast.
I think that that's an immediate thing that can be marketed and provide value.
If we could get like 500 token per second deep seek, full deepseek.
Should be doable.
The hardware, the MI300x hardware is great.
Yeah, so with our driver, get deep seek.
Yeah, and then deep seek plays Pokemon on Twitch.
I don't know if you saw Claude's.
It's cool, but it runs slow.
It's so slow.
Claude's so slow.

##### **Chenyu** [[00:02:32](https://www.youtube.com/watch?v=swYfv-dheuc&t=152)]
So that's because they put all the things on each position as a very long sentence and things like that.

##### **Geohot** [[00:02:42](https://www.youtube.com/watch?v=swYfv-dheuc&t=162)]
I mean, yeah, that certainly doesn't help.

##### **Chenyu** [[00:02:46](https://www.youtube.com/watch?v=swYfv-dheuc&t=166)]
OK, cool.
Yeah, since we're talking about deep seek, do you want to say more about MOE?

##### **Geohot** [[00:02:55](https://www.youtube.com/watch?v=swYfv-dheuc&t=175)]
Yeah, so I did a stream this weekend.
I got a tiny, open, state-of-the-art MOE model.
It's in TinyGrad now.
We have a test.
It was a $500 bounty, but now that I did half the work for you, it's a $300 bounty to get that MOE in the JIT.
I think also Top K was merged today.
Zibokapi got top K merged.
So yeah, that's just a question of figuring out how to get the indexing.
I don't know really how that works.
Is the indexing going to NumPy or not?
Does it have to realize the tensor in order to index using it?

##### **Chenyu** [[00:03:52](https://www.youtube.com/watch?v=swYfv-dheuc&t=232)]
I think for now, because you need to pick.
How do you pick the experts now?

##### **Geohot** [[00:04:04](https://www.youtube.com/watch?v=swYfv-dheuc&t=244)]
Well, I pick the expert.
It's just the top k function should just work.
That might be the easiest $300 for someone to get right now.
It might just be a two line change.

##### **Chenyu** [[00:04:23](https://www.youtube.com/watch?v=swYfv-dheuc&t=263)]
OK.
If it's just selecting the indexing, then you can do the same shrink to that thing?
Or just, oh, no, it's the tensor indexing, right?
So you just pass that as a tensor to the index, and it would just work?

##### **Geohot** [[00:04:40](https://www.youtube.com/watch?v=swYfv-dheuc&t=280)]
It's tensor indexing.
Yeah, it's entirely tensor indexing.
So if it's doing Arange masking and stuff, then it really might just work.

##### **Chenyu** [[00:04:49](https://www.youtube.com/watch?v=swYfv-dheuc&t=289)]
Great.
Let's see.
I hope that works.

##### **Geohot** [[00:04:58](https://www.youtube.com/watch?v=swYfv-dheuc&t=298)]
Oh, if you're getting out of memory, you can fix the memory too.
If the memory is so wasteful in that thing, I don't really know why.
There's a memory leak.

##### **Chenyu** [[00:05:06](https://www.youtube.com/watch?v=swYfv-dheuc&t=306)]
OK.

##### **Chenyu** [[00:05:10](https://www.youtube.com/watch?v=swYfv-dheuc&t=310)]
Tiny model.
Unless you have 16 gigs of RAM.
If you have 16 gigs of RAM, I don't know.
But if you have 32 or even 24, it should be fine.
You can use a tiny box, but you've got to fix the RAM leak.
Wow, that's not many gigs.
Oh, then just do it.
You don't do all the layers.
Just do one layer.
See if you can get it.
Start there.

##### **Chenyu** [[00:05:40](https://www.youtube.com/watch?v=swYfv-dheuc&t=340)]
Try one layer or try something smaller.
If it works, if it looks like it's going to work, someone else can test for you.
Cool, now that's MoE
Anything to say for the contract?

##### **Geohot** [[00:06:00](https://www.youtube.com/watch?v=swYfv-dheuc&t=360)]
Yeah, I got to stop doing this USB stuff.
It's very addictive.
It's very addictive.
So it's to the point now it works.
We fixed the reliability issue today.
But there's still the, it doesn't work through a hub, and it doesn't work on tiny10.
So I don't know why that stuff is.
If I plug a hub in, it just gives minus 7 errors.
And I don't know why.
So yeah, I didn't do the quantize.
I got to get back to quantize-mobile-net.
Tomorrow, back to quantize-mobile-net.
No more USB.
I'll write it on the whiteboard.
I'm going to get a whiteboard in here and write USB.

##### **Chenyu** [[00:06:42](https://www.youtube.com/watch?v=swYfv-dheuc&t=402)]
We have a Nimlgen that will help hold you accountable for that.

##### **Geohot** [[00:06:47](https://www.youtube.com/watch?v=swYfv-dheuc&t=407)]
Oh, yeah, no, Nimlgen did all the work today.
I just sat here and typed.

##### **Chenyu** [[00:06:52](https://www.youtube.com/watch?v=swYfv-dheuc&t=412)]
No, no, my point is Nimlgen will watch you do the context stuff.

##### **Geohot** [[00:06:57](https://www.youtube.com/watch?v=swYfv-dheuc&t=417)]
Yeah, not do USB.
Good point.

##### **Chenyu** [[00:06:59](https://www.youtube.com/watch?v=swYfv-dheuc&t=419)]
OK.
I think Nimlgen in the office, next point is for you.
Any GPU, USB driver stuff you want to update?

##### **Nimlgen** [[00:07:12](https://www.youtube.com/watch?v=swYfv-dheuc&t=432)]
So yeah, actually, it's
on the previous week fixed some AM bugs.
So basically, it was hit a bit flashing missing.
And now AM runs in benchmarks in ci.
Oh, yeah.

##### **Chenyu** [[00:07:34](https://www.youtube.com/watch?v=swYfv-dheuc&t=454)]
Yeah, it's everything ran benchmark on CI am now.

##### **Nimlgen** [[00:07:39](https://www.youtube.com/watch?v=swYfv-dheuc&t=459)]
Yeah, I mean, both training and
training benchmark and just benchmark.
We still have some like heap tests and I think some AMD tests.
So it's just still like on one machine switches from driver to driverless.
But yeah, training is fully on AM.

##### **Chenyu** [[00:08:01](https://www.youtube.com/watch?v=swYfv-dheuc&t=481)]
That's good.
Oh, I have one question about the HCQ timeout stuff.
I think now it timeout after 30 seconds.
Is that one dispatch of the whole command, no matter how big the command is?
So for the BERT one, it might legitimately hit 30 seconds.

##### **Nimlgen** [[00:08:33](https://www.youtube.com/watch?v=swYfv-dheuc&t=513)]
yes so actually in beam so like that i tested like three days ago just easily hit found some kernels that are just 30 seconds long and yeah but but like answering your question yeah it's just from the point you just submit it to the gpu and you just
So yeah, it's for several kernels and for several commands.

##### **Chenyu** [[00:08:59](https://www.youtube.com/watch?v=swYfv-dheuc&t=539)]
It's just slightly weird that it's kind of a limit no matter how big your command is.

##### **Nimlgen** [[00:09:16](https://www.youtube.com/watch?v=swYfv-dheuc&t=556)]
Yeah.
I think, yeah, I can easily fix that.
Maybe just see if,
if this timeline is progressing.

##### **Chenyu** [[00:09:27](https://www.youtube.com/watch?v=swYfv-dheuc&t=567)]
Yeah, I will leave that to you.
My use case is sometimes for BERT, because even if we are using BEAM, we don't BEAM the first round.
And the first round, depends on the setup, might take a lot more than 30 seconds.
Because we have Arange, that default is not the most efficient one.
And if we do fuse Arange,
other stuff, the hand coded optimization might be very slow.
But the subsequent beam search one should be good.
For now, I'm just pass that flag and say, like, 10 minutes or something like that.

##### **Nimlgen** [[00:10:08](https://www.youtube.com/watch?v=swYfv-dheuc&t=608)]
OK.
OK.
That's fixable, yeah.

##### **Chenyu** [[00:10:11](https://www.youtube.com/watch?v=swYfv-dheuc&t=611)]
Cool.
OK.
Anything else?

##### **Nimlgen** [[00:10:19](https://www.youtube.com/watch?v=swYfv-dheuc&t=619)]
So no going to work on the USB stuff this week.
So maybe some runs to make as they might be in default.

##### **Chenyu** [[00:10:28](https://www.youtube.com/watch?v=swYfv-dheuc&t=628)]
That's good.
Okay.
Next is Bert.
Uh, so you say our new deadline is May 2nd.

##### **Geohot** [[00:10:47](https://www.youtube.com/watch?v=swYfv-dheuc&t=647)]
Yup.

##### **Chenyu** [[00:10:54](https://www.youtube.com/watch?v=swYfv-dheuc&t=654)]
Great.
So I merged some small improvements, like realized some small stuff.
The latest experiment is, so BERT apparently can train with float16 ACC.
I tried that, and it converged similarly.
Well, that's good, because it's faster.
And so it's two things.
Using the float16 ACC kernel is still faster.
Using that is faster.
And also because we don't do the expand the cast.
So for now, if we do a cast to half, then do a half
matrix multiplication, then we realize the first expand and use extra memory, because that expand you also need for backward.
I think this is separate, but combining these two, we can fit batch size 96, and it's like 20% faster compared to master now.
So we'll try to merge in a version of this.
Also, spend some time on the Fuse Arange.
The Fuse Arange with embedding is great.
If we can get that in, it's like 3% faster because the embedding kernel is very slow.
The issue I was hitting was it's also fused with the threefry kernel, and that is very, very slow.
So I don't know if there's a
concept for just fusing part of stuff in fuse Arange?

##### **Geohot** [[00:12:43](https://www.youtube.com/watch?v=swYfv-dheuc&t=763)]
Well, why is it slow with the three-fry kernel?

##### **Chenyu** [[00:12:48](https://www.youtube.com/watch?v=swYfv-dheuc&t=768)]
Because three-fry kernel is very big.

##### **Geohot** [[00:12:51](https://www.youtube.com/watch?v=swYfv-dheuc&t=771)]
No, but like, fuse Arange should become nothing.
Like, fuse Arange means if fuse Arange is slow, it almost has to mean that the, like,
Arange isn't folding once it's being fused.

##### **Qazalin** [[00:13:10](https://www.youtube.com/watch?v=swYfv-dheuc&t=790)]
Exactly.
Yeah, it's not folding.
It's creating a giant loop in dropout.
So there's this giant loop in the middle that's actually doing a for loop for Arange.
It's not fusing it.

##### **Geohot** [[00:13:24](https://www.youtube.com/watch?v=swYfv-dheuc&t=804)]
Yeah, so I mean, it's fusing it.
But can we fix the Arange folding in the fused kernel?

##### **Chenyu** [[00:13:32](https://www.youtube.com/watch?v=swYfv-dheuc&t=812)]
Not yet.
We need to first make random one kernel.

##### **Qazalin** [[00:13:40](https://www.youtube.com/watch?v=swYfv-dheuc&t=820)]
Is that a prereq?
Like, I would love for Arange to always work.
Because I did spend time looking into making fuse Arange not fuse sometimes.
But I don't even know what the heuristic is.
Yeah, I don't think that's Arange to just not have a for loop
ever if I fuse something that's an Arange kernel.

##### **Geohot** [[00:14:05](https://www.youtube.com/watch?v=swYfv-dheuc&t=845)]
I think we have to improve our Arange folder to work in all cases.
And we should figure out what cases it's not working in, because that's not what I expect fuse Arange to always be OK.

##### **Qazalin** [[00:14:19](https://www.youtube.com/watch?v=swYfv-dheuc&t=859)]
Mm-hmm.
OK.
I can make a test for that one.

##### **Chenyu** [[00:14:27](https://www.youtube.com/watch?v=swYfv-dheuc&t=867)]
Yeah, OK.
Let's start there.
I would take a look.
I think it's just some cases that we are not handling, and it's very big.

##### **Geohot** [[00:14:38](https://www.youtube.com/watch?v=swYfv-dheuc&t=878)]
Yeah, we just got to add more cases to the test Arange tests that don't work when they're fused.
Like the ones that test the flop complexity, like 10 action only.

##### **Chenyu** [[00:14:59](https://www.youtube.com/watch?v=swYfv-dheuc&t=899)]
that sounds good yeah so i think the next speed i will coming from the acc change, fuse arange maybe then and we'll see where we are after these two also the float16 acc doesn't quite work on it on the red tiny box but i don't know why i will also take a look later

##### **Geohot** [[00:15:28](https://www.youtube.com/watch?v=swYfv-dheuc&t=928)]
When you say it doesn't work, you mean it doesn't converge or crashes?

##### **Chenyu** [[00:15:32](https://www.youtube.com/watch?v=swYfv-dheuc&t=932)]
It doesn't converge.
It NaN out almost immediately.

##### **Geohot** [[00:15:40](https://www.youtube.com/watch?v=swYfv-dheuc&t=940)]
Interesting.
I'm surprised that you're telling me that works.
I almost have a theory that it's not actually accumulating in FP16.

##### **Chenyu** [[00:15:47](https://www.youtube.com/watch?v=swYfv-dheuc&t=947)]
Then what is it doing?

##### **Geohot** [[00:15:58](https://www.youtube.com/watch?v=swYfv-dheuc&t=958)]
I mean, I think it has more to do, I think the speed probably has more to do with whatever this gradient change is.
I think it's accumulating in FP32.

##### **Chenyu** [[00:16:10](https://www.youtube.com/watch?v=swYfv-dheuc&t=970)]
No.
So the only thing I changed is I changed the default type promotion behavior for sum to not do that.
That's my only change.
And we already know the float16 in, float16 out kernel is faster.

##### **Geohot** [[00:16:36](https://www.youtube.com/watch?v=swYfv-dheuc&t=996)]
Yeah, I'm OK.
I guess I don't really know why it's so different on red.
But I'm surprised that it works.
But maybe BERT's just really stable.

##### **Chenyu** [[00:16:44](https://www.youtube.com/watch?v=swYfv-dheuc&t=1004)]
Yeah, my theory is now people can do this float8, float16, float4 training probably because it just worked.

##### **Geohot** [[00:16:53](https://www.youtube.com/watch?v=swYfv-dheuc&t=1013)]
Oh.
Oh.
Of course it's faster on NVIDIA.
That's the thing NVIDIA nerfs.
Float16, float16 has double the flops.
Oh, yeah, yeah, yeah.
It's not nerfed from AMD.
It's not any faster.

##### **Chenyu** [[00:17:08](https://www.youtube.com/watch?v=swYfv-dheuc&t=1028)]
Yeah, so we know that thing is faster on the NVIDIA.
So make everything faster.
And the memory thing is our, it's Tinygrad's Issue.
So this just realize less.
Cool.
Yeah.
OK.
So let's move on to scheduler.

##### **Qazalin** [[00:17:36](https://www.youtube.com/watch?v=swYfv-dheuc&t=1056)]
So last week, I actually did some work on the emulator.
But when I got back to the scheduler work, I merged the removal of views from the kernel graph.
So no views there.
It's just also some sizes.

##### **Geohot** [[00:17:54](https://www.youtube.com/watch?v=swYfv-dheuc&t=1074)]
Great.
Let me check it.

##### **Qazalin** [[00:17:58](https://www.youtube.com/watch?v=swYfv-dheuc&t=1078)]
You can check it.
There's no views.

##### **Geohot** [[00:17:59](https://www.youtube.com/watch?v=swYfv-dheuc&t=1079)]
Sorry, go ahead.
I'll listen.

##### **Qazalin** [[00:18:02](https://www.youtube.com/watch?v=swYfv-dheuc&t=1082)]
Yeah, copy is still a kernel.
I understand why you want it not to be, but it's like the scheduler sort of treats copy as a kernel too because of how assign changes the dependencies.
So copy is sort of like a kernel.

##### **Geohot** [[00:18:21](https://www.youtube.com/watch?v=swYfv-dheuc&t=1101)]
I'm okay with copy being a kernel.
I'm okay with it.
It kind of, it is a kernel.
It's just a kernel that runs on special hardware.
It's totally fine to keep the kernel.

##### **Qazalin** [[00:18:34](https://www.youtube.com/watch?v=swYfv-dheuc&t=1114)]
Now the big thing I'm working on is refactoring the grouper.
So between the tensor simplifier and the kernel map creation, we still have this middleware that's deciding what things to realize.
That's where all the infamous realize before expand and stuff like that exists.
I'm experimenting with moving all those decisions to a pattern matcher that looks something like push the views towards the children or the parents, otherwise inserts contiguous.
Then what the kernel rewrite does is just look at the contiguous, and if you see a contiguous, make it a kernel.

##### **Geohot** [[00:19:23](https://www.youtube.com/watch?v=swYfv-dheuc&t=1163)]
I think that's largely right, yeah.

##### **Qazalin** [[00:19:27](https://www.youtube.com/watch?v=swYfv-dheuc&t=1167)]
The problem is you need to have two stages of graph rewrite.
You need to have one stage that pushes it to parents, and then one stage to push it to children.
And maintaining the map and just dabbling with the dictionaries, you have two dictionaries at that point.
Merging those dictionaries, it makes it really hard to reason about.
I'll try to figure out the simple ways to do it.

##### **Geohot** [[00:19:53](https://www.youtube.com/watch?v=swYfv-dheuc&t=1193)]
Can we do multi-output first?

##### **Qazalin** [[00:19:56](https://www.youtube.com/watch?v=swYfv-dheuc&t=1196)]
Multi-output first.
Sure.
I mean, I'm way more interested in this because this is going to get us BERT speed.
But I can't do multi-output too.

##### **Geohot** [[00:20:11](https://www.youtube.com/watch?v=swYfv-dheuc&t=1211)]
Wait.
Multi-output should get us speed too.

##### **Qazalin** [[00:20:20](https://www.youtube.com/watch?v=swYfv-dheuc&t=1220)]
Maybe.
I profiled BERT again.
It's mostly just realizing things that we should never realize.

##### **Geohot** [[00:20:32](https://www.youtube.com/watch?v=swYfv-dheuc&t=1232)]
Multi-output's also a regression, which is why I'm like, unless multi-output will become easier in the future, it should probably be done first.
But if you think that it's going to be a lot easier to do multi-output once this is done, then fine.

##### **Qazalin** [[00:20:48](https://www.youtube.com/watch?v=swYfv-dheuc&t=1248)]
Yeah, I think it's going to be easier.
I tried multi-output, and it's like, okay, I need another grouper now, and it's like...
Maybe there's a better way to do this that requires a grouper.

##### **Geohot** [[00:21:05](https://www.youtube.com/watch?v=swYfv-dheuc&t=1265)]
So what you're saying you want to do, basically, I'm looking at the MNIST model now.
What you're saying you want to do, basically, is insert contiguouses and push contiguouses in the graph.

##### **Qazalin** [[00:21:17](https://www.youtube.com/watch?v=swYfv-dheuc&t=1277)]
Push views in the graph, and whenever you can't push a view, insert a contiguous.

##### **Geohot** [[00:21:23](https://www.youtube.com/watch?v=swYfv-dheuc&t=1283)]
That makes sense, yeah.
I mean, it can be two passes, too.
You can have a left and right one, the same as before.

##### **Qazalin** [[00:21:33](https://www.youtube.com/watch?v=swYfv-dheuc&t=1293)]
Yeah, of course.
It's two passes.
Otherwise, it's an infinite loop.
One pushes it to right, one pushes it to left.
You never resolve anything.
But yeah.
So you can imagine it's kind of like the final expression.
If you have an add and then you have an expand, you have a child that uses an expanded version of the add.
And one child that doesn't.
If you push that expand over before the add, now if you visit the kernel, it has two ads in the graph.
So before it had one add, and it has two adds.
So it clearly describes the trade-off that we're making in the scheduler between realizing something or recomputing that thing.
I like this style.
It's tricky in all cases to implement, but I think it's the future.
This is going to take me like two weeks.
It's hard.

##### **Geohot** [[00:22:31](https://www.youtube.com/watch?v=swYfv-dheuc&t=1351)]
So there'll be, if you want to split it, there'd be an add before the contiguous and an add after the contiguous.

##### **Qazalin** [[00:22:39](https://www.youtube.com/watch?v=swYfv-dheuc&t=1359)]
You basically have two versions of the add.
You have one version of the add that loads in the buffer input, and you have one version of the add that's just the normal add.
It's like views only exist on the edges, which in this case means on a buffer or in a const.
Views never exist in an add.
When you visit the kernel creation right now, there are views in the middle of the graph.
There shouldn't be any.

##### **Geohot** [[00:23:10](https://www.youtube.com/watch?v=swYfv-dheuc&t=1390)]
In fact, you can do the contiguous insertion as a separate thing, and then you could make the create kernel be a context-free rewrite if you want that as an intermediate step.
Do you see what I mean by that?

##### **Qazalin** [[00:23:36](https://www.youtube.com/watch?v=swYfv-dheuc&t=1416)]
No.

##### **Geohot** [[00:23:40](https://www.youtube.com/watch?v=swYfv-dheuc&t=1420)]
So right now, the thing on schedule, the thing called create kernels.
Create kernels is taking in as a context this thing called kernel context.
But you could imagine splitting this into two different things, and this might be worthwhile to do as a first step.
You're going to want to use kernel context to insert the contiguouses.
And then you're going to want to have the kernel graph be separate.
And then you can basically like, you want to push the views in the big graph.
This also gets rid of all those stupid schedules where you're like pushing the schedules everywhere.
That's basically what you want, right?

##### **Qazalin** [[00:24:32](https://www.youtube.com/watch?v=swYfv-dheuc&t=1472)]
I want a framework for you guys to go in the scheduler.
And if you see a realize that's dumb, you can change that with a rule.
Right now, you can't.

##### **Geohot** [[00:24:44](https://www.youtube.com/watch?v=swYfv-dheuc&t=1484)]
Great.
I think you're on the right track.

##### **Qazalin** [[00:24:52](https://www.youtube.com/watch?v=swYfv-dheuc&t=1492)]
Maybe a bigger fracture will make everything easy.

##### **Chenyu** [[00:24:58](https://www.youtube.com/watch?v=swYfv-dheuc&t=1498)]
Oh, do you know what's happening for the random and JIT thing?
So I don't think it's affecting BERT.
I tried realizing everything before the jitting step.
I don't see anything obviously different.
So I don't think that's affecting the BERT now.
But having some tests or cases that the JIT silently behavior differently, especially for random, is very annoying.

##### **Qazalin** [[00:25:34](https://www.youtube.com/watch?v=swYfv-dheuc&t=1534)]
It is very annoying.
Yeah, I tried to read jit.py.
I can't read that code.
But what I could find based on printing stuff and the behavior, if you do a copy on the RAND, the JIT sort of realizes that, hey, this thing is a parameter.
And in the zero pass, realizes that tensor.
realizes the seed tensor, and then you move on.
Because basically like the bug, the root cause of the bug is that it's not realizing the seed.
And when you don't realize the seed, the seed plus one assign increment is not actually an assign, it's a replace.
If it's a replace and you put that replace in the JIT, of course that's going to be wrong because the buffer is the same.
So the seed ends up being the same across every single JIT run.
Sometimes it's just like that seed.
Sometimes it doesn't.

##### **Chenyu** [[00:26:35](https://www.youtube.com/watch?v=swYfv-dheuc&t=1595)]
If it's just that, is it fine if we say always realize the first one, the 0, or the seed?

##### **Qazalin** [[00:26:46](https://www.youtube.com/watch?v=swYfv-dheuc&t=1606)]
Yeah, you can insert a contiguous in tensor.py to do that.
I actually did the diff run.
It was mostly the same.
Stable diffusion XL creates a lot more kernels because you have a contiguous in there.

##### **Chenyu** [[00:27:07](https://www.youtube.com/watch?v=swYfv-dheuc&t=1627)]
Let's see.
Yeah, so this behavior apparently is a pretty bad regression.
So if there is a way that we can either fix the behavior, maybe with performance regression, or we at least assert if this is happening, I think it would be helpful.
Asserting seems more difficult.
So if you say you have a fix, that kind of fix list, I think we can start with that.

##### **Qazalin** [[00:27:38](https://www.youtube.com/watch?v=swYfv-dheuc&t=1658)]
It's a workaround.
I'm not fine with it.
I don't know.
I'll look into it.
But it's more like a workaround.
Just insert a continuous.

##### **Chenyu** [[00:27:47](https://www.youtube.com/watch?v=swYfv-dheuc&t=1667)]
Yeah, I understand.

##### **Qazalin** [[00:27:48](https://www.youtube.com/watch?v=swYfv-dheuc&t=1668)]
We really have to understand the JIT and fix it in the JIT.

##### **Chenyu** [[00:28:02](https://www.youtube.com/watch?v=swYfv-dheuc&t=1682)]
OK.
Sounds good.
Scheduler.
ONNX, where are we on ONNX?
Oh, I think there's a PR that I asked for the dry run flag, and I saw the PR for dry run.
I will test this later today.
True float16 sounds good.

##### **Chenyu** [[00:28:40](https://www.youtube.com/watch?v=swYfv-dheuc&t=1720)]
I think test should be whatever the model is using.
So for now, we have been using float32 for those.
If inputs specify float16, we should use float16.
And if it has any discrepancy between our implementation to our next runtime, we want to know if it's a bug or it's just numerical issues.
I would test the script to test models with dry run and with full download everything.
And if that's merged, then that one is yours.
Cool.
OK.

##### **Chenyu** [[00:29:31](https://www.youtube.com/watch?v=swYfv-dheuc&t=1771)]
Next, WebGPU.
We merge everything TinyChat and bounty gives to Hooved.
You want to say something?

##### **Hooved** [[00:29:45](https://www.youtube.com/watch?v=swYfv-dheuc&t=1785)]
Sure.
Yeah, thanks.
Glad to have finished that.
I'm starting to work on the WebGPU export model refactor.
What I want that to do is to work well with the Torch frontend so we can get the most users and have the most value there.
And also, I want to be able to eventually articulate
why I would use this over the ONNX web runtime.
So I'm just doing research on that stuff.
And I checked in with WPMed, and he's really busy, but he encouraged me to push forward and open a PR.
So I'm working on that, and I'm happy to keep him in the loop and try to incorporate all his feedback, et cetera.

##### **Chenyu** [[00:30:45](https://www.youtube.com/watch?v=swYfv-dheuc&t=1845)]
Use TinyGray instead of ONNX Runtime, because TinyGray will be faster.

##### **Hooved** [[00:30:50](https://www.youtube.com/watch?v=swYfv-dheuc&t=1850)]
Right, right.
No, I believe that.
I think it'll be faster and lighter weight.
But there could be other wins as well in terms of supporting more models, et cetera.

##### **Geohot** [[00:31:04](https://www.youtube.com/watch?v=swYfv-dheuc&t=1864)]
Oh, I wasn't aware they had ONNX Runtime Web.
Is it good?

##### **Hooved** [[00:31:10](https://www.youtube.com/watch?v=swYfv-dheuc&t=1870)]
That's what I'm researching.
That's what I'm trying to understand.
I mean, I looked at some of their demos.
Microsoft's GitHub repo has some, or they have GitHub pages with demos up.
I'm not sure how good it is.

##### **Chenyu** [[00:31:28](https://www.youtube.com/watch?v=swYfv-dheuc&t=1888)]
OK.
I think.
So next is torch frontend.

##### **Chenyu** [[00:31:41](https://www.youtube.com/watch?v=swYfv-dheuc&t=1901)]
I don't know if we have a person here.
So there are a few open bounties.
There's one for test ops.
The author gets almost everything asked except one, and he mentioned
needs to change something for the last one to pass.
And there are many ways to do that.
He was not sure which one to go for.
And I basically come and says, you pick one.
And you remove the all true in test, making sure it's passing CI.
Then we can decide.
Well, that was four days ago.
I haven't seen an update after that.
uh several other ones for training for like nano gpt other training and multi gpu training uh so one is from b1tg you want to say something
I don't know if you can say anything.

##### **Geohot** [[00:32:58](https://www.youtube.com/watch?v=swYfv-dheuc&t=1978)]
B1tg is a speaker, I know he's had some issues with the Discord thing before.

##### **Chenyu** [[00:33:05](https://www.youtube.com/watch?v=swYfv-dheuc&t=1985)]
OK.

##### **B1tg** [[00:33:08](https://www.youtube.com/watch?v=swYfv-dheuc&t=1988)]
Oh, the.
Oh, there we go.
The memory leak, the.
comment today that he fired a PR to fix the VRAM leak.
It seems to realize all the tensors in the optimizer, which didn't seem to be the solution.
And that's why I was working on the COMGR PR, not working on the nanoGPT stuff.

##### **Geohot** [[00:33:55](https://www.youtube.com/watch?v=swYfv-dheuc&t=2035)]
For the realize the all tensors thing, yeah, we can't really merge that.
We have to find some better way to do this.
In some ways, this is a TinyGrad problem.
TinyGrad should kind of have a depth limit, where there is a point where you can no longer create tensors in a virtual world, and the laziness does eventually resolve at some point.
We should look at what the patterns are that are explicitly causing problems here.
because realizing all the tensors is not a solution, unfortunately.
Though I like tocubed's other PR on this, the in-place operations on views.
Is that good to merge?
We can talk also about the LLVM.
I think that's getting close.

##### **B1tg** [[00:35:09](https://www.youtube.com/watch?v=swYfv-dheuc&t=2109)]
Are you talking about the COMGR PR?

##### **Geohot** [[00:35:14](https://www.youtube.com/watch?v=swYfv-dheuc&t=2114)]
Yes, yes.

##### **B1tg** [[00:35:14](https://www.youtube.com/watch?v=swYfv-dheuc&t=2114)]
last week the renew box got fixed and i removed the lld sub process now we directly load the relocatable uf and i did some clean up to make it simple i guess we can merge it this week is is there any

##### **Geohot** [[00:35:46](https://www.youtube.com/watch?v=swYfv-dheuc&t=2146)]
I think so, yeah.
The only things are the render cast function looks very complex.
AFN is being removed from flags.
Is there anything that you can separate out into a different PR?
There's a mock GPU change here.
Is there anything that's not the feature that's a prerequisite?

##### **Geohot** [[00:36:18](https://www.youtube.com/watch?v=swYfv-dheuc&t=2178)]
I think maybe some of these, like I see also asm-parser is removed from component.
Whenever there's changes like this, they really have to be in separate PRs.
Because I mean, like the asm-parser thing looks just unintentional.
And it looks like that's going to introduce a subtle bug when someone tries to use
And you have a white space change on Ops LLVM.
So yeah, before we can really review this PR, and this is universal for everybody contributing to TinyGrad, read your diff three times before you want me to review it.
If it has random white space changes in it, it's not ready to be reviewed.

##### **B1tg** [[00:37:06](https://www.youtube.com/watch?v=swYfv-dheuc&t=2226)]
OK, I know.

##### **Chenyu** [[00:37:18](https://www.youtube.com/watch?v=swYfv-dheuc&t=2238)]
Speaking of memory leak, Arrow opened an issue saying QCOM driver is having memory leak.
Do we know anything about that?

##### **Geohot** [[00:37:30](https://www.youtube.com/watch?v=swYfv-dheuc&t=2250)]
Let's see what he's saying.
Yeah, it seems like something we should fix.
Comma team should fix that.
Comma team should fix that.

##### **Chenyu** [[00:38:00](https://www.youtube.com/watch?v=swYfv-dheuc&t=2280)]
Are you sure?
OK, I don't know.

##### **Geohot** [[00:38:04](https://www.youtube.com/watch?v=swYfv-dheuc&t=2284)]
No, we should fix that.
We should fix that.
But who's going to do it?

##### **Chenyu** [[00:38:11](https://www.youtube.com/watch?v=swYfv-dheuc&t=2291)]
OK.
Retinanet?

##### **Flata** [[00:38:32](https://www.youtube.com/watch?v=swYfv-dheuc&t=2312)]
So for my update, I think the correctness runs are fully done in float 32.
So what I'm trying to work on now is to make sure that it works on float 16.
So that should definitely put us in the sub 24 hour time and hopefully faster than that.
So that's what I'm currently working on.
I think after that, I'll also start taking a look at the eval script, because I know topk just got recently merged, and that's one of the things that the eval script for RetinaNet uses.
So hopefully, if I rewrite everything there in TinyGrad, we can get that as well, and it should be much faster too.

##### **Chenyu** [[00:39:11](https://www.youtube.com/watch?v=swYfv-dheuc&t=2351)]
Depends on how big your K is.
Yes, try that.

##### **Flata** [[00:39:16](https://www.youtube.com/watch?v=swYfv-dheuc&t=2356)]
I think it's 1,000, so yeah, that will definitely be pretty big.

##### **Chenyu** [[00:39:23](https://www.youtube.com/watch?v=swYfv-dheuc&t=2363)]
OK, let's see how that goes.
Oh, I didn't know it was in float 32.
If that's OK, 70 tflops doesn't seem too bad.
I don't know, but we should do this in float 16.
It would be a lot faster.

##### **Flata** [[00:39:40](https://www.youtube.com/watch?v=swYfv-dheuc&t=2380)]
Sounds good.

##### **Chenyu** [[00:39:44](https://www.youtube.com/watch?v=swYfv-dheuc&t=2384)]
OK.
other bounties.
Ignaciosica, you want to say something?
I didn't see your change, so I don't know if you are working on anything.
OK, I see you have a big block.

##### **Ignaciosica** [[00:40:00](https://www.youtube.com/watch?v=swYfv-dheuc&t=2400)]
Yes, I write it because it's easier.
Sorry.

##### **Chenyu** [[00:40:06](https://www.youtube.com/watch?v=swYfv-dheuc&t=2406)]
Oh, you want to talk about this?

##### **Ignaciosica** [[00:40:10](https://www.youtube.com/watch?v=swYfv-dheuc&t=2410)]
Yes, I found it trickier, the refactor I was working on, than I expected, mainly because some patterns didn't fold because of the load.
And I have to fix those.
And the way of fixing it, I don't like it how I'm doing it right now, because it's like being careful the pattern fails, but also careful that if it fails and it removes the define acc, I also have to remove the load.
And it's like being very picky about that.
And I don't like it.
So I'm still working on doing it more cleanly.
I hoped to finish it by today, but I couldn't make it happen.
So sorry about that.

##### **Geohot** [[00:41:07](https://www.youtube.com/watch?v=swYfv-dheuc&t=2467)]
No worries.
I also just casually, when I was working on the FastAMD multiply, it seems like TC equals 3 is broken, and I'm curious why.

##### **Ignaciosica** [[00:41:24](https://www.youtube.com/watch?v=swYfv-dheuc&t=2484)]
I'll take a look.

##### **Geohot** [[00:41:26](https://www.youtube.com/watch?v=swYfv-dheuc&t=2486)]
It works in the test.
It works in the test, but it gives wrong answers for bigger matrices.

##### **Ignaciosica** [[00:41:38](https://www.youtube.com/watch?v=swYfv-dheuc&t=2498)]
Sorry, go ahead.

##### **Geohot** [[00:41:41](https://www.youtube.com/watch?v=swYfv-dheuc&t=2501)]
I tried test gemm.
Test gemm was just 4096 by 4096 with TC equals 3 on Mac, and it gave wrong answers.
I don't think it should.

##### **Ignaciosica** [[00:41:50](https://www.youtube.com/watch?v=swYfv-dheuc&t=2510)]
No, TC equals 3 on Mac.
For what I tested, it didn't work for matrices bigger than like 64 by 64, because it's a local run out of local.

##### **Geohot** [[00:42:04](https://www.youtube.com/watch?v=swYfv-dheuc&t=2524)]
Oh, because it runs out of local?

##### **Ignaciosica** [[00:42:08](https://www.youtube.com/watch?v=swYfv-dheuc&t=2528)]
Yes, I think.
Like, I only could do it with small matrices.
That's why I

##### **Geohot** [[00:42:22](https://www.youtube.com/watch?v=swYfv-dheuc&t=2542)]
TC equals 3 is the closest thing we have to what's the stuff that's going to make things really fast.
Oh, yeah, I get compiler encountered an internal error.
So maybe this is just locals.
Is it like a crazy amount of locals?

##### **Ignaciosica** [[00:42:47](https://www.youtube.com/watch?v=swYfv-dheuc&t=2567)]
Yes.
If you see the kernel.

##### **Geohot** [[00:42:52](https://www.youtube.com/watch?v=swYfv-dheuc&t=2572)]
Should it be a crazy amount of locals?
Oh, yeah.
Wow, it's really, really big.
Should it be that big?
It seems like a bug.
Ah, it seems like a bug.

##### **Ignaciosica** [[00:43:06](https://www.youtube.com/watch?v=swYfv-dheuc&t=2586)]
I can take a look into it.
Yes, I will.

##### **Geohot** [[00:43:13](https://www.youtube.com/watch?v=swYfv-dheuc&t=2593)]
I'll put $200 on that.

##### **Ignaciosica** [[00:43:14](https://www.youtube.com/watch?v=swYfv-dheuc&t=2594)]
To fix the TC=3?
OK.

##### **Geohot** [[00:43:20](https://www.youtube.com/watch?v=swYfv-dheuc&t=2600)]
Yeah, yeah, yeah.
Cool.
Sorry, do you have something else?

##### **Ignaciosica** [[00:43:38](https://www.youtube.com/watch?v=swYfv-dheuc&t=2618)]
No, that's it.

##### **Chenyu** [[00:43:50](https://www.youtube.com/watch?v=swYfv-dheuc&t=2630)]
Okay, anything else?
So I think there are, we're trying to do the Boolean indexing.
I think we just accept if it's data dependent, we have a realized somewhere and have a graph break.

##### **Geohot** [[00:44:23](https://www.youtube.com/watch?v=swYfv-dheuc&t=2663)]
The Boolean, which is the Boolean indexing?

##### **Chenyu** [[00:44:26](https://www.youtube.com/watch?v=swYfv-dheuc&t=2666)]
So you index like tensor dot non-zero, basically.

##### **Geohot** [[00:44:31](https://www.youtube.com/watch?v=swYfv-dheuc&t=2671)]
Yeah, yeah, yeah.
Anything with dependent shapes is going to have a graph break.
That's fine.
Yeah, I'm OK with that.
Anything that's variable shaped from the output, that's just not supported by TinyGrad.
And you shouldn't be doing that in any neural network framework.

##### **Chenyu** [[00:45:03](https://www.youtube.com/watch?v=swYfv-dheuc&t=2703)]
OK.
So there is an update for the x86 backend.
The author said it's 20% slower than O0, 3x slower than O1.

##### **Geohot** [[00:45:16](https://www.youtube.com/watch?v=swYfv-dheuc&t=2716)]
How do we get it faster than O0?
That's kind of my requirement for that.

##### **Chenyu** [[00:45:27](https://www.youtube.com/watch?v=swYfv-dheuc&t=2727)]
I think the author is aware of that.
OK.
That's all of the agenda.
Anything else?

##### **Geohot** [[00:45:48](https://www.youtube.com/watch?v=swYfv-dheuc&t=2748)]
No, I think it's just we're going to be nice to AMD now.
But this is the thing.
It's not like they just sent me those boxes.
It's not like I signed.
I signed literally nothing.
They sent me a FedEx track number.
We got some boxes.
This is how things should work.
This is the new way of doing business.
This is the future.
And yeah, let's try to make them happy that they sent them to us.
I think DeepSeek.
DeepSeek's a good one.

##### **Chenyu** [[00:46:26](https://www.youtube.com/watch?v=swYfv-dheuc&t=2786)]
Sounds good.
Do we need to do anything for that, or we just wait until the box is set up and working on the JIT MOE and see where we are on stuff?

##### **Geohot** [[00:46:42](https://www.youtube.com/watch?v=swYfv-dheuc&t=2802)]
Yeah.
I mean, there's a whole bunch of aspects to this.
There's JIT-ing MOE.
After we get UUVN's current bounty done, I think I'll put up bounties for the driver.
We're going to do the driver.
We're going to do the runtime.
We'll get some people in here access to the boxes.
And then, yeah, then we just have to find all the bottlenecks that make large LLM batch size one slow.

##### **Chenyu** [[00:47:19](https://www.youtube.com/watch?v=swYfv-dheuc&t=2839)]
That concludes this meeting.
Thanks everyone.
See you next week.
