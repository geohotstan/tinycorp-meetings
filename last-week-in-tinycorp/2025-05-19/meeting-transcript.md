# 2025-05-19 Meeting

### Meeting Agenda

**Time:** 9am Monday San Diego time
- company update
- tinygrad 1.0 plan, speed, lines
- MLPerf ci / div and mod / quantize onnx
- scheduler
- driver
- WebGPU
- locals
- onnx
- z3 fuzzer
- other bounties

### Audio

[Youtube Link](https://www.youtube.com/watch?v=gZ6FvO5RYz4)

### Highlights

- **[Company Update](#geohot-000032)**: Tinyboxes are finally shipping this week after fixing a USB boot drive issue caused by a faulty USB splitter.

- **[Tinygrad 1.0 Plan](#geohot-000143)**: Considering a 1.0 release within two months due to API stability since version 0.7; the JIT still needs cleanup.

- **[MLPerf CI](#chenyu-000631)**: Chenyu completed an initial three-hour MLPerf CI training run on Nvidia (green) hardware. Discussion about adding AMD (red) hardware to CI.

- **[Integer Division Bug](#chenyu-000926)**: Chenyu found and fixed a bug involving incorrect float-based integer division in quantize ONNX.

- **[Scheduler Update](#qazalin-001139)**: Fixed unnecessary padding realization bug. "Fuse A range" mostly ready pending some boundary-checking issues.

- **[Driver (USB GPU)](#nimlgen-001923)**: Improved USB GPU write speed merged; read speed improvements still ongoing due to complexity in USB logic.

- **[WebGPU Backend](#hooved-002804)**: Significant progress on graph capture refactor; working on dealing with tensor state initialization post-capture.

- **[Local Memory (LDS) Bug](#ignaciosica-003311)**: LDS implementation ready but blocked due to compiler optimization bugs on CI Macs; testing workaround by disabling optimizations (O0).

- **[ONNX Integration](#geohot-004159)**: ONNX integration mostly complete; removing protobuf parsing dependency is not mandatory but desired ($300 bounty available).

- **[Z3 Fuzzer](#sied-lykles-004406)**: Fuzzer identified subtle rewrite rule bugs causing potential out-of-bound accesses; plan to temporarily disable certain optimizations to move forward.

- **[Cloud Infrastructure](#geohot-004517)**: All machines moving to Ubuntu 24.04; plans for GPU-based hashing for a distributed filesystem progressing, aiming for high-throughput hash computation.

- **[Open Bounties](#geohot-005313)**: Various open bounties mentioned, including ONNX protobuf parsing ($300), Whisper fixes ($200), Blake3 hashing, and torch operations compatibility.

### Transcript

##### **Geohot** [[00:00:00](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=0)]
All right, let's get started.
So this is meeting 71.
And no wozeparrot either.
Oh.

##### **Geohot** [[00:00:32](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=32)]
All right, so the main thing for the company is that Tinyboxes are shipping this week.
Finally, we're actually going to get a whole bunch of them in the mail.
We had a few problems with.. So Tinyboxes have a RAID array with four NVMe drives in them.
They also have a USB boot drive.
We had a problem where the USB boot drive wouldn't show up.
Maybe a third of the time.
And you'd have to reboot.
And it was terrible.
So we try swapping the drive, we try swapping the enclosure.
And none of those things fix it.
It turned out, so we're thinking that's got to be the processor, it's got to be the BIOS.
It turns out what was wrong, there's this small splitter we have that plugs into the motherboard that splits the USB ports out.
And somehow that was broken.
We switched the same splitter that was used on the TinyBox V1, and that one just worked.
So yeah, I think that's the last.
We good to ship Tinyboxes this week?

##### **Geohot** [[00:01:41](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=101)]
I think some are going out today.

##### **Geohot** [[00:01:43](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=103)]
Some are going out today, great.
And someone bought two refurbished greens.
I think we'll get those out this week too.
So that's company update.
And yeah, let's talk about Tinygrad 1.0.
So I think this is a decision that we're going to have to make.
Someone posted in general, I'm currently tasked with writing a book about AI application development for beginners.
I'm considering using Tinygrad instead of PyTorch as a framework of choice.
However, since we aren't at 1.0 yet, how stable are the interfaces?
And I think the answer to that is the interfaces are actually extremely stable.
You can look at the Tinygrad example page, and it used to break back when we were in 0.4, 0.5, 0.6.
But from 0.7, 0.8 onwards, there haven't really been many breaking changes to the API.
So I think we sort of might be ready for 1.0, if by 1.0 we mean that the API is stable.
So yeah, I mean, 1.0 might happen before we do speed.
The only thing that I really think that still needs to be cleaned up for 1.0 is the JIT.
I think that there's a lot of quirky edge cases in the JIT that need to be understood and documented.
But other than that, I think it kind of is 1.0.
So we might be doing the 1.0 release maybe in like two months.
Before we're on par with PyTorch for Speed.
I also put out a document.
I'll repost it in Discord right now about how to get speed.

##### **Geohot** [[00:03:47](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=227)]
So..

##### **Geohot** [[00:03:52](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=232)]
This is just like a list of.. It's nice.
We're finally kind of at the point where we can reasonably talk about these things.
And I think it would just be this list.
And if we did just this list, we'd be on par with PyTorch.
So the first one on the list is upcasted warps.
Maybe we'll get to locals later in the meeting.
Upcasted warps mean..
GPUs process data.
GPUs are like single instruction multiple data machines.
Or, well, SIMT is the acronym used because they don't appear like a SIMT machine.
You don't get a wide vector.
But under the hood, they have a vector register that are as wide as the warp.
And we should expose that to the program because there's some things you can do across the warp.
We already are doing one thing across the warp, TensorCores.

##### **Geohot** [[00:04:51](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=291)]
Yeah.
So it would be nice to actually expose that to the code.

##### **Geohot** [[00:05:03](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=303)]
Like right now, there's all these hacks which look for certain local variables, and the tensor core thing could be wrong, and we want to just not do that.

##### **Geohot** [[00:05:13](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=313)]
So yeah.

##### **Geohot** [[00:05:16](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=316)]
Lines, the other thing that I worked on, if you look at, I made a branch on Tinygrad called V2.
It's not really V2.
V2 is about 7,000-ish lines, and those 7,000 lines let you run beautiful MNIST on metal.
So about half of Tinygrad is critically required.
It's just good to think about.
We have grown a lot in lines.
We've grown a lot in lines from 1,000.
I mean, 1,000 was never realistic, but there was a time where 5,000 and 7,000 were kind of realistic.
But I think a lot of that line growth has come more from features.
New backend support and things that are a lot more like orthogonal to the main code base, right?
Like take something like the AMD driver.
The AMD driver added a thousand lines, but it doesn't affect you.
It's not like we have to understand those.
You have to understand those thousand lines in order to understand Tinygrad.
So they're nicely factorized.
Oh, I see Chenyu just showed up.
And we are right up to your item, MLPerfCI DivinMod Quantize Onnx.

##### **Chenyu** [[00:06:31](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=391)]
Yeah, so MLPerfCI.
Let me check if that runs finish.
So I think I would manually test that for a few rounds.
And I think features like trigger from our branch, like update benchmark, and really make it a daily Cron job.
And we'll also add the new stats feature so we can capture the stats.
I think we pretty much care about our step time and time to converge.
Okay.
Yeah, so the job finish in three hours.
That sounds about right.

##### **Geohot** [[00:07:14](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=428)]
Wait.
Oh, you trained the whole thing?
Yeah, yeah.

##### **Chenyu** [[00:07:17](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=428)]
I thought that's the idea.
Oh.

##### **Geohot & Chenyu** [[00:07:23](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=443)]
I mean, yeah, I guess we can.
Oh, I was imagining it was just going to be more of a.. No, I don't know.
Maybe we should just train the whole thing.
I thought we were just going to do the BEAM search and get the time, but..
Yeah, I think since we can, this seems to be better in case.
But I think our ResNet is still suffering from the fact that it doesn't converge to the original number.
Oh, you know, I found a bug.
The optimizer was keeping its momentum in float 16.
None of the other ones do that.

##### **Chenyu** [[00:08:07](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=487)]
That's the optimizer used by ResNet?

##### **Geohot & Chenyu** [[00:08:11](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=491)]
I believe so.
It's just like SGD.
So Atom was keeping its two parameters in float32, but SGD was keeping it in whatever the tensor was in.
OK, I would do something to this log in.
Otherwise, it's generating like a, I don't know, in this log.
I'll clean this up.
But it looks nice.
And I think, if possible, we should try and do it in three hours.
It should be fine.
Cool.
Yeah, no, I like it.
Are we running on, is this AMD or Nvidia?
This is green.
This is green.
Green is faster.
There's no reason we cannot run on both.

##### **Geohot & Chenyu** [[00:08:55](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=535)]
Cool.
I mean, we don't have that many green.
We can definitely put more red in the CI pool, too.
Sure, then maybe that's better.
We add more red to CI, then we run this on red.
Yeah, I like that.
Okay, that sounds good.
I like that idea.
Yeah, yeah, yeah.
Let's just run it on red.
We'll add another red to the CI pool.
And yeah, let's run them both.
I like this.
Yeah, let's just run our ML-versus-ground-drops.
Yep.

##### **Chenyu** [[00:09:26](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=566)]
And the next thing is, so I found a bug for integer div.
I have an issue and repro for that.
I also have a fix for that.
It's kind of gated by Quantice ONNX.
The test has some off by one arrows that I'm not too sure.
So I was looking into that.
Otherwise, everything else would be correct.
The issue was we were previously using a float to do the diff, then do the rounding, and that's incorrect for some cases.

##### **Geohot** [[00:10:01](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=601)]
We were casting it to float, you're saying?

##### **Chenyu & Geohot** [[00:10:11](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=611)]
Yes.
I see.
I did a comment for the PR for Quantize Onnx. OK, great.
Yeah.
I don't know if the old quantized ONNX bug or any of the behavior difference are coming from this bug, but something we definitely want to fix.
I see ONNX is later down on the list, but is this kind of the last block around bringing ONNX into the code base?

##### **Chenyu** [[00:10:45](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=645)]
I believe so.
I think this is independent.
Because currently, the context on extra passed, right?
Even if it's passed on the incorrect implementation, it should be independent to bring that into Tinygrad.

##### **Geohot & Chenyu** [[00:11:04](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=664)]
Cool.
We'll discuss that when we get down to ONNX, if there's any more blockers or anything more I can do.
Because I definitely want that.
I think that's a 1.0 requirement.
I want that front end to be in Tinygrad.
Let's discuss when we are at ONNX.
Cool.

##### **Geohot** [[00:11:22](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=682)]
Yeah.
OK.
Cool.
Let's scheduler.

##### **Qazalin** [[00:11:39](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=699)]
I found a bug in padding.
We were realizing some paddings we didn't have to realize.
So we fixed that.

##### **Geohot** [[00:11:44](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=704)]
When you say a bug, it wasn't giving wrong output.
It was just fusing.
It was just realizing some things it didn't have to realize.

##### **Qazalin** [[00:11:53](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=713)]
It was doing something dumb.
Yeah.
Cool.
It wasn't wrong.
It was trying to be safe and not push paths through division.
They didn't have to if they were realizing that division.
So yeah, that's fixed.
I'm working on fuse A range.
Pretty much everything is done.
If you look at my PR for fuse A range default, it's PR number 10333.
I have a bunch of skips for out-of-bounds access and linearizer failures.
I post some of them in the scheduler channel.
So I'm wondering if those are blockers to make this default.

##### **Geohot** [[00:12:39](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=759)]
Well, if we're getting.. I mean, the Z3 thing should be very good about out-of-bound access.
So if we're getting any real out-of-bounds access, we got to fix that.
That's probably real.
This isn't like the..
Like, yeah, that's now all computed by Z3, and I trust it a lot.
Oh, so just like you said, it's a bug in the Z3 setup that it's not considering some gates.
So it might not be real.
It might just be our Z3 setup.

##### **Sied Lykles** [[00:13:12](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=792)]
No, it was real.
It's like, what was happening is, if you have
Like, if you have a valid, some of the valids will simplify the other valids next to it.
But if the valid, like if the condition had a load in it, then it would simplify the load of the gate in the load.

##### **Geohot** [[00:13:38](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=818)]
That's not supposed to do that.

##### **Sied Lykles** [[00:13:44](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=824)]
I don't know if that makes sense, but I have a PR for it.

##### **Geohot** [[00:13:50](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=830)]
Okay, cool.
So it's real, the PR for it.
Yeah, yeah, it was real.

##### **Geohot** [[00:13:56](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=836)]
Great.
Great, let's get that merged.
Hopefully that fixes it.
Yeah, I see your post in scheduler where it's removing some gate.
Yeah, we shouldn't ever be removing the gate if it can go out of bounds.
Oh, cool.
Yeah.
Oh, so I see this.

##### **Geohot** [[00:14:18](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=858)]
I see this PR.
Yeah, just posted last night.
Great.
Hopefully that fixes it.

##### **Qazalin** [[00:14:30](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=870)]
I pretty much fixed everything on the schedule.
There are some edge cases left.
Yeah, I'll get the mirror shift.
Unless the de-vectorize issue ends up being a major bug, I think that's pretty much it for Phoenix ARange.
There are some cases where the ARange isn't folding.
It's creating a for loop.

##### **Geohot** [[00:14:50](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=890)]
Yeah, I can look at those too.
If you post.. I hope that new reduced stuff should be powerful enough to get all the A ranges.
And if there's something that's not, we need to make sure those for loops go away, because you can get really slow performance then.
Or actually, even better, write some tests that are currently failing.
Not folding the A-range.
We've got to fix that.

##### **Qazalin** [[00:15:29](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=929)]
Yeah, I think we're still trying to master testing and fixing.
I'll just end it.

##### **Geohot** [[00:15:38](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=938)]
Great.
Yeah, no, I'm very excited to have fuse A-range be the default.
That's something that I'll still set manually.

##### **Geohot** [[00:15:45](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=945)]
And yeah, it should be better.

##### **Qazalin** [[00:15:51](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=951)]
That's it for this week.
There is the kernelized issue with assign.
So currently, the way we do setitem sort of expects you to realize that setitem before you access the buffer again.

##### **Geohot** [[00:16:11](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=971)]
Is that those failing assign things?
I think Hooved posted them.

##### **Qazalin** [[00:16:16](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=976)]
Correct.

##### **Geohot** [[00:16:19](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=979)]
So that's a real bug.

##### **Qazalin** [[00:16:22](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=982)]
It's a spec limitation.
It's not a bug.
It's actually an expected behavior.

##### **Geohot** [[00:16:29](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=989)]
I see.
Oh, I was actually just, yeah, I was just thinking about basically doing this.
I mean, this is one place where Tinygrad's performance is way worse than PyTorch.
Like if you have something in a loop where you'll just set one variable over and over again.
I'll write some stress tests like this where you just like, you know, make a tensor that's 10 long and then you put
You know, A sub 0 equals A sub 1 equals A sub 2 equals.
We've got to make sure things like that are fast.
Is that the same sort of thing, like a chain of setitems?

##### **Qazalin** [[00:17:05](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=1025)]
Correct.
You have to basically lazily evaluate that graph instead of having to in-place realize it every single time, which poses an interesting connection of like,
What is the actual dependencies of these graphs?
So I think I'm going to put up a Tinygrad improvement proposal this week just to spec it out because it's a spec issue.
We need to maybe rethink some parts of assign and how it relates to buffers and views of buffers.

##### **Geohot** [[00:17:40](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=1060)]
I see.
Yeah, I know that we'll get long chains in the random stuff too, where we're just repeatedly assigning to the random counter.

##### **Qazalin** [[00:17:50](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=1070)]
Yeah, I think that's easier because the random counter is a single value.
The problem exists when you have multiple views on a chunk of memory.
So if you're assigning to different sub-buffers, how are you going to chain those different sub-buffer assigns?
And link them back to the main buffer.
There's a space memory and you have to sort of create edges to different offsets and sizes.
I see what you're saying.

##### **Geohot** [[00:18:27](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=1107)]
Yeah.
Like, like if, if two assigns are assigning to different parts, different regions of the, of the buffer, then sure they can run in parallel.
They don't have to be dependent on each other.
Is that what you mean?

##### **Qazalin** [[00:18:39](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=1119)]
You have to actually express that thing.
What is that, your graph?

##### **Geohot** [[00:18:44](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=1124)]
Yeah, I mean, it shouldn't be wrong to make them all sequential.
If we do make them all sequential, I would imagine that would still give the right answer.
It may not be optimal, but cool.
OK, if this test assign thing is a real bug, let's understand it and let's fix it.

##### **Geohot** [[00:19:12](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=1152)]
Cool.
Driver?

##### **Nimlgen** [[00:19:23](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=1163)]
So the USB GPU, I mostly merge all the things related to the write speed.
So the only thing is the copy out.
I just got it.
Two times better, like three megabytes a second.
But yeah, it's still pretty slow.
So yeah, I'll continue reversing that.

##### **Geohot** [[00:19:54](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=1194)]
So we're still doing a mem copy in the 805.1?
Yeah.
Oh, no, yeah.

##### **Nimlgen** [[00:20:08](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=1208)]
But yeah, yeah, definitely we can remove that.
I just need to find how to do that.
Actually, it's a bit trickier than right because actually the whole logic happens after the comment is posted to the NVMe.
So all this weight logic and it's a bit, it's way bigger.
Because when we do the right command, we can just stop after that and just free all the endpoints, just release them.
So the buffer will be filled up already before this command.
That's not the case for the read.
So yeah, it's logic.
More complicated.

##### **Geohot** [[00:20:57](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=1257)]
Yeah, I see what you mean.
Like, it actually has to, the drive has to take the action before the USB in the read case, or in the write case, the USB takes the action first.

##### **Nimlgen** [[00:21:09](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=1269)]
Yeah, I mean, actually, I see, like, where the path differs, like, for the NVMe and GPU.
I just, yeah, so I'm just trying to..
Cool.

##### **Geohot** [[00:21:37](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=1297)]
The other patch I want to make to the firmware is I have an idea that if you change the class from a mass storage device to a custom device, then it won't require sudo on Mac anymore.

##### **Nimlgen** [[00:21:50](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=1310)]
So yeah, I tried that.
It still requires sudo, but actually, I'm not sure if my patch is correct, but I'll double check that.
But I'm unsure how to reliably see what interface is used on Mac OS for the USB device.

##### **Geohot** [[00:22:12](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=1332)]
I believe it's in the descriptor.
I believe you can get the USB class in the descriptor.

##### **Nimlgen** [[00:22:23](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=1343)]
Yeah, I'll double check that.
I don't see it in the list.
When I just connected with not modified firmware, when I just connected the controller with the GPU, it's already not in the list of the USB mass storage interface.
But when it's in BME, it's there.

##### **Geohot** [[00:22:44](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=1364)]
Well, yeah, so there may be like, there's probably a difference between the driver actually like, right, like there's a probe function in the driver, right?
The probe function is either going to return true or false.
And maybe if it doesn't, if it has the GPU, it's returning false.
But I'm not sure that releases the driver's claim on the device.
I'm pretty sure it's just in the descriptor.
How do things know?
I mean, it's not the VID and stuff that determine.. No, no, no.

##### **Nimlgen** [[00:23:19](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=1399)]
Yeah, I mean, I found this in the firmware.
Like this USB descriptor and I patched it.

##### **Geohot** [[00:23:25](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=1405)]
Yeah.
Nothing.
Yeah, so B device class is specifically what I'm thinking of.

##### **Nimlgen** [[00:23:34](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=1414)]
I think it should be like B interface class.

##### **Geohot** [[00:23:40](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=1420)]
No, specifically B device class, not the interface.
So there's the interface descriptor, but then there's the device descriptor.
It's called B device class.
And it's set at the device level.
And then, yeah, 08 is a mass storage device.
I think if you change that to 0f,
It won't.. Sorry, FF.
It won't be claimed.

##### **Nimlgen** [[00:24:16](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=1456)]
Okay, yeah.
I'll check that.

##### **Geohot** [[00:24:20](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=1460)]
I mean, we should also check if Mac can access normal USB devices without sudo from user space.

##### **Nimlgen** [[00:24:33](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=1473)]
Um..
Actually, when I just asked ChatGPT about that, it said that the only way to do that is just using driver kit.
And you need to sign your application with the permission to access USB devices.

##### **Geohot** [[00:24:52](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=1492)]
That's annoying.
Yeah.
Yeah, I mean, all right, if that's really the case.
But yeah, I mean, I still think it shouldn't be a mass storage device because then we won't have to call that LibUSB unclaimed kernel driver anymore.

##### **Nimlgen** [[00:25:09](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=1509)]
Yeah, probably.

##### **Geohot** [[00:25:13](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=1513)]
Also, on the Comma device, there's a ton of CPU usage because it seems like LibUSB is polling.
And I wonder, on Linux, if we can go one level lower and directly use the interface libUSB is using.

##### **Geohot** [[00:25:35](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=1535)]
Yeah.
Yeah, I mean, we can do that.

##### **Nimlgen** [[00:25:40](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=1540)]
Actually, it's pretty good.

##### **Geohot** [[00:25:41](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=1541)]
Do you know what it is?

##### **Nimlgen** [[00:25:44](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=1544)]
Yeah, I looked into that.
I think it should be, as far as I remember, it's just mostly..
Yeah, just like the same, it just talks to the CSFS to do all this stuff with USB.
But yeah, actually, I'm interested in just looking into the common device timings.
So yeah, I mean, how about the CPU usage there?
Can we plug the GPU into some common device?

##### **Geohot** [[00:26:20](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=1580)]
Um, yeah, let me, yeah, I'll work on that today.
I bought a bunch more of the adapters.
One of the annoying things about doing that, we need a hub.
Yeah, we need a hub because we got to make sure that the network's okay.
But yeah, we'll definitely figure out how to do that.
We'll try to get GPUs on the common devices.

##### **Geohot** [[00:26:43](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=1603)]
Cool.
You think we'll get to the 5090 this week?
Um,

##### **Nimlgen** [[00:26:50](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=1610)]
Yeah, I hope.
So what's the priority, 5090 or driver in Tinygrad?

##### **Geohot** [[00:26:59](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=1619)]
I think the USB device is higher priority, but if you feel stuck, I don't think it's much higher priority.
You're welcome to kind of work on both.
However you, whatever you feel like.
They're both pretty important things to do, especially the 5090 with the runtime.
I'm interested in.. I hope that getting rid of the kernel driver will be easy.
And then in Tinygrad we won't have to deal with maintaining a patched kernel driver anymore.
It'll just automatically get you P2P if you use Tinygrad and remove the driver.

##### **Nimlgen** [[00:27:42](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=1662)]
Yeah, okay.

##### **Geohot** [[00:27:44](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=1664)]
But cool, yeah, whatever.

##### **Geohot** [[00:27:46](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=1666)]
I'd say the USB is slightly higher priority, but only slightly.
Great.
OK.
I saw the PR moving along with WebGPU.

##### **Hooved** [[00:28:04](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=1684)]
Yeah.
I'm pretty happy with where it is.
So a couple of recent changes where I implemented or I limited the ability to realize when capturing the graph.
I don't think we should ban it completely.
I don't think we should ban realize completely.
I sort of wrote about it in the Discord, but basically,
Realizing can be useful if you're just setting stuff up that shouldn't be in the exported graph.
Very convenient to be able to realize.
So I implemented that.
Basically, we're banning realizes if the tensor has input UOps in its graph.
So there's that.
And also there's some annoying edge cases with initializing state after you've captured the graph.
So I thought I could just go and round up all the tensors that had
It's not that simple because if a tensor has state in it and it hasn't been realized, and then you build the graph and the graph does compute on that tensor, then you've mixed together loading state with compute in one tensor.
And so it's not really straightforward to realize only part of that.
The simplest solution is actually just to run the exec items that don't do compute, that just move data around, so buffer copy and view up.
So that seems to work.

##### **Geohot** [[00:29:45](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=1785)]
Well, I think you have to be careful there.
So check out, I have a PR called compile for, which might do exactly what you want.
So instead of separating it based on doing copies and not copies,
I believe, and correct me if I'm wrong about this, but what you're looking for is the set that's independent.
So you could imagine in the graph you have like an input node and an output node, and then there's going to be some nodes that are on that path, and then there are going to be some nodes that are independent from that path.
So everything that's independent from that path, you can run before, and then you want things that are dependent on that path to actually be the ones you capture.
Am I getting it the right thing?

##### **Hooved** [[00:30:31](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=1831)]
I think so.
I just have to see how you define the paths and how you interact.
How do you actually implement that so I can look at it?

##### **Geohot** [[00:30:40](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=1840)]
Here, I will link it in general.
And yeah, I mean, this is like a common story that is happening all over.
And this is like all part of, I think you're really pointing the way for what the jittery factor is going to look like here.
Because I want the JIT, so right now we have this option to the JIT called prune, but it's kind of hacky.
I want this to be done super generically.
And then in the JIT, like you've always defined these things that are like different, like these.
So we have input state, we have implicit input state, we have explicit output state, and then we have implicit output state, which are things like assigns.
So I think that what you're thinking about here is like on the implicit input state, you want to do as much processing as you can that doesn't interfere with the explicit input state.
And that's kind of what this independent path thing is doing.

##### **Hooved** [[00:31:39](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=1899)]
I need to actually look at the code that you wrote.

##### **Geohot** [[00:31:44](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=1904)]
But yeah, no, I think, I mean, this is only going to get easier.
And it's not going to interfere with.. I think the core of your PR is the concept of the graph renderer that produces the JavaScript, and that interface should be quite stable.

##### **Hooved** [[00:32:02](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=1922)]
Yeah, no, I feel pretty satisfied overall with the way I'm capturing the graph.
It's very satisfying.
I don't know, that you're just not running anything or running as much as possible.
It just feels pretty cool.
So OK, I can try to see what you're doing with state and with the paths and so forth.
And then aside from that, like, of course, there's the issues with Chronalize SAT item.
But also, I want to discover if there's anything else just by testing the different WebGPU examples and making sure they still work with the refactor.
So I can do that.
And yeah, we can go from there.

##### **Geohot** [[00:32:52](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=1972)]
Sounds good.
Yeah, I know.
It looks very clean.
Cool.
How are locals coming?

##### **Ignaciosica** [[00:33:11](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=1991)]
So the PR is only blocked now by the
The bug in CI, I couldn't connect yet to the new machine to test if the.. You mean the new Mac?
Yeah.
I mean, I could connect, but it keeps logging me out every five seconds, so I couldn't even install testing dependencies.
It's logging you out?
No, it's disconnecting.
The connection is.. You're tunneling through a gateway machine.
Yeah, I went through green 14 and red 10, and I have the same problems in both of them.

##### **Geohot** [[00:34:00](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2040)]
I see.
You're saying TinyMac 3 is disconnecting you.

##### **Ignaciosica** [[00:34:06](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2046)]
Yeah.
Any ideas?

##### **Geohot** [[00:34:14](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2054)]
Did you see any problem?
It's not high.
Yeah, I checked it too.
I installed unload.
Yeah, but moving gateway one definitely fixed the switch thing.
No, but I mean, gateway one can have a lot of bandwidth if we're hitting stats Tinygrad.
Like, I think it actually was surging that bandwidth.
But I mean.. The times I was monitoring it, it didn't really spike that high.
I didn't see it either, but I don't know.
Moving that one definitely fixed the laggy SSH issue, but this seems like a different issue.
I didn't get any.. I thought it was power management and it was going to sleep.
It disabled sleep on it, so it might be better.
Oh, on the Mac?

##### **Geohot** [[00:35:01](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2101)]
Yeah.

##### **Geohot** [[00:35:07](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2107)]
Wait, so how come I can't SSH to it?

##### **Geohot** [[00:35:10](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2110)]
Okay, I am logged in.

##### **Geohot** [[00:35:39](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2139)]
From something on the network.
I don't see myself being disconnected.
So you're saying you have stable connections to other machines, like Tiny?
Yeah, yeah, yeah.

##### **Ignaciosica** [[00:35:54](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2154)]
I don't have any problem with 14.
I even had a stable connection when I proxied to the TinyAMG2, the one with the MIX300.

##### **Geohot** [[00:36:10](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2170)]
Huh.
I mean, could it be.. So you're logging in with a different user.
I'm just going to add you to authorized keys of the Tiny user and then try that user.
Maybe that's the problem.
Okay.

##### **Geohot** [[00:36:39](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2199)]
Okay, so I added you to the Tiny account.
Try logging in with user Tiny and see if it still does it.
So I'm logged in with user Tiny and I can't imagine why it would be different for me and you.

##### **Geohot** [[00:36:52](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2212)]
And also, what?
Why is it laggy?
We just bought that computer.
It came from eBay.
I don't know.

##### **Geohot** [[00:37:12](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2232)]
It's newer Mac OS?
We know Apple made Mac OS worse.
Okay, so we have.. We will definitely look into this.

##### **Ignaciosica** [[00:37:25](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2245)]
Okay, so we have..
No, the thing I want to test if it's still broken with the new Mac OS release, because disabling the compiler optimizations made the issue disappear in the CI box.
So maybe it's resolved.

##### **Geohot & Ignaciosica** [[00:37:47](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2267)]
Oh, so you're saying if you just set it to O0?
It works.
It works?
I mean, can that be anything but a compiler bug?

##### **Geohot** [[00:38:04](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2284)]
Wow.
Okay.
Can we just find a way to force those tests to use O0?
I was thinking about that, but..

##### **Ignaciosica** [[00:38:30](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2310)]
I mean, it's not.
I want to test first if it's fixed with this new release.
The new Mac OS release.

##### **Geohot** [[00:38:39](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2319)]
Then we could update all the Mac OSes.
Now they all have the SSH issue.
Yes, that's great.
That's great.
We're upgrading them.

##### **Ignaciosica** [[00:38:52](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2332)]
I mean, it's not to solve now, but I'm trying to connect with Tiny User and I still
Can't connect, so I don't know.
Wait, you can't connect or it's kicking you out?
No, now it's like it's setting up SSH host to connect to TinyMac 3 and it's waiting since three minutes.

##### **Geohot** [[00:39:16](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2356)]
I mean, there is something like slow about this too.
I don't know.
Macs don't work anymore.
Apple broke it.
Wait, yeah, I just got a timeout when I tried to connect.
But that time it connected, yeah.
You tried to SSH and it connected.
All right, well, the chaff time expired.
I'm running with a bunch of Vs.
Okay, yeah, but we'll look into that.
If it really is.. I'll test it today, too.
If it really is an O0 thing, that's not.. I can wire it up to just force it to.. Or if it really works with O0, I'm kind of fine with skipping the tests.
It's hard for me to think about a time when you're doing something wrong and it works with O0, but it doesn't work with O2.
The compiler should pretty much guarantee you they're the same, unless there's some..
Obvious wrong thing.
So it works locally on your M3?

##### **Ignaciosica** [[00:40:15](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2415)]
Yeah.
With my M3, it works with all default optimization flags and in civil machines also.
Because I wanted to test the code, and it worked also.

##### **Geohot** [[00:40:30](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2430)]
Interesting.
Cool.
But no, I mean, this is great.
If we can get this merged.

##### **Ignaciosica** [[00:40:39](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2439)]
Yeah, I moved the thing you told me about the alignment to another PR.

##### **Geohot** [[00:40:44](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2444)]
Yeah, that's just what I was going to say.
The alignment thing should be in a different PR, and then anything else should be in a different PR.
No, the rest of it looks like it's actual LDS stuff.
Yeah, let's get the alignment thing merged first.
Actually.
I wonder if the alignment thing can trigger the bug.

##### **Ignaciosica** [[00:41:05](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2465)]
Maybe that's the.. I tested the different alignment configurations when I had access to the TinyCI machine and it didn't fix it.
Also, one thing that I couldn't do much because the disassembled Apple GPU doesn't work for my M3, so I couldn't compare the assembly output.

##### **Geohot** [[00:41:27](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2487)]
Yeah, the M3 has the.. It never worked for M3.
M3 has a totally different bytecode.
But all right, cool.
Yeah, let's try to get this merged today.
We'll skip the O0 thing if we have to.
But very exciting to finally have this done.
I think this is a great step toward making our GEMMs fast.

##### **Geohot** [[00:41:52](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2512)]
All right, we're up to ONNX.

##### **Geohot** [[00:41:59](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2519)]
Quantize ONNX.
The bug wasn't in ONNX.
Yeah, let's get ONNX merged into main Tinygrad.
Is removing ONNX protobuf parsing a requirement to merge ONNX into main Tinygrad?
I think no.
It's not that difficult.
I mean, you're just going to need to write a parser for protobuf.
It's probably on par with like GDML kind of stuff.
The parser does not have to be complete for all the protobuf either.
It just needs to work for ONNX.
The thing that I'm really excited about about having our own protobuf parser is that we could remove the copy.
Like right now, if you do ONNX load, it's loading that whole thing into RAM, which is kind of annoying.
And yeah, then we can just directly move from the
Once we have these things in Tinygrad, they'll happily just run on the GPU or run wherever they are.
And yeah, we can avoid this extra copy.
So yeah, that's a $300 bounty.
If somebody's interested, it's doable in a day.

##### **Geohot** [[00:43:11](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2591)]
If you put a good day into it.

##### **Geohot** [[00:43:20](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2600)]
Yeah, I think that's the kind of thing also where ChatGPT can definitely help you a lot.
You can't use AI to write code you don't understand, but I think it used to be a day, and I think with the right person who's good with ChatGPT, they could do it in three hours.
But no, yeah, I don't think it's a requirement.
I'm fine with just requiring import of ONNX for now to get that merged, but even better if we can remove that requirement.

##### **Geohot** [[00:43:55](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2635)]
Cool.
Okay, Z3 Fuzzer?
Yeah, I haven't really worked on that last week.

##### **Sied Lykles** [[00:44:06](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2646)]
So same thing that needs to be done about the.. I guess there's more stuff that needs to be fixed first.

##### **Geohot** [[00:44:14](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2654)]
What needs to be fixed first?
Sorry.

##### **Sied Lykles** [[00:44:17](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2657)]
There's a rewrite rule now that's incorrect for some..
They're falling.
The problem is if you fix it, then there's a lot of regression in open pilot, like gated loads.
So, yeah, to fix that, I was trying to make some improvements to uop-given-valid, so I can still do the same simplification, but..

##### **Geohot** [[00:44:53](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2693)]
So the way that I would deal with this is I would just make it a context variable to disable that optimization.
You can leave it on by default so it's still good for OpenPilot, but just disable it when you're fuzzing and then, yeah, you won't hit it.
And then we know that's something we have to fix, but we can still move forward on the fuzzer.

##### **Sied Lykles** [[00:45:14](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2714)]
Okay, yeah, I can do that.
Sounds good.

##### **Geohot** [[00:45:17](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2717)]
Cool.
Yeah, no, I mean, and finding bugs is a gift.
I mean, that's great.
The whole point of the fuzzer is to find subtle bugs in these rewrite rules that would cause huge problems for somebody down the line.
So yeah, it sounds like we're already finding stuff.
That's great.

##### **Geohot** [[00:45:34](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2734)]
Yeah, I mean, it's almost done then.
Cool.
You want to talk about cloud stuff?
Sure.
Probably wiping machines today.
All of them?
The ones I can get through.
Alright.
We're moving them all to 24-4.
New image, be nicer.
Some of them are moving to other stuff.
What other bugs are we adding to Red Sea Eye?
Oh.
I don't know, like 15?

##### **Geohot** [[00:46:17](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2777)]
Yeah, we'll put another box on RedCI.
We'll kick people off.
I mean, it'll be nice to just have all the boxes.
It'll be so nice.
I love this idea of a real MLPerfCron training job.
Yeah, so we'll add one more box to RedCI.
I mean, or, I don't know, you want to stand up Tiny11?
It's an option as well.
Could do that.

##### **Wozeparrot** [[00:46:41](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2801)]
No Rackspace.

##### **Geohot** [[00:46:43](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2803)]
Just Rackspace.
Upper left, there's no power, but there's rack space.
The room is out of power.
I mean, actually, not only is the room out of power, I think that if we used the power, if we ran all those boxes at full load, I think that room would get to 110 degrees.
So we're going to have to do something about cooling.
Um..
By the way, I don't know.
We got a lot of people in the meeting today.
I don't know if anyone's interested in coming to work here for the summer on supply chain management stuff, just TinyBox management stuff, like physical computer builder kind of stuff, sales support, what else?
Everything having to do with the physical computers.
Buying box fans from Home Depot and sticking them in the window.
Alright, so we're re-imaging the boxes this week.
And then if no one picks up the GPU hashing bounty, because I kind of need that to move forward.
Yeah, yeah.
I mean, okay, so we've decided on 4 megs for the block size.
I mean, do you think we can get 4 megs to fully saturate the GPU while it's hashing?
Like, how quickly can we compute a 4 meg hash on a GPU?

##### **Wozeparrot** [[00:48:09](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2889)]
I feel like we can get it to saturate.

##### **Geohot** [[00:48:13](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2893)]
You think?
Maybe.
Saturate what?
Oh, I see.
Like, just 4 megs.

##### **Geohot** [[00:48:22](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2902)]
Well, just 4 megs, yeah.
No, I mean, there'd be some in parallel, too.
I don't know, like, how quickly can we compute a 4 meg hash is kind of the question.

##### **Chenyu** [[00:48:30](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2910)]
Yeah.

##### **Geohot** [[00:48:31](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2911)]
Right, because, like.. No, no, no, no, no, no, no.
I want something that's, like, close to the GPU memory.
Or maybe, I don't know, 100 gigabytes a second would be good.
And then we could do 10 in parallel and get the full.
Yeah, I'm okay with having to require 10 hashes, but we have to basically be running a massive amount of these hashes at GPU memory speed.
I don't know if this is at all doable.
Maybe this is just a pipe dream.
I don't know.
We might need to lower the block size.
You want to lower the block size?
Or increase it more.
This is more overhead.
I think four is kind of the compromise.
Yeah, we're building out a distributed file system for Tinygrad's cloud.
Basically, yeah, it's just going to be like an easy way to, right now you can like load tensors from URLs and stuff.
And we'll still support loading tensors from URLs.
But what this is going to do under the hood is we'll have some database that maps URLs to a hash.
And then the hash is accessible in the file system.

##### **Nimlgen** [[00:49:43](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2983)]
In terms of placement stuff, is that their crush?

##### **Geohot** [[00:49:48](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2988)]
I was looking into where crush is.

##### **Wozeparrot** [[00:49:49](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2989)]
It's basically what you want.

##### **Geohot** [[00:49:50](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2990)]
Yeah, crush.

##### **Wozeparrot** [[00:49:53](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2993)]
Because it's a deterministic, basically user-defined.

##### **Geohot** [[00:49:56](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=2996)]
Yeah.
I mean, EQ value works like this too, where the subtleties here become, okay, we add another drive, what happens?
Yeah, that's basically the problem with crush.
Yeah.
When you..
Start scaling it up.
Like, after you've already done a deployment, you have to replace everything.
Yeah, let's avoid that.
I don't know if we can.. Yeah, and then the way people usually solve this is they spin up a metadata server, and then that tells you where everything is placed.
So those are the two categories of distributed cloud systems.
A metadata server is okay.
I just don't want to have to require for each hash to hit some central server to say where that actual hash is stored.
I mean, that's usually the solution.
Oh..
Like basically all the big ones are either metadata server or you have.. Big rebalance issues?
Yeah.
Maybe big rebalance issues is okay then.
Because that metadata server has to be so high throughput.
It's not that high throughput.
The blocks are generally smaller and you can cache a lot of the stuff on the client.
And then if we lose the metadata server.. Yeah, and that's where it gets complicated.
We're going to do backups and then there's state that can be out of sync.
Oh, what a nightmare.
Connection seems stable now with Tinyuser.
I don't know if it's that or the power management change.
Who knows?
Whatever.
Glad it's working.
All right, so other bounties.
Let's just run through bounties for new people here.
Also, if anyone has any questions, just post them in general.
This is a good time to ask questions.
Yeah, so there's a $300 bounty for loading ONIX without the ONIX library.
Just parse some protobufs.
Oh, general public service announcement.
Please do not submit your Codex PRs.
Codex is not good.
There was one last week where it just changed the white space around and said it solved the problem and made no functional change to the thing.
It's not good.
Codex seems, yeah, I don't know who has a code base that Codex can actually improve, but that code base is way lower quality than ours.
OpenPilot uses it?
Interesting.
Well, yeah, but no, look, you can obviously use AI.
I'm encouraging you to use AI for loading ONIX without the ONIX library.
But if you don't read what the AI wrote and understand it, it's probably just wrong.
And if you're not capable of understanding it, don't submit it as a PR.
You're wasting everybody's time.
All right.
Make Tinygrad Whisper work on Tiny Recording.
I think there's some bug for that.
$200 for that.
5090 support.
I think we're going to get to that.
Do you still want the ACO shader compiler back in?
I mean, yeah, I'd pay someone out if they did it.
Yeah, if someone wants to write the ACO shader compiler back in, that's pretty easy.
I can't believe I'm offering $300 for that.
Crypto hash function, I know there's some progress on Blake.
If someone can get a crypto hash function, that's like.. Blake is probably not that great for content address.
It only has 2 to the 64 bit collation resistance.
What do you mean?
Someone has a collision in Blake?

##### **Wozeparrot** [[00:53:35](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=3215)]
No, no, it's just not as great as, like, SHA-256.
Wait.
The collision resistance is less.

##### **Geohot** [[00:53:43](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=3223)]
But if it's 2 to the 64, I could probably find a collision.

##### **Chenyu** [[00:53:46](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=3226)]
Yeah, it's not that great.

##### **Geohot** [[00:53:47](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=3227)]
So it's not a crypto hash function?

##### **Chenyu** [[00:53:48](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=3228)]
It is a crypto hash function.

##### **Geohot** [[00:53:50](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=3230)]
What the hell kind of crypto hash function can I find a collision in?

##### **Sied Lykles** [[00:53:54](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=3234)]
But it's 2 to the 64, at least claim collision resistance.
It's a 128-bit hash, but it only has 64 bits.

##### **Geohot** [[00:54:00](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=3240)]
Well, everything only has 64 bits.
Yeah, yeah.
Oh, yeah.
It's an 128-bit hash?
It's a 128-bit hash, but it only has.. So everything is only going to have half, then?

##### **Wozeparrot** [[00:54:11](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=3251)]
Yeah, yeah.

##### **Geohot** [[00:54:12](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=3252)]
You can always birthday attack to divide the thing by two.
So maybe it's fine.
I mean, I don't know.
It's not like.. This isn't really for security.
What would happen if.. I mean, we can't have something like..
Finding one collision with a birthday attack, I don't think would break our whole thing.
I think it would just break that user's flow.
Versus what you can have is something that can do like pre-image attacks.

##### **Geohot** [[00:54:38](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=3278)]
Yeah.
So, I don't know.
But cool, we could find a clue.

##### **Nimlgen** [[00:54:47](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=3287)]
I think it has about the same amount of collision resistance.

##### **Geohot** [[00:54:49](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=3289)]
It's a little bit better than XXHash, at least according to SMHash.
Well, XXHash looks more like CRC to me.
Xhash is not cryptographic.
Yeah.
But the collision resistance of those two are about the same.
At least.
Interesting.
XmHasher.
XmHasher has good tests on this.
How can you get a task assigned to you?
What do you think this is?
Who do you think is assigning tasks?
You can just decide I'm doing this task.
Uh, UVN mentioned XXHash.
I looked at it, it looks more like CRC to me.
We can't do that.

##### **Wozeparrot** [[00:55:31](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=3331)]
It is a little bit more CRC.

##### **Geohot** [[00:55:33](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=3333)]
But like, pre-image?
You know, we definitely want something cryptographic.
We definitely want something with high pre-image resistance.
2 to the 64, you're telling me 2 to the 64, how much GPUs do we need to run, to find a collision in Blake 3?
Can we do that?
Not GPUs, but for C8 large instances on AWS, it's like 80 for a couple months.
80 for a couple months.
I don't know.
We've done a whole rabbit hole last night of trying to compute digits of pi.
I'm trying to get Torch Index Push to work.
Doing it naively leads to two kernels being generated by every assign.
Oh, I'm not worried about that.
Just writing the function with UOps is acceptable?
No.
If it's more kernels, that's fine.
But if it's written with UOps, I don't think that's fine.
I'm not even sure why you'd want to do that.
Add HVAC decode support through COVID to the NV driver.
Someone made some progress on that.
500 bucks if someone can do that.
RKNN backend.
Someone's got that rock chip.
Flash attention.
That's going to be, it will make that hard.
That's going to be hard.
Oh, the MM peak one.
I think someone got close with that.
So I think hopefully we can just port that to use the Tinygrad runtime infra.
I saw someone linked a GitHub repo for that.
Yeah, and then a bunch of torch things.
I saw a PR for the moving the stuff off the CPU back end.
Is this real?

##### **Geohot** [[00:57:27](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=3447)]
Why is it going to the devices?
This looks kind of real, but I.. Oh, maybe it does have to go to the devices.
I don't know.

##### **Geohot** [[00:57:54](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=3474)]
Yeah, I don't know, this Mr. Super Wealthy looks kind of real.
I mean, the tests are failing.
My Custom Tests?

##### **Wozeparrot** [[00:58:05](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=3485)]
Wait.

##### **Geohot** [[00:58:07](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=3487)]
It's added by this?
What?
We actually have something in there called My Custom Tests?
How'd this get merged?
Whatever.
But yeah, when that's passing the test, we'll look into that.
HLV CIFAR, I think I actually locked that bounty.
I think someone's making progress on that.

##### **Geohot** [[00:58:34](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=3514)]
Yeah, the ad guide, that's progress.
We'll lock that.
You got tensor-unfold working, movements only, tensor-gather, tensor-unfold, let's say.
So what is tensor-unfold supposed to do?
I think that's a view.

##### **Geohot** [[00:59:24](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=3564)]
Expand, then shift a little bit, then slice.
Oh yeah, it definitely shouldn't be done with Gather.
Even Torch says it's a view, so it should be a view.
If Torch says it's a view, yeah, yeah, yeah.
So you definitely can't do this with Gather.
The problem with Gather is you're creating this big tensor that's

##### **Geohot** [[00:59:54](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=3594)]
You're creating this big tensor full of indices, and then you're loading into it when you don't have to.
Cool.
What else we got?
Someone wants to do the Torch compile stuff.
And someone wants to start benchmarking GPT fast.
Cool.
Got a whole bunch of open bounties for people.

##### **Geohot** [[01:00:31](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=3631)]
New people, if you don't know the link, it's bounties.tinygrad.org.
We're also considering a Tinygrad hackathon in person sometime next month or the month after.
And yeah, I was wrong at first.
I had the thing only for Tinygrad contributors.
If you're a Tinygrad user, I mean, that's what I realized.
Like, we're building a library here.
We need to get users of the application or people who are excited to use Tinygrad who want to come to the hackathon.
So just, you know, write some toy thing with Tinygrad.
Submit that as a hackathon submission.
And yeah, we'll invite you out.

##### **Geohot** [[01:01:10](https://www.youtube.com/watch?v=gZ6FvO5RYz4&t=3670)]
We'll make it fun.
Cool.
That's it for this week.
I think so.
Bye.
Thanks, everyone.
