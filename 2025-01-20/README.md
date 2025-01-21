# 2025-01-20 Meeting

### Meeting Agenda

**Time:** 9:30 AM San Diego time (PST)
- company update, new meeting time 6am Monday San Diego time starting next week
- gradient, new multi, cloud machines
- scheduler
- driver
- mlperf bert, softmax, attention
- tensor cores
- onnx
- bounties: int64 merged, webgpu f16, retinanet, whisper, graph rewrite?, x86?, BLAKE3?, some new bounties!

### Audio

[Youtube Link](https://www.youtube.com/watch?v=Bm_blXgmlLo)

### Highlights

- Next week's meeting will be 6:00 AM San Diego time. (3.5 hours earlier)
- [Need for speed](#need-for-speed) Call for anyone who can improve speed of anything in TinyGrad. (including python level, tensor level, compilation level or kernel level) This year is the year of speed.
- [Newly added bounties](#briefing-of-newly-added-bounties) Bunch of bounties up for grabs. Read the transcript for details.
- [Tenstorrent](#tenstorrent) Two new Tenstorrent bounties both worth $1000.
- [Blake3](#blake3) Request for updates on PR before next week, else bounty may be unlocked. Need benchmarks.
- For developers using Tinygrad, feel free to post about your experiences and difficulties when using Tinygrad. We want to provide tools and resources to make Tinygrad great for developers.

### Transcript

**Geohot** [[00:00:01](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=1)]  
Company update.  
We are sold out of green and pro tiny boxes.  
So we placed a big order for 4090s last year, and I was scared for a bit that it was too many 4090s.  
It was not too many 4090s.  
Now we've learned that it was too few 4090s.  
So yeah, greens and pros are out of stock.  
I'm not sure.  
We might have a few more to sell.  
As we go through, like, we have some broken 4090s we have to get RMA'd.  
But it's unlikely they're going to come back into stock in a big way since 4090s aren't made anymore.  
We are planning stuff for the 5090s.  
So, yeah, you guys will see.  
We'll buy the 5090 this time.  
Hopefully.  
Yeah, no, we're buying, hopefully we're buying enough 5090s.  
Though I will say, like, the 5090, the performance boost is going to be proportional to the price increase.  
So it's unfortunate, but that's how it is.  
It's the same process.  
There's not really a way to gain.  
That chip's also super expensive to make.  
They made a huge chip with all those GDDR7 PHYs.  
Like, that's just an expensive tape out.  
And since it's a 512-bit bus, they can't disable any of them, so the yields probably aren't high.  
I don't even know what they're going to do with the ones that don't yield.  
Oh, that'll be interesting.  
That's the card I really want.  
We also stood up the beginning of the cloud.  
We have five tiny box reds.  
It's going to be nine.  
I was playing with the networking switch last night, so we're going to have...  
a big cluster of AMD GPUs.  

**Chenyu** [[00:01:52](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=112)]  
We'll have a new meeting time starting next week for  
maybe about like two months, we will shift to 6 a.m.  
So that would be three and a half earlier than our usual time.  
We might adjust and see how things go.  
If you are in this meeting or if you have the talk permission and this time doesn't really work for you, post somewhere and we can discuss.  

**Geohot** [[00:02:23](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=143)]  
Yeah, we got to cover America, Asia, and Europe.  
It's hard to find a time that does that.  
Tiny Corp is going to be in Hong Kong.  
Get a little office there.  
Same thing we did last year.  

**Chenyu** [[00:02:37](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=157)]  
Cool.  
We'll move onto your stuff.  

**Geohot** [[00:02:43](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=163)]  
Cool.  
Yeah, so Gradient is blocked on new multi.  
New multi is not blocked on anything.  
I think I'm making pretty good progress on that.  
This basically takes multi lazy buffer and turns it into a UOP.  
So it's UOP multi where the sources are the individual lazy buffers.  
And then you can do something that looks a lot like the way we push unroll through the graph with multi to expand it to a full  
You know, expand it.  
Basically, if you're on six devices, it's 6x is the graph.  
Someday, maybe we could move multi after the scheduler, which will get us speedups.  
But for now, it's just basically going to be the same thing.  
But it's going to be uops.  
And then we can differentiate through it.  
And then gradient will work.  
Because right now, gradient's broken.  
Because it can't call the...  
Like, it can't call the UOP methods, and the different UOP methods are on multi-lazy buffer now.  
So that needs to be rewritten in a rewrite rule, and that kind of continues in the UOP-ification of everything.  
We move things from being done instantly to being specified and then transformed.  
So the specification transform thing is slower, but it's much easier to reason about.  
If you guys haven't tried Viz, it's really beautiful.  
Viz equals one.  
VIZ.  

**Chenyu** [[00:04:05](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=245)]  
Yeah, and also to prepare or kind of making new multi easier, I disabled all the uneven sharding.  
So as a result, we currently don't have Llama running on 6 GPU because it doesn't shard evenly.  
And I also disabled the 70B for now.  
I will find a way to add it back later with the new multi stuff, probably with some padding.  
But the idea is we want  
We want the UOPs and kernels to be the same on each device.  

**Geohot** [[00:04:42](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=282)]  
Yeah, and then the kernels can take in an argument, which says which GPU they're in.  
But you never want, basically, to have different kernels running on the devices, because one kernel is always faster, and you're always going to be bound by the slower one.  
So yeah, it should be the same kernel on both devices.  
Yeah, the cloud machines too.  
You know, there's been great progress on the AM driver.  
We're moving sort of toward where these machines are just basically going to be dumb boxes with GPUs in them.  
And we'll move all of the scheduling, all of the optimization stuff onto a gateway machine.  
On this gateway machine, we'll just drive the GPUs, and this is how we're going to get to, not next MLPerf, but the MLPerf after, training on a cluster.  

**Chenyu & Geohot** [[00:05:30](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=330)]  
We will put 54 in...  
numbers of accelerators.  
Yeah, yeah, well, 36.  
I think we're going to turn on 6.  
I think that the cloud's going to be nine machines, but we're not going to be able to use them all.  
I think 6 is the most we're going to be able to use as well.  
OK, 36 is nice.  
36 is good.  
OK.  

**Chenyu** [[00:05:50](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=350)]  
Sounds good.  
We can move on to scheduler.  

**Qazalin** [[00:05:56](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=356)]  
So I have two simplification diffs ready.  
The problem that I have run across is that it's just really hard to add the optimizations back with also doing the simplifications at the same time.  
So the first one is delete forced_realize.  
This makes Llama 4 GPU slower.  
But I think it's the right path to move forward, because it's really hard to move forward with anything if we have that force-realized set existing.  
The same goes for simplified tensors, [8580](https://github.com/tinygrad/tinygrad/pull/8580).  
This one,  
It's a simplification bin, but it's a regression in performance.  
Again, I'll leave the judgment to you if you want to.  

**Geohot** [[00:06:58](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=418)]  
So where do these things come down to.  
Okay, we can't regress performance on OpenPilot.  
That's the most important thing that we keep performance on.  
So if they're regressing performance on OpenPilot, I think we've got to fix that.  
Performance regressions elsewhere, it comes down to why they're happening.  
If they're happening because fundamentally we can't express something that we want to express, then maybe it's not good.  
But if it comes down to something like cast before view, which was kind of arbitrary to begin with, then, yeah, whatever.  
So, forced_realized, is it still making a crazy number of kernels for OpenPilot?  

**Qazalin** [[00:07:40](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=460)]  
I think one kernel to OpenPilot.  

**Geohot & Chenyu** [[00:07:44](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=464)]  
Oh, one kernel.  
A single one.  
Probably find them.  
Is it slower?  
Or is it basically the same?  
I don't think you can tell.  
You cannot tell from the current dashboard.  
We've got to fix that.  
The compile one tells you, I think.  
Oh, does that one even work anymore?  
No.  
So now you can check the  
Let me read this.  
OK, so allowed kernel count goes up one.  
Allowed image reads go up one.  
This arange fusion no longer works.  

**Qazalin** [[00:08:26](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=506)]  
It requires the contiguous.  
Has a contiguous that is just, it requires force to realize for the hack to work.  
Otherwise, it doesn't work.  

**Geohot** [[00:08:40](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=520)]  
uh yeah i think we merged this i think this is good uh yeah forget force realize this is force realize is awful um sold merged uh and then yeah the other one i don't understand why that allowed read image goes way down on [8580](https://github.com/tinygrad/tinygrad/pull/8580).  

**Qazalin** [[00:09:04](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=544)]  
I don't either.  
I just literally apply the symbolic symbol on the tensors.  
Because image Dtype is like, if you have an image F with different shapes, it doesn't fold that, right?  
But right now in master, what we have is that we first rewrite that image Dtype to be the float32.  
So a float32, cast float32 just does fold.  
But image is not...  

**Geohot** [[00:09:33](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=573)]  
Do you have a benchmark run on here?  
Let's just see if OpenPilot gets way worse.  
Just, yeah, maybe make [8580](https://github.com/tinygrad/tinygrad/pull/8580) not draft, do a benchmark run, and we'll check it out.  
Again, I'm tempted to merge it.  
I first realized I just had to go.  
This one... Also, what I'm doing with multi, I'm hoping I can kind of merge that with something like what you're doing with RevTensorMap.  
If you see what I'm doing with multi, I do two passes of tensor rewriting.  
I abstracted that out.  
That's already in master.  
I don't know.  
But yeah, I think look into why that allowed read image thing is happening.  
And if it's kind of benign, then I think we merge that one too.  

**Qazalin** [[00:10:22](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=622)]  
Yeah, the problem is that it's not benign.  
It's actually making openpilot bad.  
So they can work on making it good.  

**Geohot** [[00:10:30](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=630)]  
But the force realized one wasn't making it bad, right?  

**Qazalin** [[00:10:33](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=633)]  
No, it wasn't.  

**Geohot** [[00:10:34](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=634)]  
Yeah.  

**Qazalin** [[00:10:34](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=634)]  
Yeah.  
Okay.  
That seems image.  
Others the same.  

**Geohot** [[00:10:42](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=642)]  
Wait, sorry, say that again.  

**Qazalin** [[00:10:46](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=646)]  
This one is a big change for image.  
This the same pretty much for everyone that can have the PR on it basically is an op.  

**Geohot** [[00:10:58](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=658)]  
Yeah, just just  
Explain to me the change.  
And yeah, let's understand what's going on first.  
But again, I'm tempted to just push forward with this stuff.  

**Qazalin** [[00:11:12](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=672)]  
Cool.  
image.  
And then we have to, at some point, make them float once they are loaded.  
I don't fully understand this image thing either.  
So I have to understand it myself.  

**Geohot** [[00:11:28](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=688)]  
Okay, so what the image thing is, is like, let's say you do an expand on an image, right?  
You have an image that's the correct size for the underlying data, and then you do an expand.  
Now, if you do an expand, and then you like contiguous that expand, it can no longer be that image because it doesn't fit in the type.  
So that's when it has to be turned into float.  

**Qazalin** [[00:12:00](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=720)]  
So this tensor, tensor doesn't do that, right?  
The UOP that you're describing, if I visit, if I visit literal tensor, it's image.  

**Geohot** [[00:12:13](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=733)]  
Yeah, so the problem, the reason tensor can't do it is, well, tensor could certainly detect when you're doing that expand.  
But what if you do that expand and then you do a sum on the expanded axis?  
Now it fits an image again, so you want it to be an image again.  
Does that make sense?  

**Qazalin** [[00:12:40](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=760)]  
Okay.  
What's the approach?  
When should we rewrite that thing to float?  

**Geohot** [[00:12:45](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=765)]  
Well, the condition there makes sense.  
You want to rewrite it to float.  
Okay, so you want to rewrite it to float whenever you're trying to output to a buffer that it can't fit in.  
Whenever you're trying to actually realize and create and put in memory the buffer, if the image type's not appropriate, that's when it needs to be converted to float.  
Like if it doesn't work with that image type.  

**Qazalin** [[00:13:15](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=795)]  
If I have an image, like I cast, like let's say I have a float and then I cast to image, contiguous it, and then add to another image.  
Does the add output become image or is it a float?  

**Geohot** [[00:13:30](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=810)]  
If you're doing an add, which isn't going to change the shape, it's still an image.  
The only time it can't be an image is, or let's say you do like a shrink, right?  
You do a shrink and then you do a realize.  
Well, then it can't fit in the image anymore.  
If you read the condition, I think the condition for when it does that rewrite is pretty clear.  

**Qazalin** [[00:13:52](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=832)]  
That's not the only rewrite.  
There's also one thing that exists in the scheduler  

**Geohot** [[00:14:00](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=840)]  
Oh, the expand thing.  

**Qazalin** [[00:14:03](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=843)]  
No, no, like just an image becomes a float in the scheduler.  
That's the first step in scheduling.  
That has existed ever since like lazy was a thing.  
Yeah.  
Look at the thing, even in the recursive lazy op, there was dtype.base and you were initiating the lazy op.  
So it's like it's carried through to the day, and I don't really...   

**Geohot** [[00:14:33](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=873)]  
Okay, if you're still being bothered by that, I can look at it more.  
What you can maybe do, look at what I'm doing in multi with the tensor rewrite.  
You might be able to do that sort of thing for image too, like even before it goes to scheduling, just do a big rewrite of all the uops to make the image ones that can't be image, not image, and you can put casts around it.  

**Qazalin** [[00:14:54](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=894)]  
That's not the problem here.  
The problem is more like images were float before in the scheduler.  

**Geohot** [[00:15:07](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=907)]  
Yeah, OK.  
I don't think we're going to solve this right now.  
I don't think we can merge 8580 until there's not big regressions on OpenPilot.  
And I want to first spend time to understand exactly what it's changing.  
Because I don't even see that being touched.  
I don't even see the image thing being touched.  

**Qazalin** [[00:15:31](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=931)]  
Exactly.  
That's the problem, right?  
I don't change anything about image and image breaks.  

**Geohot** [[00:15:36](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=936)]  
Yeah, well, okay.  
So why is it happening?  
Maybe it's something stupid.  
Maybe it's not.  
I mean, I don't know.  
Does it still break if you don't remove movement ops?  
Which rule can you remove to make it not break?  
Like on 494, with the tensor map equals graph rewrite map, what happens if you put no rules there?  
Does image still break?  
But I think there's good progress here.  
I think just figure out what's going on, and we'll see there.  

**Chenyu** [[00:16:18](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=978)]  
Cool.  
Let's move on to driver.  

**Nimlgen** [[00:16:25](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=985)]  
Yes.  
So this week I spent optimizing AM.  
So now I think we reached the target.  
So it's just the cold boot now takes about two seconds and the warm boot is less than one second.  

**Geohot** [[00:16:50](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=1010)]  
And you got it less than a second!!  
Great!  

**Nimlgen** [[00:16:56](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=1016)]  
Um,  
So yeah, I also added locks, so I think now it's safe to use, like try to use for several users access the same device.  
Uh, yeah.  
So the next week, um, yeah, the next week I think I'm just going to move to USB driver.  
I still have some things to do.  
But yeah, I think I'll have time, and we'll move to USB driver.  

**Geohot** [[00:17:28](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=1048)]  
Great.  
I'm going to plug in.  
I have one more USB thing that I got.  
I'll plug it in today.  
It's a different RDNA3 GPU.  
But that shouldn't be a big problem, right?  
It's just like a cheaper RDNA3 GPU.  

**Nimlgen** [[00:17:44](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=1064)]  
Yeah, we'll see.  

**Geohot** [[00:17:45](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=1065)]  
Cool.  
But those other two USBs are still set up.  
I think this is a huge win if we get a full USB stack.  
I also want it to move away from the SCSI thing that that's using and use libUSB so that it works on Mac.  

**Nimlgen** [[00:18:10](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=1090)]  
Yeah, yeah.  
I mean, that's the first thing I'm going to do.  

**Geohot** [[00:18:14](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=1094)]  
Cool.  
Yeah, and I know it's working now, but it's slow.  
So there's the two chips.  
We only know how to do it on the 23 chip.  
There's also the 24 chip.  
I have some reason to believe that the 24 chip is better.  
Because the 24 chip actually does work with GPUs.  
It just requires USB 4 or Thunderbolt.  
But there's definitely ways to set up basically DMAs.  
Well, not DMAs, but to not just do one rewrite, to basically put a big thing on the bus.  
On the 24-hour chip, we just had to figure out how to do it.  
So, yeah, no, I see no reason why this shouldn't be... Cool.  
Yeah, great work, making it fast.  
uh i think we should also if you uh run ctrl c spam uh can it get into a bad state   

**Nimlgen** [[00:19:15](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=1155)]  
Not anymore i mean like yeah not anymore   

**Geohot** [[00:19:19](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=1159)]  
Do we have a fuzz tester for that   

**Nimlgen** [[00:19:22](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=1162)]  
Um okay not a fuzz tester but  
Yeah, okay, I'll edit but basically like the I just handle these Ctrl C operations.  

**Geohot** [[00:19:38](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=1178)]  
You're in Oh, no, but okay, what if I kill minus nine?  

**Nimlgen** [[00:19:41](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=1181)]  
Yeah, we'll see.  
Okay.  

**Geohot** [[00:19:51](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=1191)]  
Yeah, yeah.  
So handling control C isn't enough because you can't guarantee that that thing runs.  
If I kill minus nine, it's totally okay if it has to do a cold boot of the GPU after I do that, but it can't be in a bad state.  
It can't be in an unrecoverable state that requires like reboot or like some flag to be added.  
It always has to be able to recover no matter how much I...  
thrash this thing.  
This is what we criticize AMD for, and I think we can do a lot better.  
But the other thing, do we have the power and thermal management?  

**Nimlgen** [[00:20:40](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=1240)]  
Very primitive, I would say.  
We set only to the high clocks during boot up, and that's all what we do.  

**Geohot** [[00:20:48](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=1248)]  
The main thing I want to check, just like you can just check this one off, is after you do a good shutdown, how low does the power draw get?  
We should check that, because when nothing is running, if the last thing we used was an AM driver, I don't want the GPU to sit there and draw 100 watts when it should be drawing 15.  

**Nimlgen** [[00:21:15](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=1275)]  
Yeah, okay, I'll check that.  

**Geohot** [[00:21:18](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=1278)]  
We might even be able to do better than the real driver, because maybe we can turn the memory off.  

**Nimlgen** [[00:21:26](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=1286)]  
Uh-huh.  
So... Yeah, yeah, I mean, potentially we can do that.  
I mean, I've seen some flags to do that, definitely.  

**Geohot** [[00:21:37](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=1297)]  
Yeah, yeah, yeah, yeah.  
Unused... Like, yeah, after tinygrad turn off, low power draw is...  
as a target.  
And I think the, let me see what the normal driver uses.  
Yeah, so the GPUs are drawing about 20 watts at idle with the kernel driver.  
Cool.  
Yeah, great progress there.  

**Chenyu** [[00:22:21](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=1341)]  
Great.  
Next is BERT.  

**Chenyu** [[00:22:27](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=1347)]  
BERT is great and slow.  
So I think recently there are two directions.  
One is optimizing memories and the reset or the time between reset.  
George put in the free intermediate.  
I had the repro let's slow.  
I think Nimlgen was looking into let.  

**Geohot** [[00:22:52](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=1372)]  
Did I?  
Do you know if I did that wrong?  
Did I write a bug in that?  

**Nimlgen** [[00:22:59](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=1379)]  
I'm just looking.  
I think it's something related to the sub buffers because I see sub buffers like still had old addresses.  
Yeah.  
I had a patch for this.  
I need just to beta test it and find a small repro for this.  

**Geohot** [[00:23:19](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=1399)]  
Cool.  
Yeah, no, I didn't test sub-buffers.  
I guess I thought that would be OK, because I destroy the whole graph.  
But maybe, yeah.  
Yeah, I should try to test it.  

**Chenyu & Geohot** [[00:23:30](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=1411)]  
Yeah, and another is Softmax being tweaking or understand.  
So we are currently about 20% MFU, or I guess 22% MFU, and our target is like 50%.  
So one big difference is our attention in general, comparing to flash attention or our more fused version, we are a lot more memory bound on these reduces.  
The shorter term way to fix it is something more like cast before view or some of the intermediate buffer Dtype management, but that's not a very sustainable solution.  
I think for now, I will understand the impact really pinned down to these.  
And I made some small optimizations and adjustments to make it slightly faster.  
I also have a version that can run a bigger batch size that's like 10% faster.  
I'm testing that.  
We might need to retune some numbers for bigger batch size.  
I think for softmax, the goal is to write that in one kernel, that's kind of a scheduler change we need to make because there's a max and there's a normalization after you subtract the max.  
That's now, I think, three kernels.  
attention is adding one matmul before and one matmul after this.  
So there is a bounty for flash attention, but we really need to make some max one kernel first.  
And so I think making one kernel is probably the same as the old making the back-to-back  
Mean and standard deviation?  
Yeah, so mean and standard deviation one kernel.  
That's probably the same thing.  
And I know there's an optimization that can make it like two paths instead of three paths.  
That's the online softmax.  
Not sure if there's a clean way to write this, but I think the first step is probably to just squeeze those all into one kernel.  
Do you think, if I, you want me to spend some time thinking about the argmax thing?  
I think that'll help you.  
Oh, sure.  
So I think that thing is tied to ...  
So for now, to do argmax, we also need to do two paths.  
The first pass is finding the max, and the second pass is finding the index that's that.  
So I think that's similar in concept, because basically, to do one path on this, we want to loop over a range.  
while tracking the max property on one entry, but we keep the other entry and eventually output the other entry and not the max entry.  
So I think that's similar.  
I kind of see how to do it with kind of like a, it's like a gated store, really.  
I mean, you have like a define ACC and you have like a gated store, and then that store gate is the max.  
Yeah, but how do you know... This is, like, sequential.  
It's not sequential.  
It fits in UOPs.  
I don't exactly know how we're going to do the transformation to UOPs.  
But okay, so you have this, like, is this the max, which is a bool.  
And then that's your gate for a store.  
And then the store, instead of being to memory, is to a defined ACC.  
It's like a gated assign, which is...  
It's fancier than what we're doing, but I certainly see the correct UOPs for it.  
Okay, great.  
You see what I mean, though.  
When you have the max, you're tracking that in a defined ACC.  
You're tracking the max, and then you can do a compare there, and then get a Boolean signal out, which is just true or false, like, is this one the max?  
Whenever that's true, you want it to be a store.  
That's fine if it's sequential.  
Oh, that's why it's assign.  
Okay.  
It's gated assign, basically.  
That's a better way to put it.  
It's gated assign.  
Does it require... It doesn't require order, does it?  
Oh, no.  
No, it doesn't require order.  
Same thing for Softmax.  
It also doesn't require order.  
Well, it does require that the two orders be the same.  
It does require that they both point to the same range UOP.  
Both the max and the arg are in the same.  
I mean, they obviously would be.  

**Chenyu** [[00:28:38](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=1718)]  
Yeah.  

**Geohot** [[00:28:39](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=1719)]  
As long as those are the same, the order doesn't matter.  
I don't want order to start mattering.  
If order starts mattering, we have a problem.  

**Chenyu & Geohot** [[00:28:44](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=1724)]  
So these, similar to associate scan, are like an operator applying on a range and you don't... It's ordered independently.  
Yeah, I think this should...  
It's a little fancier than what we're doing, but not that much.  
Yeah, so that's softmax.  
So I think my strategy is I'll update this in the BERT channel as well, basically just to break down where we are bad now.  
So for now, if you run it, it's somewhere between, I think, six hours to nine hours, because the bigger variants for training BERT  
probably have like two hours just running like rescheduling stuff in between evaluation that needs to be fixed but yeah so direction is memory optimization softmax and just generally making this pipeline faster i'm so we we already have a hand code optimization  
thing that is on BERT model, but I'm also working on making a smaller script to just isolate it into individual parts and get some ideas for what the bottleneck is.  

**Chenyu** [[00:29:59](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=1799)]  
Yeah, so this is important of making progress.  

**Geohot** [[00:30:07](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=1807)]  
Yeah, BERT is a... BERT is one of the most important things we're going to do in like the first half of the year.  
Except for a while, this is the year of speed.  
Last year was like the year of like correctness.  
Now we're not going to find something better.  
There's nothing better than UOPs and graph rewrite, right?  
Like UOPs and graph rewrite is the end of the line.  
It will be in the final tinygrad.  
So just like this style of writing code is what we spent most of last year figuring out.  
And then I think we did that.  
A phenomenal style.  
When you look at UOPs and graph rewrite and you compare that to... You read an LLVM rewrite rule.  
Read an MLIR rewrite rule.  
They're so difficult to understand compared to UOPs and graph rewrite.  
So yeah, I think we did a great job of that last year.  
And this year we got to prove that it's great by actually making things fast.  

**Chenyu** [[00:31:04](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=1864)]  
Okay.  
Tensor Cores.  

**Ignaciosica** [[00:31:11](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=1871)]  
Hi, hello.  
I have kind of an unstable connection, so sorry if it doesn't work correctly.  
Well, last week I finished the TF32 bounty and the Turing bounty, and I've been working on adding a half accumulation support for the CUDA backend.  
And also I'm working on  
Searching over the tensor core shape.  
I already sent a PR.  
It's like kind of hacky and it's in need of a lot of cleanup.  
But basically, what it does is it limits the linearizer, the kernel with only one tensor core shape.  
And it searches over that.  
And it works.  
It's simple.  
But that's the overview.  
And it consistently hits over 150.  
And I saw it, bounty is now 160.  

**Geohot** [[00:32:15](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=1935)]  
Yeah.  
Yeah, sorry about that.  
Yeah, I typoed that.  
I forgot that torch was 160, but I don't know.  
If we're really hitting 150 and things and this is searchable, I'll give you the bounty and I'll add a second bounty for what I want to get to 160.  
If I hit 150 on my computer, I'll give you the bounty after we get this merged and it's usable and doesn't slow things down a lot.  

**Ignaciosica** [[00:32:49](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=1969)]  
OK, yes, for what I see, the search run didn't end up so much longer.  
It's basically the same.  

**Geohot** [[00:32:59](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=1979)]  
Hang on, though.  
What is this search doing?  
Oh, it's in this.  

**Ignaciosica** [[00:33:09](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=1989)]  
Yes.  

**Geohot** [[00:33:14](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=1994)]  
Get kernel actions, but it's not a, so this is in the TC action?  

**Ignaciosica** [[00:33:22](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=2002)]  
No.  
What this does is the code in the kernel stays basically the same.  
But when searching, it iterates over all the Tensor Core shapes available and gives only one Tensor Core  
and tries all the actions, and only one that tries all the actions.  
Because before, it only grabbed the bigger, the tensor cores with reference.  

**Geohot** [[00:33:52](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=2032)]  
Well, but what I'm saying is, so a kernel needs to be uniquely determined by its specification and opt ops.  
Is that still true?  

**Ignaciosica** [[00:34:07](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=2047)]  
In a general case, no, because there is no way of specifying the...   

**Geohot** [[00:34:15](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=2055)]  
Yeah, that doesn't work.  
By the way, I'll put the bounty back to 150.  
And speed is very, very important to us.  
I'm down to pay out tons of bounties for 150.  
And I will add a second bounty for 160.  
okay uh well actually what i really want that bounty to be is not even that but is um uh 160 tflop uh with multi-stage yes uh yeah okay so the thing flammit's been working on uh i'll add that bounty later but uh  

**Chenyu** [[00:35:01](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=2041)]  
Is it clear to you why the kernel not specified by opt ops is bad to you?  

**Ignaciosica** [[00:35:14](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=2114)]  
For me or for George?  

**Chenyu** [[00:35:16](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=2116)]  
For you.  
For George it's clear.  

**Ignaciosica** [[00:35:19](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=2119)]  
No, yes, I understand that.  

**Chenyu** [[00:35:22](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=2122)]  
Yeah.  
So I think it's fine to add like some TC actions, but it needs to be, uh, basically the optimized kernel should be recreatable by just AST and the opt apply opts.  

**Ignaciosica** [[00:35:36](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=2136)]  
Okay.  
Yeah, sure.  
Thank you.  

**Chenyu** [[00:35:46](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=2146)]  
Uh, looking for something.  

**Geohot & Chenyu** [[00:35:48](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=2148)]  
Yeah.  
What does torch actually get on the 4090?  
I'll just say match torch.  
I mean, it's cool that these... I'll lock the 160 T-flop to you based on... But yeah, the...  
You can't do any out-of-band search.  
It's got to be functional programming.  
It's like AST plus OptOps yields single code.  
I'm not even sure how this is working, if that's not true.  
I guess you can just, yeah, kind of loop it.  
If it's in the same process as cache, right?  
No, no, no, no.  
But then what if it's like, how does it go in the Beam cache?  
I mean, isn't it all you... I don't know, maybe it picks the same thing every time.  

##### need for speed  
In general, we're down to, if anybody can figure out how to sustainably improve speed of things in TinyGrad, there's going to be big bounties for this.  
This is very valuable to us.  
Yes, everything down from, things at tensor level, if there's different ways to rewrite certain stuff that makes it faster, less kernel.  
in a in a good way not in a like a hacky weird way or in a numerical unstable way   
yeah like just sustainable ways to get speed yeah   
so that uh from the tensor level to better write some kind some operations so that is faster down to the middle where for any of the rewriting rules that makes the kernel faster and  
And anything in the render or compiler that makes the same kernel compile to a faster result.  
And I think that's pretty much it.  
And maybe also making Python time faster.  
I'm interested in Python speed too.  
I'm down.  
There's $3,000 of bounties on the table for somebody who can make the matching engine decent.  
And that's just the matching engine.  
I'll add more for graph rewrite.  
Again, if you're in this channel and you can actually improve speed of anything in tinygrad in sustainable ways, that's super valuable to us.  
Yeah.  
Oh, okay.  
So that's the tensor core.  
Yeah, ONNX.  
I see.  
I see.  
He's typing stuff.  

**more Chenyu & Geohot** [[00:38:31](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=2311)]  
Which refactor?  
Oh, did you?  
Yeah, I saw that refactor.  
I saw you commented on it.  
Were you... Yeah, it seemed fine to me.  
To make it a class instead?  
Um...  
Yeah, what's wrong with making it a class?  
It's fine.  
I was waiting for it.  
Oh, yeah.  
Oh, I commented on this.  
Does it have the same?  
It should have the same API, basically.  
Oh, change it to call?  
Yeah, I think that.  
Yeah, as long as it's call and just instead of get run onyx, use onyx runner.  
I think I pushed this to benchmark.  
Training.  
Did it work on benchmark?  
All right, great.  
I'll merge this.  
Done.  
Wait, let me just see what the changes are to ONNX.  
Make sure there's nothing here.  
Yeah.  
I mean it was awful what it was done merge the meeting is where things just happen we just do it yes next time you don't need to wait for this if we seems like we review something but we don't respond in I don't know a few reasonable time then just you can just ask in our next channel or dev channel  
Yeah, yeah, yeah.  
If you feel blocked... If anyone ever feels blocked on getting a PR merged and you're a known contributor, ping me.  
I'm not upset at all.  
I'm happy to.  
If you're like, I'm blocked on this, that's my job here to unblock you.  
Especially if it's something that we have commented.  
Yeah, if we've commented and you fixed something...  
I really liked, yeah.  
I didn't like that it had a .run, but the call, yeah, this is clean.  
ONNX runner is much more beautiful than get_run_onnx, which returns a function.  

**Chenyu** [[00:40:24](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=2424)]  
Great.  
Okay.  
That's good.  
Yep.  
So go over bounties.  
I merged the index int64 index.  

**Geohot** [[00:40:39](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=2439)]  
Do I have to pay that out?  
Do I pay that?  

**Chenyu** [[00:40:42](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=2442)]  
I don't know.  

**Geohot & Chenyu** [[00:40:43](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=2443)]  
Oh, I owe someone a crypto bounty.  
I only do crypto once a week.  
It's like getting out your little kit.  
You gotta get wild out.  
When is that time?  
Monday?  
Usually like Wednesday or Thursday.  
Okay.  
I'll think I'll get a crypto day.  

**Chenyu & Geohot** [[00:41:00](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=2460)]  
Great.  
So webGPU, Float16.  
I don't know what's the progress on that.  
I saw PRs.  
Did you review it?  
Yeah, yeah.  
He has a custom py_dawn thing.  
That's a custom package.  
I want to put that in the...   
Autogen?  
I want to put it in AutoGen, but I'm fine with pulling release builds from some GitHub agent.  
So I think that's the first step on that.  
I clearly want to switch it on anyway, which I'm fine with.  
wgpu is a maintained package.  
I first started, remember when I had gpu ctypes as a package?  
This is just not the way to go.  
We've got to just put these things in TinyGrad.  
And then actually, if you want to use it externally for other people or other things, just install TinyGrad.  
And it's not like TinyGrad's importing many other dependencies.  
Great.  
Retinanet?  

**Flata** [[00:42:02](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=2522)]  
Hey, guys.  
So right now, I'm trying to debug the, there's this loss on the regression loss.  
And I looked at the other PRs, but they tend to omit it.  
So I didn't really feel comfortable using the same approach.  
So right now, I'm just kind of investigating it, trying to narrow it down.  

**Chenyu** [[00:42:19](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=2539)]  
Are you training with float16?  

**Flata** [[00:42:23](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=2543)]  
No, just float32.  

**Chenyu** [[00:42:26](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=2546)]  
Oh, OK.  
So most likely a bug somewhere.  

**Flata** [[00:42:23](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=2543)]  
Yeah, so I think I've narrowed it down to this class called a box coder.  
I think it's just part of retina net, but it's also just like a shared code in mask-rcnn, which is, I check it's pretty much the same implementation as MLPerf.  
So I'm just trying to narrow it down further just to see what's going on there.  
But I think once that's good, I'll be ready to start training.  
So I've just kind of been slightly testing here and there on Tiny18.  
I was on Tiny10, but I think the GPUs are down, I think.  

**Geohot** [[00:42:59](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=2579)]  
Yeah, you might have to use the AM driver.  
Let me know if you're at all... If you're working on MLPerf and you're ever blocked by machines, we will get you more machines.  
Just let me know.  
Would you rather reds or greens?  
We have a lot of reds now.  
I can get you more reds.  
So yeah, just let me know if that would help.  
And we'll make sure... If you're working on MLPerf, you should never be blocked on machines.  

**Flata** [[00:43:24](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=2604)]  
Okay, sounds good.  

**Geohot** [[00:43:26](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=2606)]  
Yeah, feel free to ping me.  
Be like, hey, George, I'm working on MLPerf and I don't have any computers.  
I'll get you computers.  

**Chenyu** [[00:43:34](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=2614)]  
Yeah.  

**Geohot** [[00:43:35](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=2615)]  
You know, it'd be great if we get rid of that on this cycle too.  

**Chenyu** [[00:43:42](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=2622)]  
Yeah, and I mean, feel free to share these.  
I think...  
It's also important for TinyGrad to provide good researcher experience.  
So the problems, how you debug it, and if you find it very hard to debug, I think these are important to share somewhere so we can think if there is a way we make tools to make these better.  
It's not enough for TinyGrad itself to be great.  
It also needs the researchers or developers who work with TinyGrad to make process to feel great in the experience.  
Numerical issues are notoriously hard to debug in deep learning.  
Not clear how much better we can make, but we want to make it better.  
I also didn't realize that RetinaNet looked more like MaskRCNN where it's got fancy loss function stuff.  
So I'm going to raise the bounty of that to $1,000.  
And then it's $1,000 for getting it merged.  
And if we actually manage to get it on MLPerf, it's $2,000.  

**Chenyu** [[00:44:55](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=2695)]  
Sounds good.  
Can we go back to... Yeah.  
What's next?  
Whisper...  

**Geohot** [[00:45:03](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=2703)]  
Any comments?  
Oh, I haven't tested the working whisper.  
I'll test it on this week's audio.  
Great.  
Yeah, I think, again, we pay that one out as soon as we get it actually used on the tiny recording.  
And that's another thing.  
I think you have access to tiny box, but if you need compute, just let me know.  

**Chenyu** [[00:45:26](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=2726)]  
OK.  
Graph rewrites.  
I put a question mark because I don't know if it's actively being worked on.  

**Geohot** [[00:45:31](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=2731)]  
I think I saw him in here, but now he's not.  
Isn't it this one?  
No?  
Oh, yeah, here it is.  
Hey.  
Can't hear you.  
You're trying to talk.  
Okay.  

**Sied Lykles** [[00:45:58](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=2758)]  
Hi, can you hear me?  
Yeah.  
Yeah, sorry, I've been just caught up the last few weeks, but I'm planning to finish it.  
The most difficult thing was that it broke the HLB CIFAR on float16, and it's a bit hard to debug.  

**Geohot & Chenyu** [[00:46:24](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=2784)]  
Are we talking about the same thing?  
No, but I mean, since he's here.  
Yeah, totally fine.  
But this isn't graph rewrite 2.0.  
But no, no, we want to hear which one are you talking about?  
Sorry.  

**Sied Lykles** [[00:46:36](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=2796)]  
Oh, this is there was like the flattening of the ordering of things.  

**Geohot** [[00:46:43](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=2803)]  
Oh, yes, yes, yes.  
Oh, yes.  
I'm actually I'm very excited about this.  
I was just thinking about this.  
You mean moving like the ACC to the front?  

**Sied Lykles** [[00:46:52](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=2812)]  
Well, that's part of the bigger boundary.  
I needed that, because otherwise, then.  

**Chenyu** [[00:47:00](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=2820)]  
Let's get that merge first.  
It has been there a while.  
So we'll just add some simple tests to show some basic property for this moving ACC to the front property.  
And I think we are ready to merge that.  
The performance looks fine.  

**Sied Lykles** [[00:47:14](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=2834)]  
OK.  

**Chenyu** [[00:47:15](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=2835)]  
Yeah.  

**Sied Lykles** [[00:47:18](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=2838)]  
Yeah, and then for the thing that I actually have the bounty on, which is ordering the chains, that wasn't broken because of moving the ACC.  
So yeah, I just have to figure that out.  
No, sounds good.  

**Chenyu** [[00:47:44](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=2864)]  
I was not sure if you are still working on those because it's been quiet for a few weeks.  
But as long as you are interested and still working on those, I can keep the bounty lock for you.  

**Sied Lykles** [[00:47:58](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=2878)]  
Yeah, that works.  
Thanks.  

**Chenyu** [[00:47:59](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=2879)]  
Okay, now go back to, I think, the real Graph Rewrite 2.0.  
Or...  
Yeah, Thompson, can you?  

**Tomsa** [[00:48:23](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=2903)]  
Yeah, so I did the write up, I guess, just to explain the challenges.  
And I'm basically figuring that out.  
It's not going to be much more code.  
It's similar to before.  
But the previous implementation was very inefficient.  
I was not trying to focus on speed.  
I wanted to see if the bottom-up matching actually worked.  
But it's extremely inefficient, because you can imagine that if you match three symbols, then the parent node has three states for the first source.  
And if it's the same for the second source, where the second source matches three symbols, because it's the product of the possible state of each source, you have nine states.  to consider versus just one.  
The good thing about a DFA is that it doesn't matter if you have 10 patterns or 1,000, there's only one transition, which is why even though it's maybe only going to be three or four times faster, the more patterns get added, the more beneficial it is because it will scale much better.  

**Geohot** [[00:49:32](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=2972)]  
Four times faster gets you two grand.  
Yeah, no.  
I mean, four times faster would be awesome.  
No, totally.  
I totally understand.  
Right now, it's just a loop over the patterns versus something that compiles the patterns and does the transitions would be great.  
And I think it can make it a ton faster.  
The one that we have also has been pretty optimized.  
So not only is the approach bad for the one we have,  
it's been, I've spent a good bit of time optimizing it, reordering the conditions and stuff, like the stupid micro-optimizations.  
So yeah, it'll be great to switch to a new approach, and it starts a new S-curve.  

**Tomsa** [[00:50:15](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=3015)]  
That's why it won't be such a huge speed-up, because the current implementation already prunes a lot of stuff, and gets rid of a lot of calls to match, and yeah.  

**Geohot** [[00:50:29](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=3029)]  
Oh.  
I mean, deleting that would be great too, deleting that LER thing, that early reject stuff.  
I mean, it's just complexity.  

**Tomsa** [[00:50:38](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=3038)]  
Yep.  

**Geohot** [[00:50:40](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=3040)]  
Cool.  
And I think you're also doing x86.  
Yes.  
Yeah, I think the gate for x86 is that it matches O0 of Clang or LLVM.  

**Tomsa** [[00:50:56](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=3056)]  
Yeah, I haven't touched it in a while because I guess this is more interesting, but I'll get to it.  

**Geohot** [[00:51:05](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=3065)]  
Yeah.  
The graph rewrite thing is much more important to us, but I know you mentioned arm assembly back in too, and I'll double the bounty if it works for both.  

**Tomsa** [[00:51:16](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=3076)]  
Yeah, I can get that done.  

**Geohot & Chenyu** [[00:51:19](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=3079)]  
But yeah, no, let's definitely focus on graph free write.  
I mean, Python speed is like, again, speed is the focus for this year.  
Anything that can improve speed is important.  

##### Blake3  
Blake3.  
I don't know if the person is still working on it.  
I think you asked for benchmarks.  
Yeah, I've asked for benchmarks for a while on this.  
I don't know.  
Do we really want this?  
Or probably want this?  
We definitely want this, but we want benchmarks.  
Okay.  
I think we probably close this if there's still no response before next meeting.  
And we unlock this so other people can maybe take from here.  

##### Briefing of newly added bounties  
Okay, what else?  
We'll go over the new bounties quickly.  
Okay.  
So if somebody can get Windows working in GitHub CI with any one of the backends, I don't care which one you choose, I think it might be a little tricky now with the...  
With the new Clang thing.  
Oh, I got to merge that LLVM thing too.  
Okay, I got to get to that today.  
I think it's pretty much ready.  
We've switched Clang and LLVM.  
Well, UUVN switched Clang and LLVM to generate basically shellcode.  
So, I mean, it's super nice.  
You can just mmap it and jump to it.  
And you don't have to deal with, like, loading a DLL, which is absurdly slow.  
I mean, just the amount of syscalls that DLLopen is going to make.  
So now you're making one syscall, and in fact, you don't even really have to make that syscall.  
You could just map a huge chunk of memory and do a...  
But, uh...  
Yeah, no, I mean, 1 mmap is still a lot better than DL Open, so.  
Yeah, if somebody can get Windows working on any backend and add it to GitHub CI, $200, that's a great new bounty.  
What test to put in the CI?  
Test tiny is fine.  
You can literally get any Windows tests running.  
No, I can do like, yeah, maybe do the ops test.  
Do some representative set, but mostly I just, even just test tiny is good.  
for the bounty.  
Okay, let's just do test tiny then.  
I think we also do that for like hip and CUDA, basically other less tested thing on our machine.  
So I think that's good enough.  
Basically that we didn't like break an import or break a pipeline.  
Yeah, test tiny is going to get you most of it.  
Move LLVM BF16 cache from rewrite rules to renderer.  
I saw somebody take a shot at this.  
Uh, I remember it not looking right for some reason.  
Let's see, let's see this one.  
Oh, it doesn't even pass the tests.  
Okay, this doesn't pass tests.  
It doesn't pass the linter.  
Uh, that's another good bounty for a new person.  
These $200 bounties probably will work out to be, uh, 10 lines of code, uh,  
There's a bounty for... Oh, has this one... has there been progress on this one?  
On the... Oh, okay, nobody rebased it.  
I might unlock that one if there's no progress on it by next meeting.  
The PTX working on OSX.  
We have all the infrastructure now because AMD works on OSX, so that one's great.  
The guys on the Phronix forum told me about a different shader compiler that works for RDNA 3 that's not LLVM based.  
It's based on this thing called ACO, and it looks better.  
LLVM's backend for RDNA 3 is not very good.  
but the ACO one is written by the guys at Valve I trust it if anyone's going to make it, good $300 bounty if someone can get that working it looks like it's in Mesa, it looks like Mesa has this thing called NIR which looks a lot like PTX so you'll have to write an NIR renderer and then probably just all the compiler and it should work  
So yeah, $300 for that.  
$300 if someone can get FP8 support on NVIDIA with Tensor cores.  
I've seen some PRs for that.  
I haven't seen any that have Tensor cores, and none of them have looked particularly clean.  
We got... I think maybe it's $165 in Torch.  
Okay, so we got matmul bounty speed.  
If somebody can get fast matmuls on pretty much any GPU, $400.  
Uh...  
Maybe 500 if someone could do the multistage kernel.  
HVAC decode support for the NV driver.  
If you're good at the low-level stuff,  
You know, you got to read the NVIDIA driver, figure out, use the I.O. control sniffer, figure out what calls it's making to use CU vid.  
Probably works out to be something like 30 lines.  
And then, yeah, you want to basically, you can kind of hack it in with like a custom UOP now that just magically makes a tensor have an HVAC.  
So that's a fun one if you want to play with NVIDIA drivers.  
Matching engine speed bounties.  
These have all been discussed.  
Ttomsa, I'll lock these to you.  
I've seen good progress on this.  
Yeah, hopefully we see progress for the next meeting.  
I'll lock all three of them to you, however much speed you get.  
That's old and no one's going to do it.  
Flash attention was already discussed.  
FSDP.  
You like the FSDP PR?  

**Chenyu** [[00:57:36](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=3456)]  
FSDP PR?  

**Geohot & Chenyu** [[00:57:37](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=3457)]  
Yeah, there was an FSDP one, right?  
I think you commented on it, but I think it's like, it kind of like, yeah.  
It breaks everything, so no.  
Yeah.  
Yeah.  
My recommendation was wait until the new multi is done.  
Oh, okay.  
Reasonable.  
But yeah, so to lock FSDP, just show training a model on multi-GPU that doesn't fit on one GPU.  
And it should be, I think there are some other attempts before that was supposed to be closer.  
I'm not sure.  
Yeah, that one's definitely been attempted.  
I don't exactly understand what FSDP is.  
So yeah, the goal of this is more, it's definitely a way to use TinyGrad, not hacking core TinyGrad APIs.  
And we should be able to understand what FSDP really is from the PR.  
I actually think that once people understand what FSDP is, that's actually very, it's very simple to do.  
I think you're just going to have to like shard.  
You're going to have to like, like loop over.  
It might even be like a one liner where you just like loop over the optimizer and shard it in a certain way or something.  
Um, I know it involves not putting all the optimizer on one GPU.  
Uh,  
Yeah, that was not going to happen.  

**Geohot** [[00:58:55](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=3535)]  
Okay.  
Assembly backends.  
SAS assembly backend.  
Tense torrent backend.  
RDNA 3 assembly backend.  
We added a $10,000 bounty.  
I mean, someone should do the first bounty first.  
If somebody can get a RDNA assembly backend to match the performance of HIP, that's $1,000.  
And if someone can get one that's 50% faster...  
Again, the LLVM thing leaves a lot on the table, so I will actually pay $10,000 for that.  
The main reason that we are getting better times on NVIDIA than AMD on our MLPerf is because the NVIDIA PTX to SASS compiler is better.  
Everything else about it is pretty much the same.  
When you compare like a 4090 to a 7900 XTX.  
It's not the flops that are really helping you.  

**Chenyu & Geohot** [[01:00:00](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=3600)]  
How do you know this?  
No, it's not.  
Where do you think the flops are helping you?  
Because the flops are... The output... The flop reporting are higher on Greenbox.  
I mean, the flop... Yeah, but no, I think it has almost everything to do with memory.  
Yes, but don't the two machines have the same memory?  
Well, that's the thing.  
The two machines do have the same memory.  
The memory hierarchies of the 4090 and the 7900XTX are almost identical.  
NVIDIA is just so much better with their compiler at pretty much register packing.  
So I think there is a big perf gain to be had here.  
And that's why it's worth $10,000 to us.  

##### Tenstorrent  
And then maybe the last one to talk about is the Tenstorrent backend.  
I haven't put this up before because it used to be a lot of effort to maintain backends, but I think the new webGPU has really shown that things have gotten a lot better and that we can deal with more backends.  
So if someone writes a Tenstorrent backend, $1,000.  
And then Corsix, put up an extra $1,000 if someone also gets it to work on Wormhole.  
So if you can write a Ten's Torrent backend that works on Greyskull and Wormhole, $2,000.  
And these, will they be performance?  
Or is it just run correctly?  
Just correctly.  
Okay.  
Yeah.  
Just correctly.  
Performance on Tenstorrent is going to be a whole separate rabbit hole.  
Okay.  
Oh, yeah.  
I have thoughts.  
We have to put more effort into DSP.  
We have a due date.  
We have a due date on DSP the end of March.  
Don't forget DSP.  
Don't forget DSP.  
We've got a contract as a company and we're going to do it.  
I think it's going to be those kind of things where it's two weeks before the deadline and I'm going to be like, holy shit, okay.  
That's what I've got to do.  

**Chenyu & Geohot** [[01:02:02](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=3725)]  
Questions?  
Anything in this chat?  
today uh if a bounty's locked another guy solves it by sending a solid mergeable pr who gets the bounty uh the locked uh you know we we give we if you think there's a bounty that here's if you're in that situation what i would do is i would post in bounties uh hey you know this bounty's been locked and there hasn't been any progress on it in a week uh pretty much if there hasn't been any progress on it in a week i will unlock the bounty  
Yeah, and I mean, you can also kind of deal with the author and say you can split the bounty or whatever.  
Yeah, if you guys are both working on it, that's great too.  
I'm happy to split bounties.  
But yeah.  
Yeah, we want to award the work itself and how you split it, who get it, really it's just as long as it's fair, we'll figure it out.  

**Geohot** [[01:03:12](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=3792)]  
Oh, cool.  

**Chenyu** [[01:03:14](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=3794)]  
Okay, that's it for this meeting.  
And remember, next week, we will have a different meeting time that's 3.5 hours earlier.  
And see you next week.  

**Geohot** [[01:03:26](https://www.youtube.com/watch?v=Bm_blXgmlLo&t=3806)]  
Bye.  
