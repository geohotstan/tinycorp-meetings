# 2025-03-17 Meeting

### Meeting Agenda

**Time:** 7am Monday San Diego time (10pm HK time)
- company update, MI300X, intel GPU
- quantized mobile net
- bert, rand
- scheduler
- gpu on usb, driver
- tensor core
- onnx, bitonic sort, jit moe
- WebGPU
- torch frontend (test_ops, nano gpt, multi gpu training)
- retinanet
- AMD comgr -> LLVM

### Audio

[Youtube Link](https://www.youtube.com/watch?v=jn3no5UZLmI)

### Highlights

- [Company & GPU Update](#geohot-000012) MI300x progress advances with successful setups, Intel carrier board arrival, and AMD 9070 runtime confirmation.
- [BERT & RAND Optimizations](#chenyu-000743) Sub-three-hour BERT training achieved via float16 accumulation; investigation into a RAND bug affecting random output order.
- [Scheduler Refactoring](#qazalin-001435) New grouper and fusion strategies reduce memory usage and eliminate redundant E-kernels in the scheduler.
- [USB GPU Driver Updates](#nimlgen-001924) USB GPU firmware improvements and SDMA command fixes stabilize boot times and copy speeds.
- [Tensor Core Enhancements](#ignaciosica-002330) Fixes for local memory and swizzle bugs in Tensor Core kernels are underway, with additional tests added for robustness.
- [MOE JIT Integration](#geohot-003010) JIT integration for the MOE model now leverages Top-K merging; bounty open to optimize its performance further.
- [WebGPU Export Refactor](#hooved-003146) The WebGPU export API is being streamlined for cleaner Python-to-JavaScript integration, with future Clang/WASM support planned.
- [Torch Frontend & NanoGPT Updates](#b1tg-004013) Test ops improvements and backward hook fixes address nanoGPT VRAM spikes and multi-GPU training challenges.
- [RetinaNet Float16 Optimization](#flata-004303) Float16 integration and segmented PRs target sub-24-hour RetinaNet training alongside Top-K evaluation enhancements.
- [AMD Compiler Migration to LLVM](#geohot-004730) LLVM compiler refactors simplify AMD COMGR transitions, paving the way for host LLVM integration.
- [JIT Memory & Python Overhead](#chenyu-005031) Ongoing efforts to eliminate JIT memory leaks and reduce Python overhead aim to boost overall performance.

### Transcript

##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=jn3no5UZLmI&t=0)]
Let's start with any company update.
And also because other people sponsor machines to us, we can give updates to those as well.

##### **Geohot** [[00:00:12](https://www.youtube.com/watch?v=jn3no5UZLmI&t=12)]
So I think we're making some good progress on the MI300x stuff.
uuuvn's working on that bounty.
Yeah, machines are up.
I showed them off a bit on stream this weekend.
We'll have a runtime form soon.
It's a little annoying because you've got to synchronize across the whole GPU.
HIP does it using AQL packets, but I'd rather not use AQL.
So I'm going to work with PM4.
For Intel, they are sending us a board.
They're sending us a carrier board for those GPUs.
So hopefully we'll get those up soon.
There's a lot of steps.
And I haven't heard anything yet about a deal for what we can actually buy them for.
The only price I've heard is still probably too high for what makes sense for us.
Oh, and we got RDNA 4.

##### **Chenyu** [[00:01:21](https://www.youtube.com/watch?v=jn3no5UZLmI&t=81)]
We got the 9070?

##### **Geohot** [[00:01:24](https://www.youtube.com/watch?v=jn3no5UZLmI&t=84)]
Yeah, we got a 9070 up.
The runtime works.
Nimlgen's working on drivers, so yeah.
Very bullish on AMD.

##### **Chenyu** [[00:01:40](https://www.youtube.com/watch?v=jn3no5UZLmI&t=100)]
Yeah, we'll be able to see if we want to submit MLPerf.

##### **Geohot** [[00:01:47](https://www.youtube.com/watch?v=jn3no5UZLmI&t=107)]
I don't know if it's fast.
Yeah, only if it happens.
I mean, maybe it will be.
I don't know.

##### **Chenyu** [[00:01:55](https://www.youtube.com/watch?v=jn3no5UZLmI&t=115)]
We'll see.
We'll see.

##### **Geohot** [[00:01:57](https://www.youtube.com/watch?v=jn3no5UZLmI&t=117)]
Yeah.
What do we have to get to get a good time?
Like 10 minutes?

##### **Chenyu** [[00:02:09](https://www.youtube.com/watch?v=jn3no5UZLmI&t=129)]
I don't know.
We need to check, but it needs to be good.

##### **Geohot** [[00:02:19](https://www.youtube.com/watch?v=jn3no5UZLmI&t=139)]
We can also always hack around the setup time.
I don't know what they consider the setup time and what they don't, but we could always just pickle the JIT.

##### **Chenyu** [[00:02:32](https://www.youtube.com/watch?v=jn3no5UZLmI&t=152)]
Yeah, so the definition for setup time is you can do like pickle the JIT, you can pre-compile, you can do whatever.
Basically, as long as you don't touch the data.
And yeah, I think as long as you don't touch the data, it's like fair game.
And you have like 30 minutes, up to 30 minutes for that.

##### **Geohot** [[00:02:59](https://www.youtube.com/watch?v=jn3no5UZLmI&t=179)]
Cool.
Yeah, so I mean, we can definitely do that.

##### **Chenyu** [[00:03:01](https://www.youtube.com/watch?v=jn3no5UZLmI&t=181)]
Before we only run BEAM and use like 20 minutes or something.

##### **Geohot** [[00:03:08](https://www.youtube.com/watch?v=jn3no5UZLmI&t=188)]
Well, that's for setup, but it still takes some time.
I think you're talking about like six minutes to just actually get all the terms.

##### **Chenyu** [[00:03:16](https://www.youtube.com/watch?v=jn3no5UZLmI&t=196)]
Yes.
If we do pickle JIT if it only directly wrong from the ExecItem..
Yeah, I imagine we can save those five minutes, six minutes.

##### **Geohot** [[00:03:37](https://www.youtube.com/watch?v=jn3no5UZLmI&t=217)]
Yeah, I think if we can get a sub 10 minute time, I think we should submit it.

##### **Chenyu** [[00:03:45](https://www.youtube.com/watch?v=jn3no5UZLmI&t=225)]
OK, we can start testing the speed time and see what it looks like after we have run time and matmul stuff.

##### **Geohot** [[00:03:56](https://www.youtube.com/watch?v=jn3no5UZLmI&t=236)]
Yeah, sounds good.

##### **Chenyu** [[00:03:57](https://www.youtube.com/watch?v=jn3no5UZLmI&t=237)]
Cool.
OK, let's move on to our contract.

##### **Geohot** [[00:04:05](https://www.youtube.com/watch?v=jn3no5UZLmI&t=245)]
I mean, if we're flop bound, 12x is actually reasonable.
If we could get it down to two hours, and then, yeah, go 12x faster.

##### **Chenyu** [[00:04:16](https://www.youtube.com/watch?v=jn3no5UZLmI&t=256)]
I mean, if it's really 12x, then now it's like 15 minutes, right?
Or already not yet.
But I don't know if that's the case.
I think for some part, we are flop-bound, and for some part, we are still memory.

##### **Geohot** [[00:04:31](https://www.youtube.com/watch?v=jn3no5UZLmI&t=271)]
The flops are really 10x.
The flops are 10x.
Oh, but it's not just 10x, because we also have 8 instead of 6.

##### **Chenyu** [[00:04:41](https://www.youtube.com/watch?v=jn3no5UZLmI&t=281)]
Yeah, so that's why it's 12.
We'll see.

##### **Geohot** [[00:04:53](https://www.youtube.com/watch?v=jn3no5UZLmI&t=293)]
Cool.
Yeah, our contract, OK.
So I've gotten, in two months, I've gotten a 5x speedup.

##### **Chenyu** [[00:04:59](https://www.youtube.com/watch?v=jn3no5UZLmI&t=299)]
How much more do we need?

##### **Geohot** [[00:05:07](https://www.youtube.com/watch?v=jn3no5UZLmI&t=307)]
13x more.

##### **Chenyu** [[00:05:10](https://www.youtube.com/watch?v=jn3no5UZLmI&t=310)]
OK then, that's a lot.

##### **Geohot** [[00:05:14](https://www.youtube.com/watch?v=jn3no5UZLmI&t=314)]
Well, okay.
So in reality, in reality, divide by two.
So really, we need 6.5.
Really, I need to just do again what I did.
Because you can use two, it has two cores.
So I just need to, that's just the runtime and making it work.

##### **Chenyu** [[00:05:31](https://www.youtube.com/watch?v=jn3no5UZLmI&t=331)]
Yeah.

##### **Geohot** [[00:05:33](https://www.youtube.com/watch?v=jn3no5UZLmI&t=333)]
Like, it would be pretty easy to just get it to show up as two DSPs and just use all the multi stuff for it.
It'll work trivially.
But,
Yeah.

##### **Chenyu** [[00:05:48](https://www.youtube.com/watch?v=jn3no5UZLmI&t=348)]
And you know how to get the that again? Because usually the second half is more difficult in the first half when speed running stuff like this.

##### **Geohot** [[00:05:58](https://www.youtube.com/watch?v=jn3no5UZLmI&t=358)]
I'd say it's about the same actually.
Unfortunately, that took me two months.
I know how to get the second half.
I'm hoping that there's going to be some easy things.
I'm hoping that like just LLVM is actually just quite bad.
I haven't, what I have correct now is like all the, like all the transformations are pretty much done.
I fixed the const thing.
I fixed all the quantization stuff.
There's one minor scheduler thing, but it's only costing us a few percent.
The big thing is like, there's some big disparity between even my hand-coded kernel is only getting 47 gigaflops, but this thing is supposed to be able to get 1500.
What's different?
I don't get it.
So I think tomorrow I'm going to work to understand that.
I'm going to start writing these things at assembly.

##### **Chenyu** [[00:07:01](https://www.youtube.com/watch?v=jn3no5UZLmI&t=421)]
Aside from that, nothing else that other people can help you to make it faster?

##### **Geohot** [[00:07:08](https://www.youtube.com/watch?v=jn3no5UZLmI&t=428)]
The only thing that could help is if you see those E kernels there,
That comes from the scheduler.
And if we could fix that in the scheduler, those could just go away.
It's kind of annoying.
Qazalin, maybe I'll show you this tomorrow, if there's an easy way to make them disappear in the scheduler.
Oh, not otherwise.

##### **Chenyu** [[00:07:31](https://www.youtube.com/watch?v=jn3no5UZLmI&t=451)]
OK.
Let's see how that goes.
You have two weeks left.

##### **Geohot** [[00:07:39](https://www.youtube.com/watch?v=jn3no5UZLmI&t=459)]
Yeah, let's go.

##### **Chenyu** [[00:07:43](https://www.youtube.com/watch?v=jn3no5UZLmI&t=463)]
Uh, okay.
Uh, next is Bert.
We got our first sub three hour round.
That was pretty nice.
Mostly the speed was coming from using float16 for accumulation in Matmul.
Then do some hyper parameter searching to make it converge as fast as the
basically the threshold on MLPerf.
So when we do the estimation for total time, we can always assume it's like 2.5 million examples.
Because even if we do lower than that, by the rules, we need to use that number.
So I think the rest of the BERT,
If we want to do two hours, we need to scrape some other stuff.
We were saying something?

##### **Geohot** [[00:08:47](https://www.youtube.com/watch?v=jn3no5UZLmI&t=527)]
How is it on the red box?

##### **Chenyu** [[00:08:50](https://www.youtube.com/watch?v=jn3no5UZLmI&t=530)]
So red is, I was rounding it, I think four hours something.

##### **Geohot** [[00:08:56](https://www.youtube.com/watch?v=jn3no5UZLmI&t=536)]
Got it.
And it's just because Nvidia has a lot more 1616 flops?
Oh, it's actually 5.5 hours.

##### **Chenyu** [[00:09:05](https://www.youtube.com/watch?v=jn3no5UZLmI&t=545)]
No, so for some reason, it converges slightly worse.
So if proportional to use the same example, it's like 5 hours.
And it's just flop, less flop.

##### **Geohot** [[00:09:23](https://www.youtube.com/watch?v=jn3no5UZLmI&t=563)]
Yeah, how much slower is it if we stick with 32?

##### **Chenyu** [[00:09:28](https://www.youtube.com/watch?v=jn3no5UZLmI&t=568)]
32, we cannot do this batch size.

##### **Geohot** [[00:09:33](https://www.youtube.com/watch?v=jn3no5UZLmI&t=573)]
I see.

##### **Chenyu** [[00:09:36](https://www.youtube.com/watch?v=jn3no5UZLmI&t=576)]
So about five hours.

##### **Geohot** [[00:09:41](https://www.youtube.com/watch?v=jn3no5UZLmI&t=581)]
How is that stuff going with that rewrite you posted?
I didn't totally understand that.

##### **Chenyu** [[00:09:49](https://www.youtube.com/watch?v=jn3no5UZLmI&t=589)]
Oh, which part you don't understand?

##### **Geohot** [[00:09:52](https://www.youtube.com/watch?v=jn3no5UZLmI&t=592)]
You said some of these got surprisingly smart, and you removed a bunch of the gates.

##### **Chenyu** [[00:09:57](https://www.youtube.com/watch?v=jn3no5UZLmI&t=597)]
Yeah, I think what's happening is the where rewrite or the conditional thing we had for
VALIDHACK was probably not correctly implemented, like added.
I don't know yet. So the rewrite rule basically so basically the idea is if you have a where in a where or something it's a good idea to combine those conditions because you create a you create a more easy to reasoned uh closures for your conditions and our like VALIDHACK rules would
would narrow down the variable ranges and sometimes do some math to remove turns.
It's not clear to me the one I posted is correct or not.
I mean, test pass, but I imagine it might be sometimes incorrect because the VALIDHACK was for image only.

##### **Geohot** [[00:11:04](https://www.youtube.com/watch?v=jn3no5UZLmI&t=664)]
Well, yeah, I mean, the image guarantees that reads out of bounds are going to return zero, whereas this, you have no guarantees.

##### **Chenyu** [[00:11:12](https://www.youtube.com/watch?v=jn3no5UZLmI&t=672)]
We need to check if it's a legit removal or just incorrect behavior.

##### **Geohot** [[00:11:19](https://www.youtube.com/watch?v=jn3no5UZLmI&t=679)]
Yeah, I mean, what you should do is create a buffer and surround the buffer by NANs.
Because you might accidentally get zeros, yeah.

##### **Chenyu** [[00:11:29](https://www.youtube.com/watch?v=jn3no5UZLmI&t=689)]
We have a test for that.

##### **Geohot** [[00:11:32](https://www.youtube.com/watch?v=jn3no5UZLmI&t=692)]
Cool.
Oh, also.
Check out the ignore stuff.
You say you're using pad and BERT?

##### **Chenyu** [[00:11:41](https://www.youtube.com/watch?v=jn3no5UZLmI&t=701)]
Yes.
Removing that is bad.

##### **Geohot** [[00:11:45](https://www.youtube.com/watch?v=jn3no5UZLmI&t=705)]
Well, yeah, but check out the ignore stuff that I have in the quantize stuff.
I think you can take it out.
I think you can apply that to all.
So I have this thing called ignore, which just kind of pushes a shape tracker to if the things are going to be ignored on the store, and that fix all the const things.

##### **Chenyu** [[00:12:08](https://www.youtube.com/watch?v=jn3no5UZLmI&t=728)]
Do you mean by fix all the consts?

##### **Geohot** [[00:12:10](https://www.youtube.com/watch?v=jn3no5UZLmI&t=730)]
So right now, when we do a pad, we mask all the consts with the same pad.
But many times, you don't actually need to mask the const.
So yeah, check out what Ops.IGNORE does.
It's in the lower.
And I think you could pull all that stuff out of the quantizer and just run it before the quantizer.
And then you'll get some speed on those padded kernels.

##### **Chenyu** [[00:12:44](https://www.youtube.com/watch?v=jn3no5UZLmI&t=764)]
I see.
OK, I will check it.

##### **Geohot** [[00:12:47](https://www.youtube.com/watch?v=jn3no5UZLmI&t=767)]
It would help with the DSP stuff, too, because it's not perfect on the DSP yet.
Genericizing that and making that good would improve the DSP stuff.

##### **Chenyu** [[00:12:55](https://www.youtube.com/watch?v=jn3no5UZLmI&t=775)]
OK, I will take a look.
Oh, sure.
Yeah, BERT, because BERT has this weird recap site, mostly.
And our embedding is still slow.
So there's that.

##### **Chenyu** [[00:13:16](https://www.youtube.com/watch?v=jn3no5UZLmI&t=796)]
And last night, I found a bug, I think, in RAND.
I saw your comment.
And yeah, I had the same workaround.
But I need to fix a bunch of stuff to merge that.
So the bug was if we create a different size rand, the count in the internal counters to generate the random bits are not necessarily sequential.
So you might get weird orders compared to how you would do if it's a sequential and,
There might be some subtle properties for how if this thing go out of the
32-bit and recycled, some behavior might be different.
Yeah, we only start with see that because we have drop-off for different size of tensor.
And I think for the benchmark, stable diffusion was fine.
But stable diffusion large now generates a different image because it's a different random, effectively.

##### **Geohot** [[00:14:23](https://www.youtube.com/watch?v=jn3no5UZLmI&t=863)]
Makes sense.

##### **Chenyu** [[00:14:28](https://www.youtube.com/watch?v=jn3no5UZLmI&t=868)]
Okay, let's move on to scheduler.

##### **Qazalin** [[00:14:35](https://www.youtube.com/watch?v=jn3no5UZLmI&t=875)]
So last week I merged a bunch of refactors towards the new grouper that I'm working on.
It's on 9480.
The diff is still quite large, but I'm hoping it's going to open up a new path.
It's probably the final big refactor that we need to do in the scheduler.
I'll look into your E-kernels tomorrow and see if there's some way to genericize some of the work that I'm doing here to fix those.
But basically, right now, we're using way too much RAM.
We're accessing global memory too many times for expands, for multiple reduces.
I think our code gen is good enough that we can at least fuse Arange.
And come back word.
Some other stuff are a bit tricky.
So I'm working through all the cases.
There's going to be a good stress test for the codegen as well.
So yeah, there's going to be for the rest of my week.
Getting things slowly from the new grouper merged into master.
Some things are already in.
So if you want to look into them,
There are right now loads and stores created only at the end, load source valid.
Everything pretty much, we preserve the tensor graph as long as we can, and we add the new ops only in the end.
Ops like define global, load store, stuff like that, are only in the very, very, very end part of the rewrite rules right before we hand it off to the kernel.
So yeah, that's the new way.

##### **Chenyu** [[00:16:32](https://www.youtube.com/watch?v=jn3no5UZLmI&t=992)]
I saw your reply on the issue are open for FUSE ARANGE, contiguous.
I think some of those we start to have more FUSE rules and what take precedent of another.

##### **Qazalin** [[00:16:52](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1012)]
Well, the reason why that
thing exists as an env variable is that the current way we decide which things to realize is very custom.
So you can't actually make a decision.

##### **Chenyu** [[00:17:06](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1026)]
Yeah, my point is, for example, I think you say the issue was contiguous was not respect because of this flag.
Something like, no matter what the fusing rules is, there are some orders to it.
And setting contiguous makes it a separate kernel, I think, is one of the most important ones.

##### **Qazalin** [[00:17:29](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1049)]
Yeah.
That should definitely override it.

##### **Chenyu** [[00:17:38](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1058)]
Yeah, I will look into random and these views Arange thing.
Because random, effectively, is just some element-wise stuff on top of a big Arange.
Well, random is still slowish.
If I replace the random with just one stuck contiguous, I think it's like 5% faster.
And since it's just a bunch of element-wise stuff, I think it shouldn't be 5%.
We'll see.

##### **Geohot** [[00:18:07](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1087)]
Well, random is a ton of kernels now.
It's part of it has to do with the way that threefry is a 64 bit thing.
It's the same as the cat thing.
We've talked about it.

##### **Chenyu** [[00:18:19](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1099)]
Uh, yes, but that part, so you can, you can do that as like one big arange for now we do two aranges and a cat at the end.
So I was thinking, if we can fuse this ARange into that, then we don't need to separate into.
So we initially split that into two ARanges to save some memory, because your first part of ARange and the second part of ARange can be reused.
But if we can fuse all the ARange into the real compute kernel, then we don't need to do this split.

##### **Geohot** [[00:18:58](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1138)]
Great.
Yeah, OK.
We don't have to solve the cat problem then.
Yeah, I saw a fused argmax kernel this morning.
It was very exciting.

##### **Chenyu** [[00:19:06](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1146)]
Oh, great.
Yeah, that would be nice too.
Cool.
OK, let's move on to driver.

##### **Nimlgen** [[00:19:24](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1164)]
Yeah, so for the USB GPU, so making some progress.
So it has that compile3 today.
So it just runs fine.
So we only lock copies, copy speeds right now.
So that's my primary focus for this week.
So yeah, to get the copy speeds.
So we discussed with this in the office.
So yeah, the plan is try to emulate NVME drive.
So, yeah.
And for.
And then a four, it's just, um,
It's actually the biggest block that differs is DMA because it's now, it's just been rewritten completely.
In RDNA 4, it's now also RISC.
It's just RISC chipset.

##### **Geohot** [[00:20:18](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1218)]
You mean the firmware is RISC for SDMA?

##### **Nimlgen** [[00:20:21](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1221)]
Yeah, yeah.

##### **Geohot** [[00:20:23](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1223)]
And they changed the commands?

##### **Nimlgen** [[00:20:27](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1227)]
No, no, that looks the same, some registers.

##### **Geohot** [[00:20:31](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1231)]
Yeah, it's usually not.
So the RISC one is pretty much just a straight up recompile of the F32 ones.
I actually think the chips can run both.
I think you can initialize the chip as either one, like their cores are dual architecture.

##### **Nimlgen** [[00:20:48](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1248)]
I'm not sure about that.

##### **Geohot** [[00:20:50](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1250)]
I mean, do you think the SDMA block is actually RISC-V in some and F32 in others?

##### **Nimlgen** [[00:21:01](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1261)]
Yeah.
I mean, everything A4, yeah.
It's RISC, and before that, it was F32.

##### **Geohot** [[00:21:07](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1267)]
Yeah, OK.
Maybe something actually did change.
Is it still like 13, or did they bump it up one number?
Or six?

##### **Nimlgen** [[00:21:19](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1279)]
What do you mean?

##### **Geohot** [[00:21:23](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1283)]
On RDNA 3, it was called like SDMA 6.

##### **Nimlgen** [[00:21:30](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1290)]
Yeah, now it's SDMA 7.

##### **Geohot** [[00:21:31](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1291)]
OK, maybe it's different.
How fast is the boot time over USB now?

##### **Nimlgen** [[00:21:40](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1300)]
I fixed this problem when I just constantly cold booted it.
It's not the first.
But yeah, I mean, the cold boot is just the same as we had on Friday.

##### **Geohot** [[00:21:56](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1316)]
I didn't see a full call boot on Friday.

##### **Nimlgen** [[00:22:04](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1324)]
Probably like two minutes, like the full week right now without SDMA.

##### **Geohot** [[00:22:11](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1331)]
Yeah, not too bad.

##### **Nimlgen** [[00:22:14](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1334)]
So yeah, and actually SDMA working, SDMA working.
We'll focus on GPU, USB GPU, and some reflectors for our driver to support their flow.

##### **Geohot** [[00:22:39](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1359)]
Yeah, we talked also at lunch today about rewriting the Clang header parser thing to be fast and good.
Yeah, I wish I had more.
I got two weeks to do DSP.

##### **Chenyu** [[00:22:56](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1376)]
Yes, that's important.
Let's finish that first.

##### **Geohot** [[00:22:59](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1379)]
Yes, OK.
All right, I'm going to have to wait till after the DSP.
But yeah, no, I know there was talk about switching to the UMR registers.
I'd like to keep using the headers from the kernel.
And if the client generation is slow, it's slow, whatever.
It's a one-time thing.

##### **Chenyu** [[00:23:23](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1403)]
Sounds good.
Sounds good.
OK.
Move on to Tensor Core.

##### **Ignaciosica** [[00:23:30](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1410)]
Hi.
Hello.
I found what was wrong with the Tensor Core 3 from last week.
And I actually think I was the one that introduced one of the bugs that I removed.
I localized global dimensions, and that was
making the usage of locals way high.
And also, the swizzle was also wrong.
So I'm cleaning up that right now.
And I'm going to continue to work with locals.

##### **Geohot** [[00:24:09](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1449)]
Cool.
Can you add tests that would have caught this?

##### **Ignaciosica** [[00:24:14](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1454)]
Yes.

##### **Geohot** [[00:24:16](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1456)]
Great.
Sure.
And then how is the
MFMA coming, or whatever it's called, on M300.

##### **Ignaciosica** [[00:24:28](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1468)]
For F16, I added the support.
I also tested other shapes, but it's actually not faster.
I mean, I've been hesitant to merge, because it's not tested anywhere else.
So until somebody else tests or, I mean, it's good to merge.
Like right now, it's used as a TensorFlow core.
It's not using other functionalities it has, but it's faster.

##### **Geohot** [[00:25:01](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1501)]
I think you should, yeah.
I mean, if it's correct and tested to be correct, by all means merge it.

##### **Ignaciosica** [[00:25:15](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1515)]
OK.

##### **Chenyu** [[00:25:10](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1510)]
Great.
Thanks.
Cool.
Moving on.
This is for zibokapi.
Your stuff.
You can just type if you can talk during recording.
I saw you have the sort thing going.

##### **Chenyu** [[00:25:35](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1535)]
Is that ready?
Is it correct?
And is it fast?
How many kernels it is to sort an item?
OK.
Sure, even better.
Yeah, I mean, if you think it's ready, I would take a look.
And we can merge that as long as it's, I mean, correctness is most important.
And if you say the performance is nice, then that's even better.
You can always improve the code.

##### **Geohot** [[00:26:44](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1604)]
We have to have contiguous, OK.
I wonder why that is.
You should never have to have contiguous.
But yeah, no, I mean, the tonic sort is the right algorithm for GPUs.
Oh, and the max pool indices.

##### **Chenyu** [[00:27:12](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1632)]
I heard we are going to have good argmax, so maybe we will have good max pool indices.

##### **Geohot** [[00:27:21](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1641)]
Tinygrad's getting sold legit.

##### **Chenyu** [[00:27:24](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1644)]
Great.
OK, sounds good.
I will review that PR later.
And just making sure you put all the tests you can think to, making sure it's correct.

##### **Ignaciosica** [[00:27:40](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1660)]
And sorry.
Can I say something?

##### **Ignaciosica** [[00:27:49](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1669)]
Yes, I've been working a lot last week with locals and kernel stuff.
And I found that it usually breaks with the vectorizer stuff.
I found it quite fragile there.
So I don't know if it's like changes that were introduced lately or things that came from before.

##### **Geohot** [[00:28:17](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1697)]
Wait, what specifically breaks?
Do you have failing tests?

##### **Ignaciosica** [[00:28:23](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1703)]
No, but I think I can write.
Like, for example, with the TensorCores, with three, if I don't add the TensorCores, hand coded optimizations, like the extra upcast and the extra locals.
There is failings with the.. 

##### **Geohot** [[00:28:42](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1722)]
I rewrote the Vectorizer.
We have a whole new vectorizer now that's like brand new.
So I mean the best I can do when I write things like that is pass all the tests.
If you give me failing tests that are the vectorizer failing, I will fix them right away.
Like I can't do better than the tests passed, right?
Like I could try, but.. Yeah no, so failing tests would be great.
and I will fix them right away.
I've seen some issues in the vectorizer with the DSP stuff.
I had to rewrite it for the DSP stuff.
The new vectorizer is much cleaner.
The new vectorizer separates vectorization into the three things that it really is, which is grouping contiguous things,
deciding how you want to group your loads, and then deciding how you want to, like, GeP your loads, like reassign them to their correct positions.
And these are three completely separate things, and they're now handled by three separate passes.
So it's so much easier to debug now.
So any bug I can fix really fast.

##### **Ignaciosica** [[00:29:45](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1785)]
Okay, that's cool.
So I'll try to come up with clean tests and upstream them.

##### **Geohot** [[00:29:52](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1792)]
Yep, anything you can be failing, that's a vectorizing failure I'll fix.


##### **Chenyu** [[00:30:06](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1806)]
OK.
So that's sort.
Let's move on to WebGPU.
We have hooved here.

##### **Geohot** [[00:30:10](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1810)]
For jitting MOE, why is the sort in there?
You shouldn't need sort for that.
You should just be able to use topK.

##### **Chenyu** [[00:30:19](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1819)]
I think it's just sort.
Sorry, I think it's just topK.
Oh, it was pretty bad.

##### **Geohot** [[00:30:26](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1826)]
Even if it's bad, it's still like,
Can you get it.
Or.
Sorry, my internet glitched for a minute.

##### **Geohot** [[00:30:59](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1859)]
But we should be able to JIT it, even if things are slow.
Oh, it was JIT-able?
Well, then put it together, clean it up, and claim the bounty, even if it's slow.

##### **Chenyu** [[00:31:10](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1870)]
Yeah, I think the scope of that bounty is to just JIT it.
Then we will figure out the speed issue later.
We can even have a separate speed bounty just to make it fast.

##### **Geohot** [[00:31:24](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1884)]
Yeah, like if there's something absurdly slow, OK, then we have to think about it.
But if all you're saying is, oh, well, it's doing 16 maxes to get the top Ks, whatever.
It still qualifies.

##### **Chenyu** [[00:31:34](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1894)]
OK.
Sounds good.
OK, Hooved, up to you for WebGPU.

##### **Hooved** [[00:31:46](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1906)]
Hey, yeah, so I opened a PR for refactoring the WebGPU export model.
I simplified the APIs for exporting from Python and importing to the JavaScript app.
So it's pretty simple now, trying not to lose any of the power that we've had.
And I am working on the refactor.
of all the internal logic, just trying to condense it and make the code high quality and good enough for being in main TinyGrad.
So that's going to take a little time.
But after that, it's writing docs and tests.
And yeah, pretty excited about this.
Let me know if you have any questions.

##### **Chenyu** [[00:32:42](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1962)]
If you have anything that needs review or just want someone to discuss, feel free to post what you have in the WebGPU channel and the Dev channel.

##### **Hooved** [[00:32:53](https://www.youtube.com/watch?v=jn3no5UZLmI&t=1973)]
OK.
Yeah, I mean, I was going to say, I would say it's not quite ready for review, because I want to have the code that goes into Tinygrad needs to be cleaned up a lot.
But yeah, I can do that.
I mean, if you want to see what it looks like right now, there's a test in CI that's our WebGPU Puppeteer test that compiles an efficient net and then runs it with Puppeteer.
So that's using the new APIs.

##### **Geohot** [[00:33:24](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2004)]
So I think export should also be able to export to Clang.

##### **Hooved** [[00:33:29](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2009)]
Sure.
Yeah, we can include that.
Yeah, I mean, it does already within Extra.
My understanding of the intended scope of the bounty was that it was WebGPU, but we can definitely include Clang and even Wasm if we want to include that.
But I had thought that that wasn't the first thing we're going to do with this bounty, but happy to.

##### **Geohot** [[00:33:56](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2036)]
I'm OK with for the bounty.
It's not a requirement for the bounty.
But what I don't want to have is export code that is pretty much just only for JavaScript.
I see a lot of strings here that are just big chunks of JavaScript.

##### **Hooved** [[00:34:11](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2051)]
Yeah.
No, that needs to be cleaned up.
And yes, it absolutely has to be compatible to also export C code.

##### **Geohot** [[00:34:21](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2061)]
Yeah, like I almost look at, again, it's not that like, I think it probably is a good idea to do the C code in the WASM as well, because like, I really don't want to merge into tiny grad something that is just a huge F string of JavaScript.
We should think about what that actually is, right?
Because think about like adding a new export.
To write this code really well, you want to be able to easily add a new export target.

##### **Hooved** [[00:34:49](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2089)]
Right.
No, I agree.
That's part of the refactor.
We're really just taking the JIT cache and trying to map what's in there as concisely as possible to other languages.

##### **Geohot** [[00:35:03](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2103)]
Yeah, no, I think that's right.
And I think then there should be almost like a good framework for doing that.

##### **Hooved** [[00:35:09](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2109)]
Yeah.
Cool.

##### **Chenyu** [[00:35:12](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2112)]
Yeah, and it's like API designs or high level things like this.
I think you can get some feedback if you post.
how you want to do it in the channel and people can take a look.

##### **Geohot** [[00:35:28](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2128)]
My ideal test that it is good is that you write the web GPU one and then it is intuitive and easy for me to add Clang.

##### **Hooved** [[00:35:38](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2138)]
Okay.

##### **Geohot** [[00:35:42](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2142)]
I mean, yeah, there should be like, yeah, like an obvious like way to do it when you've written this code, I think in a way that's..
That's correct.
There's a bunch of, you're right, it's the JIT cache.
And then there's a bunch of different things that you want to map.
There's buffer setup, there's model setup, and then there's model runtime.
Maybe there's something I'm missing there too.

##### **Hooved** [[00:36:08](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2168)]
No, I think that's roughly right.
I mean, it's actually pretty simple.
You don't even have to, the only reason you need to,
think about the model aside from what's in the JIT cache is if you want to have recognizable references to your state that are exported.
Because right now with the API, and I can post an example in the chat later, but all you need is for the API right now is a function that returns one or more tensors and input to that function and a place to save it on disk.
Because the JIT cache has all the weight buffers
in it, of course.
And they're recognizable just because of the patterns.
The first reference to them is not an output.
And they're not an input or output buffer.
And you're able to just discern what the state is from that.
So you don't necessarily even need a model to pass it into the export.

##### **Geohot** [[00:37:06](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2226)]
Yeah, that's not really what I mean by model.
I guess what I mean by model is more like you have basically three separate things.
You have a definition of compute.
You have data, which is the tensors you've stored to disk.
And then you have a way to run that compute.

##### **Hooved** [[00:37:23](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2243)]
Yeah.

##### **Geohot** [[00:37:25](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2245)]
But it's basically those three things abstracted.
So yeah, no, I shouldn't have used the word model.
These things should definitely be far abstracted from a model.
But yeah, you have the definition of compute, you have the contents of data, and then you have the runtime.

##### **Hooved** [[00:37:40](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2260)]
Right, yeah.
So that should be recognizable when looking at the refactored code.
And it should be somewhat intuitive how you would translate that to something other than JavaScript, such as C.

##### **Geohot** [[00:37:52](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2272)]
Yep, sounds good.
Cool.
OK.

##### **Chenyu** [[00:38:03](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2283)]
Well, torch front end, I just ask in the PR for the first one for the test ops.
I think that is getting close, some tests failing, like small ones.
I'm not sure why.
See if the author will reply.
And nanoGPT.

##### **Geohot** [[00:38:37](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2317)]
I see a few here with Boolean indexing and tensor non-zero, add mask select to tensor.py.
Have you been looking at those?

##### **Chenyu** [[00:38:49](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2329)]
Oh, me?
I think I closed a bunch.
I saw one that looks reasonable, but not really.
Okay, I can take a look.
So it's 9405.

##### **Geohot** [[00:39:20](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2360)]
So there's 9468 and 9405 are the two.
I'm just looking at them now.

##### **Chenyu** [[00:39:27](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2367)]
But the mention is duplicate from 9405 anyway.

##### **Geohot** [[00:39:32](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2372)]
Yeah.
I mean, there's a question of which one you think is cleaner.

##### **Chenyu** [[00:39:36](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2376)]
I don't know.
I opened this PR.
It doesn't look good, so I don't know.

##### **Geohot** [[00:39:42](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2382)]
Yeah, 9405 does not.
I think the other one looks better.
I think 9468 looks better than 9405.

##### **Chenyu** [[00:39:48](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2388)]
Yeah, I agree.

##### **Geohot** [[00:39:50](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2390)]
That's kind of why.
Yeah.

##### **Chenyu** [[00:39:54](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2394)]
OK.
I will comment on this and resolve it.

##### **Geohot** [[00:39:58](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2398)]
Yeah.
Cool.

##### **Chenyu** [[00:40:02](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2402)]
There's that.
I think the nano GPT authors here.
Or someone was talking.
Hello.

##### **B1tg** [[00:40:13](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2413)]
After we merged the memory leak fix in the master, I replaced the master and found the OEM still exist when running the nanoGPT.
There have high VRAM spike during the backward pass, so I hooked the backward pass.
and realize the module's parameters to fix this.

##### **Geohot** [[00:40:52](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2452)]
So wait, does this backward hook fix it?

##### **B1tg** [[00:40:58](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2458)]
Yes, it fixed the VRAM spike.

##### **Geohot** [[00:41:05](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2465)]
Great.
Yeah, I see.

##### **B1tg** [[00:41:08](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2468)]
But we have a problem.
If we use the register module for backward hook, it doesn't work with relu, as this is an existing issue in pytorch.

##### **Geohot** [[00:41:33](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2493)]
So should I expect this to work?
If I test this tomorrow on NanoGPT, should this work?

##### **B1tg** [[00:41:40](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2500)]
Yeah.

##### **Geohot** [[00:41:42](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2502)]
Cool.

##### **Geohot** [[00:41:43](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2503)]
Yeah, I'll test it tomorrow.
I see what you're doing here.
I think it's fine, at least for starters.
So yeah, I'll test this tomorrow.
And if it works, then yeah, the bounty is yours.

##### **Chenyu** [[00:41:58](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2518)]
OK.
The multi-GPU one.

##### **Geohot** [[00:42:13](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2533)]
tocubed has been working on that.
He's done a lot of the PyTorch stuff.
It's been good.

##### **Geohot** [[00:42:21](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2541)]
So I haven't looked at these in a while.

##### **Chenyu** [[00:42:28](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2548)]
OK, eight hours ago, he said a few more steps to clean up and test more.
So we will leave that to him.

##### **Geohot** [[00:42:34](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2554)]
Yeah.

##### **Chenyu** [[00:42:35](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2555)]
OK, sounds good.
Yeah, I think that's pretty much torch frontend.
And I will follow up with the test ops.
And I think once these three are clear, we can add more performance and really clean up the rest of the ops that is not supported.

##### **Geohot** [[00:42:53](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2573)]
Sounds good.
Yeah, I'll test nanoGPT tomorrow.

##### **Chenyu** [[00:42:58](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2578)]
OK.
Next, RetinaNet.

##### **Flata** [[00:43:03](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2583)]
Hello.
So for RetinaNet, I was able to integrate float16.
So the TinyBox screen benchmark that I did, I think it's sub 20 hours, so it's like 19 hours.
for training time.
So there's that.
Currently I'm trying to fix a small bug on just the beaming on the eval.
So because it was getting stuck, but I'm trying to see how to fix that.
So I'm working on that.
And then in the meantime, I'm starting to split up the big PR into smaller PR.
So I'm going to introduce, I think one for data loader and then another one for the model eval changes just to make sure everything is good.
And then
I just kind of get it down so that the main PR just has the training loop itself.
And I think what I'm planning to do after all this is done, and Chenyu, you can reproduce it, is actually just focus on getting the TinyBox set to be a bit better.
Even though it's sub 30 hours, it's still not under 24 hours.
So there's also that that I want to tackle as well.
So that's kind of like what I'm envisioning in this week.

##### **Chenyu** [[00:44:12](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2652)]
Yeah, as I said, at least the first bounty scope is if you can train the model on a reasonable machine in 24 hours, then bounty is yours for that.
And oh, speaking of eval, I check again.
For ResNet, we somehow only BEAM train.
We didn't BEAM eval for some reason.
I cannot remember.
But for BERT, we've been both.
And it's kind of important to be in eval if eval is the bottleneck.
I think for ResNet, it was fast enough, so we didn't really bother.

##### **Flata** [[00:44:51](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2691)]
Yeah.
Yeah, OK.
I was also going to say that with zibokapi's TopK, I think that's also, I'll also definitely revisit that as well to make the post-processing faster too.
So there's also that that can be, that is at least actionable now.

##### **Chenyu** [[00:45:10](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2710)]
Yeah, so for your change, I'd like you to, for everything that touches model eval, can be a standalone thing if you want to rewrite using topk or sorts, things like that.
And we're first making sure that eval is still correct, because that's the same eval we are going to use while training a model.

##### **Flata** [[00:45:32](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2732)]
OK, sounds good.

##### **Chenyu** [[00:45:38](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2738)]
Anyway, if you have a that's focusing on merging stuff that is ready, because this round would take a long time, I'd like to.
If you are confident already, I can reproduce when you are ready.
We can do that early.
Then we can think about making it fast.

##### **Flata** [[00:45:58](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2758)]
OK, sounds good.
I also had one question.
So is the second half of the bounty, does it only apply for this MLPerf season?
Or is it like?
Once we get it submitted, that also applies too.

##### **Chenyu** [[00:46:11](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2771)]
It's just not clear to me if they will keep RetinaNet around in the next round.
If it's still available and we can submit to it in the next round, then of course you can do it in the next cycle.
But if they decided to remove that as a benchmark, then sorry, no.
That's what happened.

##### **Flata** [[00:46:32](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2792)]
Right.
That's fair.
That's fair.
Okay.
I just wanted to ask.
Okay.
Sounds good.

##### **Geohot** [[00:46:38](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2798)]
Yeah, if you continue to improve it, I'm happy to pay out $1,000 per MLPerf cycle for the model.

##### **Chenyu** [[00:46:49](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2809)]
Yeah, I think for MLPerf, they are running into this problem that they also want to introduce some models, but having a benchmark is difficult.
I don't know.
I mean, this is a good run for us, because we can compare with CUDA and Torch stuff.
But it's probably less exciting for if they want to show off new hardware on new architectures.

##### **Chenyu** [[00:47:22](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2842)]
OK.
AMD compiler to LLVM.

##### **Geohot** [[00:47:30](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2850)]
I just saw that I have a refactor LLVM compiler looks good.
Sorry, I didn't see the updates on this.
I will get this merge if test pass.
Yeah, I think this is a good way to do it, like LLVM compiler, and then you override it with host LLVM compiler.

##### **B1tg** [[00:47:47](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2867)]
OK.
I found you using this branch in the Saturday streaming.
Did it work in the end?

##### **Geohot** [[00:47:58](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2878)]
Uh, yes, it did work.
But it was not the issue.
So yeah, you're getting close.
Let's just get it merged.
Sorry, I'll be more on top of the PRs.
I saw it originally and saw there was like a GPUR.
We can't do that.
Like we got all right, really high quality stuff.
But yeah, this one looks good.

##### **B1tg** [[00:48:18](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2898)]
Okay.

##### **Geohot** [[00:48:20](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2900)]
Cool.
So yeah, when CI passes, I will click merge on this.
Okay.
Yeah, no, I'm excited about that.

##### **Geohot** [[00:48:32](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2912)]
Sorry, I haven't been on top of this.
I think it's great that we're using LLVM and removing the last piece of AMD software.
I almost want to just make it the default.
I guess we kind of got to keep the other one around because it uses HIP.
But yeah, if we could just do probably that one refactor pull request and then maybe two more.
And yeah, that'll be it.

##### **Chenyu** [[00:49:01](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2941)]
OK.
Yeah, that's everything on the list.

##### **Chenyu** [[00:49:10](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2950)]
Do we have other open things that we can discuss?

##### **Geohot** [[00:49:16](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2956)]
I wish GitHub would let me star pull requests.
I could star them for tomorrow.
I can star them in my browser.

##### **Chenyu** [[00:49:31](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2971)]
Yeah, you can open some tabs for it, maybe.

##### **Geohot** [[00:49:35](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2975)]
Yeah, yeah, yeah.
Leave them in some window.
That makes sense.

##### **Chenyu** [[00:49:42](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2982)]
Oh, we have memory leak.
Harold reports more memory leak on stuff.

##### **Geohot** [[00:49:48](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2988)]
Oh.
Well, that doesn't sound good.
Who wants to be in charge of memory leaks here?

##### **Chenyu** [[00:49:50](https://www.youtube.com/watch?v=jn3no5UZLmI&t=2990)]
I think one is QCOM..
only, and one affects every backend for JIT.

##### **Geohot** [[00:50:15](https://www.youtube.com/watch?v=jn3no5UZLmI&t=3015)]
Yeah, we definitely need to fix this stuff.
It should be really easy to write tests for, too.
We'll just put it in a loop and OOM on the CI machine.
It should be fast.


##### **Chenyu** [[00:50:31](https://www.youtube.com/watch?v=jn3no5UZLmI&t=3031)]
Yeah.
OK.
I will spend some time to close some issues.
I'd like to see less than 100 three digits, a lot more three digits.

##### **Geohot** [[00:50:45](https://www.youtube.com/watch?v=jn3no5UZLmI&t=3045)]
I'll go through PRs tomorrow.
OK.

##### **Chenyu** [[00:50:51](https://www.youtube.com/watch?v=jn3no5UZLmI&t=3051)]
Sounds good.

##### **Geohot** [[00:50:52](https://www.youtube.com/watch?v=jn3no5UZLmI&t=3052)]
Anything to avoid working on the DSP.

##### **Chenyu** [[00:50:56](https://www.youtube.com/watch?v=jn3no5UZLmI&t=3056)]
No, you only have two weeks left.

##### **Geohot** [[00:51:00](https://www.youtube.com/watch?v=jn3no5UZLmI&t=3060)]
It's so awful.

##### **Chenyu** [[00:51:03](https://www.youtube.com/watch?v=jn3no5UZLmI&t=3063)]
And four weeks ago, you said it would be done in two weeks.

##### **Geohot** [[00:51:06](https://www.youtube.com/watch?v=jn3no5UZLmI&t=3066)]
Yeah, I know.
I know.
OK, OK.
Today is the first day that I've posted a real speed up.
I've got the whole thing running end-to-end on the DSP.
It's correct.

##### **Geohot** [[00:51:20](https://www.youtube.com/watch?v=jn3no5UZLmI&t=3080)]
It's just 182 milliseconds.
Yeah, I'll do PRs tomorrow, and then get back to it.
I think this got it.
LLVM is just generating bad code.
Yeah, Qualcomm wrote all this stuff in assembly, it seems.

##### **Chenyu** [[00:51:47](https://www.youtube.com/watch?v=jn3no5UZLmI&t=3107)]
OK, yeah.
That's good.
I want to also post the stable diffusion large is slow.
I'll probably benchmark that later.

##### **Geohot** [[00:51:58](https://www.youtube.com/watch?v=jn3no5UZLmI&t=3118)]
Yeah, the large one seems to have even more of a disparity.
than the non-large.

##### **Chenyu** [[00:52:05](https://www.youtube.com/watch?v=jn3no5UZLmI&t=3125)]
If I remember correctly, I think the large one is not all jitted.
So there's scheduling time there.

##### **Geohot** [[00:52:15](https://www.youtube.com/watch?v=jn3no5UZLmI&t=3135)]
Well, that's going to make it real slow.

##### **Chenyu** [[00:52:18](https://www.youtube.com/watch?v=jn3no5UZLmI&t=3138)]
Yeah.
So I think that's the main reason why it's slow.
Because for the examples that we don't really try making fast, some of these Python time issue.

##### **Geohot** [[00:52:31](https://www.youtube.com/watch?v=jn3no5UZLmI&t=3151)]
Yeah, no, we should definitely fully JIT that.
I have two projects after the DSP.
One is rewriting the Clang parser thing, and the other is fast graph rewrite.
And I'll get serious about Python time, because it's gotten out of control.
The Python time is out of control.
You can really see.

##### **Chenyu** [[00:52:55](https://www.youtube.com/watch?v=jn3no5UZLmI&t=3175)]
stable recently.

##### **Geohot** [[00:53:01](https://www.youtube.com/watch?v=jn3no5UZLmI&t=3181)]
I mean, it hasn't been getting worse, sure, but it's just out of control.
And like the HLB CIFAR is now like twice as slow as it used to be.
Yeah.

##### **Chenyu** [[00:53:16](https://www.youtube.com/watch?v=jn3no5UZLmI&t=3196)]
And mixtral without JIT is like three times.

##### **Geohot** [[00:53:20](https://www.youtube.com/watch?v=jn3no5UZLmI&t=3200)]
I know, I know.
LLaMA used to run at 100 milliseconds.

##### **Chenyu** [[00:53:25](https://www.youtube.com/watch?v=jn3no5UZLmI&t=3205)]
That was almost two years ago.

##### **Geohot** [[00:53:27](https://www.youtube.com/watch?v=jn3no5UZLmI&t=3207)]
I know.
Tinygrad used to be fast.
Used to be tiny.
Those were the days.
But now the generated code is fast.

##### **Geohot** [[00:53:41](https://www.youtube.com/watch?v=jn3no5UZLmI&t=3221)]
No, I think we're about to have some major breakthroughs with the scheduler that are just going to 30% down RAM.
And that's not just RAM capacity.
That's also bandwidth.
So I'm really excited for that.
That sounds good.

##### **Chenyu** [[00:54:10](https://www.youtube.com/watch?v=jn3no5UZLmI&t=3250)]
OK, I think that's it for this week.
Thanks, everyone, and see you next week.

##### **Geohot** [[00:54:18](https://www.youtube.com/watch?v=jn3no5UZLmI&t=3258)]
Bye.

