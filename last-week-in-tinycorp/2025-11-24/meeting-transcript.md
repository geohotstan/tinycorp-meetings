# 2025-11-24 Meeting

### Meeting Agenda

**Time:** 9am Monday San Diego time
- AMD contract general
- flash attention
- VIZ/Profiling
- nvidia HEVC decode
- investigate macOS SIP-free packaging
- QCOM MESA backend
- Python speed
- assemblers?

### Audio

[Youtube Link](https://www.youtube.com/watch?v=22O5E5aAnJU)

### Highlights

- **[AMD Contract Targets](#geohot-000026)**: The team is aiming to complete the AMD contract by May, with specific performance targets including single machine, two-machine clusters, and beating NVIDIA performance benchmarks, each valued at $400,000.
- **[Flash Attention Progress](#geohot-000126)**: Flash attention is identified as the primary blocker for training Llama 405B; the forward pass works on MI350, and the backward pass is scheduled for implementation this week to enable training Llama 8B.
- **[Visualization and Profiling](#geohot-000252)**: Occupancy visualization is working, allowing users to see wave patterns; discussion includes setting `sqtt-limit-se` to zero by default to improve performance on instruction tracing.
- **[Optimizing Instruction Tracing](#geohot-000752)**: Geohot critiques the current profiler for listing every instruction hit in loops, suggesting a UI update to aggregate hits and offer expandable views for better usability.
- **[NVIDIA HEVC Decode](#geohot-001513)**: HEVC decode is functional; Nimlgen implemented a custom file format parser because the hardware requires specific bit offsets and physical address spacing in a dedicated video queue.
- **[macOS SIP-free Packaging](#geohot-002502)**: The team discusses improving the macOS eGPU driver packaging to remove the requirement for disabling System Integrity Protection (SIP), aiming to make the installation process user-friendly.
- **[Qualcomm Mesa Backend](#nimlgen-002813)**: The fully open-source Qualcomm Mesa backend is ready to merge; it now requires Tiny Mesa for disassembly, and while CI passes, there are ongoing investigations into race conditions in the ONNX loader.
- **[Python Speed Improvements](#geohot-003640)**: Geohot is focusing on Python speed optimizations, achieving significant speedups recently, and plans to improve `vmap` handling and string ranges for backward passes.
- **[Assembly Backends & LLVM](#geohot-004633)**: Plans are set to eventually replace LLVM with custom assembly backends for GPUs, particularly for CDNA4/MI350, due to suboptimal code generation by the current LLVM backend.
- **[WebGPU & Bounties](#geohot-004932)**: The WebGPU PR passed CI and was merged; the team briefly reviews the status of the GPT-OSS bounty, noting it still requires significant speed optimizations.

### Transcript
##### **Geohot** [[00:00:00](https://www.youtube.com/watch?v=22O5E5aAnJU&t=0)]
Chen Yu is out this week, so I will lead the meeting. I'm not as good at it as Chen Yu.

##### **Geohot** [[00:00:09](https://www.youtube.com/watch?v=22O5E5aAnJU&t=9)]
So, yeah, we'll start with, instead of company general, we'll start with AMD contract general,

##### **Nimlgen** [[00:00:14](https://www.youtube.com/watch?v=22O5E5aAnJU&t=14)]
because the main purpose of this company is the AMD contract.

##### **Nimlgen** [[00:00:20](https://www.youtube.com/watch?v=22O5E5aAnJU&t=20)]
You know, the AMD contract should be hopefully done to the best of our abilities by May.

##### **Geohot** [[00:00:26](https://www.youtube.com/watch?v=22O5E5aAnJU&t=26)]
You know, look, we have four potential targets. We have a single machine one, a two machine one,

##### **Geohot** [[00:00:36](https://www.youtube.com/watch?v=22O5E5aAnJU&t=36)]
and then if we can get anything, or if we can get faster than NVIDIA, and those are $400,000 each.

##### **Geohot** [[00:00:47](https://www.youtube.com/watch?v=22O5E5aAnJU&t=47)]
You know, I just want to show that Tinygrad can run the absolute best, train the absolute best models.

##### **Geohot** [[00:00:54](https://www.youtube.com/watch?v=22O5E5aAnJU&t=54)]
If we're training Lama 405B.

##### **Geohot** [[00:00:57](https://www.youtube.com/watch?v=22O5E5aAnJU&t=57)]
There's a few things bigger than Lama 405B, of course, at the crazy labs.

##### **Nimlgen** [[00:01:03](https://www.youtube.com/watch?v=22O5E5aAnJU&t=63)]
So, I think it's a good target, and I think it stress tests a lot of pieces of Tinygrad in a way that's very important,

##### **Nimlgen** [[00:01:10](https://www.youtube.com/watch?v=22O5E5aAnJU&t=70)]
because if you can train Lama 405B, if you can start up the process that trains Lama 405B in a minute,

##### **Geohot** [[00:01:15](https://www.youtube.com/watch?v=22O5E5aAnJU&t=75)]
you can start up the one that trains Lama 8B in five seconds.

##### **Geohot** [[00:01:19](https://www.youtube.com/watch?v=22O5E5aAnJU&t=79)]
So, you know, all these things trickle down our economics is real.

##### **Geohot** [[00:01:24](https://www.youtube.com/watch?v=22O5E5aAnJU&t=84)]
So, yeah, let's start with...

##### **Geohot** [[00:01:26](https://www.youtube.com/watch?v=22O5E5aAnJU&t=86)]
I think the biggest thing holding us back right now from just actually training this stuff is flash retention.

##### **Geohot** [[00:01:32](https://www.youtube.com/watch?v=22O5E5aAnJU&t=92)]
A bunch of the stuff to implement flash retention is done.

##### **Nimlgen** [[00:01:35](https://www.youtube.com/watch?v=22O5E5aAnJU&t=95)]
There's a...

##### **Nimlgen** [[00:01:36](https://www.youtube.com/watch?v=22O5E5aAnJU&t=96)]
Currently, on my branch, there's a flash retention forward that works on MI350,

##### **Geohot** [[00:01:41](https://www.youtube.com/watch?v=22O5E5aAnJU&t=101)]
and then that's currently missing just GQA.

##### **Geohot** [[00:01:44](https://www.youtube.com/watch?v=22O5E5aAnJU&t=104)]
Actually, GQA works now.

##### **Geohot** [[00:01:46](https://www.youtube.com/watch?v=22O5E5aAnJU&t=106)]
And just the causal mask.

##### **Geohot** [[00:01:48](https://www.youtube.com/watch?v=22O5E5aAnJU&t=108)]
And then I will write backwards this week, and hoping to get something training before Thanksgiving weekend.

##### **Geohot** [[00:01:53](https://www.youtube.com/watch?v=22O5E5aAnJU&t=113)]
Great.

##### **Nimlgen** [[00:01:55](https://www.youtube.com/watch?v=22O5E5aAnJU&t=115)]
Yeah.

##### **Nimlgen** [[00:01:56](https://www.youtube.com/watch?v=22O5E5aAnJU&t=116)]
I think once we flash retention, we'll be able to train 8B.

##### **Geohot** [[00:01:59](https://www.youtube.com/watch?v=22O5E5aAnJU&t=119)]
We can retrain 8B now, but the time is crazy,

##### **Geohot** [[00:02:02](https://www.youtube.com/watch?v=22O5E5aAnJU&t=122)]
because we should kick off one with...

##### **Geohot** [[00:02:04](https://www.youtube.com/watch?v=22O5E5aAnJU&t=124)]
Do you want to kick off one with 1.2.4 context or something?

##### **Geohot** [[00:02:07](https://www.youtube.com/watch?v=22O5E5aAnJU&t=127)]
Just to make sure everything works.

##### **Geohot** [[00:02:10](https://www.youtube.com/watch?v=22O5E5aAnJU&t=130)]
Yeah, that's fine.

##### **Nimlgen** [[00:02:11](https://www.youtube.com/watch?v=22O5E5aAnJU&t=131)]
I had a week-long one going before, and that was fine.

##### **Nimlgen** [[00:02:14](https://www.youtube.com/watch?v=22O5E5aAnJU&t=134)]
It was 1D, 1.2.4, though.

##### **Geohot** [[00:02:16](https://www.youtube.com/watch?v=22O5E5aAnJU&t=136)]
Let's check it again.

##### **Geohot** [[00:02:17](https://www.youtube.com/watch?v=22O5E5aAnJU&t=137)]
Yeah.

##### **Geohot** [[00:02:17](https://www.youtube.com/watch?v=22O5E5aAnJU&t=137)]
Can we do 8B, 1.2.4?

##### **Geohot** [[00:02:19](https://www.youtube.com/watch?v=22O5E5aAnJU&t=139)]
Yeah.

##### **Geohot** [[00:02:19](https://www.youtube.com/watch?v=22O5E5aAnJU&t=139)]
Yeah.

##### **Nimlgen** [[00:02:21](https://www.youtube.com/watch?v=22O5E5aAnJU&t=141)]
Especially, let's do 8B, 1.2.4, 8GPUs.

##### **Nimlgen** [[00:02:23](https://www.youtube.com/watch?v=22O5E5aAnJU&t=143)]
Yeah.

##### **Geohot** [[00:02:24](https://www.youtube.com/watch?v=22O5E5aAnJU&t=144)]
I fixed MP.

##### **Geohot** [[00:02:25](https://www.youtube.com/watch?v=22O5E5aAnJU&t=145)]
So that should work now.

##### **Geohot** [[00:02:27](https://www.youtube.com/watch?v=22O5E5aAnJU&t=147)]
We should quickly benchmark them.

##### **Geohot** [[00:02:29](https://www.youtube.com/watch?v=22O5E5aAnJU&t=149)]
But yeah, we should start always having training jobs running on one of our MI350 boxes, the other ones to play with.

##### **Geohot** [[00:02:39](https://www.youtube.com/watch?v=22O5E5aAnJU&t=159)]
So yeah, that's that.

##### **Nimlgen** [[00:02:41](https://www.youtube.com/watch?v=22O5E5aAnJU&t=161)]
All right, cool.

##### **Nimlgen** [[00:02:41](https://www.youtube.com/watch?v=22O5E5aAnJU&t=161)]
So that'll be done this week.

##### **Geohot** [[00:02:43](https://www.youtube.com/watch?v=22O5E5aAnJU&t=163)]
Let's talk about Viz and profiling.

##### **Geohot** [[00:02:46](https://www.youtube.com/watch?v=22O5E5aAnJU&t=166)]
So I see you got all the occupancies working?

##### **Geohot** [[00:02:52](https://www.youtube.com/watch?v=22O5E5aAnJU&t=172)]
Yep.

##### **Geohot** [[00:02:52](https://www.youtube.com/watch?v=22O5E5aAnJU&t=172)]
I got all the occupancies.

##### **Geohot** [[00:02:55](https://www.youtube.com/watch?v=22O5E5aAnJU&t=175)]
So I can see the same stuff in there.

##### **Nimlgen** [[00:02:58](https://www.youtube.com/watch?v=22O5E5aAnJU&t=178)]
It's pretty nice, actually, that we have all the same Ds right there.

##### **Nimlgen** [[00:03:03](https://www.youtube.com/watch?v=22O5E5aAnJU&t=183)]
And you can see the patterns of some things getting weakened.

##### **Geohot** [[00:03:07](https://www.youtube.com/watch?v=22O5E5aAnJU&t=187)]
Great.

##### **Geohot** [[00:03:09](https://www.youtube.com/watch?v=22O5E5aAnJU&t=189)]
Yeah.

##### **Geohot** [[00:03:09](https://www.youtube.com/watch?v=22O5E5aAnJU&t=189)]
I think we should probably set that SEMask thing to zero by default.

##### **Geohot** [[00:03:16](https://www.youtube.com/watch?v=22O5E5aAnJU&t=196)]
And we have that, like, SQTT SEMask.

##### **Geohot** [[00:03:21](https://www.youtube.com/watch?v=22O5E5aAnJU&t=201)]
Mm-hmm.

##### **Nimlgen** [[00:03:21](https://www.youtube.com/watch?v=22O5E5aAnJU&t=201)]
Yeah, for the instruction ones.

##### **Nimlgen** [[00:03:23](https://www.youtube.com/watch?v=22O5E5aAnJU&t=203)]
That will just disable instruction.

##### **Geohot** [[00:03:25](https://www.youtube.com/watch?v=22O5E5aAnJU&t=205)]
So we can keep instruction tracing on all of them.

##### **Geohot** [[00:03:26](https://www.youtube.com/watch?v=22O5E5aAnJU&t=206)]
No, I don't want to disable instruction tracing on all of them.

##### **Geohot** [[00:03:29](https://www.youtube.com/watch?v=22O5E5aAnJU&t=209)]
We can keep instruction tracing on one.

##### **Geohot** [[00:03:32](https://www.youtube.com/watch?v=22O5E5aAnJU&t=212)]
Well, actually, if we disable instruction tracing, is it, like, really fast?

##### **Geohot** [[00:03:41](https://www.youtube.com/watch?v=22O5E5aAnJU&t=221)]
I think so, because the only thing that is tracing is the start and end of every wave.

##### **Nimlgen** [[00:03:49](https://www.youtube.com/watch?v=22O5E5aAnJU&t=229)]
Yeah.

##### **Nimlgen** [[00:03:51](https://www.youtube.com/watch?v=22O5E5aAnJU&t=231)]
I mean, it's fast.

##### **Geohot** [[00:03:53](https://www.youtube.com/watch?v=22O5E5aAnJU&t=233)]
Even...

##### **Geohot** [[00:03:53](https://www.youtube.com/watch?v=22O5E5aAnJU&t=233)]
It's kind of fast even with instruction tracing if we do not limit any SEs.

##### **Geohot** [[00:03:58](https://www.youtube.com/watch?v=22O5E5aAnJU&t=238)]
But there is a stage to copy out the buffer after each kernel.

##### **Geohot** [[00:04:06](https://www.youtube.com/watch?v=22O5E5aAnJU&t=246)]
So actually, that will take some time.

##### **Geohot** [[00:04:09](https://www.youtube.com/watch?v=22O5E5aAnJU&t=249)]
Got it.

##### **Nimlgen** [[00:04:10](https://www.youtube.com/watch?v=22O5E5aAnJU&t=250)]
I mean, I think what we should do for viz equals 2 is just make sqtt-livet-se, by default, not be on.

##### **Nimlgen** [[00:04:27](https://www.youtube.com/watch?v=22O5E5aAnJU&t=267)]
So we can keep it on.

##### **Geohot** [[00:04:27](https://www.youtube.com/watch?v=22O5E5aAnJU&t=267)]
I see.

##### **Geohot** [[00:04:27](https://www.youtube.com/watch?v=22O5E5aAnJU&t=267)]
You won't have any instruction tracing for that, then?

##### **Geohot** [[00:04:30](https://www.youtube.com/watch?v=22O5E5aAnJU&t=270)]
No instruction timings?

##### **Geohot** [[00:04:31](https://www.youtube.com/watch?v=22O5E5aAnJU&t=271)]
I won't have any instruction tracing.

##### **Geohot** [[00:04:32](https://www.youtube.com/watch?v=22O5E5aAnJU&t=272)]
Okay.

##### **Nimlgen** [[00:04:33](https://www.youtube.com/watch?v=22O5E5aAnJU&t=273)]
So I just ran one, and nothing is...

##### **Nimlgen** [[00:04:35](https://www.youtube.com/watch?v=22O5E5aAnJU&t=275)]
It's, like, broken in my counters view.

##### **Geohot** [[00:04:40](https://www.youtube.com/watch?v=22O5E5aAnJU&t=280)]
Let me make sure I'm on the latest master.

##### **Geohot** [[00:04:46](https://www.youtube.com/watch?v=22O5E5aAnJU&t=286)]
Yeah.

##### **Geohot** [[00:04:47](https://www.youtube.com/watch?v=22O5E5aAnJU&t=287)]
I'm seeing nothing in my counters view.

##### **Geohot** [[00:04:51](https://www.youtube.com/watch?v=22O5E5aAnJU&t=291)]
Oh.

##### **Geohot** [[00:04:52](https://www.youtube.com/watch?v=22O5E5aAnJU&t=292)]
Canvas exceeds the maximum number of times.

##### **Nimlgen** [[00:04:53](https://www.youtube.com/watch?v=22O5E5aAnJU&t=293)]
It's max size.

##### **Nimlgen** [[00:04:58](https://www.youtube.com/watch?v=22O5E5aAnJU&t=298)]
That sounds weird.

##### **Geohot** [[00:05:00](https://www.youtube.com/watch?v=22O5E5aAnJU&t=300)]
Yeah.

##### **Geohot** [[00:05:01](https://www.youtube.com/watch?v=22O5E5aAnJU&t=301)]
I'm in Firefox.

##### **Geohot** [[00:05:04](https://www.youtube.com/watch?v=22O5E5aAnJU&t=304)]
But, yeah.

##### **Geohot** [[00:05:06](https://www.youtube.com/watch?v=22O5E5aAnJU&t=306)]
So I think the thing that I really want you to focus on this week is just starting to stress test this on bigger and bigger kernels.

##### **Geohot** [[00:05:16](https://www.youtube.com/watch?v=22O5E5aAnJU&t=316)]
And on bigger and bigger...

##### **Nimlgen** [[00:05:20](https://www.youtube.com/watch?v=22O5E5aAnJU&t=320)]
You know, we have to get LLAMA-405B tracing with viz.

##### **Nimlgen** [[00:05:23](https://www.youtube.com/watch?v=22O5E5aAnJU&t=323)]
viz equals two, basically.

##### **Geohot** [[00:05:24](https://www.youtube.com/watch?v=22O5E5aAnJU&t=324)]
Like, that's the goal.

##### **Geohot** [[00:05:26](https://www.youtube.com/watch?v=22O5E5aAnJU&t=326)]
SQTT-Limit-SE is totally fine.

##### **Geohot** [[00:05:28](https://www.youtube.com/watch?v=22O5E5aAnJU&t=328)]
We can leave that on.

##### **Geohot** [[00:05:31](https://www.youtube.com/watch?v=22O5E5aAnJU&t=331)]
Let me see if this...

##### **Geohot** [[00:05:32](https://www.youtube.com/watch?v=22O5E5aAnJU&t=332)]
Let me see if Chrome has a better max size of a canvas.

##### **Nimlgen** [[00:05:37](https://www.youtube.com/watch?v=22O5E5aAnJU&t=337)]
Oh, it does!

##### **Nimlgen** [[00:05:38](https://www.youtube.com/watch?v=22O5E5aAnJU&t=338)]
Hey, look at that!

##### **Geohot** [[00:05:39](https://www.youtube.com/watch?v=22O5E5aAnJU&t=339)]
But it's...

##### **Geohot** [[00:05:40](https://www.youtube.com/watch?v=22O5E5aAnJU&t=340)]
Oh, it's absurdly slow.

##### **Geohot** [[00:05:42](https://www.youtube.com/watch?v=22O5E5aAnJU&t=342)]
And oh, oh...

##### **Geohot** [[00:05:45](https://www.youtube.com/watch?v=22O5E5aAnJU&t=345)]
I mean, this isn't even that big of a kernel, and it's really slow.

##### **Geohot** [[00:05:51](https://www.youtube.com/watch?v=22O5E5aAnJU&t=351)]
Okay, cool.

##### **Nimlgen** [[00:05:51](https://www.youtube.com/watch?v=22O5E5aAnJU&t=351)]
But I like this INSWAVE-OCWAVE.

##### **Nimlgen** [[00:05:53](https://www.youtube.com/watch?v=22O5E5aAnJU&t=353)]
Okay.

##### **Geohot** [[00:05:56](https://www.youtube.com/watch?v=22O5E5aAnJU&t=356)]
So, let's see if I can get that.

##### **Geohot** [[00:05:56](https://www.youtube.com/watch?v=22O5E5aAnJU&t=356)]
And then we got to IMPROVE...

##### **Geohot** [[00:05:56](https://www.youtube.com/watch?v=22O5E5aAnJU&t=356)]
Yeah.

##### **Geohot** [[00:05:57](https://www.youtube.com/watch?v=22O5E5aAnJU&t=357)]
And then we got to IMPROVE...

##### **Geohot** [[00:05:58](https://www.youtube.com/watch?v=22O5E5aAnJU&t=358)]
So my parser is pretty good now.

##### **Nimlgen** [[00:06:00](https://www.youtube.com/watch?v=22O5E5aAnJU&t=360)]
If you run with SQTT-PARSE equals 1, I figured out the whole format.

##### **Nimlgen** [[00:06:06](https://www.youtube.com/watch?v=22O5E5aAnJU&t=366)]
I still haven't lined it up with the instructions, so I wouldn't use it quite yet.

##### **Geohot** [[00:06:10](https://www.youtube.com/watch?v=22O5E5aAnJU&t=370)]
But just if you're like trying to figure out like actually what's going on and you're on like a small kernel, you can run it and it will print it all out.

##### **Geohot** [[00:06:16](https://www.youtube.com/watch?v=22O5E5aAnJU&t=376)]
It's pretty cool.

##### **Geohot** [[00:06:19](https://www.youtube.com/watch?v=22O5E5aAnJU&t=379)]
But, yeah.

##### **Geohot** [[00:06:19](https://www.youtube.com/watch?v=22O5E5aAnJU&t=379)]
So I think...

##### **Geohot** [[00:06:20](https://www.youtube.com/watch?v=22O5E5aAnJU&t=380)]
When you're showing the like idle duration and so on, I think it's really cool.

##### **Nimlgen** [[00:06:23](https://www.youtube.com/watch?v=22O5E5aAnJU&t=383)]
So, I'm going to go ahead and install.

##### **Nimlgen** [[00:06:24](https://www.youtube.com/watch?v=22O5E5aAnJU&t=384)]
Are those three numbers just given to you by the thing?

##### **Geohot** [[00:06:29](https://www.youtube.com/watch?v=22O5E5aAnJU&t=389)]
Yeah.

##### **Geohot** [[00:06:31](https://www.youtube.com/watch?v=22O5E5aAnJU&t=391)]
And does it give you...

##### **Geohot** [[00:06:34](https://www.youtube.com/watch?v=22O5E5aAnJU&t=394)]
How many number...

##### **Geohot** [[00:06:35](https://www.youtube.com/watch?v=22O5E5aAnJU&t=395)]
If you're in a loop where an instruction runs 10 times, does it give you those numbers 10 times or one time?

##### **Geohot** [[00:06:40](https://www.youtube.com/watch?v=22O5E5aAnJU&t=400)]
10 times.

##### **Nimlgen** [[00:06:42](https://www.youtube.com/watch?v=22O5E5aAnJU&t=402)]
It gives you the numbers 10 times.

##### **Nimlgen** [[00:06:43](https://www.youtube.com/watch?v=22O5E5aAnJU&t=403)]
Okay.

##### **Geohot** [[00:06:43](https://www.youtube.com/watch?v=22O5E5aAnJU&t=403)]
So right now, you're just literally copying in the entire trace, even if it's the same instruction over and over again.

##### **Geohot** [[00:06:51](https://www.youtube.com/watch?v=22O5E5aAnJU&t=411)]
Yeah.

##### **Geohot** [[00:06:51](https://www.youtube.com/watch?v=22O5E5aAnJU&t=411)]
Okay, cool.

##### **Geohot** [[00:06:52](https://www.youtube.com/watch?v=22O5E5aAnJU&t=412)]
Yeah.

##### **Geohot** [[00:06:53](https://www.youtube.com/watch?v=22O5E5aAnJU&t=413)]
Yeah.

##### **Nimlgen** [[00:06:53](https://www.youtube.com/watch?v=22O5E5aAnJU&t=413)]
So if I do a search.

##### **Nimlgen** [[00:06:54](https://www.youtube.com/watch?v=22O5E5aAnJU&t=414)]
So we got to fix that.

##### **Geohot** [[00:06:57](https://www.youtube.com/watch?v=22O5E5aAnJU&t=417)]
What we should be doing is you have like the PC address of each of those instructions, right?

##### **Geohot** [[00:07:02](https://www.youtube.com/watch?v=22O5E5aAnJU&t=422)]
Yeah.

##### **Geohot** [[00:07:03](https://www.youtube.com/watch?v=22O5E5aAnJU&t=423)]
Yeah.

##### **Geohot** [[00:07:04](https://www.youtube.com/watch?v=22O5E5aAnJU&t=424)]
So what we want to do, and if you read these in the profilers, is we want to show like a min, max, and an average if things are hit multiple times.

##### **Geohot** [[00:07:19](https://www.youtube.com/watch?v=22O5E5aAnJU&t=439)]
You want to show the sum?

##### **Nimlgen** [[00:07:25](https://www.youtube.com/watch?v=22O5E5aAnJU&t=445)]
Sum.

##### **Nimlgen** [[00:07:27](https://www.youtube.com/watch?v=22O5E5aAnJU&t=447)]
Yeah, maybe the sum.

##### **Geohot** [[00:07:28](https://www.youtube.com/watch?v=22O5E5aAnJU&t=448)]
Whatever the other one show.

##### **Geohot** [[00:07:29](https://www.youtube.com/watch?v=22O5E5aAnJU&t=449)]
But yeah, I mean these traces are...

##### **Geohot** [[00:07:31](https://www.youtube.com/watch?v=22O5E5aAnJU&t=451)]
Oh, should we show the sum?

##### **Geohot** [[00:07:32](https://www.youtube.com/watch?v=22O5E5aAnJU&t=452)]
Yeah.

##### **Geohot** [[00:07:33](https://www.youtube.com/watch?v=22O5E5aAnJU&t=453)]
Cool.

##### **Nimlgen** [[00:07:34](https://www.youtube.com/watch?v=22O5E5aAnJU&t=454)]
Yeah, the sum is good.

##### **Nimlgen** [[00:07:35](https://www.youtube.com/watch?v=22O5E5aAnJU&t=455)]
These traces are absurdly long and unusable right now.

##### **Geohot** [[00:07:38](https://www.youtube.com/watch?v=22O5E5aAnJU&t=458)]
Yeah.

##### **Geohot** [[00:07:39](https://www.youtube.com/watch?v=22O5E5aAnJU&t=459)]
Like maybe in the leftmost column, I want to see the number of hits.

##### **Geohot** [[00:07:44](https://www.youtube.com/watch?v=22O5E5aAnJU&t=464)]
I mean we should really just copy, copy RGP.

##### **Geohot** [[00:07:48](https://www.youtube.com/watch?v=22O5E5aAnJU&t=468)]
Yeah.

##### **Geohot** [[00:07:49](https://www.youtube.com/watch?v=22O5E5aAnJU&t=469)]
Yeah.

##### **Nimlgen** [[00:07:49](https://www.youtube.com/watch?v=22O5E5aAnJU&t=469)]
But right now, with...

##### **Nimlgen** [[00:07:51](https://www.youtube.com/watch?v=22O5E5aAnJU&t=471)]
When you have this, like, the number of hits, I want to see the number of hits.

##### **Geohot** [[00:07:52](https://www.youtube.com/watch?v=22O5E5aAnJU&t=472)]
Whenever you have a kernel with a loop, this is pretty much unusable because I'm not going to scroll through this huge, massive list.

##### **Geohot** [[00:08:00](https://www.youtube.com/watch?v=22O5E5aAnJU&t=480)]
And it would be nice...

##### **Geohot** [[00:08:01](https://www.youtube.com/watch?v=22O5E5aAnJU&t=481)]
I mean, what would be really cool actually is if there was a little triangle next to it and I could expand it, I could see all the hits of the instruction.

##### **Geohot** [[00:08:15](https://www.youtube.com/watch?v=22O5E5aAnJU&t=495)]
But yeah, so I think good goals for this week are...

##### **Geohot** [[00:08:21](https://www.youtube.com/watch?v=22O5E5aAnJU&t=501)]
Cleaning up the instruction trace to be that.

##### **Nimlgen** [[00:08:25](https://www.youtube.com/watch?v=22O5E5aAnJU&t=505)]
We have to fix this.

##### **Nimlgen** [[00:08:26](https://www.youtube.com/watch?v=22O5E5aAnJU&t=506)]
This profile is way too slow, even in Chrome.

##### **Geohot** [[00:08:29](https://www.youtube.com/watch?v=22O5E5aAnJU&t=509)]
And this is a pretty tiny kernel too.

##### **Geohot** [[00:08:32](https://www.youtube.com/watch?v=22O5E5aAnJU&t=512)]
Like this doesn't have a lot of occupancy.

##### **Geohot** [[00:08:38](https://www.youtube.com/watch?v=22O5E5aAnJU&t=518)]
Yeah.

##### **Geohot** [[00:08:39](https://www.youtube.com/watch?v=22O5E5aAnJU&t=519)]
Yeah, I'm getting like half an FPS.

##### **Geohot** [[00:08:54](https://www.youtube.com/watch?v=22O5E5aAnJU&t=534)]
So, yeah, what do you think that is?

##### **Nimlgen** [[00:08:58](https://www.youtube.com/watch?v=22O5E5aAnJU&t=538)]
Oh, the slowness?

##### **Nimlgen** [[00:08:59](https://www.youtube.com/watch?v=22O5E5aAnJU&t=539)]
Yeah.

##### **Geohot** [[00:09:00](https://www.youtube.com/watch?v=22O5E5aAnJU&t=540)]
Are you experiencing it too?

##### **Geohot** [[00:09:01](https://www.youtube.com/watch?v=22O5E5aAnJU&t=541)]
My rendering is pretty naive.

##### **Geohot** [[00:09:06](https://www.youtube.com/watch?v=22O5E5aAnJU&t=546)]
It's rendering every single thing, even if it's not in the view.

##### **Geohot** [[00:09:10](https://www.youtube.com/watch?v=22O5E5aAnJU&t=550)]
No, but that's not even the problem.

##### **Geohot** [[00:09:12](https://www.youtube.com/watch?v=22O5E5aAnJU&t=552)]
Like on this kernel, I don't really know why this is that slow.

##### **Nimlgen** [[00:09:17](https://www.youtube.com/watch?v=22O5E5aAnJU&t=557)]
I mean, we also have to make it thinner, smaller.

##### **Nimlgen** [[00:09:19](https://www.youtube.com/watch?v=22O5E5aAnJU&t=559)]
I mean, it's not...

##### **Geohot** [[00:09:19](https://www.youtube.com/watch?v=22O5E5aAnJU&t=559)]
I really do want to fit the whole GPU on a single screen.

##### **Geohot** [[00:09:26](https://www.youtube.com/watch?v=22O5E5aAnJU&t=566)]
Yeah.

##### **Geohot** [[00:09:28](https://www.youtube.com/watch?v=22O5E5aAnJU&t=568)]
I tried.

##### **Geohot** [[00:09:29](https://www.youtube.com/watch?v=22O5E5aAnJU&t=569)]
At some point, it gets so small that you see nothing.

##### **Geohot** [[00:09:33](https://www.youtube.com/watch?v=22O5E5aAnJU&t=573)]
Yeah.

##### **Nimlgen** [[00:09:37](https://www.youtube.com/watch?v=22O5E5aAnJU&t=577)]
Let's think about how we can do this.

##### **Nimlgen** [[00:09:44](https://www.youtube.com/watch?v=22O5E5aAnJU&t=584)]
Maybe we should talk about this more after the meeting.

##### **Geohot** [[00:09:50](https://www.youtube.com/watch?v=22O5E5aAnJU&t=590)]
Yeah, I have a lot of...

##### **Geohot** [[00:09:53](https://www.youtube.com/watch?v=22O5E5aAnJU&t=593)]
I think there's so much capability here to go like beyond what the existing GPU profilers

##### **Geohot** [[00:10:00](https://www.youtube.com/watch?v=22O5E5aAnJU&t=600)]
have done.

##### **Geohot** [[00:10:01](https://www.youtube.com/watch?v=22O5E5aAnJU&t=601)]
But first, let's meet the existing GPU profilers where they are.

##### **Geohot** [[00:10:07](https://www.youtube.com/watch?v=22O5E5aAnJU&t=607)]
Yeah.

##### **Nimlgen** [[00:10:07](https://www.youtube.com/watch?v=22O5E5aAnJU&t=607)]
And I'll change sqtt limit se to be zero by default.

##### **Nimlgen** [[00:10:12](https://www.youtube.com/watch?v=22O5E5aAnJU&t=612)]
So that's pretty nice.

##### **Geohot** [[00:10:14](https://www.youtube.com/watch?v=22O5E5aAnJU&t=614)]
I mean, yeah, this is beautiful.

##### **Geohot** [[00:10:16](https://www.youtube.com/watch?v=22O5E5aAnJU&t=616)]
Like it's so beautiful that we can see like, oh, this is a lot of stuff.

##### **Geohot** [[00:10:18](https://www.youtube.com/watch?v=22O5E5aAnJU&t=618)]
Like, I really like the way the inst waves are lit up differently from the awk waves.

##### **Geohot** [[00:10:22](https://www.youtube.com/watch?v=22O5E5aAnJU&t=622)]
Oh, yeah.

##### **Geohot** [[00:10:23](https://www.youtube.com/watch?v=22O5E5aAnJU&t=623)]
Why have we still not added where I can double click on an inst wave?

##### **Nimlgen** [[00:10:26](https://www.youtube.com/watch?v=22O5E5aAnJU&t=626)]
Is this hard?

##### **Nimlgen** [[00:10:27](https://www.youtube.com/watch?v=22O5E5aAnJU&t=627)]
Oh, I don't know.

##### **Geohot** [[00:10:29](https://www.youtube.com/watch?v=22O5E5aAnJU&t=629)]
I just didn't spend time on it.

##### **Geohot** [[00:10:31](https://www.youtube.com/watch?v=22O5E5aAnJU&t=631)]
Okay, cool.

##### **Geohot** [[00:10:31](https://www.youtube.com/watch?v=22O5E5aAnJU&t=631)]
I mean, I've asked for it a whole bunch of times.

##### **Geohot** [[00:10:33](https://www.youtube.com/watch?v=22O5E5aAnJU&t=633)]
And I feel like when I'm asking for something a bunch of times, there's a reason it's like

##### **Geohot** [[00:10:36](https://www.youtube.com/watch?v=22O5E5aAnJU&t=636)]
subtly hard and...

##### **Nimlgen** [[00:10:40](https://www.youtube.com/watch?v=22O5E5aAnJU&t=640)]
No, just work on other things.

##### **Nimlgen** [[00:10:42](https://www.youtube.com/watch?v=22O5E5aAnJU&t=642)]
I'll do that.

##### **Geohot** [[00:10:43](https://www.youtube.com/watch?v=22O5E5aAnJU&t=643)]
Okay, cool.

##### **Geohot** [[00:10:43](https://www.youtube.com/watch?v=22O5E5aAnJU&t=643)]
Yeah.

##### **Geohot** [[00:10:43](https://www.youtube.com/watch?v=22O5E5aAnJU&t=643)]
Yeah.

##### **Geohot** [[00:10:44](https://www.youtube.com/watch?v=22O5E5aAnJU&t=644)]
So double click on an inst wave.

##### **Geohot** [[00:10:46](https://www.youtube.com/watch?v=22O5E5aAnJU&t=646)]
Then I can go to the instructions.

##### **Nimlgen** [[00:10:47](https://www.youtube.com/watch?v=22O5E5aAnJU&t=647)]
And I can go to the instructions.

##### **Nimlgen** [[00:10:48](https://www.youtube.com/watch?v=22O5E5aAnJU&t=648)]
And then the instructions have to be like deduced.

##### **Geohot** [[00:10:51](https://www.youtube.com/watch?v=22O5E5aAnJU&t=651)]
There should be at most one line per instruction.

##### **Geohot** [[00:10:57](https://www.youtube.com/watch?v=22O5E5aAnJU&t=657)]
Not per hit of the instruction, but per like PC of the instruction.

##### **Geohot** [[00:11:04](https://www.youtube.com/watch?v=22O5E5aAnJU&t=664)]
Yeah, makes sense.

##### **Geohot** [[00:11:05](https://www.youtube.com/watch?v=22O5E5aAnJU&t=665)]
Actually, that'd be kind of cool too, to just put the PC, not like the whole PC, but just

##### **Geohot** [[00:11:08](https://www.youtube.com/watch?v=22O5E5aAnJU&t=668)]
like the offset from the top.

##### **Nimlgen** [[00:11:12](https://www.youtube.com/watch?v=22O5E5aAnJU&t=672)]
My new fun weekend project since my tracer is kind of done has been to start on an assembly

##### **Nimlgen** [[00:11:17](https://www.youtube.com/watch?v=22O5E5aAnJU&t=677)]
dialect.

##### **Geohot** [[00:11:18](https://www.youtube.com/watch?v=22O5E5aAnJU&t=678)]
So it's like an assembly DSL.

##### **Geohot** [[00:11:19](https://www.youtube.com/watch?v=22O5E5aAnJU&t=679)]
I have this really nice assembly DSL where you'll be able to pretty much just write the

##### **Geohot** [[00:11:23](https://www.youtube.com/watch?v=22O5E5aAnJU&t=683)]
assembly instructions in Python, but as functions, which will be kind of nice.

##### **Geohot** [[00:11:32](https://www.youtube.com/watch?v=22O5E5aAnJU&t=692)]
But yeah.

##### **Geohot** [[00:11:33](https://www.youtube.com/watch?v=22O5E5aAnJU&t=693)]
No, this is shaping up to be a very good GPU tracer.

##### **Nimlgen** [[00:11:39](https://www.youtube.com/watch?v=22O5E5aAnJU&t=699)]
It's all pretty easy to use now too.

##### **Nimlgen** [[00:11:41](https://www.youtube.com/watch?v=22O5E5aAnJU&t=701)]
I put a lot of work into like...

##### **Geohot** [[00:11:42](https://www.youtube.com/watch?v=22O5E5aAnJU&t=702)]
I put the power thing automatically in viz equals two.

##### **Geohot** [[00:11:46](https://www.youtube.com/watch?v=22O5E5aAnJU&t=706)]
I mean, viz equals two should basically just...

##### **Geohot** [[00:11:48](https://www.youtube.com/watch?v=22O5E5aAnJU&t=708)]
I mean, viz equals two should basically just work everywhere viz does, and we just accept

##### **Geohot** [[00:11:50](https://www.youtube.com/watch?v=22O5E5aAnJU&t=710)]
that there's a little bit more overhead.

##### **Geohot** [[00:11:55](https://www.youtube.com/watch?v=22O5E5aAnJU&t=715)]
Yeah, I don't think we need the sqtt limit thing.

##### **Nimlgen** [[00:11:59](https://www.youtube.com/watch?v=22O5E5aAnJU&t=719)]
I think that's only if you really want to trace like a tiny kernel, but we should be

##### **Nimlgen** [[00:12:02](https://www.youtube.com/watch?v=22O5E5aAnJU&t=722)]
just tracing the whole kernel and you know, you get whatever waves you get.

##### **Geohot** [[00:12:06](https://www.youtube.com/watch?v=22O5E5aAnJU&t=726)]
It's nice when you can like see the occupancy.

##### **Geohot** [[00:12:11](https://www.youtube.com/watch?v=22O5E5aAnJU&t=731)]
Whoa.

##### **Geohot** [[00:12:13](https://www.youtube.com/watch?v=22O5E5aAnJU&t=733)]
Oh yeah, this has to be a lot faster.

##### **Geohot** [[00:12:17](https://www.youtube.com/watch?v=22O5E5aAnJU&t=737)]
Oh, I'm sorry.

##### **Geohot** [[00:12:18](https://www.youtube.com/watch?v=22O5E5aAnJU&t=738)]
Also, can you...

##### **Nimlgen** [[00:12:20](https://www.youtube.com/watch?v=22O5E5aAnJU&t=740)]
By default on the zoom, can you not start it at zero?

##### **Nimlgen** [[00:12:28](https://www.youtube.com/watch?v=22O5E5aAnJU&t=748)]
At the clock that it starts doing instruction?

##### **Geohot** [[00:12:32](https://www.youtube.com/watch?v=22O5E5aAnJU&t=752)]
Yeah, just at the first clock that we have anything for.

##### **Geohot** [[00:12:35](https://www.youtube.com/watch?v=22O5E5aAnJU&t=755)]
We can do that on the main profiler too, right?

##### **Geohot** [[00:12:37](https://www.youtube.com/watch?v=22O5E5aAnJU&t=757)]
If the thing just sits idle for 10 seconds and then does something, and you should be

##### **Geohot** [[00:12:42](https://www.youtube.com/watch?v=22O5E5aAnJU&t=762)]
able to zoom out to get to zero.

##### **Geohot** [[00:12:44](https://www.youtube.com/watch?v=22O5E5aAnJU&t=764)]
Like if I zoom back on the wheel, I'm just saying the default zoom should be at zero.

##### **Nimlgen** [[00:12:48](https://www.youtube.com/watch?v=22O5E5aAnJU&t=768)]
The same way you have the max of the default zoom be the end of the last kernel, the min

##### **Nimlgen** [[00:12:54](https://www.youtube.com/watch?v=22O5E5aAnJU&t=774)]
of the default zoom should be the start of the first kernel.

##### **Geohot** [[00:12:58](https://www.youtube.com/watch?v=22O5E5aAnJU&t=778)]
Yeah, because you can scroll back.

##### **Geohot** [[00:13:01](https://www.youtube.com/watch?v=22O5E5aAnJU&t=781)]
Does that make sense?

##### **Geohot** [[00:13:02](https://www.youtube.com/watch?v=22O5E5aAnJU&t=782)]
Great.

##### **Geohot** [[00:13:03](https://www.youtube.com/watch?v=22O5E5aAnJU&t=783)]
Yeah.

##### **Geohot** [[00:13:03](https://www.youtube.com/watch?v=22O5E5aAnJU&t=783)]
Double click, speed, instruction deduping.

##### **Nimlgen** [[00:13:09](https://www.youtube.com/watch?v=22O5E5aAnJU&t=789)]
Yeah, this is turning into a great GPU profiler.

##### **Nimlgen** [[00:13:17](https://www.youtube.com/watch?v=22O5E5aAnJU&t=797)]
I mean, you can go back and see what's going on.

##### **Geohot** [[00:13:18](https://www.youtube.com/watch?v=22O5E5aAnJU&t=798)]
So did you try sqtt trace equals one at all?

##### **Geohot** [[00:13:23](https://www.youtube.com/watch?v=22O5E5aAnJU&t=803)]
Your decoder?

##### **Geohot** [[00:13:25](https://www.youtube.com/watch?v=22O5E5aAnJU&t=805)]
Yeah.

##### **Geohot** [[00:13:27](https://www.youtube.com/watch?v=22O5E5aAnJU&t=807)]
I got a cert that some fields should be zero, but it wasn't zero.

##### **Geohot** [[00:13:30](https://www.youtube.com/watch?v=22O5E5aAnJU&t=810)]
Oh, I think I fixed that.

##### **Nimlgen** [[00:13:31](https://www.youtube.com/watch?v=22O5E5aAnJU&t=811)]
Try now.

##### **Nimlgen** [[00:13:33](https://www.youtube.com/watch?v=22O5E5aAnJU&t=813)]
Okay, I'll try again.

##### **Geohot** [[00:13:34](https://www.youtube.com/watch?v=22O5E5aAnJU&t=814)]
See if it works for you.

##### **Geohot** [[00:13:35](https://www.youtube.com/watch?v=22O5E5aAnJU&t=815)]
I think I tried Saturday night.

##### **Geohot** [[00:13:38](https://www.youtube.com/watch?v=22O5E5aAnJU&t=818)]
So maybe it's fixed.

##### **Geohot** [[00:13:39](https://www.youtube.com/watch?v=22O5E5aAnJU&t=819)]
Yeah, I fixed a bunch of things.

##### **Geohot** [[00:13:41](https://www.youtube.com/watch?v=22O5E5aAnJU&t=821)]
I fixed a bunch of things Saturday, but why didn't that work?

##### **Nimlgen** [[00:13:48](https://www.youtube.com/watch?v=22O5E5aAnJU&t=828)]
Is it sqtt trace?

##### **Nimlgen** [[00:13:49](https://www.youtube.com/watch?v=22O5E5aAnJU&t=829)]
What did I name it?

##### **Geohot** [[00:13:51](https://www.youtube.com/watch?v=22O5E5aAnJU&t=831)]
Oh, sqtt parse.

##### **Geohot** [[00:13:53](https://www.youtube.com/watch?v=22O5E5aAnJU&t=833)]
Oh, God.

##### **Geohot** [[00:13:55](https://www.youtube.com/watch?v=22O5E5aAnJU&t=835)]
Too many flags.

##### **Geohot** [[00:13:56](https://www.youtube.com/watch?v=22O5E5aAnJU&t=836)]
Yeah, I added two new counters to the thing where we count the number of flags and the

##### **Geohot** [[00:14:01](https://www.youtube.com/watch?v=22O5E5aAnJU&t=841)]
number of ops, and I want them both to go down.

##### **Nimlgen** [[00:14:04](https://www.youtube.com/watch?v=22O5E5aAnJU&t=844)]
Yeah, yeah, yeah, sqtt, like this line works.

##### **Nimlgen** [[00:14:08](https://www.youtube.com/watch?v=22O5E5aAnJU&t=848)]
I added like pretty colors to them and stuff.

##### **Geohot** [[00:14:12](https://www.youtube.com/watch?v=22O5E5aAnJU&t=852)]
So it shows you when the instruction is going to be ready.

##### **Geohot** [[00:14:18](https://www.youtube.com/watch?v=22O5E5aAnJU&t=858)]
So it shows you when the instruction gets enqueued and then when the instruction executes

##### **Geohot** [[00:14:23](https://www.youtube.com/watch?v=22O5E5aAnJU&t=863)]
for ALU and memory instructions.

##### **Geohot** [[00:14:25](https://www.youtube.com/watch?v=22O5E5aAnJU&t=865)]
And then there's another class of instructions called immediate, which is just

##### **Geohot** [[00:14:33](https://www.youtube.com/watch?v=22O5E5aAnJU&t=873)]
And then, yeah, there's a bunch of it shows you all the way starts and way ends and stuff.

##### **Nimlgen** [[00:14:36](https://www.youtube.com/watch?v=22O5E5aAnJU&t=876)]
So it's pretty cool.

##### **Nimlgen** [[00:14:40](https://www.youtube.com/watch?v=22O5E5aAnJU&t=880)]
Great.

##### **Geohot** [[00:14:46](https://www.youtube.com/watch?v=22O5E5aAnJU&t=886)]
Cool.

##### **Geohot** [[00:14:46](https://www.youtube.com/watch?v=22O5E5aAnJU&t=886)]
Yeah, I think we got stuff for that.

##### **Geohot** [[00:14:51](https://www.youtube.com/watch?v=22O5E5aAnJU&t=891)]
But so yeah, is everything clear?

##### **Geohot** [[00:14:53](https://www.youtube.com/watch?v=22O5E5aAnJU&t=893)]
Is there anything I can clear up about like the instruction do dooping or the speed of

##### **Geohot** [[00:14:58](https://www.youtube.com/watch?v=22O5E5aAnJU&t=898)]
stuff?

##### **Nimlgen** [[00:15:02](https://www.youtube.com/watch?v=22O5E5aAnJU&t=902)]
I think that's done is clear.

##### **Nimlgen** [[00:15:05](https://www.youtube.com/watch?v=22O5E5aAnJU&t=905)]
Great.

##### **Geohot** [[00:15:08](https://www.youtube.com/watch?v=22O5E5aAnJU&t=908)]
NVIDIA HVAC decode.

##### **Geohot** [[00:15:13](https://www.youtube.com/watch?v=22O5E5aAnJU&t=913)]
Yeah.

##### **Geohot** [[00:15:16](https://www.youtube.com/watch?v=22O5E5aAnJU&t=916)]
So it works.

##### **Geohot** [[00:15:18](https://www.youtube.com/watch?v=22O5E5aAnJU&t=918)]
So.

##### **Geohot** [[00:15:22](https://www.youtube.com/watch?v=22O5E5aAnJU&t=922)]
Right.

##### **Nimlgen** [[00:15:23](https://www.youtube.com/watch?v=22O5E5aAnJU&t=923)]
I just implemented a custom parser of the file format because we need some fields which we cannot get from.

##### **Nimlgen** [[00:15:35](https://www.youtube.com/watch?v=22O5E5aAnJU&t=935)]
So like hardware needs them.

##### **Geohot** [[00:15:41](https://www.youtube.com/watch?v=22O5E5aAnJU&t=941)]
Which is interesting.

##### **Geohot** [[00:15:43](https://www.youtube.com/watch?v=22O5E5aAnJU&t=943)]
Yeah.

##### **Geohot** [[00:15:44](https://www.youtube.com/watch?v=22O5E5aAnJU&t=944)]
So when you use the NVIDIA API, how does it get that stuff?

##### **Geohot** [[00:15:51](https://www.youtube.com/watch?v=22O5E5aAnJU&t=951)]
I mean, you just parse you just fit the whole file into the qubit.

##### **Geohot** [[00:15:57](https://www.youtube.com/watch?v=22O5E5aAnJU&t=957)]
Really?

##### **Nimlgen** [[00:15:58](https://www.youtube.com/watch?v=22O5E5aAnJU&t=958)]
Just yeah.

##### **Nimlgen** [[00:16:00](https://www.youtube.com/watch?v=22O5E5aAnJU&t=960)]
I don't remember requiring that, but I'm probably wrong.

##### **Geohot** [[00:16:04](https://www.youtube.com/watch?v=22O5E5aAnJU&t=964)]
I mean, basically they need this because like all these headers, they just have different sizes dependent on the features.

##### **Geohot** [[00:16:13](https://www.youtube.com/watch?v=22O5E5aAnJU&t=973)]
And actually even numbers are like encoded to the way that they depended on the value they had.

##### **Geohot** [[00:16:20](https://www.youtube.com/watch?v=22O5E5aAnJU&t=980)]
They can have different sizes.

##### **Geohot** [[00:16:22](https://www.youtube.com/watch?v=22O5E5aAnJU&t=982)]
So not it.

##### **Geohot** [[00:16:24](https://www.youtube.com/watch?v=22O5E5aAnJU&t=984)]
Yeah.

##### **Nimlgen** [[00:16:25](https://www.youtube.com/watch?v=22O5E5aAnJU&t=985)]
And actually hardware needs to know how many beats it need to skip for such things.

##### **Nimlgen** [[00:16:33](https://www.youtube.com/watch?v=22O5E5aAnJU&t=993)]
Cool.

##### **Geohot** [[00:16:34](https://www.youtube.com/watch?v=22O5E5aAnJU&t=994)]
Yeah.

##### **Geohot** [[00:16:35](https://www.youtube.com/watch?v=22O5E5aAnJU&t=995)]
Yeah.

##### **Geohot** [[00:16:35](https://www.youtube.com/watch?v=22O5E5aAnJU&t=995)]
No, I mean, the way that we use this at Comma is we have this stage called VidIndex, which extracts all the GOPs from all the HVACs.

##### **Geohot** [[00:16:42](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1002)]
Yeah.

##### **Geohot** [[00:16:43](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1003)]
Like in Comma's files.

##### **Nimlgen** [[00:16:44](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1004)]
And then in order to decode for training, we just shove the GOPs into the decoder.

##### **Nimlgen** [[00:16:50](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1010)]
But I guess that works because they all are they all have the same like format.

##### **Geohot** [[00:16:57](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1017)]
Yeah.

##### **Geohot** [[00:16:59](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1019)]
There's a crazy amount of flags here.

##### **Geohot** [[00:17:03](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1023)]
Yeah.

##### **Geohot** [[00:17:04](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1024)]
It's so yeah, actually, I'm just it works.

##### **Geohot** [[00:17:09](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1029)]
I know I can just try and.

##### **Nimlgen** [[00:17:12](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1032)]
Oh.

##### **Nimlgen** [[00:17:13](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1033)]
I'm just trying to figure out what the

##### **Geohot** [[00:17:14](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1034)]
Are these flags per frame or these flags per video stream?

##### **Geohot** [[00:17:23](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1043)]
Like some of them like PPC and SPC just per video stream.

##### **Geohot** [[00:17:31](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1051)]
And there are also some amount of flags per frame.

##### **Geohot** [[00:17:37](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1057)]
I see.

##### **Geohot** [[00:17:39](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1059)]
Yeah.

##### **Nimlgen** [[00:17:40](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1060)]
Cool.

##### **Nimlgen** [[00:17:41](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1061)]
Okay.

##### **Geohot** [[00:17:41](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1061)]
Yeah.

##### **Geohot** [[00:17:42](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1062)]
And then let's talk about, yeah, the front end thing.

##### **Geohot** [[00:17:43](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1063)]
So I see you added an op called AncDec.

##### **Geohot** [[00:17:48](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1068)]
Yeah, that's probably the right way to do it.

##### **Geohot** [[00:17:53](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1073)]
I mean, how does that like become a kernel and stuff?

##### **Nimlgen** [[00:18:02](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1082)]
I mean, what is the.

##### **Nimlgen** [[00:18:04](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1084)]
I mean, it's a.

##### **Geohot** [[00:18:05](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1085)]
It's a.

##### **Geohot** [[00:18:08](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1088)]
It's a.

##### **Geohot** [[00:18:08](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1088)]
It's a.

##### **Geohot** [[00:18:08](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1088)]
It's a.

##### **Geohot** [[00:18:08](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1088)]
It's a.

##### **Nimlgen** [[00:18:09](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1089)]
It's a.

##### **Nimlgen** [[00:18:10](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1090)]
I mean, actually, so what we need to decode each frame is like basically we need to know

##### **Geohot** [[00:18:17](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1097)]
the history in the current state.

##### **Geohot** [[00:18:18](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1098)]
So and actually, that's what I just tried to pass to the run times.

##### **Geohot** [[00:18:26](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1106)]
So.

##### **Geohot** [[00:18:30](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1110)]
Yeah.

##### **Geohot** [[00:18:30](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1110)]
So AncDec is going to have some kind of a little bit of a little bit of a pre-trial

##### **Nimlgen** [[00:18:35](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1115)]
several inputs, which is the history and the context as an argument.

##### **Nimlgen** [[00:18:45](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1125)]
Got it. Is it going to look like copy, the way that we use the copy engine?

##### **Geohot** [[00:18:52](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1132)]
Yeah.

##### **Geohot** [[00:18:52](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1132)]
I'm just thinking of what the abstraction of this is going to look like.

##### **Geohot** [[00:18:56](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1136)]
On the low level, do you submit it to the

##### **Geohot** [[00:18:59](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1139)]
status or the same queue as the copies or a new queue entirely?

##### **Geohot** [[00:19:02](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1142)]
No, actually it's a completely different queue. And NVIDIA, their CUDA library doesn't...

##### **Nimlgen** [[00:19:11](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1151)]
So actually, they don't set up the UVM to this engine. And I couldn't make it work with the UVM.

##### **Nimlgen** [[00:19:23](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1163)]
The UVM. Do we use the UVM?

##### **Geohot** [[00:19:27](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1167)]
Yeah, I mean, it's for P2P.

##### **Geohot** [[00:19:31](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1171)]
So basically,

##### **Geohot** [[00:19:32](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1172)]
The P2P.

##### **Geohot** [[00:19:32](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1172)]
Wait, wait, wait. The P2P thing doesn't use UVM. The P2P thing just shoves the page

##### **Geohot** [[00:19:39](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1179)]
table, just shoves the other address in the page table. I don't really know what UVM is.

##### **Nimlgen** [[00:19:46](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1186)]
I mean, that's kind of their implementation of like unified virtual memory and actually it's just

##### **Nimlgen** [[00:19:54](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1194)]
manages all tables across all GPUs.

##### **Geohot** [[00:19:57](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1197)]
Yeah, my understanding of UVM always was that it was something that lives in the kernel.

##### **Geohot** [[00:20:02](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1202)]
That like intercepts rights to the GPU memory and then like,

##### **Geohot** [[00:20:06](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1206)]
you know, moves them and stuff if you have like small bar or something.

##### **Geohot** [[00:20:12](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1212)]
Like UVM lets you effectively map your whole GPU even if you have small bar.

##### **Geohot** [[00:20:16](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1216)]
But I'm not sure it's UVM if you're using it right on the GPU, right? Like the way that we do P2P,

##### **Nimlgen** [[00:20:21](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1221)]
like I wrote that P2P driver, we just shove the other address in the page table.

##### **Nimlgen** [[00:20:26](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1226)]
So what specifically are you saying?

##### **Geohot** [[00:20:28](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1228)]
But actually, that was part of the UVM. I mean,

##### **Geohot** [[00:20:31](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1231)]
That's part of UVM, correct.

##### **Geohot** [[00:20:32](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1232)]
of the UVM more than anything.

##### **Geohot** [[00:20:32](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1232)]
Yeah. I mean, basically, it's better to say like that, that you like, I couldn't set the,

##### **Geohot** [[00:20:39](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1239)]
I couldn't make this engine work with the, like virtual address space.

##### **Nimlgen** [[00:20:46](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1246)]
Got it.

##### **Nimlgen** [[00:20:47](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1247)]
So when I just, yeah. So when I just

##### **Geohot** [[00:20:53](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1253)]
You're basically telling me the engine works at a lower level than the GMMU and you have to put the

##### **Geohot** [[00:20:57](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1257)]
physical address of the GPU memory in there.

##### **Geohot** [[00:21:01](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1261)]
No, I mean,

##### **Geohot** [[00:21:03](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1263)]
I think it's just a physical address space.

##### **Geohot** [[00:21:04](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1264)]
Actually, I think it will be clear for me, then I just implement these for like our driver

##### **Nimlgen** [[00:21:08](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1268)]
and I'll just see what it's actually accessing underneath. But I mean, just frozen error now,

##### **Nimlgen** [[00:21:17](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1277)]
like the GSP throws an error if you just try to allocate this engine with the virtual address space

##### **Geohot** [[00:21:25](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1285)]
set.

##### **Geohot** [[00:21:27](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1287)]
Got it. But so you have to give it a physical address space.

##### **Geohot** [[00:21:31](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1291)]
Yeah.

##### **Geohot** [[00:21:32](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1292)]
Yeah.

##### **Geohot** [[00:21:32](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1292)]
Yeah.

##### **Nimlgen** [[00:21:32](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1292)]
No, you kind of do, you kind of allocate another virtual memory and you just,

##### **Nimlgen** [[00:21:39](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1299)]
I see.

##### **Geohot** [[00:21:40](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1300)]
And you just map it there, but this is virtual, like memory is not managed by UVM. So actually,

##### **Geohot** [[00:21:46](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1306)]
Oh, I see. I see. I'm reading the code here. You're doing this, there's UVM create

##### **Geohot** [[00:21:50](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1310)]
external range. So it's like an IOMMU kind of.

##### **Geohot** [[00:21:54](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1314)]
Yeah. So,

##### **Geohot** [[00:21:58](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1318)]
and because of that, the only limitation is that this engine,

##### **Nimlgen** [[00:22:02](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1322)]
in the current implementation, cannot access like P2P memory of other GPUs.

##### **Nimlgen** [[00:22:08](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1328)]
That seems okay.

##### **Geohot** [[00:22:11](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1331)]
Yeah. But yeah, maybe that's fixable. I need to implement this for our driver and see.

##### **Geohot** [[00:22:17](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1337)]
Yeah. But even if it's not, that doesn't seem like a big deal. We can just add a rewrite rule that,

##### **Geohot** [[00:22:24](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1344)]
like it has to be on your device. I think it's totally fine.

##### **Geohot** [[00:22:30](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1350)]
But I see. So it's in a totally different five-fold.

##### **Geohot** [[00:22:32](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1352)]
It's in this NV video queue thing, which is like, yeah. Okay. Perfect.

##### **Nimlgen** [[00:22:37](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1357)]
NV compute queue, NV copy queue, NV video queue. That's great.

##### **Nimlgen** [[00:22:41](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1361)]
We probably, unless it's really fast, we probably also don't want to build a video queue unless you

##### **Geohot** [[00:22:47](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1367)]
use it, but eh, I'm worried about that later. Like, can we move these setup GP FIFOs to like on the

##### **Geohot** [[00:22:56](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1376)]
fly?

##### **Geohot** [[00:23:01](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1381)]
What do you mean?

##### **Geohot** [[00:23:02](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1382)]
I mean, like...

##### **Geohot** [[00:23:04](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1384)]
Right now, if I open an NVIDIA GPU, I'm going to create a video queue every time, right?

##### **Nimlgen** [[00:23:10](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1390)]
Oh yeah. I mean, that's pretty fast, but we can of course, like laser locations,

##### **Nimlgen** [[00:23:15](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1395)]
but it's pretty fast.

##### **Geohot** [[00:23:17](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1397)]
Got it. Yeah. No, I'm just saying like, we kind of need to like abstract these things

##### **Geohot** [[00:23:23](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1403)]
like into something, right? Like, like copy is this thing that like uses the copy engine.

##### **Geohot** [[00:23:29](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1409)]
I think we almost want like, like a UOP for that.

##### **Geohot** [[00:23:32](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1412)]
Like an engine UOP that says this is a, this doesn't use the normal, I don't know. I don't

##### **Geohot** [[00:23:38](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1418)]
know exactly what the abstraction is going to be like, but not that worried about that. Cool.

##### **Nimlgen** [[00:23:41](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1421)]
Uh, so, okay.

##### **Nimlgen** [[00:23:44](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1424)]
Yeah. I mean, actually the only thing is like, uh, to finish that is to somehow make these,

##### **Geohot** [[00:23:54](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1434)]
um, like to make this state hashable because currently it's not hashable and I'm just really

##### **Geohot** [[00:24:01](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1441)]
afraid that it will...

##### **Geohot** [[00:24:02](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1442)]
Yeah.

##### **Geohot** [[00:24:02](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1442)]
Take a lot of lines if I just create the frozen, uh, like the frozen data, how it's called.

##### **Geohot** [[00:24:12](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1452)]
Make it hash. So you mean like...

##### **Nimlgen** [[00:24:14](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1454)]
Data class. Yeah. Yeah. Because I need to pass...

##### **Nimlgen** [[00:24:17](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1457)]
CTF data. Yes.

##### **Geohot** [[00:24:19](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1459)]
Yeah. So, you know, I'll think about this, how to make it. Yeah.

##### **Geohot** [[00:24:29](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1469)]
Got it.

##### **Geohot** [[00:24:29](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1469)]
It's actually, it's, yeah, it's a lot of data you need to fit into.

##### **Geohot** [[00:24:32](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1472)]
GPU to decodes each frame. So...

##### **Geohot** [[00:24:35](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1475)]
Yeah. Seriously. I'm staring at it right now. Um,

##### **Nimlgen** [[00:24:39](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1479)]
I don't know. So everybody else can, can see what's being discussed.

##### **Nimlgen** [[00:24:48](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1488)]
Um, uh, but cool. All right. It seems like good progress on

##### **Geohot** [[00:24:56](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1496)]
week. Um, when, when HVAC decode is in, uh, have you looked at all into the

##### **Geohot** [[00:25:02](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1502)]
SIP free Mac OS stuff?

##### **Geohot** [[00:25:07](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1507)]
No. Um, yeah, I can look into that, but...

##### **Geohot** [[00:25:13](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1513)]
I'm look, I'm mad at Apple for doing this too, but like you see how many,

##### **Geohot** [[00:25:19](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1519)]
these things get so many likes on Twitter. Like so many people are excited about eGPU

##### **Nimlgen** [[00:25:24](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1524)]
and I think that 80% of people won't turn off SIP to try it. So yeah, it's worth putting some time.

##### **Nimlgen** [[00:25:32](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1532)]
And if it's something that's going to be very easy to maintain, um, we also should just improve like

##### **Geohot** [[00:25:37](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1537)]
the packaging quality of that, right? Because like right now, in order to install that driver,

##### **Geohot** [[00:25:41](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1541)]
you have to know about the special thing in extra, you have to know that you have to disable SIP.

##### **Geohot** [[00:25:46](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1546)]
You have to go in there, build this project. You need Xcode on your Mac.

##### **Geohot** [[00:25:51](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1551)]
Um, and yeah, and then you install this thing. Uh, you get very little feedback if it works.

##### **Geohot** [[00:25:56](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1556)]
Otherwise it just throws an error saying IO open failed. Um, so many people, every single person

##### **Nimlgen** [[00:26:01](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1561)]
who's tried to use the SIP free Mac OS, they're like, oh, I don't know. I don't know. I don't know.

##### **Nimlgen** [[00:26:02](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1562)]
I don't know how to use this. Sets AMD iFace equal to USB and not PCI.

##### **Geohot** [[00:26:08](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1568)]
Uh, which is just like, uh, you know, a little old old foot gunner. I thought it's plugged into the

##### **Geohot** [[00:26:13](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1573)]
USB port, USB for PCI, blah, blah, blah. But yeah, no, I think we can, um, I think it's worth putting

##### **Geohot** [[00:26:20](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1580)]
some effort into like improving the overall packaging of this. And then, I mean, hopefully

##### **Geohot** [[00:26:25](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1585)]
without SIP, what we can do is we can create the context. Like the only thing we should have to do,

##### **Geohot** [[00:26:31](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1591)]
hopefully, is IOS.

##### **Nimlgen** [[00:26:32](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1592)]
I think we can do a little bit of audio service open in the sign process.

##### **Nimlgen** [[00:26:37](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1597)]
Yeah.

##### **Geohot** [[00:26:38](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1598)]
Yeah. And then do like mock ports send. Take that Apple.

##### **Geohot** [[00:26:46](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1606)]
Um, but cool. Yeah, I think, I think it's worth putting a, putting a bit of time in time.

##### **Geohot** [[00:26:54](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1614)]
Uh, oh, and then also the bug that, uh, Chen Yu hit on the 350.

##### **Geohot** [[00:27:04](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1624)]
Um, no, it is. Yeah.

##### **Geohot** [[00:27:06](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1626)]
No, it is. Yeah. Cool. Yeah. No, he said it worked with hip equals one. So

##### **Nimlgen** [[00:27:16](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1636)]
cool. Anything else?

##### **Nimlgen** [[00:27:19](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1639)]
Um, no.

##### **Geohot** [[00:27:21](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1641)]
Yeah. Good work on the decoder.

##### **Geohot** [[00:27:24](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1644)]
Um, are we really gonna put in, uh, 12 megabytes of big bug bunny in the PR?

##### **Geohot** [[00:27:37](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1657)]
Um, we want to play at home.

##### **Geohot** [[00:27:41](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1661)]
Gotta play ass 와ff.

##### **Geohot** [[00:27:41](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1661)]
We should definitely have .

##### **Nimlgen** [[00:27:42](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1662)]
This is good. We should have tests in the, uh, in the benchmark.

##### **Nimlgen** [[00:27:52](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1672)]
And, uh, yeah, it commas HVACs should be pretty much like there's tons of places that have

##### **Geohot** [[00:27:56](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1676)]
HVACs we should just test it on, but we should also probably test on like 10 different HVACs.

##### **Geohot** [[00:28:01](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1681)]
Etc.

##### **Geohot** [[00:28:03](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1683)]
to make sure we got all these things right.

##### **Geohot** [[00:28:07](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1687)]
Cool.

##### **Geohot** [[00:28:09](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1689)]
All right, Qualcomm Mesa backend.

##### **Nimlgen** [[00:28:13](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1693)]
Yeah, that's pretty much ready to click merge.

##### **Nimlgen** [[00:28:16](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1696)]
I mean, unless there's something that comes up in this meeting,

##### **Geohot** [[00:28:17](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1697)]
I was going to click merge on it when this is done.

##### **Geohot** [[00:28:21](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1701)]
But yeah, it's great that we have a fully open source stack

##### **Geohot** [[00:28:26](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1706)]
for that whole backend.

##### **Geohot** [[00:28:29](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1709)]
I'm trying to think what's sort of major

##### **Geohot** [[00:28:31](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1711)]
that also has changed in this thing.

##### **Nimlgen** [[00:28:34](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1714)]
Where's the PR?

##### **Nimlgen** [[00:28:36](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1716)]
Oh, yeah, let me see.

##### **Geohot** [[00:28:48](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1728)]
All right.

##### **Geohot** [[00:28:50](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1730)]
Can you change your default sort to sort by updated?

##### **Geohot** [[00:28:53](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1733)]
I don't have to have sorts by authored date by default.

##### **Geohot** [[00:28:57](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1737)]
Oh, I see.

##### **Geohot** [[00:28:58](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1738)]
Okay.

##### **Nimlgen** [[00:28:58](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1738)]
Sorry, my bad.

##### **Nimlgen** [[00:29:00](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1740)]
All right, I'm looking at it.

##### **Geohot** [[00:29:01](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1741)]
Yeah.

##### **Geohot** [[00:29:04](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1744)]
Yeah, so one of the things that this adds,

##### **Geohot** [[00:29:07](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1747)]
it bumps the tiny Mesa version and also the Mesa version,

##### **Geohot** [[00:29:11](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1751)]
but I mean, that should be fine.

##### **Geohot** [[00:29:13](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1753)]
All the CI passed, and it's just like,

##### **Nimlgen** [[00:29:17](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1757)]
it's not even a minor version update.

##### **Nimlgen** [[00:29:19](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1759)]
It's a patch version update, so I think it's fine.

##### **Geohot** [[00:29:24](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1764)]
Yeah, the big thing that this changes

##### **Geohot** [[00:29:26](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1766)]
that might mess some people up,

##### **Geohot** [[00:29:27](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1767)]
so it's worth saying here,

##### **Geohot** [[00:29:29](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1769)]
is that...

##### **Geohot** [[00:29:31](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1771)]
The disassembler for the Qualcomm CL backend

##### **Nimlgen** [[00:29:36](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1776)]
now uses Tiny Mesa to disassemble.

##### **Nimlgen** [[00:29:40](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1780)]
So it won't cause any problems unless you run with debug equals seven,

##### **Geohot** [[00:29:43](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1783)]
or I guess it will if you run in Viz and you click on disassemble.

##### **Geohot** [[00:29:48](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1788)]
But yeah, if you're running into errors trying to disassemble stuff

##### **Geohot** [[00:29:51](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1791)]
on the Qualcomm CL backend, it's because you need Tiny Mesa.

##### **Geohot** [[00:29:54](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1794)]
Yeah, and hopefully, does it have an error that tells you that?

##### **Geohot** [[00:29:59](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1799)]
It should.

##### **Nimlgen** [[00:29:59](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1799)]
I haven't tested it.

##### **Nimlgen** [[00:30:00](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1800)]
I can test it.

##### **Geohot** [[00:30:02](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1802)]
But yeah, I mean, I think in general,

##### **Geohot** [[00:30:06](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1806)]
we need to fix the error handling for all of the library dependencies,

##### **Geohot** [[00:30:11](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1811)]
and hopefully we can just unify all that stuff,

##### **Geohot** [[00:30:13](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1813)]
because otherwise we're just going to have like 10 copies of that

##### **Geohot** [[00:30:16](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1816)]
for every library that we import.

##### **Nimlgen** [[00:30:20](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1820)]
Yeah.

##### **Nimlgen** [[00:30:22](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1822)]
What else was one other thing I was going to say?

##### **Geohot** [[00:30:24](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1824)]
Oh, yeah.

##### **Geohot** [[00:30:25](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1825)]
Do you know about Update Benchmark, by the way?

##### **Geohot** [[00:30:28](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1828)]
Oh, yeah, yeah, I do.

##### **Geohot** [[00:30:31](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1831)]
But there, okay, I didn't, this PR doesn't have any benchmarks set up in it.

##### **Geohot** [[00:30:35](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1835)]
I was going to do that maybe in a separate PR, but I can do that in this PR.

##### **Nimlgen** [[00:30:38](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1838)]
Oh, I'm not talking about adding benchmarks in this PR.

##### **Nimlgen** [[00:30:41](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1841)]
I'm just talking about making sure that the other Qualcomm is not broken

##### **Geohot** [[00:30:45](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1845)]
so that you push it to Update Benchmark before you merge the PR.

##### **Geohot** [[00:30:48](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1848)]
Oh, yeah, that's a good for sure.

##### **Geohot** [[00:30:50](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1850)]
I will do that.

##### **Geohot** [[00:30:52](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1852)]
I see here that it's setting ISA mode to ISA mode GL instead of ISA mode CL.

##### **Geohot** [[00:30:59](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1859)]
That is correct.

##### **Nimlgen** [[00:31:01](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1861)]
That's a side effect of the fact that Mesa is a GL compiler and not a CL compiler.

##### **Nimlgen** [[00:31:06](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1866)]
I don't, I mean, yeah.

##### **Geohot** [[00:31:09](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1869)]
Oh, do we also have a final verdict on the speed?

##### **Geohot** [[00:31:13](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1873)]
Yeah, I mean, I sent that screenshot in Qualcomm hardware.

##### **Geohot** [[00:31:18](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1878)]
So you can compare that.

##### **Geohot** [[00:31:20](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1880)]
That's like actually a valid comparison now because it's a half

##### **Geohot** [[00:31:23](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1883)]
instead of a float three shoot like it was before.

##### **Nimlgen** [[00:31:26](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1886)]
But yeah, that's the image stuff running.

##### **Nimlgen** [[00:31:28](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1888)]
And then the one you sent is the...

##### **Geohot** [[00:31:31](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1891)]
In CI running with the CL backend.

##### **Geohot** [[00:31:34](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1894)]
So it's faster on some stuff.

##### **Geohot** [[00:31:35](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1895)]
It's not faster on everything.

##### **Geohot** [[00:31:36](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1896)]
Yeah, I mean, it's a little confusing that screenshot because like the this first kernel is at a very different time.

##### **Geohot** [[00:31:43](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1903)]
Like the kernels that are before the better before the the JIT cache.

##### **Nimlgen** [[00:31:48](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1908)]
I mean, I'm curious what it like says total for the runtime of the vision model is the total runtime.

##### **Nimlgen** [[00:31:55](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1915)]
Yeah, I have to SSH into that tiny C3 right now, so I don't have that right now.

##### **Geohot** [[00:32:01](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1921)]
But I can.

##### **Geohot** [[00:32:01](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1921)]
I pulled up.

##### **Geohot** [[00:32:02](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1922)]
I'll send that in Qualcomm hardware hardware.

##### **Geohot** [[00:32:05](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1925)]
But if I remember correctly, it was like.

##### **Geohot** [[00:32:09](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1929)]
Right that the right now the full model runs in like 16 milliseconds or something like that.

##### **Nimlgen** [[00:32:13](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1933)]
Is that is that right?

##### **Nimlgen** [[00:32:14](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1934)]
That's not right.

##### **Geohot** [[00:32:15](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1935)]
I think it's 16 on.

##### **Geohot** [[00:32:16](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1936)]
Yeah, but I'm just curious which one's faster.

##### **Geohot** [[00:32:18](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1938)]
I mean, the thing the real thing to do here.

##### **Geohot** [[00:32:20](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1940)]
The Qualcomm, the existing one was definitely faster, but it was faster by like two milliseconds or something like that.

##### **Geohot** [[00:32:25](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1945)]
Got it.

##### **Nimlgen** [[00:32:26](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1946)]
Yeah.

##### **Nimlgen** [[00:32:27](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1947)]
So the right thing to do here is to get a get it running in.

##### **Geohot** [[00:32:31](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1951)]
In benchmark, but you're welcome to merge the PR beforehand.

##### **Geohot** [[00:32:34](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1954)]
Yeah, the thing that I'm worried about running it in benchmark is that stupid race condition in the onyx loader or whatever it is.

##### **Geohot** [[00:32:42](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1962)]
I don't know if it's race condition or memory corruption or what.

##### **Geohot** [[00:32:44](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1964)]
So I was worried that was going to be super flaky.

##### **Geohot** [[00:32:46](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1966)]
So I got to figure out what that bug is before I can add the benchmark.

##### **Nimlgen** [[00:32:51](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1971)]
It's crazy.

##### **Nimlgen** [[00:32:52](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1972)]
It's crazy that how can that be affected by the back end at all?

##### **Geohot** [[00:32:56](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1976)]
Or do you think it's always there and it just doesn't hit as much?

##### **Geohot** [[00:32:58](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1978)]
I mean, I have no idea, but I like it.

##### **Geohot** [[00:33:00](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1980)]
Yeah.

##### **Geohot** [[00:33:00](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1980)]
It doesn't.

##### **Geohot** [[00:33:01](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1981)]
Make any sense to me because like the error is in like NN onyx.

##### **Nimlgen** [[00:33:05](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1985)]
I'm pretty sure

##### **Nimlgen** [[00:33:07](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1987)]
like and it's a reshape like it's trying to reshape to zero.

##### **Geohot** [[00:33:10](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1990)]
Like it's just trying to do an invalid reshape, which like I don't even like I don't even understand how that could possibly be affected by the back end.

##### **Geohot** [[00:33:16](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1996)]
So I have no theory of why.

##### **Geohot** [[00:33:19](https://www.youtube.com/watch?v=22O5E5aAnJU&t=1999)]
Yeah, exactly.

##### **Geohot** [[00:33:20](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2000)]
Memory corruption use after free.

##### **Geohot** [[00:33:21](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2001)]
That's what that sounds like.

##### **Nimlgen** [[00:33:22](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2002)]
Something like that.

##### **Nimlgen** [[00:33:24](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2004)]
Oh, yeah.

##### **Geohot** [[00:33:24](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2004)]
I just remember that the one other thing I wanted to mention is that the null back end now has the secondary role.

##### **Geohot** [[00:33:30](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2010)]
So right now, our previous.

##### **Geohot** [[00:33:31](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2011)]
It was only used for the emulate stuff, but I also wanted to add it as a compile only back end.

##### **Geohot** [[00:33:38](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2018)]
So the idea being that you could set like null equals one and then null underscore IR three equals one.

##### **Geohot** [[00:33:43](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2023)]
And then that will it'll it'll just compile your code.

##### **Nimlgen** [[00:33:49](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2029)]
So it'll run the renderer and I'll run the compiler, but then it won't try and run your code.

##### **Nimlgen** [[00:33:52](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2032)]
And the idea is that we could we could put basically every we could put everything into CI or pretty much everything into CI.

##### **Geohot** [[00:34:00](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2040)]
And, you know, like there's no there's no Qualcomm chips in CI, obviously, but, you know, we could be verifying that, like, you know, that your stuff actually compiles and hopefully catch a lot more bugs.

##### **Geohot** [[00:34:11](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2051)]
So there is that testing for Qualcomm, but I think it would be, you know, it should be a relatively quick process to just add everything.

##### **Geohot** [[00:34:20](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2060)]
Yeah, I see.

##### **Geohot** [[00:34:21](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2061)]
Yeah, but I see here how you did it.

##### **Geohot** [[00:34:24](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2064)]
That looks great.

##### **Nimlgen** [[00:34:27](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2067)]
It's totally reasonable to me.

##### **Nimlgen** [[00:34:29](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2069)]
Are there other tests that I should run?

##### **Geohot** [[00:34:31](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2071)]
Not just test ops?

##### **Geohot** [[00:34:33](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2073)]
Well, yeah, you should run the whole test suite.

##### **Geohot** [[00:34:36](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2076)]
True.

##### **Geohot** [[00:34:37](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2077)]
Yeah.

##### **Geohot** [[00:34:37](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2077)]
Okay.

##### **Nimlgen** [[00:34:38](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2078)]
Run the whole test suite.

##### **Nimlgen** [[00:34:40](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2080)]
It probably all doesn't pass.

##### **Geohot** [[00:34:42](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2082)]
It probably all doesn't pass.

##### **Geohot** [[00:34:43](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2083)]
I can die there.

##### **Geohot** [[00:34:45](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2085)]
But yeah, if there's any like, well, the nice thing about test ops is that it was super easy to just go in like.

##### **Geohot** [[00:34:59](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2099)]
Right.

##### **Geohot** [[00:35:00](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2100)]
Wait, you glitched out for a second.

##### **Nimlgen** [[00:35:03](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2103)]
I heard.

##### **Nimlgen** [[00:35:03](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2103)]
Oh, sorry.

##### **Geohot** [[00:35:04](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2104)]
The super easy thing about test ops was.

##### **Geohot** [[00:35:07](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2107)]
Yeah, the super easy thing about test ops was that it was super easy to go in and just put a return right in front of the compare.

##### **Geohot** [[00:35:14](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2114)]
Like the asserts all close.

##### **Geohot** [[00:35:17](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2117)]
Because they all use helper test op.

##### **Geohot** [[00:35:19](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2119)]
Like they all use helper test op.

##### **Nimlgen** [[00:35:20](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2120)]
Oh, that's what you mean.

##### **Nimlgen** [[00:35:22](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2122)]
Oh, you're talking about CI.

##### **Geohot** [[00:35:24](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2124)]
Oh, I wouldn't worry about that.

##### **Geohot** [[00:35:25](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2125)]
I think test ops is more than enough for for testing the compiler.

##### **Geohot** [[00:35:29](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2129)]
Yeah.

##### **Geohot** [[00:35:30](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2130)]
Okay.

##### **Geohot** [[00:35:30](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2130)]
Yeah.

##### **Nimlgen** [[00:35:30](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2130)]
Okay.

##### **Nimlgen** [[00:35:31](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2131)]
Yeah.

##### **Geohot** [[00:35:31](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2131)]
Yeah.

##### **Geohot** [[00:35:31](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2131)]
Yeah.

##### **Geohot** [[00:35:32](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2132)]
That's good.

##### **Geohot** [[00:35:32](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2132)]
Yeah.

##### **Geohot** [[00:35:32](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2132)]
If you can check with the back end, just do that.

##### **Nimlgen** [[00:35:34](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2134)]
Yeah.

##### **Nimlgen** [[00:35:35](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2135)]
The other thing that's worth adding that isn't in there right now is probably doing an image equals two on the test ops.

##### **Geohot** [[00:35:40](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2140)]
So you run one with image equals two and one without.

##### **Geohot** [[00:35:43](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2143)]
That seems good.

##### **Geohot** [[00:35:44](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2144)]
Yeah.

##### **Geohot** [[00:35:45](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2145)]
Yeah.

##### **Geohot** [[00:35:46](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2146)]
I mean, eventually we want to separate tests into like tests that require hardware and tests that don't require hardware.

##### **Nimlgen** [[00:35:51](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2151)]
And yeah, there's a lot of there's a lot of work to do here.

##### **Nimlgen** [[00:35:54](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2154)]
You know, to like better tighten our abstraction layers so we can like, yeah, this all runs in CI.

##### **Geohot** [[00:35:59](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2159)]
I mean, this is one of the huge wins of LLVM and like projects like this in general, whereas you don't need the hardware actually to to compile for it.

##### **Geohot** [[00:36:08](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2168)]
And there's no reason that you should.

##### **Geohot** [[00:36:09](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2169)]
I mean, this is like the failure of the open CL API.

##### **Geohot** [[00:36:12](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2172)]
But yeah.

##### **Geohot** [[00:36:14](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2174)]
Yeah.

##### **Nimlgen** [[00:36:14](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2174)]
Cool.

##### **Nimlgen** [[00:36:15](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2175)]
Yeah.

##### **Geohot** [[00:36:15](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2175)]
Yeah.

##### **Geohot** [[00:36:16](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2176)]
So if there's anything, if there's not anything, anything that I think we'll click merge on this after the meeting.

##### **Geohot** [[00:36:21](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2181)]
But yeah.

##### **Geohot** [[00:36:21](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2181)]
Yeah.

##### **Geohot** [[00:36:22](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2182)]
It looks good to merge as long as benchmarks passing.

##### **Nimlgen** [[00:36:24](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2184)]
And then I think the next thing to do is to add this to benchmark and then figure out how we can get more.

##### **Nimlgen** [[00:36:29](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2189)]
Speed.

##### **Geohot** [[00:36:29](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2189)]
Speed.

##### **Geohot** [[00:36:30](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2190)]
Speed.

##### **Geohot** [[00:36:30](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2190)]
Speed.

##### **Geohot** [[00:36:30](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2190)]
Speed.

##### **Geohot** [[00:36:31](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2191)]
Yep.

##### **Nimlgen** [[00:36:32](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2192)]
Sounds good.

##### **Nimlgen** [[00:36:33](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2193)]
Cool.

##### **Geohot** [[00:36:36](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2196)]
Speaking of speed, Python speed.

##### **Geohot** [[00:36:40](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2200)]
So, yeah, I think this is going to be my project for the week.

##### **Geohot** [[00:36:46](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2206)]
We made Chen, you worked on this a whole bit, a whole bunch last week, too.

##### **Geohot** [[00:36:51](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2211)]
We've made pretty good progress.

##### **Geohot** [[00:36:53](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2213)]
I think everything's like twice as fast.

##### **Nimlgen** [[00:36:54](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2214)]
I think that seems about like every week you work on it, you can get another two X.

##### **Nimlgen** [[00:36:59](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2219)]
So that seems about right.

##### **Geohot** [[00:37:01](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2221)]
What were you saying about the onyx thing?

##### **Geohot** [[00:37:03](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2223)]
Do you have an idea?

##### **Geohot** [[00:37:05](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2225)]
It might be back in the letter because I think onyx, if it does any conversions from disk, it will go through the back end.

##### **Geohot** [[00:37:13](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2233)]
Oh.

##### **Geohot** [[00:37:17](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2237)]
Interesting.

##### **Nimlgen** [[00:37:17](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2237)]
Oh, interesting.

##### **Nimlgen** [[00:37:19](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2239)]
Maybe.

##### **Geohot** [[00:37:21](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2241)]
Okay.

##### **Geohot** [[00:37:21](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2241)]
I'll have to look at the types.

##### **Geohot** [[00:37:22](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2242)]
That might that might explain it.

##### **Geohot** [[00:37:25](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2245)]
Can we just force that to CPU?

##### **Geohot** [[00:37:27](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2247)]
Yeah.

##### **Nimlgen** [[00:37:28](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2248)]
Maybe it already does.

##### **Nimlgen** [[00:37:29](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2249)]
This I could I could very well believe that it doesn't.

##### **Geohot** [[00:37:33](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2253)]
Yeah.

##### **Geohot** [[00:37:34](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2254)]
Yeah.

##### **Geohot** [[00:37:34](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2254)]
That there's some like contiguous and it's like making this little kernel.

##### **Geohot** [[00:37:38](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2258)]
Yeah.

##### **Geohot** [[00:37:39](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2259)]
And then it's like, well, that's interesting.

##### **Nimlgen** [[00:37:41](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2261)]
Also, it seems like it surfaces a bug in the back end.

##### **Nimlgen** [[00:37:44](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2264)]
Yeah.

##### **Geohot** [[00:37:45](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2265)]
But that explains why it could be broken.

##### **Geohot** [[00:37:46](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2266)]
Yeah.

##### **Geohot** [[00:37:47](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2267)]
If you're like reading from.

##### **Geohot** [[00:37:47](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2267)]
But it's doing the conversions because it knows the back end doesn't support the type, but then it's using the back end to write.

##### **Geohot** [[00:37:56](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2276)]
That I don't know.

##### **Nimlgen** [[00:37:58](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2278)]
But yeah, I mean.

##### **Nimlgen** [[00:37:59](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2279)]
Yeah.

##### **Geohot** [[00:37:59](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2279)]
Run with debug equals four and see if Onyx is actually like creating kernels.

##### **Geohot** [[00:38:03](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2283)]
Yeah.

##### **Geohot** [[00:38:05](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2285)]
Yeah.

##### **Geohot** [[00:38:05](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2285)]
I mean, this could also potentially be with Qualcomm in particular.

##### **Geohot** [[00:38:09](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2289)]
I'm worried about cache and validation bugs.

##### **Nimlgen** [[00:38:12](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2292)]
If we're not properly invalidating the cache, there's a chance you're like creating something.

##### **Nimlgen** [[00:38:18](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2298)]
The GPU is copying it, but that's hanging out in the because the Qualcomm has a different L2 cache for each like subsystem.

##### **Geohot** [[00:38:25](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2305)]
So the Qualcomm has three L2 caches.

##### **Geohot** [[00:38:27](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2307)]
The big island, the little island and the GPU and the DSP has one too.

##### **Geohot** [[00:38:31](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2311)]
So this is four.

##### **Geohot** [[00:38:33](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2313)]
So yeah, I worried something like that.

##### **Geohot** [[00:38:35](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2315)]
But yeah, no, good, good idea.

##### **Nimlgen** [[00:38:37](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2317)]
That's that's probably what it is.

##### **Nimlgen** [[00:38:40](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2320)]
You think I should just force that to the CPU?

##### **Geohot** [[00:38:42](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2322)]
I mean, I can see what the errors are, but if it's like.

##### **Geohot** [[00:38:44](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2324)]
No, I think we should figure out what the we should figure out what the errors are and not force it to CPU.

##### **Geohot** [[00:38:50](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2330)]
I think we should figure out who's ever working on Onyx should figure out how to force CPU more generally.

##### **Geohot** [[00:38:55](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2335)]
This is just a.

##### **Geohot** [[00:38:57](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2337)]
There's a little bit of a.

##### **Nimlgen** [[00:38:57](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2337)]
There's a lot of bugs like this around a disk too.

##### **Nimlgen** [[00:39:01](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2341)]
But yeah, no, this is definitely this is definitely just surfacing a bug in the back end.

##### **Geohot** [[00:39:05](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2345)]
That's probably a cache and validation bug, and that's why it's flaky.

##### **Geohot** [[00:39:08](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2348)]
That makes a lot of sense to me.

##### **Geohot** [[00:39:10](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2350)]
So it's a failing test or a gift.

##### **Geohot** [[00:39:13](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2353)]
Yep.

##### **Geohot** [[00:39:15](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2355)]
Yeah.

##### **Nimlgen** [[00:39:16](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2356)]
So yeah, Python speed.

##### **Nimlgen** [[00:39:17](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2357)]
That's what I'm going to work on this week.

##### **Geohot** [[00:39:20](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2360)]
You know, scan would be great, but I don't think we need it for.

##### **Geohot** [[00:39:27](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2367)]
This and scan is no excuse for not making the other thing fast anyway.

##### **Geohot** [[00:39:33](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2373)]
We have the V map story is much better now.

##### **Geohot** [[00:39:37](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2377)]
I really cleaned up the V map story where you can use shrink and then the derivative shrink is pad so we can do derivatives on V maps mostly.

##### **Geohot** [[00:39:47](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2387)]
There's a few annoyances.

##### **Nimlgen** [[00:39:48](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2388)]
One of the things you're going to want to.

##### **Nimlgen** [[00:39:50](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2390)]
One of the things that probably I need to do first is get string ranges supported.

##### **Geohot** [[00:39:56](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2396)]
Because like if you have a range.

##### **Geohot** [[00:39:57](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2397)]
In the forward pass like range zero, you need to create a corresponding range in the backward pass.

##### **Geohot** [[00:40:03](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2403)]
It would be nice to just call that like zero underscore grad, right?

##### **Geohot** [[00:40:06](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2406)]
Because like if you're looping through on the forward, you're going to have to loop through on the backward, and that's the creation of a new range.

##### **Geohot** [[00:40:11](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2411)]
So then what do you call that range?

##### **Nimlgen** [[00:40:14](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2414)]
So this is why.

##### **Nimlgen** [[00:40:15](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2415)]
Yeah.

##### **Geohot** [[00:40:15](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2415)]
Halide and TVM both use strings, so we should move the ranges to strings.

##### **Geohot** [[00:40:19](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2419)]
The problem with moving the ranges to strings is that you then have to think about what your range priority order is.

##### **Geohot** [[00:40:24](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2424)]
So currently we sort the args of the range.

##### **Geohot** [[00:40:27](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2427)]
And that's the way you're going to do it.

##### **Geohot** [[00:40:27](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2427)]
So you're going to have to think about what your range is.

##### **Nimlgen** [[00:40:27](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2427)]
And that determines the range priority.

##### **Nimlgen** [[00:40:29](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2429)]
But that story needs to be cleaned up to.

##### **Geohot** [[00:40:32](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2432)]
So that's my real job.

##### **Geohot** [[00:40:35](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2435)]
It's the kind of stuff I'm going to work on this week.

##### **Geohot** [[00:40:38](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2438)]
Yeah.

##### **Geohot** [[00:40:38](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2438)]
And get it to the point where we're reasonably, you know, I think that a minute startup time for four or five B is totally reasonable.

##### **Geohot** [[00:40:45](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2445)]
You know, it's going to be a 11 day training job anyway.

##### **Nimlgen** [[00:40:47](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2447)]
So I mean, it is fine.

##### **Nimlgen** [[00:40:49](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2449)]
Yeah.

##### **Geohot** [[00:40:50](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2450)]
We should be able to test quickly.

##### **Geohot** [[00:40:51](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2451)]
We could test with a small number of layers.

##### **Geohot** [[00:40:53](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2453)]
Even a couple of minutes is probably fine.

##### **Geohot** [[00:40:55](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2455)]
10 minutes is a little much.

##### **Geohot** [[00:40:57](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2457)]
Yeah.

##### **Nimlgen** [[00:40:57](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2457)]
You know, you don't wait 10 minutes to find out you have a bug.

##### **Nimlgen** [[00:41:00](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2460)]
But yeah, Python speed.

##### **Geohot** [[00:41:02](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2462)]
Yeah.

##### **Geohot** [[00:41:02](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2462)]
And then my other my other weekend project, you can check out my PR for that.

##### **Geohot** [[00:41:10](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2470)]
It's just called having fun with Python as MDSL.

##### **Geohot** [[00:41:14](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2474)]
So, yeah, as we move to.

##### **Geohot** [[00:41:18](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2478)]
We're going to want to start putting assemblers into tiny grad.

##### **Nimlgen** [[00:41:23](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2483)]
And this is just stuff with making like all the bit fields really nice.

##### **Nimlgen** [[00:41:27](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2487)]
So you can see my like my instruction encodings are pretty much as beautiful as you can make a DSL.

##### **Geohot** [[00:41:39](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2499)]
And then it's going to support things like this.

##### **Geohot** [[00:41:45](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2505)]
So like create an instruction.

##### **Geohot** [[00:41:48](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2508)]
So that's like, you know, the instruction and all those helpers are going to be auto genned.

##### **Geohot** [[00:41:55](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2515)]
I'm going to extract all these.

##### **Geohot** [[00:41:57](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2517)]
It's going to be like as auto gen as possible to get you the cleanest DSL.

##### **Nimlgen** [[00:42:03](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2523)]
Those those classes are as copied as I possibly.

##### **Nimlgen** [[00:42:09](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2529)]
So it would be nice to have.

##### **Geohot** [[00:42:10](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2530)]
Yeah.

##### **Geohot** [[00:42:11](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2531)]
How much assembly do you think we're going to have to do for?

##### **Geohot** [[00:42:15](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2535)]
It's just.

##### **Geohot** [[00:42:18](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2538)]
Yeah.

##### **Geohot** [[00:42:18](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2538)]
I mean, I think we start with doing the custom thing and say, how does.

##### **Nimlgen** [[00:42:22](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2542)]
I don't see how I can specify register from custom.

##### **Nimlgen** [[00:42:26](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2546)]
Like, how do I link a U of two registered?

##### **Geohot** [[00:42:31](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2551)]
How does how does that get started?

##### **Geohot** [[00:42:33](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2553)]
Well, they're just in C++.

##### **Geohot** [[00:42:34](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2554)]
It is in volatile.

##### **Geohot** [[00:42:36](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2556)]
They can just pass in the variable.

##### **Geohot** [[00:42:37](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2557)]
You can.

##### **Nimlgen** [[00:42:38](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2558)]
Oh, you're going to ask him volatile with a custom instruction.

##### **Nimlgen** [[00:42:42](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2562)]
Yeah.

##### **Geohot** [[00:42:43](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2563)]
But what's the variable name?

##### **Geohot** [[00:42:45](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2565)]
Parentheses zero.

##### **Geohot** [[00:42:46](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2566)]
It's like a little templating language.

##### **Geohot** [[00:42:48](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2568)]
No.

##### **Geohot** [[00:42:48](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2568)]
Yeah.

##### **Nimlgen** [[00:42:49](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2569)]
I know for ASM.

##### **Nimlgen** [[00:42:49](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2569)]
Yeah.

##### **Geohot** [[00:42:50](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2570)]
No, no, no.

##### **Geohot** [[00:42:51](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2571)]
It's the same.

##### **Geohot** [[00:42:52](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2572)]
It's the same.

##### **Geohot** [[00:42:53](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2573)]
Oh, really?

##### **Geohot** [[00:42:53](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2573)]
Yeah.

##### **Nimlgen** [[00:42:53](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2573)]
It has a little like you can pass in args to the custom and they just show up as like,

##### **Nimlgen** [[00:42:57](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2577)]
oh, you read that.

##### **Geohot** [[00:42:58](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2578)]
Yeah.

##### **Geohot** [[00:42:58](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2578)]
And if it doesn't support that, you're welcome to add it.

##### **Geohot** [[00:43:01](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2581)]
But it's the same sort of templating language.

##### **Geohot** [[00:43:04](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2584)]
Yes, you can totally.

##### **Geohot** [[00:43:05](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2585)]
Yeah.

##### **Nimlgen** [[00:43:05](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2585)]
You can like pass in a thing and then however that thing is going to be rendered.

##### **Nimlgen** [[00:43:09](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2589)]
I see.

##### **Geohot** [[00:43:10](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2590)]
Is how it's passed into custom and custom will do that replace for you at the end.

##### **Geohot** [[00:43:15](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2595)]
Yeah.

##### **Geohot** [[00:43:15](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2595)]
I mean, a custom would be pretty useless if you didn't couldn't get the variables.

##### **Geohot** [[00:43:19](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2599)]
Yeah.

##### **Geohot** [[00:43:20](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2600)]
So all that should work.

##### **Nimlgen** [[00:43:20](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2600)]
Yeah.

##### **Nimlgen** [[00:43:21](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2601)]
We should.

##### **Geohot** [[00:43:21](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2601)]
Yeah.

##### **Geohot** [[00:43:21](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2601)]
We should just make custom work to get our inline assembly working.

##### **Geohot** [[00:43:24](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2604)]
And then we can like tell this we can we can start transitioning to an assembly much more

##### **Geohot** [[00:43:28](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2608)]
gradually.

##### **Geohot** [[00:43:31](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2611)]
You know, for assembly, we need we need a bunch of things first.

##### **Nimlgen** [[00:43:34](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2614)]
Oh, we still need someone wants to work on this.

##### **Nimlgen** [[00:43:37](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2617)]
So we have this memory planner that we run in the big graph for globals.

##### **Geohot** [[00:43:41](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2621)]
But we need basically that same memory planner.

##### **Geohot** [[00:43:44](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2624)]
We can do it right now for locals.

##### **Geohot** [[00:43:45](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2625)]
And this is already a thing in auto gen flash attention where it creates three local memory

##### **Geohot** [[00:43:51](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2631)]
locales, but they're never used at the same time.

##### **Geohot** [[00:43:53](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2633)]
So all three of those locales can actually just be one local.

##### **Nimlgen** [[00:43:56](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2636)]
You know, you just got to you have to like look at like like the defuse and the you know,

##### **Nimlgen** [[00:44:01](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2641)]
that the liveness analysis.

##### **Geohot** [[00:44:05](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2645)]
But yeah, no, I mean, that should be unified with with a memory planner.

##### **Geohot** [[00:44:08](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2648)]
And then the story for registers, I think is pretty good.

##### **Geohot** [[00:44:11](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2651)]
So we have this op called define reg.

##### **Geohot** [[00:44:15](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2655)]
Define reg is used if you need to like basically do a back reference to the register.

##### **Geohot** [[00:44:19](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2659)]
If you're using that register as an accumulator.

##### **Nimlgen** [[00:44:21](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2661)]
You have to do it explicitly with define reg.

##### **Nimlgen** [[00:44:24](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2664)]
And I actually like this better than LVM's fee instruction.

##### **Geohot** [[00:44:29](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2669)]
You can do the same thing in LVM too.

##### **Geohot** [[00:44:31](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2671)]
But LVM has this like fee instruction where they like pass it through.

##### **Geohot** [[00:44:35](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2675)]
Actually, I guess you can do the other thing in LVM too.

##### **Geohot** [[00:44:37](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2677)]
So and this is actually how we generate the LVM.

##### **Geohot** [[00:44:40](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2680)]
So yeah, when you define reg, that's just going to be pre allocated in specific registers.

##### **Nimlgen** [[00:44:45](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2685)]
Again, you can do that exact same liveness analysis that you do in locals to see if these

##### **Nimlgen** [[00:44:50](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2690)]
these big clusters are going to be.

##### **Geohot** [[00:44:51](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2691)]
I mean, the chunks are not overlapping, but those will be the first registers allocated.

##### **Geohot** [[00:44:54](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2694)]
The registers that use your accumulator on CDNA.

##### **Geohot** [[00:44:58](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2698)]
We can use the A-GPRs.

##### **Geohot** [[00:45:00](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2700)]
So CDNA has these special accumulator GPRs if your output is from a WAMA, which is pretty cool.

##### **Geohot** [[00:45:09](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2709)]
Yeah, so you'll assign those registers.

##### **Nimlgen** [[00:45:12](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2712)]
And then I think even a very naive register allocator would work pretty well for GPUs.

##### **Nimlgen** [[00:45:19](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2719)]
I think that register allocation on CPUs is a much more constrained problem than register allocation on GPUs.

##### **Geohot** [[00:45:28](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2728)]
A register allocation on a CPU, you just have a lot less registers.

##### **Geohot** [[00:45:31](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2731)]
I mean, GPUs, it kind of matters for warp occupancy.

##### **Geohot** [[00:45:34](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2734)]
But I think the more difficult thing about assembly is not going to be the register allocator.

##### **Geohot** [[00:45:38](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2738)]
It's going to be cleaning up symbolic.

##### **Geohot** [[00:45:41](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2741)]
So right now in symbolic, we pay very little attention to like if you're doing A plus three.

##### **Nimlgen** [[00:45:47](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2747)]
Right.

##### **Nimlgen** [[00:45:47](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2747)]
So let's say you have like a range A and you do A plus three.

##### **Geohot** [[00:45:51](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2751)]
Well, where should you do the A plus three?

##### **Geohot** [[00:45:53](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2753)]
Should you do the A plus three at the top and keep around two registers?

##### **Geohot** [[00:45:56](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2756)]
Or A plus three right when you need it?

##### **Geohot** [[00:46:01](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2761)]
But it's that exact same tradeoff that you have in every other part of GPUs, which is do you want to recompute or do you want to store?

##### **Geohot** [[00:46:10](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2770)]
It's the same problems.

##### **Nimlgen** [[00:46:12](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2772)]
It's the same problems at every single layer of the subtraction hierarchy.

##### **Nimlgen** [[00:46:16](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2776)]
It's just a question of accuracy.

##### **Geohot** [[00:46:17](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2777)]
It's just a question of accuracy.

##### **Geohot** [[00:46:18](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2778)]
And so, yeah, I think that by the end of next year, we're going to have some serious non LLVM backends, some completely full tiny grad all the way to GPU assembly.

##### **Geohot** [[00:46:33](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2793)]
And I think GPUs are the place to do it, especially when you look at the MI350 and you see that LLVM is not that good.

##### **Geohot** [[00:46:40](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2800)]
The LLVM backend for the MI350 makes all these ridiculous mistakes when you look at the code.

##### **Geohot** [[00:46:46](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2806)]
And that's why the fundamental question is, how do I do it?

##### **Nimlgen** [[00:46:47](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2807)]
Well, I think the underkittens people need just go to assembly for that.

##### **Nimlgen** [[00:46:50](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2810)]
The nvidia does not do this.

##### **Geohot** [[00:46:52](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2812)]
The nvidia compiler is a lot better.

##### **Geohot** [[00:46:55](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2815)]
It seems like mostly a cdna4 problem.

##### **Geohot** [[00:46:58](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2818)]
The three one looks better, too.

##### **Geohot** [[00:47:01](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2821)]
The MI300, I don't know what they broke.

##### **Geohot** [[00:47:03](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2823)]
The MI300 code looks better.

##### **Nimlgen** [[00:47:05](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2825)]
But if the LLVM equals one also just doesn't work on three, it like crashes on a bunch of semperfords.

##### **Nimlgen** [[00:47:14](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2834)]
Well, that's a different.

##### **Geohot** [[00:47:15](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2835)]
Oh, that's probably because we don't know the layers where it's developing.

##### **Geohot** [[00:47:17](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2837)]
I bumped it to 21 and it still doesn't work.

##### **Geohot** [[00:47:19](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2839)]
I thought it was LLVM version.

##### **Geohot** [[00:47:21](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2841)]
I thought it was an upstream.

##### **Geohot** [[00:47:23](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2843)]
There's some changes that aren't in 21 yet.

##### **Nimlgen** [[00:47:28](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2848)]
Yeah, probably because they're janky

##### **Nimlgen** [[00:47:30](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2850)]
and the LLVM people told them no.

##### **Geohot** [[00:47:31](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2851)]
They're like, no, no, no, we just hacked it for this one thing.

##### **Geohot** [[00:47:34](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2854)]
Okay, there's your problem.

##### **Geohot** [[00:47:37](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2857)]
Yeah, so TinyGrad needs to eventually replace LLVM anyway,

##### **Geohot** [[00:47:42](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2862)]
but we shouldn't really do this

##### **Geohot** [[00:47:44](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2864)]
until we have a very good story around all of these.

##### **Nimlgen** [[00:47:50](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2870)]
The register allocator in many ways is the memory allocator.

##### **Nimlgen** [[00:47:54](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2874)]
And then things about symbolic,

##### **Geohot** [[00:47:56](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2876)]
it really starts to matter

##### **Geohot** [[00:47:57](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2877)]
because we don't have this extra compiler stage.

##### **Geohot** [[00:48:00](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2880)]
You can give Clang crap.

##### **Geohot** [[00:48:01](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2881)]
You can tell Clang B equals A plus 6 plus 3

##### **Geohot** [[00:48:06](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2886)]
and Clang will happily turn that into A plus 9 for you.

##### **Nimlgen** [[00:48:10](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2890)]
Whereas if we get rid of that, even in PTX,

##### **Nimlgen** [[00:48:14](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2894)]
the lower level will clean all that stuff up for you.

##### **Geohot** [[00:48:18](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2898)]
But if we get rid of that,

##### **Geohot** [[00:48:21](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2901)]
if we go right to assembly,

##### **Geohot** [[00:48:23](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2903)]
we better make sure we have a really good story around that.

##### **Geohot** [[00:48:27](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2907)]
There's also tons of SGPRs.

##### **Geohot** [[00:48:29](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2909)]
I think SGPRs are underutilized.

##### **Nimlgen** [[00:48:31](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2911)]
If you read that RDNA3 map model,

##### **Nimlgen** [[00:48:33](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2913)]
he's like, I just used a lot of SGPRs.

##### **Geohot** [[00:48:35](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2915)]
And SGPRs are totally free, I believe.

##### **Geohot** [[00:48:38](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2918)]
Like, I don't know if you,

##### **Geohot** [[00:48:39](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2919)]
do you ever run into warp occupancy issues with SGPRs?

##### **Geohot** [[00:48:42](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2922)]
Do you know?

##### **Geohot** [[00:48:44](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2924)]
I don't think so.

##### **Nimlgen** [[00:48:44](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2924)]
Yeah, I mean, it's not like that big.

##### **Nimlgen** [[00:48:46](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2926)]
Why would they not like put tons of,

##### **Geohot** [[00:48:49](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2929)]
they'd probably want to do SGPRs that are big enough

##### **Geohot** [[00:48:52](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2932)]
for your full warp occupancy.

##### **Geohot** [[00:48:54](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2934)]
So yeah, I mean, it seems like these things can support

##### **Geohot** [[00:48:56](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2936)]
like 16 or 32, depending on how you count it.

##### **Geohot** [[00:49:00](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2940)]
So yeah, if there's enough SGPRs,

##### **Nimlgen** [[00:49:02](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2942)]
then you never have to worry about SGPR pressure.

##### **Nimlgen** [[00:49:05](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2945)]
You should happily use them all.

##### **Geohot** [[00:49:08](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2948)]
Yeah, I was looking at the encodings this weekend

##### **Geohot** [[00:49:10](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2950)]
and the RDNA3 stuff and they look cool.

##### **Geohot** [[00:49:13](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2953)]
All right, cool.

##### **Geohot** [[00:49:14](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2954)]
We got 10 minutes.

##### **Geohot** [[00:49:16](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2956)]
I see there's a PR for me to review on WebGPU.

##### **Nimlgen** [[00:49:21](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2961)]
Hopefully I can just click merge.

##### **Nimlgen** [[00:49:23](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2963)]
Again, the amount of talk of WebGPU versus actual WebGPU.

##### **Geohot** [[00:49:31](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2971)]
Okay, good.

##### **Geohot** [[00:49:32](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2972)]
This one looks good.

##### **Geohot** [[00:49:34](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2974)]
Assert where test models, test whisper, passing CI.

##### **Geohot** [[00:49:38](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2978)]
Great, merged.

##### **Geohot** [[00:49:42](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2982)]
Cool.

##### **Nimlgen** [[00:49:45](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2985)]
I also went through all the PRs.

##### **Nimlgen** [[00:49:47](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2987)]
There's only two pages of them now, which is nice.

##### **Geohot** [[00:49:50](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2990)]
You can't really get less than two pages,

##### **Geohot** [[00:49:51](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2991)]
but two pages is pretty good.

##### **Geohot** [[00:49:54](https://www.youtube.com/watch?v=22O5E5aAnJU&t=2994)]
How many people we have working on this?

##### **Geohot** [[00:50:03](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3003)]
SQTT instruction timeline.

##### **Geohot** [[00:50:05](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3005)]
Oh, this is pretty.

##### **Nimlgen** [[00:50:06](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3006)]
I didn't see this one.

##### **Nimlgen** [[00:50:07](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3007)]
Yeah, I mean, we also want to think about,

##### **Geohot** [[00:50:09](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3009)]
I mean, then first we got to speed up the thing,

##### **Geohot** [[00:50:11](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3011)]
but like once we have warp instructions,

##### **Geohot** [[00:50:13](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3013)]
we can start showing where stalls are.

##### **Geohot** [[00:50:14](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3014)]
All right, because the stall is like,

##### **Geohot** [[00:50:16](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3016)]
when are you, when are you,

##### **Nimlgen** [[00:50:18](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3018)]
I mean, this is the right idea.

##### **Nimlgen** [[00:50:20](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3020)]
We want to basically show the utilization of each GPU resource.

##### **Geohot** [[00:50:24](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3024)]
And then you can see where you're getting bubbles

##### **Geohot** [[00:50:26](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3026)]
and where you're getting non-utilized GPUs.

##### **Geohot** [[00:50:28](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3028)]
So yeah, this is cool.

##### **Geohot** [[00:50:29](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3029)]
This is definitely the right direction to go in here.

##### **Geohot** [[00:50:36](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3036)]
Yeah, I mean, like that's crazy

##### **Nimlgen** [[00:50:37](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3037)]
because that's like not even per warp anymore.

##### **Nimlgen** [[00:50:39](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3039)]
You just have like per, it would be per CU.

##### **Geohot** [[00:50:44](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3044)]
You want to show what your utilization

##### **Geohot** [[00:50:46](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3046)]
of all the different resources in the CU is.

##### **Geohot** [[00:50:49](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3049)]
So yeah.

##### **Geohot** [[00:50:50](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3050)]
You want to show per SIMD, I think.

##### **Geohot** [[00:50:54](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3054)]
Yeah, that's.

##### **Nimlgen** [[00:50:55](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3055)]
Because the SIMD can context switch.

##### **Nimlgen** [[00:50:58](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3058)]
So.

##### **Geohot** [[00:50:59](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3059)]
And high latency.

##### **Geohot** [[00:51:00](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3060)]
I mean, I think a SIMD is just like an ALU.

##### **Geohot** [[00:51:03](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3063)]
So I think you'd want to like show both SIMDs on the CU,

##### **Geohot** [[00:51:05](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3065)]
but does each SIMD have its own load path?

##### **Geohot** [[00:51:08](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3068)]
I don't think they do.

##### **Nimlgen** [[00:51:11](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3071)]
They do share.

##### **Nimlgen** [[00:51:13](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3073)]
I think a CU is like.

##### **Geohot** [[00:51:15](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3075)]
Two SIMDs?

##### **Geohot** [[00:51:17](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3077)]
So, yeah, I mean, that's, so I would imagine for the CU,

##### **Geohot** [[00:51:20](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3080)]
you want to show something like the memory path utilization

##### **Geohot** [[00:51:24](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3084)]
and then your ALU SIMD zero, ALU SIMD one, ALU SIMD two,

##### **Geohot** [[00:51:29](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3089)]
ALU SIMD three utilization.

##### **Nimlgen** [[00:51:34](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3094)]
You can really like, like it's really cool with that,

##### **Nimlgen** [[00:51:37](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3097)]
that SQTT parse, it shows you like what the GPU is actually doing.

##### **Geohot** [[00:51:41](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3101)]
I don't know.

##### **Geohot** [[00:51:41](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3101)]
To be fair, I didn't look at the output from RockMTraceDecoder that much.

##### **Geohot** [[00:51:44](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3104)]
I'm sure it's all there too.

##### **Geohot** [[00:51:46](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3106)]
But like for me, it's just a lot easier for me to like understand stuff when like the hardware is giving me something

##### **Geohot** [[00:51:51](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3111)]
because I can see how this was actually implemented and not going through 100,000 lines.

##### **Nimlgen** [[00:51:56](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3116)]
God knows what.

##### **Nimlgen** [[00:51:59](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3119)]
Yeah.

##### **Geohot** [[00:52:04](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3124)]
God knows what's going on in there.

##### **Geohot** [[00:52:06](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3126)]
I mean, I would love to actually just upstream the SQTT parser and put it.

##### **Geohot** [[00:52:10](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3130)]
Yeah.

##### **Geohot** [[00:52:11](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3131)]
Yeah.

##### **Geohot** [[00:52:12](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3132)]
I think, I think we will.

##### **Nimlgen** [[00:52:14](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3134)]
If you're interested.

##### **Nimlgen** [[00:52:14](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3134)]
I'm excited about that.

##### **Geohot** [[00:52:16](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3136)]
Yeah.

##### **Geohot** [[00:52:17](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3137)]
We have to do a few.

##### **Geohot** [[00:52:18](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3138)]
I think we have to do a few performance optimizations on that as let's like written really naively.

##### **Geohot** [[00:52:23](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3143)]
I vibe coded it.

##### **Geohot** [[00:52:25](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3145)]
That's why it's an extra.

##### **Nimlgen** [[00:52:27](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3147)]
Oh my God.

##### **Nimlgen** [[00:52:27](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3147)]
Like you start reading any code that ChatGPT actually wrote and you're like, this is terrible.

##### **Geohot** [[00:52:32](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3152)]
This is, this is so bad.

##### **Geohot** [[00:52:34](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3154)]
Like, why did you write this?

##### **Geohot** [[00:52:36](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3156)]
You know, like it all looks good from like a, from like a glance if you're not reading it that carefully.

##### **Geohot** [[00:52:42](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3162)]
But as soon as you do like close readings of any GPT code, you're like, oh, this is terrible.

##### **Geohot** [[00:52:44](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3164)]
Like, it's like, oh, GPT lacks taste.

##### **Nimlgen** [[00:52:50](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3170)]
Yeah.

##### **Nimlgen** [[00:52:51](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3171)]
Okay.

##### **Geohot** [[00:52:51](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3171)]
If you're excited about upstreaming that I can, I can work on it more, get it matching

##### **Geohot** [[00:52:55](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3175)]
the instructions and get it faster.

##### **Geohot** [[00:52:57](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3177)]
I don't know.

##### **Geohot** [[00:52:58](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3178)]
It was kind of easier than I thought.

##### **Geohot** [[00:53:04](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3184)]
But yeah, no, I mean, do you feel blocked at all by the rock and thing?

##### **Nimlgen** [[00:53:08](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3188)]
I don't think so.

##### **Nimlgen** [[00:53:10](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3190)]
It's pretty nice.

##### **Geohot** [[00:53:10](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3190)]
If you're not blocked on it, then it'll stay the weekend project.

##### **Geohot** [[00:53:14](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3194)]
I don't know.

##### **Geohot** [[00:53:14](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3194)]
I don't know.

##### **Geohot** [[00:53:14](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3194)]
I'm a lot more excited about working on that than I am about working on Python speed.

##### **Geohot** [[00:53:19](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3199)]
But, you know, Python speed is what we need.

##### **Nimlgen** [[00:53:22](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3202)]
I'm actually, I'm more excited about Python speed than I am about working on, excited

##### **Nimlgen** [[00:53:26](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3206)]
than I am about working on scan.

##### **Geohot** [[00:53:29](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3209)]
Scan is hard.

##### **Geohot** [[00:53:30](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3210)]
I'm like, what if you scan and assign?

##### **Geohot** [[00:53:38](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3218)]
Oh, yeah.

##### **Geohot** [[00:53:42](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3222)]
But, yeah, I'll keep that the weekend project.

##### **Geohot** [[00:53:44](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3224)]
And I think for assembly, I think for now we can just use the custom inline and it's

##### **Nimlgen** [[00:53:52](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3232)]
all pretty good.

##### **Nimlgen** [[00:53:54](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3234)]
Cool.

##### **Geohot** [[00:53:56](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3236)]
Let's quickly see if there's any other bounties.

##### **Geohot** [[00:54:02](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3242)]
Any, how's the GPT OSS one coming?

##### **Geohot** [[00:54:07](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3247)]
I know we got a locked bounty on that.

##### **Geohot** [[00:54:12](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3252)]
I see the tests failing on the winner.

##### **Geohot** [[00:54:14](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3254)]
I'm going to grab one too.

##### **Nimlgen** [[00:54:23](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3263)]
Okay.

##### **Nimlgen** [[00:54:24](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3264)]
Olmo is running fast.

##### **Geohot** [[00:54:25](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3265)]
How fast is GPT OSS running?

##### **Geohot** [[00:54:34](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3274)]
Yeah, but we were at 0.1 tokens.

##### **Geohot** [[00:54:36](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3276)]
So, a thousand X off, but it's faster now.

##### **Geohot** [[00:54:47](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3287)]
I haven't worked on it this week.

##### **Geohot** [[00:54:48](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3288)]
Okay, cool.

##### **Nimlgen** [[00:54:49](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3289)]
Yeah, yeah.

##### **Nimlgen** [[00:54:50](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3290)]
We got to get, got to get some more, more speed on that.

##### **Geohot** [[00:54:54](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3294)]
I don't know.

##### **Geohot** [[00:54:55](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3295)]
Why is it different from Olmo?

##### **Geohot** [[00:54:57](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3297)]
Is there any reason it's like harder to make fast than Olmo?

##### **Geohot** [[00:55:02](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3302)]
Let me see.

##### **Geohot** [[00:55:05](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3305)]
Something like softmax thing.

##### **Nimlgen** [[00:55:07](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3307)]
Olmo only works for batch size of one.

##### **Nimlgen** [[00:55:09](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3309)]
Oh, I don't care if this only works for batch size of one too.

##### **Geohot** [[00:55:11](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3311)]
That's fine.

##### **Geohot** [[00:55:14](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3314)]
Okay.

##### **Geohot** [[00:55:15](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3315)]
I don't think people care about it as batch size of one.

##### **Geohot** [[00:55:19](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3319)]
I was imagining making a really similar.

##### **Geohot** [[00:55:27](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3327)]
GPT OSS is an extra scatter operation.

##### **Nimlgen** [[00:55:29](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3329)]
I'll think more about that later.

##### **Nimlgen** [[00:55:31](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3331)]
But like once we have that merged, I want to merge like a 100 line web UI.

##### **Geohot** [[00:55:36](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3336)]
And I want like tiny grad apps LLVM to like reuse the infrastructure from Viz to make

##### **Geohot** [[00:55:41](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3341)]
it, but no one should work on this.

##### **Geohot** [[00:55:43](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3343)]
It's just, it's just something.

##### **Geohot** [[00:55:44](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3344)]
Yeah.

##### **Geohot** [[00:55:44](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3344)]
I don't know what to think about.

##### **Nimlgen** [[00:55:45](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3345)]
Like the tiny grad should be pip install tiny grad.

##### **Nimlgen** [[00:55:48](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3348)]
You got Python dash M tiny grad apps LLM and it opens this web interface that has zero

##### **Geohot** [[00:55:54](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3354)]
dependencies that runs in LLM.

##### **Geohot** [[00:55:56](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3356)]
I think that would be another way to get users.

##### **Geohot** [[00:56:01](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3361)]
Okay.

##### **Geohot** [[00:56:02](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3362)]
HVAC.

##### **Geohot** [[00:56:05](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3365)]
Oh, I saw a PR for the refactor multi.

##### **Nimlgen** [[00:56:09](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3369)]
Yeah.

##### **Nimlgen** [[00:56:09](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3369)]
You have to don't apply tensor map.

##### **Geohot** [[00:56:12](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3372)]
Don't.

##### **Geohot** [[00:56:15](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3375)]
Use you off map.

##### **Geohot** [[00:56:17](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3377)]
Right?

##### **Geohot** [[00:56:18](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3378)]
Like that PR was clever, but not what the, the, the, the, the boundary was about.

##### **Geohot** [[00:56:25](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3385)]
Like, I don't want to use that like map graph thing anymore.

##### **Nimlgen** [[00:56:29](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3389)]
It's, it's kind of like low quality, like multi should just be a part of everything

##### **Nimlgen** [[00:56:33](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3393)]
else.

##### **Geohot** [[00:56:33](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3393)]
It should be processed the same.

##### **Geohot** [[00:56:39](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3399)]
Yeah.

##### **Geohot** [[00:56:40](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3400)]
The Python time one.

##### **Geohot** [[00:56:41](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3401)]
Haven't seen any PRS for that.

##### **Geohot** [[00:56:43](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3403)]
All the, the T flop jam.

##### **Nimlgen** [[00:56:45](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3405)]
That should be so easy.

##### **Nimlgen** [[00:56:46](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3406)]
Now someone can totally just do that.

##### **Geohot** [[00:56:49](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3409)]
It's like practically copy paste $300 copy paste.

##### **Geohot** [[00:56:57](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3417)]
Works over USB 3.0.

##### **Geohot** [[00:56:59](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3419)]
It's probably impossible.

##### **Geohot** [[00:57:01](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3421)]
That's why it's a thousand dollars.

##### **Geohot** [[00:57:04](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3424)]
No, no, no.

##### **Nimlgen** [[00:57:05](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3425)]
Some thousand dollar bounties are very possible.

##### **Nimlgen** [[00:57:15](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3435)]
Oh, if you got fast, all Mo and you want to merge that, there's a $300 bounty there

##### **Geohot** [[00:57:20](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3440)]
too.

##### **Geohot** [[00:57:20](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3440)]
If you can get 50% of the theoretical max.

##### **Geohot** [[00:57:23](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3443)]
So I don't know if the speed ups are going there too.

##### **Geohot** [[00:57:26](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3446)]
Yeah.

##### **Geohot** [[00:57:27](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3447)]
Being able to run a MOE models fast is a, is valuable to us.

##### **Nimlgen** [[00:57:34](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3454)]
Cool.

##### **Nimlgen** [[00:57:36](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3456)]
Anyone have anything else?

##### **Geohot** [[00:57:39](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3459)]
Yeah.

##### **Geohot** [[00:57:46](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3466)]
I don't know.

##### **Geohot** [[00:57:47](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3467)]
All right.

##### **Geohot** [[00:57:47](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3467)]
This has been meeting 97.

##### **Geohot** [[00:57:48](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3468)]
Thank you everyone.

##### **Nimlgen** [[00:57:49](https://www.youtube.com/watch?v=22O5E5aAnJU&t=3469)]
All right.
