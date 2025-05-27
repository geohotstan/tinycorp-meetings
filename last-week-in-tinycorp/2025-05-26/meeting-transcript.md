# 2025-05-26 Meeting

### Meeting Agenda

**Time:** 9am Monday San Diego time
- company update
- tenstorrent
- mlperf ci, sdxl search speed
- scheduler
- driver
- wozeparrot stuff
- webgpu
- locals
- onnx (proto parser), move to tinygrad proper
- z3 fuzzer
- other bounties

### Audio

[Youtube Link](https://www.youtube.com/watch?v=bktO9YRV8pc)

### Highlights

- **[Company Update](#geohot-000005)**: Tinybox V2s shipped last week; Green V2s currently delayed due to case shortages, expected within 2-3 weeks; Reds available for immediate shipping.
- **[Tenstorrent Update](#geohot-000115)**: Tenstorrent backend integration stalled due to incomplete hardware and software stacks; progress appears worse compared to previous versions.
- **[Scheduler and View Operations](#geohot-000115)**: Implementing view inversion via caching (reverse cache), aiming to simplify `becomes_map` significantly.
- **[MLPerf CI and Stable Diffusion XL](#chenyu-000328)**: Cron jobs set up to log MLPerf results; adding similar timing metrics for Stable Diffusion XL searches and first steps.
- **[Scheduler Update (gbarrier)](#qazalin-000640)**: Introduced `gbarrier` to simplify graph scheduling; utilizes tags for efficient graph transformations and kernel separation.
- **[Multi-GPU Support (mselect, mstack)](#geohot-001249)**: Implemented `mselect` and `mstack` to optimize multi-GPU graph execution and improve AllReduce performance.
- **[NVIDIA Driver Support](#nimlgen-001750)**: Progress on PCI driver for 5090 GPU; USB copy-out performance currently at ~3MB/s, seeking optimization to reduce latency.
- **[Wozeparrot Hashing Performance](#wozeparrot-002443)**: Hashing implementation facing slow scheduler performance (~2 minutes), suggesting underlying issues.
- **[WebGPU Export Improvements](#hooved-002636)**: WebGPU refactor completed; automated end-to-end tests implemented; working on improved state handling and avoiding forced realizations.
- **[ONNX Parser and Integration](#b1tg-003728)**: ONNX parser working but currently copies tensors to CPU, to be optimized to avoid unnecessary tensor copies.
- **[Z3 Fuzzer (Symbolic Rewrite Rules)](#sied-lykkles-004525)**: Z3 fuzzer updated to test validity of symbolic rewrite rules; successfully identified several correctness issues.
- **[Bounty Updates (RetinaNet, LM Eval, FP8)](#geohot-005130)**: New bounties added, including fixing LM Eval numerical stability tests and RetinaNet post-processing; FP8 support PR pending detailed validation.
- **[Flash Attention Optimization](#geohot-005827)**: Current fused softmax kernel is two-pass; investigating if kernel optimizations or warp-level operations could improve performance.


### Transcript
##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=bktO9YRV8pc&t=0)]
Let's start with company updates.

##### **Geohot** [[00:00:05](https://www.youtube.com/watch?v=bktO9YRV8pc&t=5)]
A bunch of tiny boxes shipped last week.
Finally, we're shipping the V2s.
We're waiting to get more cases.
They should be here soon.
I paid extra to ship them air from China.
So we have all the other parts.
So hopefully more will ship this week.
But if not, next week.
And that should be everyone who's ordered one so far.
So if you order a Tinybox Green V2 today, it will probably come in two to three weeks.
And if you order a Red, it will ship literally tomorrow.

##### **Chenyu** [[00:00:41](https://www.youtube.com/watch?v=bktO9YRV8pc&t=41)]
So order a Red.
Wasn't there a discount on Red?

##### **Geohot** [[00:00:49](https://www.youtube.com/watch?v=bktO9YRV8pc&t=49)]
There was a discount on Red that nobody bought.
I don't get it.
I mean, Red software is actually getting pretty good.
So I think the discount's over.

##### **Chenyu** [[00:00:57](https://www.youtube.com/watch?v=bktO9YRV8pc&t=57)]
You can pay full price now.
Company update?

##### **Geohot** [[00:01:15](https://www.youtube.com/watch?v=bktO9YRV8pc&t=75)]
You can talk about other things you were working on.
I'm not too sure, but I only put 10th Torrent.
I know there are some other ops and multi stuff that you were working on.
Yeah, I don't have too much to say on 10th Torrent.
The hardware is just not ready.
Their software is just not ready.
Their stack is not ready for someone to write a Tinygrad stack to write a Tinygrad backend.
I don't know.
I was hoping it would be better.
It actually seems worse than the last one.
When I got their card a year or two years ago, the documentation was actually better.
The software was better.
I don't know.
I don't know.
I don't think they're going in that direction.
The other thing I'm going to work on, well, what I worked on a lot last week was scheduler stuff.
I'm going to write the function to invert views, to go from views back to movement ops, but I'm not going to do it by reasoning about the problem, I'm going to do it by caching.
So that'll probably take a few days, but then...
I think that'll simplify becomes map a lot, because we can just put views in the tensor graph.

##### **Chenyu** [[00:02:39](https://www.youtube.com/watch?v=bktO9YRV8pc&t=159)]
It just stores any previous moving ops that create all the views, something like that?

##### **Geohot** [[00:02:47](https://www.youtube.com/watch?v=bktO9YRV8pc&t=167)]
Yeah, basically.
So we're already storing them, actually.
We're using Functool's LRU cache to cache every
A movement op in the forward direction.
So I just added a reverse cache and then you can look in the reverse cache and figure out how to reconstruct a view given movement ops.

##### **Chenyu** [[00:03:10](https://www.youtube.com/watch?v=bktO9YRV8pc&t=190)]
OK.
It sounds good.
OK, we can move on.

##### **Chenyu** [[00:03:28](https://www.youtube.com/watch?v=bktO9YRV8pc&t=208)]
So for MLPerf CI, I have been adding stuff, a log that I wasn't missing.
And I should have something on the Grafana dashboard later today or tomorrow.

##### **Chenyu** [[00:03:47](https://www.youtube.com/watch?v=bktO9YRV8pc&t=227)]
Cron job is running.
It's just not logged properly for some reason.
They keep hanging.

##### **Geohot** [[00:04:01](https://www.youtube.com/watch?v=bktO9YRV8pc&t=241)]
For now, we run every MLPerf script twice for the MLPerf submission.
The first time for setup, the second time is for the full run.

##### **Chenyu** [[00:04:12](https://www.youtube.com/watch?v=bktO9YRV8pc&t=252)]
Logging includes the setup time, the full run time, and the step time.
It's not identical to our submission because the way the timing
The timing works.
They should be similar, and we should expect to see, over time, the setup times drop, and the step times should ideally drop as well.

##### **Geohot** [[00:04:42](https://www.youtube.com/watch?v=bktO9YRV8pc&t=282)]
Yeah.
It's good that we're finally addressing the CI machines crashing.
I mean, we really got to figure out why they're crashing, but at least have a way to reset them.

##### **Chenyu** [[00:04:49](https://www.youtube.com/watch?v=bktO9YRV8pc&t=289)]
Yeah.

##### **Geohot** [[00:04:55](https://www.youtube.com/watch?v=bktO9YRV8pc&t=295)]
I don't know about that, but hopefully this should at least have something that runs a longer job on CI.
And if anything breaks, we should at least notice.
So I want to add something similar for, in this case, stable diffusion XL.
So basically,
I think it's also a Chrome job.

##### **Chenyu** [[00:05:22](https://www.youtube.com/watch?v=bktO9YRV8pc&t=322)]
We probably don't want it to run every master commit.
So storing the time to search, the time to the first step, that would be the search time, and the step after that.

##### **Geohot** [[00:05:41](https://www.youtube.com/watch?v=bktO9YRV8pc&t=341)]
So it captures both the
Setup time for searching XTXL and the final step time.
And after I have this in the CI, again, it should ideally be the setup time drop and the step time drop as well.
Yeah.
If we have a good way to do this, I think we could probably also do it for the llamas we're already beaming in benchmark.
We only instrument the token time.
We don't instrument the setup time.
Yeah, I think for Lama should be easier since we have already been made.
We just need to log the time to first token or something like that.

##### **Chenyu** [[00:06:28](https://www.youtube.com/watch?v=bktO9YRV8pc&t=388)]
Cool.
OK, let's move on to scheduler.

##### **Qazalin** [[00:06:40](https://www.youtube.com/watch?v=bktO9YRV8pc&t=400)]
We now have gbarrier, which is very, very nice.
It enables a lot of simplification in the grouper, I think.
It was really hard to, like, you would basically get infinite loops whenever you would try to do any sort of grouping algorithm.
I'm glad that's merged.
It fixed a bunch of the fragility issues you saw last week with the... Good question.

##### **Geohot** [[00:07:04](https://www.youtube.com/watch?v=bktO9YRV8pc&t=424)]
What does gbarrier do?
I think I misled.
So...

##### **Qazalin** [[00:07:11](https://www.youtube.com/watch?v=bktO9YRV8pc&t=431)]
The barrier is basically a global memory barrier between two UOPs.
So it's the opposite of like fusion.
It's a wall saying that everything before this is a load and you treat it as a buffer.
And this was hard before to express.
Yeah, go ahead.

##### **Geohot** [[00:07:34](https://www.youtube.com/watch?v=bktO9YRV8pc&t=454)]
GBarrier does the same thing as Contiguous.
The only reason that I made GBarrier and Contiguous distinct is Contiguous is a user op, so you can't reorder Contiguouses.
But GBarrier is a system op, and you can reorder them however you want.
So GBarrier guarantees the kernel creation doesn't cross GBarrier, basically.
Yeah, it just encodes that.
Instead of encoding that in a dictionary, it's now encoded explicitly in the kernel.
And the main thing that, oh, this is something I should have talked about.
The main thing that makes this possible is tags.
So I added one more property to the UOP called tag.
And there's many algorithms that are just very easy to express as like two walks across the graph.
You do one walk on the graph and then you tag
Yeah, it's really hard to express things like rewriting x to x.gbarrier to put a gbarrier after the x.
Because the problem is if you put a gbarrier after the x with a rewrite rule, x is still in the graph, and of course that rewrite rule is just going to want to put another gbarrier after the x. So instead of rewriting x to x.gbarrier, I rewrite x to x with tag.gbarrier, and x with tag doesn't have a gbarrier added to it.
So that was the first practical use of tags.
And yeah, I think it should make those algorithms a lot easier to express.
And I'm hoping we can delete that entire the thing that changes becomes map when I fix the view thing.
Is that true?

##### **Qazalin** [[00:09:33](https://www.youtube.com/watch?v=bktO9YRV8pc&t=573)]
I am very looking forward to deleting that part.

##### **Geohot** [[00:09:36](https://www.youtube.com/watch?v=bktO9YRV8pc&t=576)]
Yeah, whenever I see code that looks like that, because right now, I'm not sure exactly what the case that doesn't work is, but like Beautiful MNIST is copying the entire data set from the disk every step.
And I tracked it back to the kernelized PR.
I saw also someone in the PyTorch PR complaining about kernelized.
Maybe it's the same bug.
But yeah, no, I mean, I just, I like, I see the part that obviously has the bug and it's the part that is like, I can't figure out why it's wrong.
Like I read that becomes map thing a whole bunch and like, yeah, that should be all the cases, but it's clearly not.
I don't know.
Maybe there's some like double indirection stuff.
That doesn't handle?

##### **Qazalin** [[00:10:21](https://www.youtube.com/watch?v=bktO9YRV8pc&t=621)]
Yeah, when you have a view, you have double interactions.
So the copy of a view becomes actually a view of a copy.
And then that copy base itself, well, that's not realized.
It's a best effort, what exists, but it's not.

##### **Geohot** [[00:10:39](https://www.youtube.com/watch?v=bktO9YRV8pc&t=639)]
Yeah, if something...
If something is best effort, we just shouldn't be writing it.
We have to wait until we're writing it the right way.

##### **Chenyu** [[00:10:54](https://www.youtube.com/watch?v=bktO9YRV8pc&t=654)]
If there's cases that that thing won't handle.

##### **Qazalin** [[00:11:02](https://www.youtube.com/watch?v=bktO9YRV8pc&t=662)]
What would you suggest we do?
It's going to be a view thing.
I would want to return tensor map and just

##### **Geohot** [[00:11:10](https://www.youtube.com/watch?v=bktO9YRV8pc&t=670)]
Yeah, when I fix the Vue thing, we can return TensorFlow?

##### **Qazalin** [[00:11:14](https://www.youtube.com/watch?v=bktO9YRV8pc&t=674)]
Yes.

##### **Geohot** [[00:11:15](https://www.youtube.com/watch?v=bktO9YRV8pc&t=675)]
All right, I think that's going to take me half this week, but we'll get that.

##### **Qazalin** [[00:11:21](https://www.youtube.com/watch?v=bktO9YRV8pc&t=681)]
Also, I'm looking for your mselect.

##### **Chenyu** [[00:11:26](https://www.youtube.com/watch?v=bktO9YRV8pc&t=686)]
Yeah, the remove contiguous PR?

##### **Qazalin** [[00:11:29](https://www.youtube.com/watch?v=bktO9YRV8pc&t=689)]
Yes, I have it ready.

##### **Chenyu** [[00:11:33](https://www.youtube.com/watch?v=bktO9YRV8pc&t=693)]
Oh, you fixed that, great.

##### **Qazalin** [[00:11:36](https://www.youtube.com/watch?v=bktO9YRV8pc&t=696)]
I'm going to work on mstack2.
I'm sorry about the assign graph.
It was really bad.
And I'm glad gbarrier is done, because right now it's exactly as we specced out, where assigns exist in the local graph.
So it's completely obvious what you should do in that point for your substitutes.

##### **Chenyu** [[00:11:59](https://www.youtube.com/watch?v=bktO9YRV8pc&t=719)]
Assigns exist in the local graph.
Wait, huh?

##### **Qazalin** [[00:12:08](https://www.youtube.com/watch?v=bktO9YRV8pc&t=728)]
So before, when it was bottom-up?

##### **Chenyu** [[00:12:14](https://www.youtube.com/watch?v=bktO9YRV8pc&t=734)]
Oh, wait.
You merged the top-down stuff?

##### **Qazalin** [[00:12:16](https://www.youtube.com/watch?v=bktO9YRV8pc&t=736)]
Yes.

##### **Geohot** [[00:12:17](https://www.youtube.com/watch?v=bktO9YRV8pc&t=737)]
Great.
Oh, good.
Then finally, I think we can reason.
I think, yeah.
I wanted mselect to wait until the top-down stuff was merged, because it's really hard to reason about the bottom-up stuff.
Yeah.

##### **Qazalin** [[00:12:28](https://www.youtube.com/watch?v=bktO9YRV8pc&t=748)]
mstack is not very beautiful, actually.
You can see exactly what you need to do.
Because when there's assigns and buffers in the graph,
It's expressed in this.
The problem with that graph was that you didn't see it in this at all.
So yeah.

##### **Chenyu** [[00:12:44](https://www.youtube.com/watch?v=bktO9YRV8pc&t=764)]
Cool.
Yeah.
One question again.
What's MSELECT, MSTACK?

##### **Geohot** [[00:12:49](https://www.youtube.com/watch?v=bktO9YRV8pc&t=769)]
So it's just
So multi is now all of one.
So instead of having four times as many UOPs for four GPUs, we just have one UOP that applies to all the devices.
So like if you have two buffers,
A buffer can now, instead of just being on one GPU, a buffer can be on four GPUs, and then you have two buffers on four GPUs, and you can add them together.
And that will dispatch the add kernel on all four GPUs.
So the distinction here is that instead of the size of the graph growing with O of N when you add more GPUs, it grows with O of 1.
It doesn't grow at all.
One of the, there's still a few algorithms, particularly like the way that we do ring all reduce, that require you to go down to the actual device level.
So when you have a buffer with four devices, you can put an M select up on that.
And M select is multi-select, and it will select one of the buffers.
So if you want just the buffer on device two, you can select that with M select two.
An M stack is the inverse of that.
You can put four buffers in, and it'll stack them up.

##### **Chenyu** [[00:14:15](https://www.youtube.com/watch?v=bktO9YRV8pc&t=855)]
You don't really need them to express

##### **Geohot** [[00:14:19](https://www.youtube.com/watch?v=bktO9YRV8pc&t=859)]
Like the general training, if you have an all-reduce op?
So if you have an op that can do all-reduce across the buffers, then I don't think you need mSelect and mStack.
But we don't.
We're not using some system all-reduce library.
We just write the all-reduce in uops.
So if you want to write the all-reduce, you need mSelect and mStack.
You don't need them, but you do need them to make it fast.

##### **Chenyu** [[00:14:45](https://www.youtube.com/watch?v=bktO9YRV8pc&t=885)]
So that's why we're adding them.
They should be simple.

##### **Geohot** [[00:14:57](https://www.youtube.com/watch?v=bktO9YRV8pc&t=897)]
Adding them has shown me exactly where problems are in the scheduler.
We can take them out at some point if we don't need them because right now our all reduce is not O of 1.
Our all reduce is O of N. We have to create ops proportional to the number of devices in order to get the same all reduce performance back.
Is our current OReduce on master the fast one?
It's just not present using the same multi?
No.
So this is a regression from O of 1 multi.
So we have OReduce now?
We have OReduce.
It used to be 14 gigabytes a second.
When I merged O of 1 multi, it went down to six.
Now with M select, it's up to nine.

##### **Chenyu** [[00:15:52](https://www.youtube.com/watch?v=bktO9YRV8pc&t=952)]
And with M stack, we should get the rest of it back.
OK, great.

##### **Geohot** [[00:16:02](https://www.youtube.com/watch?v=bktO9YRV8pc&t=962)]
But you know, I mean, it had to be done.
It halved the BERT scheduling time on six GPUs.
And it makes a whole bunch of things a lot easier to reason about.
Like there's now, we can now like, you can use device num.
in ShapeTrackers as a magic variable that tells you which device it's on.
So we used to have to compile kernels.
Sometimes we'd have to compile different kernels for each device.
But you updated the multi to not allow mismatched sharding.
And then the only ones that were left were just a few really very simple cases, where if it just knew the device num, it could just be a simply parametrized kernel.
So that's what it is now.

##### **Chenyu** [[00:16:56](https://www.youtube.com/watch?v=bktO9YRV8pc&t=1016)]
OK, that makes sense.
Anything else for scheduler?

##### **Qazalin** [[00:17:03](https://www.youtube.com/watch?v=bktO9YRV8pc&t=1023)]
Yeah, I posted to use removal PR on the general.
If you can take a look, I think for the first few months, I'll probably ask for your review, George.
Cool.
It looks good.

##### **Chenyu** [[00:17:15](https://www.youtube.com/watch?v=bktO9YRV8pc&t=1035)]
Yeah, it's good.
Yeah, it looks good.
Good?
OK.
Sounds good, let's move on to driver.

##### **Nimlgen** [[00:17:50](https://www.youtube.com/watch?v=bktO9YRV8pc&t=1070)]
Yeah, so our NWP can't now support, now supports 5090s, and I hope all other black holes as well, maybe even like GB200s.
But you think it's the same for GB200?
I mean, QMD is the same.
But yeah, QMD is the same.
Maybe some classes are different.
But that's a quick fix if they're different.

##### **Geohot** [[00:18:28](https://www.youtube.com/watch?v=bktO9YRV8pc&t=1108)]
Cool.
So yeah.
Yeah, it's probably worth, if you think it's like a little, I don't know.
I mean, we don't own a GB200.
But yeah, no, I tested on the 5090.
It could work.
It seems to work.

##### **Nimlgen** [[00:18:42](https://www.youtube.com/watch?v=bktO9YRV8pc&t=1122)]
Yeah, so yeah, started to this in the PCI driver.
So yeah, hope to finish it this week.
It doesn't look really complicated.
I think our main target is 5090 right now, because the path is a bit different between

##### **Geohot** [[00:19:13](https://www.youtube.com/watch?v=bktO9YRV8pc&t=1153)]
I looked into it a bit.
The 5090 looks even simpler.
I mean, the 4090 has this extra stage of indirection before it boots the GSP.
But the 5090, it looks like you pretty much just passed the GSP into the boot room.
Yeah.
Cool.
That and then any progress on copy out speed for USB?

##### **Nimlgen** [[00:19:38](https://www.youtube.com/watch?v=bktO9YRV8pc&t=1178)]
So not much progress there.
I mean, we can merge like this.
I can clean up, and we can merge like 2x sped up.
So it's about 3 megabytes a second.
But yeah.
Yeah, but we're still have hope to yet to find these like way to do this, so to eliminate this device.

##### **Geohot** [[00:20:07](https://www.youtube.com/watch?v=bktO9YRV8pc&t=1207)]
Yeah, the 3 megabytes per second is still doing an M-copy in 8051.
Yeah.
Yeah, no, I mean, we got to find that.
I know it's annoying.
Kama has one they're testing now, and they're getting, I think now it's down to 100 milliseconds, but that's still 2x too slow.

##### **Nimlgen** [[00:20:30](https://www.youtube.com/watch?v=bktO9YRV8pc&t=1230)]
Yeah, I've tested it on Comma's.
Actually, the
Um, yeah, so the, the copy out speed is definitely bad, but also it takes like three times more time on the CPU and actually like the CPU alone is like 30 milliseconds or so on Comma's while it's yeah.
Can we go a lower level than Lib USB?
Yeah, but actually I need to profile it better.
Maybe we do something stupid in Python.
I'm not sure.
Actually, yeah, because actually it looks like this tag, the Linux USB stack is faster than the one in macOS.
Like it can, it actually handles better like several streams.
I had
Like for PCI rights, I just limited it up to four for MacOS because it's just, I benchmark that to be the fastest way.
So it's better on Linux, but yeah, still, I think, yeah, because the CPU is slower, like the whole time is slower.
So yeah, I'll profile that.
Maybe we can try to use, yeah.

##### **Geohot** [[00:21:58](https://www.youtube.com/watch?v=bktO9YRV8pc&t=1318)]
Yeah, no, Comma's excited about using that once it's fast enough.
But yeah, I mean, I do think we have to fix copy out as well.
I mean, even for the 27K, for the model stuff, it's still slow.
Yeah.
But cool.
If you really think the PCI thing for the 1590 is only going to take a week, that'd be amazing.

##### **Nimlgen** [[00:22:28](https://www.youtube.com/watch?v=bktO9YRV8pc&t=1348)]
Yeah, do not see anything hard there, at least not.
Yeah, I didn't really look at what the, like, what's the communication channel with the GSP?
Yeah, actually, it should be Q. So there is actually, like, to set up the GSP, and I'm actually just
Implemented that right now.
So it just, yeah, you just write into the registers.
There is some like call, there's some bootloader called FMC.
Yeah.
And you just poke some messages to it with the location to the GSP, which should be in VRM.

##### **Geohot** [[00:23:16](https://www.youtube.com/watch?v=bktO9YRV8pc&t=1396)]
Yeah, the setup part looked easy.
No, but what I'm saying is once you have the GSP booted, how do you send it?
You're sending it the same ioctl commands that you send the kernel?

##### **Nimlgen** [[00:23:31](https://www.youtube.com/watch?v=bktO9YRV8pc&t=1411)]
Yeah.
I mean, maybe some.
There should be some processing kernel for the memory things.
Yeah, actually, the Rema logs, I think they just go straight to the DSP with some security checks.
And this UVM stuff, which is like for memory management, it's, of course, in kernel.

##### **Geohot** [[00:23:55](https://www.youtube.com/watch?v=bktO9YRV8pc&t=1435)]
The GSP is managing the page tables on the GPU?

##### **Nimlgen** [[00:23:59](https://www.youtube.com/watch?v=bktO9YRV8pc&t=1439)]
I don't think so.
No, no, no, no, no, no, no, no.
I mean, yeah, there are several file descriptors we open, and there are different IOC tables we send.
Oh, yeah, there's like NVIDIA, UBM, and .
Yeah, I just go straight to the GSP, like the device stuff and all these things.

##### **Chenyu** [[00:24:26](https://www.youtube.com/watch?v=bktO9YRV8pc&t=1466)]
But cool.
Yeah, sounds good.
Is Wozeparrot there?
Yeah.
Do you want to say something?

##### **Wozeparrot** [[00:24:43](https://www.youtube.com/watch?v=bktO9YRV8pc&t=1483)]
Still working on hashing right now.
The biggest block is just scheduler time because the hashing functions has a lot of ops.
You propose something?

##### **Geohot** [[00:24:56](https://www.youtube.com/watch?v=bktO9YRV8pc&t=1496)]
Well, yeah, I mean, there's a few things we can do.
One is to just jit it and then we have a jitted chunk for the hash function if the schedule time is like on the order of five seconds slow.
If the schedule time is on the order of 50 seconds slow, then... The schedule time is on the order of two minutes slow.
Oh.
Yeah, I'll just take a look at it.
That sounds like a bug more than anything else.
Like, how many offs is it?
A lot.
Well, it's a lot.
I don't know.
Okay, yeah, yeah, yeah.
Okay, something's wrong.
If it's two minutes, something's actually wrong.
I can look into that.
Okay.
And then we talked here about file system design.

##### **Geohot & Wozeparrot** [[00:25:44](https://www.youtube.com/watch?v=bktO9YRV8pc&t=1544)]
The biggest question for Cloud now is just, OK, so you want to load a model, right?
Where does this model come from?
You can't stream it from your computer.
That'll take forever.
So yeah, set up a little first prototype distributed file system and be able to run some models over Cloud.
I'm living in one big address space.

##### **Geohot** [[00:26:10](https://www.youtube.com/watch?v=bktO9YRV8pc&t=1570)]
I mean, I've thought about that, but I'm not really sure what that means.

##### **Chenyu** [[00:26:15](https://www.youtube.com/watch?v=bktO9YRV8pc&t=1575)]
It's a cool abstraction.
Yeah, I'll look into the schedule at times, I promise.
Sounds good.
Next for web GPU.

##### **Hooved** [[00:26:36](https://www.youtube.com/watch?v=bktO9YRV8pc&t=1596)]
So recently, I wanted to make sure that the refactored WebGPU export code worked for stuff.
So I updated all of our WebGPU demos to make sure it works, and it does.
Stable Diffusion actually found that the master branch code, I think it's actually broken.
For exporting the model and then running it, but I fixed it when I refactored it.
I also now have automated end-to-end tests of both compilation and browser testing, all automated for all the demos except for stable diffusion, but that should come soon.
And
So in addition to all that, the code is passing all tests.
There's just a few things that I want to improve.
The main thing is kind of a carryover from last week, like how to deal with realizes and the target path that we had discussed before.
And right now, I have to assert that all the state is realized.
I don't like doing that.
I want to see if I can make the target path work.
I wrote about this in the Discord, but you have to account for the state in the target path, because otherwise it ruins quantization.
So you can't have the stuff independent of the target path mutating your state.
So I want to see if I can just do that in a simple way such that we can ban all realizes and also not require the programmer to realize all their state before exporting their model.
That's my goal.
I'm not sure it's going to be simple to do that, but I want to try.
So hopefully I can get that in the next day or so.
And then I want to try to get this stuff done and then move on to documentation and other stuff.

##### **Geohot** [[00:28:39](https://www.youtube.com/watch?v=bktO9YRV8pc&t=1719)]
Cool.
Yeah.
So let me know when you're ready for me to really review the PR.
For the realizes thing, can you just detect which buffers those are and then realize them?

##### **Hooved** [[00:28:52](https://www.youtube.com/watch?v=bktO9YRV8pc&t=1732)]
Yeah.
I've done that.
It doesn't
There are cases where it doesn't work.
But yeah, you can take those buffers, and then you can scan through all tensors, and you can match them and realize.
But it doesn't work if under certain cases like KV caches, I think.
There are times when the tensors and the global scope no longer just point to the state because they've been reassigned.
I think that's the case.

##### **Geohot** [[00:29:28](https://www.youtube.com/watch?v=bktO9YRV8pc&t=1768)]
Realization of tensors that depend on these UOPs.
That's another thing.

##### **Hooved** [[00:29:36](https://www.youtube.com/watch?v=bktO9YRV8pc&t=1776)]
That'll go away if we figure out the entire fact.
I'd like to make that go away.

##### **Geohot** [[00:29:44](https://www.youtube.com/watch?v=bktO9YRV8pc&t=1784)]
I'm okay with something that bands realize inside of a JIT, but a global piece of state called no-realize-UOPs.
Let me see how you use this.

##### **Hooved** [[00:29:55](https://www.youtube.com/watch?v=bktO9YRV8pc&t=1795)]
It's basically the same thing as the target path.
It's just a different implementation.
So I'd like to get rid of that and replace it with target path.

##### **Geohot** [[00:30:06](https://www.youtube.com/watch?v=bktO9YRV8pc&t=1806)]
Target path, like the way that I did it in Compile 4?

##### **Hooved** [[00:30:09](https://www.youtube.com/watch?v=bktO9YRV8pc&t=1809)]
Yeah, that's what I'd like to do and include state in the definition of the target path.

##### **Geohot** [[00:30:21](https://www.youtube.com/watch?v=bktO9YRV8pc&t=1821)]
Yeah, I think you're kind of seeing how the refactor of the JIT is going to come together.
I mean, I think the first thing to do here is kind of just get a taxonomy of like, so you have inputs to the JIT, you have outputs from the JIT, then you have buffers that are assigned to, and then you have implicit inputs to the JIT.

##### **Chenyu** [[00:30:39](https://www.youtube.com/watch?v=bktO9YRV8pc&t=1839)]
And I think that's everything.
And you could imagine...

##### **Geohot** [[00:30:49](https://www.youtube.com/watch?v=bktO9YRV8pc&t=1849)]
You could imagine the JIT just computing which buffers are in which sets and then handling each of those sets appropriately.

##### **Hooved** [[00:30:58](https://www.youtube.com/watch?v=bktO9YRV8pc&t=1858)]
Depends what you mean by implicit inputs and buffers that are assigned to.
What do you mean by that precisely?

##### **Geohot** [[00:31:07](https://www.youtube.com/watch?v=bktO9YRV8pc&t=1867)]
OK.
So an implicit input to the JIT is a tensor that is read inside of a kernel in the JIT before it is written to.

##### **Chenyu** [[00:31:15](https://www.youtube.com/watch?v=bktO9YRV8pc&t=1875)]
So that's an implicit input to the JIT.
Right.
So if you mean state, then that makes sense.

##### **Hooved** [[00:31:25](https://www.youtube.com/watch?v=bktO9YRV8pc&t=1885)]
Yeah.

##### **Chenyu** [[00:31:26](https://www.youtube.com/watch?v=bktO9YRV8pc&t=1886)]
Yeah.

##### **Hooved** [[00:31:28](https://www.youtube.com/watch?v=bktO9YRV8pc&t=1888)]
So we have a definition of state in the code.

##### **Geohot** [[00:31:32](https://www.youtube.com/watch?v=bktO9YRV8pc&t=1892)]
So it would cover that.
I mean, state's a very, very generic term.
I mean, I like the term implicit input, because it doesn't necessarily have to be.
Like, state kind of implies that it's going to be updated.
Whereas you can just totally have things like, in beautiful MNIST, the data set is an implicit input to the jitted function.
But I'm not sure I'd call it state.

##### **Hooved** [[00:32:00](https://www.youtube.com/watch?v=bktO9YRV8pc&t=1920)]
I think I see what you're saying.
I don't think there's really any confusion.
I think I see what you're saying.

##### **Geohot** [[00:32:06](https://www.youtube.com/watch?v=bktO9YRV8pc&t=1926)]
Cool.
What's the difference between input and implicit input?

##### **Hooved** [[00:32:12](https://www.youtube.com/watch?v=bktO9YRV8pc&t=1932)]
But yeah, I don't quite understand.
Oh, well, I can explain that.
The inputs are the stuff that you pass to the jitted function.
And the implicit input is everything else that gets input to the graph that's read.
That's not completely overwritten before it's read from.

##### **Geohot** [[00:32:30](https://www.youtube.com/watch?v=bktO9YRV8pc&t=1950)]
Yes.
And then you have outputs that are explicitly passed out of the JIT, but you also have implicit outputs, which are things that are assigned to in the JIT.
And I think this is the trickiest case.
The implicit inputs are easy to find.
Figuring out if something is assigned to inside of the JIT, I mean, there's a stupid way to do it, which is to hook the assign function, but I'd much rather not do that.
I'm not sure those assigns are going to be on the path from the outputs to the explicit inputs.
And then if those assigns aren't on that path, it's unclear if they should happen.
There's more uncertainty for me around, yeah, exactly what that means.
But to me, that seems a lot more like what I would describe as state, because those are things that are going to be updated every time by the JIT.

##### **Chenyu** [[00:33:31](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2011)]
Okay, yeah, I don't completely understand.

##### **Hooved** [[00:33:34](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2014)]
I have to think about that.
I have to think about that a little bit.

##### **Geohot** [[00:33:38](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2018)]
Yeah, it's just if I have something assigned in the JET, right?
Like I do an assign inside the JET.
Now, I think there's going to be two cases there.
There's going to be one case where that assign is on the target path to the outputs.
And I think that case is pretty easy to deal with.
But I think there's another case where that assign is totally independent.
Of the target outputs, and that one I know less about.

##### **Hooved** [[00:34:03](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2043)]
And then why do we care about that?
Could you explain why we care about if it's not on the path to the outputs, why do we care about those assigns?
Do you want to ?

##### **Geohot** [[00:34:14](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2054)]
No.
So if it's not on the path to the output, unless you realize it explicitly.
If you realize it explicitly right now, it'll be captured as the JIT kernel.
Don't realize it.
It's just not going to be captured in the JIT, so it's not going to run, even though you put it in the function.

##### **Hooved** [[00:34:39](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2079)]
Yeah, I'm just trying to understand why someone would care about that being run if it's not on the path to the outputs.
You mean if it's on the path to stuff that state, as we're describing?

##### **Geohot** [[00:34:51](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2091)]
Maybe what I should do, you know what?
I will write a bunch of tests today that explain what each of these cases are.

##### **Hooved** [[00:34:58](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2098)]
That'd be great.
That'd be perfect.

##### **Geohot** [[00:35:00](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2100)]
All right, cool.

##### **Chenyu** [[00:35:01](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2101)]
I'll do that today.
All right.
Thanks.
OK.
OK, low-cost, maybe some write-up here, some rest for me.

##### **Geohot** [[00:35:36](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2136)]
I reviewed the LDS PR.
There was stuff in there that just looked like a total hack around buffer ordering.

##### **Chenyu** [[00:35:50](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2150)]
Let me see if that's fixed.
Maybe that's fixed.

##### **Geohot** [[00:36:09](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2169)]
And then there's another problem with like, if you have like alias dimensions and a convolution, you can't just take the product of your shape.

##### **Chenyu** [[00:36:19](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2179)]
So maybe that's what this is about.
Okay.
No, no, this is hard for me to understand.

##### **Geohot** [[00:36:30](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2190)]
Okay, he said he will have some other poc working this week.
Yeah, I mean, the main thing to think about here is you want your locals to be the size of, like, take every... What you want to do is you want to run every index through the global shape tracker, and then you're going to get an output set, and then the size of that set is the size of your locals.
Because every local should only be stored once.
It shouldn't have to do with the product of the shape, because I can just trivially alias things or expand things or...

##### **Chenyu** [[00:37:15](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2235)]
Next, we have Onyx.
Let's start with the protocol parser.
Red PR, that seems to pass everything.
Is that good to merge?

##### **B1tg** [[00:37:28](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2248)]
Hi, I was working on the parser last week.
Now we have Onyx parser basically works and pass all the tests.
Now the issue with math here is that it's low.
The ONNX file is protobuf encoded and not organized like GGUF and SafeSensor.
Those formats put metadata including offset type at the beginning of the file.
So, bytes by bytes is fine.
The only thing that I want to make sure is that you aren't

##### **Geohot** [[00:38:37](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2317)]
Copying the tensors to the CPU.
So parsing any sort of metadata is totally fine to do bytes by bytes.
But whenever you have to read like a chunk of data, like a 10 megabyte tensor, I want to make sure that that path is not going through tensor IO.
Because you don't want to realize that 10 megabyte tensor and bring it to the CPU.
The whole reason that we want our own ONNX parser is so that we can like
The test that I'm going to do on this before we merge this is I want to put an ONNX file, I want to copy an ONNX file to the GPU.
So I copy a 40 meg ONNX file to the GPU.
The only traffic that should be going back to the CPU is metadata.
The tensors themselves should not be going back to the CPU.
So what is the case with this now?

##### **B1tg** [[00:39:33](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2373)]
It's currently copied the chunk of data.
It's not do that.

##### **Chenyu** [[00:39:39](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2379)]
Yeah, we got to fix that.

##### **B1tg** [[00:39:42](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2382)]
When we meet a chunk of data, we assign a slice of the tensor to the .. Exactly, yeah.
OK.

##### **Chenyu** [[00:39:56](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2396)]
Yeah, so that's what

##### **B1tg** [[00:39:58](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2398)]
What I mean is that if we're parsing it in the GPU context, it will keep copying bytes to CPU.
So I'm worried about the speed.

##### **Geohot** [[00:40:17](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2417)]
Copying some bytes to the CPU is OK.

##### **B1tg** [[00:40:21](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2421)]
Copying... So many variable-wise integers across a field.
Not like GGUF only puts the metadata at the head of the field.
And it's only needed to read the metadata length and read the chunk of metadata and passing it.

##### **Geohot** [[00:40:46](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2446)]
Yeah, okay.
So you're saying there's just many, many copies from the...
And even if we're running this on the CPU, the whole goal of this parser is to avoid copying the tensors, right?
The metadata size is going to be trivial compared to the size of... So maybe you don't want to do like byte by byte, right?
Like maybe if it's something like a varint, you want to just like look ahead, read eight bytes and then decode the varint, right?
Like pick the max size or something.
Just to make that be like one copy instead of, I think there's a question of like how many copies there are per tensor.
And if it's something like three copies, that's totally fine.
If it's something like 30 copies, that's probably too many.

##### **B1tg** [[00:41:36](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2496)]
OK, I will first fix the chunk copy issue, and then look at the byte-byte problem.

##### **Geohot** [[00:41:48](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2508)]
Cool.
Yeah, the absolute key thing, though, is that the tensors themselves are never copied.
Because the whole value of writing our own parser is that we don't have to do that copy.

##### **Chenyu** [[00:42:01](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2521)]
But cool, yeah.

##### **Geohot** [[00:42:02](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2522)]
No, I mean, it's definitely getting close.
Yeah, I'll test it today and see how many copies this actually is.
So add a script or add a testing script to copy a Linux model or the gguf case you mentioned to CPU, then on this parser, see how many copies are back to CPU?
Yep.

##### **Chenyu** [[00:42:29](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2549)]
Yeah, I think, yeah, just yeah.
OK, how about moving Annex to push?
Annex runner correct file input type and true.
So the blocker for Flow 16 is the tolerance of error.

##### **Geohot** [[00:43:16](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2596)]
I'm not sure that stuff should be a blocker from getting ONNX copied to the main repo.
I'm not sure, like, yeah, like tolerance stuff, like we can just skip that.
But I think the main thing that we have to make sure is that the API is final.
Whatever API we make for ONNX runner, that should be like the final API.
And obviously that API can't be taking in an ONNX object from the ONNX library.
That API, whether you're using the new parser or the old parser, if it imports ONNX inside the thing, it's totally fine.
It's just that the API that we expose to the user has to be simple, and we have to have docs for it.

##### **Chenyu** [[00:44:00](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2640)]
And is that API final?

##### **Geohot** [[00:44:04](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2644)]
Well, I'm not sure.
I don't think so.
I think right now, ONNX is still taking in an ONNX object.
Okay, PR and draft.
I mean, you can do it with the old, it doesn't matter if it's the old parser or the new parser.
Yeah, like right now, Onyx Runner is being constructed with a model proto.

##### **Chenyu** [[00:44:29](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2669)]
It has to be constructed with a tensor or file name.
Okay.
So maybe let's start with that.
Having a...

##### **Geohot** [[00:44:45](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2685)]
I suspect also with the new parser, we can clean a lot of this like D type parse and attribute parse stuff up.

##### **Chenyu** [[00:44:55](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2695)]
Yeah.
Cool.
OK, so I think it's good.
Let's move on to these three faster.

##### **Geohot** [[00:45:14](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2714)]
I merged your smaller fix for other rules.
I think LabPR now has only the new test and a new fuzzer.

##### **Sied Lykkles** [[00:45:25](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2725)]
Yeah, that's right.

##### **Chenyu** [[00:45:30](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2730)]
Is this ready?
I don't quite remember what's the criteria for the bounty.
I think.

##### **Sied Lykkles** [[00:45:43](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2743)]
The bounty of v3 fuzzer testing validity of symbolic rewrite rules.
I mean, it's pretty much the old fuzzer with v3 and then also adding where and max and min ops.

##### **Chenyu** [[00:46:22](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2782)]
Okay, and it founds several issues for the current.

##### **Sied Lykkles** [[00:46:31](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2791)]
Yeah, I mean, all of the like, floor div, trunk div stuff, or the all the other PRs.
that I made that was found with the fuzzer.
I think, I mean, it's mostly just the division stuff.
Like, I mean, it's also fuzzing where rules, but that's, I mean, those are pretty straightforward.

##### **Chenyu** [[00:46:58](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2818)]
I get very unlikely to be bugging there and find any.
I see.

##### **Sied Lykkles** [[00:47:06](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2826)]
I mean, the old father basically disabled.
I mean, it said like it was checking an unsimplified expression with like it wasn't really doing much.
And like the old father was also watching issues.
It had a bunch of

##### **Chenyu** [[00:47:31](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2851)]
I think the new one is with C3, it's pretty fast.
It was pretty good.

##### **Sied Lykkles** [[00:47:41](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2861)]
Whenever I changed one of the symbolic rules to be incorrect, it would generally find it.

##### **Chenyu** [[00:47:51](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2871)]
This PR looks...
Good.

##### **Geohot** [[00:47:59](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2879)]
I think another thing we want for the three files, or in general, is to test individual rewrite rules to have a way to tell if it's correct to include such rules.

##### **Sied Lykkles** [[00:48:17](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2897)]
Yeah, I was thinking about, like, you want to take a new path and then just instantiate a random instance of that pattern.

##### **Geohot** [[00:48:31](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2911)]
Yeah, so the goal is to have a way to tell if the U-pad rewrite rule is correct, and what set this should be applied on, and what fuzzing criteria should be included.
I don't know yet, but that's another goal for having fuzzers like this.
Yeah.
Another thing, you mentioned that the flag for corrective div mod folding is not default applied to all.
It's because it will regress OpenPilot.
Is that something we can fix?

##### **Sied Lykkles** [[00:49:08](https://www.youtube.com/watch?v=bktO9YRV8pc&t=2948)]
I mean, yeah.
If you improve uop-given-valid, because right now uop-given-valid, it tries each
of the valid one by one and tries to simplify it.
But if you apply like all of them at the same time, then that would sometimes change the value in the numerator such that you could fold it according to like floor div simplification.
I'm looking at it, and I can do it, I think.
But I'd like to do it nicely without regressing the current you've given valid.
I haven't gotten it working yet.

##### **Geohot** [[00:50:06](https://www.youtube.com/watch?v=bktO9YRV8pc&t=3006)]
Yeah.
I think that's definitely valuable.
We don't want these rules to be conditionally applied just because maybe
Thing I put before has some issue in it.
So fixing that altogether is definitely better than having this as a flag.

##### **Chenyu** [[00:50:28](https://www.youtube.com/watch?v=bktO9YRV8pc&t=3028)]
Yeah.
Would you want to review the symbolic buzzer, or I will review it?

##### **Geohot** [[00:50:41](https://www.youtube.com/watch?v=bktO9YRV8pc&t=3041)]
I think you got this, yeah.
OK.

##### **Chenyu** [[00:50:45](https://www.youtube.com/watch?v=bktO9YRV8pc&t=3045)]
Yeah, I would take another look later today, but I think overall looks good.
All right, thanks.

##### **Chenyu** [[00:50:57](https://www.youtube.com/watch?v=bktO9YRV8pc&t=3057)]
Let's move on to other quantities.
I see FlatHouse here.
You want to say something about RetinaNet?

##### **Flata** [[00:51:08](https://www.youtube.com/watch?v=bktO9YRV8pc&t=3068)]
Not a whole lot, just still working on the post-process detections rewrite to Tinygrad.
I'm pretty much halfway there.
I'll just keep testing more, just making sure that I don't regress and make sure correctness is there.

##### **Chenyu** [[00:51:21](https://www.youtube.com/watch?v=bktO9YRV8pc&t=3081)]
Okay.
Good.

##### **Geohot** [[00:51:30](https://www.youtube.com/watch?v=bktO9YRV8pc&t=3090)]
I added a bounty for fixing the LM eval.
I think LM eval changes APIs, so some of the old stuff doesn't run anymore.
So I think it's a good starting point to think about these numerical issues.
Did you add the spreadsheet?

##### **Chenyu** [[00:51:54](https://www.youtube.com/watch?v=bktO9YRV8pc&t=3114)]
Yeah, I do.

##### **Geohot** [[00:51:55](https://www.youtube.com/watch?v=bktO9YRV8pc&t=3115)]
I did.
I don't know what it's sorting by now.
It's... Oh, I just... I put all the new bounties at the top.

##### **Chenyu** [[00:52:04](https://www.youtube.com/watch?v=bktO9YRV8pc&t=3124)]
Oh, okay.
I see it.

##### **Geohot** [[00:52:05](https://www.youtube.com/watch?v=bktO9YRV8pc&t=3125)]
Yeah, yeah.

##### **Chenyu** [[00:52:06](https://www.youtube.com/watch?v=bktO9YRV8pc&t=3126)]
I'll move it up there.
Okay, okay.
It's like... Yeah, yeah, yeah.
Also... Go ahead.
Oh, yeah, yeah.
No, go ahead.
Sorry.
I mean, the...

##### **Geohot** [[00:52:23](https://www.youtube.com/watch?v=bktO9YRV8pc&t=3143)]
Motivation is in that tweet exchange.
And we definitely should also test some of this.
For example, our Lama of, I don't know, some examples, we just convert everything to Flow16 because it worked.
But I'm pretty sure that also hurts the output of these tokens.
So it would be nice.
I think once someone fix this, we can also add it to the Chrome Job CI so this is tracked periodically.

##### **Chenyu** [[00:52:59](https://www.youtube.com/watch?v=bktO9YRV8pc&t=3179)]
Yeah, I think it would be great to show our better numerical stability than AMD.
I'll also add a $200 bounty for

##### **Geohot** [[00:53:17](https://www.youtube.com/watch?v=bktO9YRV8pc&t=3197)]
Fixing HLB CIFAR 10 to bring the data processing into Tinygrad.

##### **Chenyu** [[00:53:29](https://www.youtube.com/watch?v=bktO9YRV8pc&t=3209)]
There is one SVD stuff that we don't know how to do in Tinygrad.

##### **Geohot** [[00:53:35](https://www.youtube.com/watch?v=bktO9YRV8pc&t=3215)]
That's why there's a bounty for it.
Which one?
The whitening thing?
I don't mind if there's like initial stuff that's not in Tinygrad, but half the time in HLB CIFAR is spent like shuffling the data or something.
I think there are three steps and I think two is preview to move to Tinygrad and the third one is the middle one is hard.
Yeah, yeah, yeah.
Cut mix.
There is random crop cut mix.
So I'll just say the each epoch data processing.
It doesn't have to be the initial thing, but for each epoch, right now it takes like five CPU seconds.
Clearly, I see this YPatch thing, it's calling x.numpy.
That's got to go.

##### **Chenyu** [[00:54:44](https://www.youtube.com/watch?v=bktO9YRV8pc&t=3284)]
Tinygrad should support it now.
What else?

##### **Geohot** [[00:55:00](https://www.youtube.com/watch?v=bktO9YRV8pc&t=3300)]
I was sitting on FP8 for forever.
I don't know.
I don't know.
Maybe after we have the LAMA numerical stuff, I'll have more motivation to add FP8.
I mean, is it right or is it not right?
Is it good?
Because the reason is for now we don't have real workload running FP8.
I mean, if it's correct, we should probably merge it and pay the bounty out.
If it's correct and the code is good.
Yeah, that's the tricky part.
I see.
I mean, yeah, I see a lot.
I mean, once we have something like FBA, I would try to merge that.
That can be on me, not the author.
I think the author has done a bunch of work already, unless there's things that were not addressed initially.
That seems good, yeah.

##### **Chenyu** [[00:56:03](https://www.youtube.com/watch?v=bktO9YRV8pc&t=3363)]
Yeah, no, we should get something working with FBA.
What else?
I think there's a bunch of Torch ones.

##### **Geohot** [[00:56:27](https://www.youtube.com/watch?v=bktO9YRV8pc&t=3387)]
I think there's been some progress on that, the HLB CIFAR Torch one.
I know someone's working on that.
Are they here?

##### **Chenyu** [[00:56:37](https://www.youtube.com/watch?v=bktO9YRV8pc&t=3397)]
Is that done already?

##### **Geohot** [[00:56:38](https://www.youtube.com/watch?v=bktO9YRV8pc&t=3398)]
Which one?

##### **Chenyu** [[00:56:44](https://www.youtube.com/watch?v=bktO9YRV8pc&t=3404)]
I merged the Unfold thing.
I think that was used.

##### **Geohot** [[00:56:49](https://www.youtube.com/watch?v=bktO9YRV8pc&t=3409)]
Oh, cool.
I see.
So he's been keeping a readme.
So we're missing linaldeig.
Apparently, Torch has decompositions for these.
I'm not sure what they decompose into.
Someone on my stream yesterday was talking about this too, how they wanted the linear algebra methods in Tinygrad.

##### **Chenyu** [[00:57:18](https://www.youtube.com/watch?v=bktO9YRV8pc&t=3438)]
They opened an issue for one.
I see.
If someone's excited, I would put a bounty on that.
All SVD?

##### **Geohot** [[00:57:34](https://www.youtube.com/watch?v=bktO9YRV8pc&t=3454)]
You can do approximation.
Oh, okay.
Recursion depth issue in the Tinygrad backend, the batch crop function.
Uh, yeah, this is, I mean, this is a good, this is a good stress test.
By the way, AMD's stuff, AMD's torch just works on HLBC far now.
So, you know, we gotta, we gotta beat them.

##### **Chenyu** [[00:57:56](https://www.youtube.com/watch?v=bktO9YRV8pc&t=3476)]
Um, but yeah, I don't know.
I mean, it's great that this is, uh, oh, wow.
It just shows how much slower Tinygrad is too.
Uh, great.
We want flash attention.

##### **Geohot** [[00:58:16](https://www.youtube.com/watch?v=bktO9YRV8pc&t=3496)]
Oh, maybe not for this week.
I don't know how we can do the clicks they are doing.
Oh, what Luminal's doing?
No, no.
The two paths softmax, we currently cannot express that, I think.

##### **Chenyu** [[00:58:37](https://www.youtube.com/watch?v=bktO9YRV8pc&t=3517)]
Because you need a sequential dependency on your .

##### **Geohot** [[00:58:43](https://www.youtube.com/watch?v=bktO9YRV8pc&t=3523)]
Yeah, from what I've seen, the like, I've read like the the softmax kernels in CUDA and stuff.
They're not that far off from ours.
So the biggest thing that's holding us back from softmax is supporting, like we need to bring warps into the the u ops.
Like, so there's a there's a CUDA function to do like an all reduce across the warp.
So you have the warp, it's all 32 threads are running.
And then there's a function to reduce across the 32.
And that is something that's like hard to express.
It's the way that we express tensor cores is is not really good right now.
Because
Like, the tensor cores depend on these shape tracker things being randomly correct.
So we'd have to move to stuff being upcasted to the warp size.
We can totally do this.
Yeah, I think that's fine.
The thing I was mentioning is the 2Path Softmax use the intermediate value of the ACC.
So it has a...
That input is the ACC so far.
Yeah, we don't have anything like so far.
So that's the thing we are currently missing.
But this isn't why our softmax is slow.
I'm not sure this to pass is actually even faster.
Our few softmax is only slow because we're not supporting the warp stuff.

##### **Chenyu** [[01:00:28](https://www.youtube.com/watch?v=bktO9YRV8pc&t=3628)]
OK, I don't know.

##### **Geohot** [[01:00:32](https://www.youtube.com/watch?v=bktO9YRV8pc&t=3632)]
I'm not sure the one in cuDNN uses the 2-pass.
This is similar to how you can compute the mean and the standard deviation at the same time?

##### **Chenyu** [[01:00:48](https://www.youtube.com/watch?v=bktO9YRV8pc&t=3648)]
No, I think that's different.

##### **Geohot** [[01:00:50](https://www.youtube.com/watch?v=bktO9YRV8pc&t=3650)]
This is only true for softmax.

##### **Chenyu** [[01:01:00](https://www.youtube.com/watch?v=bktO9YRV8pc&t=3660)]
Let's see what our fused kernel looks like.
Just to account for one last pass.
So you're saying our current fused kernel has three passes.
I'm just looking at this.
I forgot what the kernel looks like.
Is it even fusing it?
Oh, yeah, okay.
No, we're only doing two passes.
So like this is this is what our
That's our fused softmax.
I mean, it's two for loops anyway.

##### **Geohot** [[01:02:23](https://www.youtube.com/watch?v=bktO9YRV8pc&t=3743)]
I think no one's really looked at it.
Maybe it's not even the warp thing that makes it slow.

##### **Chenyu** [[01:02:32](https://www.youtube.com/watch?v=bktO9YRV8pc&t=3752)]
I mean, it's definitely just looping through the thing.
It isn't one kernel.
Anyway, I think it's something the first two can be merged together.

##### **Geohot** [[01:02:52](https://www.youtube.com/watch?v=bktO9YRV8pc&t=3772)]
Wait, which two?

##### **Chenyu** [[01:02:54](https://www.youtube.com/watch?v=bktO9YRV8pc&t=3774)]
I posted that.
I posted the code in general.
Yeah, the one you get the max and the ones that you divided by max and get in a sum and be fused together.

##### **Geohot** [[01:03:08](https://www.youtube.com/watch?v=bktO9YRV8pc&t=3788)]
You think I can somehow combine those two loops?

##### **Chenyu** [[01:03:13](https://www.youtube.com/watch?v=bktO9YRV8pc&t=3793)]
Yeah.

##### **Geohot** [[01:03:15](https://www.youtube.com/watch?v=bktO9YRV8pc&t=3795)]
I would write the kernel in GPU or MED or something.
Cool.
Yeah, I mean, if there's some sort of thing that you think is a good construction that we can't express, like we can't express in UOps, write it up and I'll think about how to express it.

##### **Chenyu** [[01:03:30](https://www.youtube.com/watch?v=bktO9YRV8pc&t=3810)]
Sounds good.
OK.
That's about it.
That's the meeting for this week.
Thank you, everyone, and see you next week.

##### **Geohot** [[01:03:41](https://www.youtube.com/watch?v=bktO9YRV8pc&t=3821)]
Bye.
    