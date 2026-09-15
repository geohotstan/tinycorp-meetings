# 2026-09-15 Meeting

### Meeting Agenda

**Time:** new meeting #37, 9/15 12pm Hong Kong time
- company update
- WMMA, PADTO
- LLaMA training
- GPT-OSS training
- CI
- CONTIGUOUS, CALL
- HCQ2
- bounties, comma, RDNA


### Audio

[Youtube Link](https://www.youtube.com/watch?v=sdXQQRk2BRc)

### Highlights

- **[Company Update](#geohot-000017)**: PNY GPU sales now require customer KYC/export-control paperwork; 100 MI300s delivered with circuit boards in progress; tinybox fan fixes are being sent to ~10 respondents.
- **[PADTO/WMMA](#chenyu-000139)**: PADTO is close to becoming a default BEAM action; remaining issues are mainly WMMA/tensor cores and BF16; WMMA should become more CALL-like instead of implicitly including LOCAL.
- **[LLaMA Training](#qazalin-000546)**: Latest run is 1:42; FlashAttention moved to FP8 with custom FP8 backward assembly, ~10% higher MFU than AITER’s FP8 forward; GPT-6 used VIZ tools to iterate assembly from ~600 TFLOPs to good performance.
- **[VIZ/Profiling](#qazalin-000735)**: VIZ now maps MXFP4 GEMM instructions to packets on CDNA; barrier/overlap execution model is still open; RDNA3 overlap bugs are fixed, but RDNA4 has a nondeterministic VALU bug.
- **[GPT-OSS](#wozeparrot-001336)**: Current run is at 2:14 and ~600 ms/step after throttling; target still needs improvement, and chilling the machine would hit target but is not a reliable plan.
- **[GPT-OSS Optimizations](#wozeparrot-001424)**: Fixed gradient/weight-gather transfers using FP32 instead of BF16, moved loss-to-CPU copy to the end, and ran two forward/backward passes per JIT to save ~30 ms/step.
- **[Scheduling Priority](#geohot-002033)**: Must schedule machines to meet the GPT-OSS deadline; two-machine LLaMA is a cool milestone but secondary, while two-machine GPT-OSS remains a stretch goal.
- **[CI](#chrism-002246)**: GARM runners now work with web-UI SSH; macOS/Metal runners and dnsmasq/CA caching work; GPU runners are still needed, and the 1Gb cache link may bottleneck.
- **[CONTIGUOUS/CALL](#geohot-003020)**: Removed CONTIGUOUS; COPY and LOAD are conceptually unified; refactor aims for late fusion after STOREs and CALLs, not just while ops are STAGEs.
- **[amd_call_matmul](#geohot-003208)**: Committed a readable `amd_call_matmul` using decorator-declared RANGEs; CALL captures RANGE scope and fusion can operate on CALLs, with RANGE/END/CALL spec close to right.
- **[HCQ2](#nimlgen-003901)**: Multi-machine HCQ2 works; classes were removed in favor of default Buffer/allocator; RDMA uses SDMA, and LLaMA all-reduce is ~150 ms and under investigation.
- **[HCQ2 Migration](#geohot-004220)**: Geohot praised the two-machine run and owes a bonus; if not chasing two-machine GPT-OSS, priority is moving Metal/CL/CUDA off HCQ1 rather than optimizing HCQ2 further.
- **[INS is CALL](#geohot-005238)**: The `INS is CALL` draft PR is the main prerequisite for assembly backends; CALL bodies at `src[0]` should enable lambda-application loopback tests and adding a `.body` helper.
- **[Bounties](#chenyu-005853)**: Bounties have mostly produced spam; the only potentially useful submission so far is the GPU Ocelot work.

### Transcript
##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=0)]
Great. Okay, welcome everyone. Let's get started. It's a very small meeting. I will change the event time starting next week. We'll start with the company update.

##### **Geohot** [[00:00:17](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=17)]
The most annoying thing is that we now have to do KYC for our customers with PNY. We have to submit paperwork to PNY when we sell GPUs, so this is annoying. We'll have to think about what we want to do to deal with that, but it seems like they're getting more serious about these export controls.

There's also progress on the MI300 project. We have 100 of them delivered.

##### **Chenyu** [[00:01:00](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=60)]
Great.

##### **Geohot** [[00:01:03](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=63)]
We're working on making circuit boards for those.

##### **Chenyu** [[00:01:08](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=68)]
I also saw that we're sending out fan fixes for tinyboxes.

##### **Geohot** [[00:01:13](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=73)]
Oh, yeah. We're sending out fan fixes. I wasn't on the emails, but I think about ten people replied that they wanted them. We'll be sending them out soon.

##### **Chenyu** [[00:01:27](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=87)]
Great. Anything else for the company update?

##### **Geohot** [[00:01:35](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=95)]
No.

##### **Chenyu** [[00:01:39](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=99)]
Okay, moving on. The first item is mine. I want to get PADTO working, meaning that it becomes a default action in BEAM's search space. It isn't one now. I got through a bunch of fixes here and there. A lot of them were weird cases where invalid values weren't handled properly.

Most of the remaining issues are with WMMA and tensor cores. I'm trying to understand the tensor-core code because some of it is really old and weird. I cleaned up a bunch of it and removed some issues. I probably have another two or three fixes to go, and then it should be fine.

We also have some weird BF16 cases. I have an open change for that. Our dtype support is kind of random because it isn't really done the correct way; we do it based on the machines we have. It is what it is.

Part of this, which I think we can discuss later with the RDNA work, is that WMMA should look more like an instruction inside a CALL. Instead of having `Ops.WMMA`, we should wrap it inside a CALL.

##### **Geohot** [[00:03:30](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=210)]
I very much agree with that.

##### **Chenyu** [[00:03:31](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=211)]
I also want that to work more like assembly, so we'll see how that goes.

##### **Geohot** [[00:03:41](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=221)]
Where I see WMMA going is that right now it implicitly includes things about LOCAL, which it shouldn't. You can imagine WMMA becoming a CALL where one of the parameters is the warp, because it has to operate across the warp.

##### **Chenyu** [[00:04:03](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=243)]
Yeah. I have a model in mind that's probably similar. We'll discuss it more with RDNA. This was based on the brief exchange about the code in the assembly channel.

##### **Geohot** [[00:04:22](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=262)]
You can imagine what the WMMA CALL is. Source zero is the actual full description of the WMMA. Even though it never executes separately, it is one instruction. Then you can see how it gets substituted and handled correctly.

##### **Chenyu** [[00:04:36](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=276)]
Yes, I have a prototype there. First, I think it's generally nice to clean up the WMMA code. Some of it is pretty old and pretty bad.

After that, I think PADTO is good to go. With this, I'm also cleaning up symbolic rules that were arbitrary and bad. Many of them aren't really tested. Hopefully, after this pass, everything will be better and we can enable PADTO as a BEAM action. That's pretty much it.

##### **Chenyu** [[00:05:36](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=336)]
Okay, with that we can move on. Next is LLaMA.

##### **Qazalin** [[00:05:46](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=346)]
1:42 is our latest run. This is the comparison with last week. I moved all of our FlashAttention to FP8, which NVIDIA did in BF16. We have our own assembly for the FP8 backward pass; there was no public assembly. It's already at a higher MFU, about 10% higher than what AITER could do with the FP8 forward pass.

I think GPT-6 can finally write assembly and use our VIZ tools to make it faster.

##### **Geohot** [[00:06:30](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=390)]
Was it actually using `VIZ=2`? That would be incredible.

##### **Qazalin** [[00:06:36](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=396)]
Yeah. I have the whole conversation recorded. I'm going to go through it, review what's missing in VIZ, and see how we can improve it. I can share the conversation too. It was about a half-day Codex session to get it there.

##### **Geohot** [[00:06:53](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=413)]
That's a huge advantage we have over other people. If it can just one-shot the assembly, everyone can use GPT-6 and one-shot the assembly. But if it can actually use `VIZ=2` and close the feedback loop, we should really be able to have the fastest GEMMs.

##### **Qazalin** [[00:07:11](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=431)]
I watched it go from something very bad, around 600 teraflops, to something very good. It iterated and took time to do it. I think we can get the loop working.

##### **Geohot** [[00:07:32](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=452)]
That's the real BEAM search.

##### **Qazalin** [[00:07:35](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=455)]
Yeah. I can share what our VIZ looks like now for the MXFP4 GEMM. There is no `ALUEXEC` packet in SQTT for CDNA, but you can derive the execution interval from the documented duration of the MFMA instruction. We now have code that maps instructions to packets like it does for RDNA, so it's becoming more and more usable.

I still don't have a good execution model for barriers or for what can overlap. You can see things overlapping in SIMD 2, for example. I still don't know which things can issue at the same time, so that's an open problem I need to figure out. We're starting to model it better.

##### **Geohot** [[00:08:43](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=523)]
I'm not sure about issuing, but have we at least fixed all the overlap bugs on RDNA3 and RDNA4? The ALU can never be doing two things at the same time.

##### **Qazalin** [[00:08:53](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=533)]
RDNA3 is completely fixed and should never have overlaps. RDNA4 has a very weird, nondeterministic VALU bug that I haven't been able to track down. Even `rocprof` shows the same overlap, which is nonsense. It's still an open question.

##### **Geohot** [[00:09:18](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=558)]
If `rocprof` does it too, maybe it's hardware or RTL.

##### **Qazalin** [[00:09:23](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=563)]
Yeah, it could be. But for CDNA, I'm very certain that it's a modeling issue. Also, on RDNA we can only trace one SIMD, while on CDNA we can trace four SIMDs. That's very nice.

##### **Geohot** [[00:09:44](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=584)]
The SIMDs have a different meaning on CDNA. They're more like the warps on RDNA.

##### **Qazalin** [[00:09:53](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=593)]
Yeah. I've also noticed that the MI350P machines, the H3 machines, don't scale perfectly to MI350X. Sometimes I get 50% MFU on H3, but even if I increase the workgroup count, I can only get about 40% on MI350X. It isn't always perfect 2x scaling, so be careful with that.

##### **Geohot** [[00:10:28](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=628)]
It's always easier to get higher MFU on a smaller GPU for the same matrix size. You should get perfect scaling if you double the matrix size, but if you don't, you won't get it. With the same matrix size, you'll always get worse utilization on an X than on a P.

##### **Qazalin** [[00:10:46](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=646)]
Yeah. That was one of the challenges. Moving forward, our target is 1:22. To get there, I need three things, which I also wrote in the channel: higher MFU for the GEMMs and FlashAttention kernels, lower idle time, and faster quantizers.

Here's the latest breakdown. Our idle time went up as the kernels got faster, so idle is a higher percentage than last week. There's 82 milliseconds of idle time. The quantizers also take a larger share than our FlashAttention forwards, so I need to fix them.

##### **Geohot** [[00:11:45](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=705)]
When you say idle, do you mean communication isn't overlapping, or is nothing happening on the GPU?

##### **Qazalin** [[00:11:54](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=714)]
SDMA is running, but there is no compute. It's waiting for SDMA.

##### **Geohot** [[00:12:02](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=722)]
We should be able to hide all of that latency perfectly.

##### **Chenyu** [[00:12:16](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=736)]
Is this with HCQ2?

##### **Qazalin** [[00:12:18](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=738)]
Yeah, I switched the new run to HCQ2.

##### **Chenyu** [[00:12:21](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=741)]
Both runs, or just the new one?

##### **Qazalin** [[00:12:27](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=747)]
The old one isn't HCQ2.

##### **Chenyu** [[00:12:31](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=751)]
Does changing to HCQ2 improve it?

##### **Qazalin** [[00:12:35](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=755)]
No.

##### **Chenyu** [[00:12:38](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=758)]
But it also isn't worse. Is it more stable?

##### **Qazalin** [[00:12:45](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=765)]
I didn't have issues with HCQ1 either.

##### **Chenyu** [[00:12:49](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=769)]
I see. Okay, anything else?

##### **Qazalin** [[00:13:02](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=782)]
I'm going to try merging more of this into master. Having a branch is annoying. The assembly I'm working toward is pretty long, so I'm hoping I can make it shorter and nicer before it gets to master. That's pretty much it.

##### **Chenyu** [[00:13:25](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=805)]
Sounds good. Next is GPT-OSS.

##### **Wozeparrot** [[00:13:36](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=816)]
We're at 2:14.

##### **Chenyu** [[00:13:41](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=821)]
Pretty close, but not at the target yet.

##### **Wozeparrot** [[00:13:50](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=830)]
This is 600 milliseconds per step. It's around 570 to 580 before the machine throttles, and then it goes to 600.

##### **Chenyu** [[00:14:16](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=856)]
What did you do to make it faster, and what else can we do to make it faster?

##### **Wozeparrot** [[00:14:24](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=864)]
I've been comparing against NVIDIA's single-node B200 submissions from MLPerf v6.0. We had some gradient transfers and weight-gather transfers that weren't using the correct dtype. The dtype was too large: the weights were BF16, but we were gathering them in FP32.

##### **Chenyu** [[00:14:55](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=895)]
Are those in the custom kernel or in kernels that we generate?

##### **Wozeparrot** [[00:15:01](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=901)]
They're in kernels we generate. This run also does two steps in one JIT, which seems to hide more work.

##### **Geohot** [[00:15:32](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=932)]
What do you mean by two steps in one JIT?

##### **Wozeparrot** [[00:15:40](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=940)]
We run two forward passes and two backward passes in one JIT capture.

##### **Geohot** [[00:15:46](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=946)]
Why would that be faster?

##### **Wozeparrot** [[00:15:48](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=948)]
There is some idle time that isn't hidden properly. This saved about 30 milliseconds per step.

##### **Geohot** [[00:16:00](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=960)]
Interesting. Should we do that for LLaMA?

##### **Wozeparrot** [[00:16:08](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=968)]
Do you want to try it with LLaMA?

##### **Geohot** [[00:16:12](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=972)]
Thirty milliseconds isn't nothing. I'm curious why this is happening. It shouldn't happen unless the communication is badly scheduled.

##### **Wozeparrot** [[00:16:28](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=988)]
There are some other things. The loss-to-CPU copy was getting scheduled in the middle of the graph, which caused some of this.

##### **Geohot** [[00:16:37](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=997)]
What's overlapping between the two steps?

##### **Wozeparrot** [[00:16:44](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=1004)]
You can overlap the next forward pass during the loss copy.

##### **Geohot** [[00:17:00](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=1020)]
I imagine you can also just avoid copying and printing the loss on the CPU for every JIT.

##### **Wozeparrot** [[00:17:18](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=1038)]
Yes. The loss copy also used to be between the forward and backward passes. Just moving it to the end already made things faster.

##### **Qazalin** [[00:17:19](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=1039)]
I've already done this for LLaMA too. It was also doing the loss copy mid-batch.

##### **Geohot** [[00:17:35](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=1055)]
Is this all on HCQ1?

##### **Wozeparrot** [[00:17:36](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=1056)]
Yes. I did try HCQ2, but it was significantly slower. I haven't tried it recently because my branch isn't fully rebased onto master, so I need to try it again.

##### **Chenyu** [[00:18:02](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=1082)]
In terms of percentage, how far are we from the target?

##### **Wozeparrot** [[00:18:09](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=1089)]
We're six minutes off the target.

##### **Chenyu** [[00:18:13](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=1093)]
Even if we just chill the machine?

##### **Wozeparrot** [[00:18:16](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=1096)]
If we chill the machine, it hits the target.

##### **Chenyu** [[00:18:18](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=1098)]
Really? Can we chill the machine?

##### **Geohot** [[00:18:27](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=1107)]
I don't know. Will San Diego get cooler?

##### **Chenyu** [[00:18:32](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=1112)]
Not in the next two weeks, I don't believe. Do we have anything else that can make it slightly faster?

##### **Wozeparrot** [[00:18:49](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=1129)]
We still have some differences from the B200 submissions. The main things are that we don't bucket our gradient copies, while they do, and we don't apply gradient sharding to everything, while they do.

##### **Chenyu** [[00:19:13](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=1153)]
Our plan is to shave off a little more time and get a faster machine.

##### **Wozeparrot** [[00:19:23](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=1163)]
Yep. Then we should have a good run this week.

##### **Geohot** [[00:19:29](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=1169)]
I don't think we should count on a faster machine.

##### **Wozeparrot** [[00:19:31](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=1171)]
Yeah, I'm not counting on one.

##### **Chenyu** [[00:19:38](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=1178)]
Or we can just blow some cool air. I wish. Or rent a machine.

##### **Geohot** [[00:19:48](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=1188)]
Renting a machine requires work on VF, which hasn't been done. Blowing cold air is also very hard because the amount of cold air you need is large.

It's probably easier to get the communication to overlap a little better. Do you have a breakdown of what's still taking time?

##### **Wozeparrot** [[00:20:20](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=1220)]
I've been focusing on different things, so I don't have a current breakdown. Both machines have been used for dual-machine LLaMA, so I haven't had much access.

##### **Geohot** [[00:20:33](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=1233)]
Let's make sure we schedule this well. We absolutely have to meet the GPT-OSS time. The two-machine LLaMA training is more like, "All right, cool, we did it."

##### **Qazalin** [[00:20:52](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=1252)]
I need the machines for LLaMA too.

##### **Chrism** [[00:21:00](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=1260)]
Which workload are we giving the San Diego nighttime to? There's about a ten-degree difference, right? Ten degrees Fahrenheit.

##### **Chenyu** [[00:21:11](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=1271)]
I think comma also trains more during the nighttime, so I don't know if it's really cooler.

##### **Chrism** [[00:21:22](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=1282)]
I can ask if we can get their dashboard.

##### **Chenyu** [[00:21:27](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=1287)]
The deadline is approaching, and I think we'll try both. We need to finish GPT-OSS and the two-machine training, so we'll have to schedule it. It sounds like we have a good idea for hitting the GPT-OSS target.

##### **Geohot** [[00:21:59](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=1319)]
We also have the stretch goal of two-machine GPT-OSS. We'll see what our two-machine LLaMA scaling gets to. If it looks like we can do it without much overhead, maybe we'll hit that too.

##### **Chenyu** [[00:22:18](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=1338)]
Cool. Definitely rebase so we don't get any surprises. Anything else?

##### **Wozeparrot** [[00:22:36](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=1356)]
No.

##### **Chenyu** [[00:22:38](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=1358)]
Okay, moving on. Next is CI.

##### **Chrism** [[00:22:46](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=1366)]
We've made good progress on getting all of the GARM stuff working. You can now SSH through the web UI into those runners, which is cool. I haven't exposed that to the internet yet, but if you tunnel your traffic through, you can see it running on TGW2. The details for accessing it are in the infra repo.

I also got macOS runners working. I have a run, but I need to figure out the right way to make a macOS image. The platform tests run. Obviously the Windows tests don't run, and the other failures are because the base image I used doesn't have LLVM. These are ephemeral VMs orchestrated through GARM.

Metal works too. It looks like the way GitHub does it, with a paravirtualized Metal device rather than a real GPU. I think it pretends to be an A18 or another mobile GPU, but it runs our tests. I just need to put LLVM in the image.

It actually looks much faster than GitHub if you look at the timings. We had to split macOS dev and Metal into two separate jobs on GitHub, but both would fit together in under three minutes on these runners. I haven't tested the CPU performance. My guess is that it's slower, but I'll double-check.

I also got caching working. We have a caching server that impersonates GitHub's content domain and `github.com`. We run `dnsmasq` on TGW2 to point those domains at the cache. We install a CA certificate, and the server creates a certificate for the requested URL. That all works.

The problem is that there's only a one-gigabit link between the computer running the VMs and the cache server, so it may not even be faster. We may need a faster link between them, or we could run a caching server on each VM host. That would also work, but it might be more complicated.

##### **Wozeparrot** [[00:26:21](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=1581)]
We would need a 10-gigabit switch.

##### **Geohot** [[00:26:27](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=1587)]
Or just do it point-to-point.

##### **Chrism** [[00:26:41](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=1601)]
I don't know if the Mac can do 10-gigabit Ethernet, but I'm sure we can figure something out.

The other frustrating thing is that you can't run a VM inside the Mac VM. Previously, I built the images inside a VM, but you can't do that with the Mac, so I need to find a good way to build the Mac images.

I also updated the test timeout. It now uses `faulthandler.dump_traceback_later`, which respects the GIL. It prints `Timeout` with the duration and an exclamation mark, so you no longer have to look for `Aborted` to tell that a test timed out.

I still need to add GPU runners. That's probably the last part of this project. Then we'll have GPUs. I don't know whether we'll be able to virtualize the comma setup. I'm not sure how passing through KGSL would work or how much overhead it would have, so we'll see.

I was also seeing some CI failures on the Mac that might be related to the number of USB resets. There was a libusb issue about dereferencing an object that didn't have a reference count. I don't know exactly what it was. If we can run all of that in a virtual machine, maybe that would solve some of the problem.

I'm a little worried that this is macOS flakiness from resetting USB many times. If you reset USB a thousand times, it's bound to fail eventually, which would be frustrating. That's most of the CI update.

##### **Geohot** [[00:28:59](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=1739)]
Are you saying that after it resets USB too many times, there's no way to recover without rebooting the machine?

##### **Chrism** [[00:29:05](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=1745)]
I don't know. I haven't investigated enough to know exactly. I just noticed it happening on Tiny Mac 1. Let me see if I can find it.

##### **Geohot** [[00:29:13](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=1753)]
Linux has weird behavior with this too, where it uses up all the USB addresses or something. It might just be something that we're not releasing correctly.

##### **Chrism** [[00:29:25](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=1765)]
It might be. It just looks like a libusb error, though. I don't know enough about Mac debugging to know whether I can look in `dmesg` and see something obvious.

##### **Geohot** [[00:29:42](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=1782)]
Just ask AI now.

##### **Chrism** [[00:29:44](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=1784)]
Yeah, I'll ask it. When I SSHed into the machine, it seemed to reset the device properly. I'll try to reproduce it. I think that's pretty much everything.

##### **Chenyu** [[00:30:12](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=1812)]
Sounds good. Next is your stuff.

##### **Geohot** [[00:30:20](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=1820)]
I got rid of CONTIGUOUS. CONTIGUOUS is just nothing, and we had a bunch of weird cases for it. The way we used CONTIGUOUS was basically to say, "Create a new buffer here," which is identical to how we use COPY. Both are somewhat wrong in the long term, but for now I think it will be much easier to do the rangeify refactors if we think of them as the same thing.

COPY and LOAD are also really the same thing. The only difference is that LOAD changes the address space and COPY changes the device. They both basically mean a STORE to an anonymous buffer. You could imagine rewriting LOADs in assembly backends as STOREs to declared registers. Then you wouldn't even have to support LOAD.

##### **Geohot** [[00:31:18](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=1878)]
That's getting done. I've been trying to use the AIs to help with the qualify refactor, like the devectorizer refactor, but they aren't useful because they don't think about things from first principles.

The basics of qualify are straightforward. Much of qualify's complexity only exists because rangeify can't do simplifications that it should be able to do. For example, qualify has a lot of logic to avoid making extra copies from CALLs to custom kernels, but you should be able to merge those much later. That's what I've been working on.

##### **Geohot** [[00:32:08](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=1928)]
Yesterday I committed `amd_call_matmul`. I think it's the most readable version yet. It's handwritten like `amd_copy_matmul`, but it uses a decorator to declare the RANGEs.

I played with changing the semantics so all RANGEs would be ended by the CALL, but it turns out you don't need to. I think we have the right spec now. You can imagine RANGEs on the arguments of a CALL being captured by the CALL, which provides scoping, and then having END after the CALL.

Kernel fusion would then take two consecutive CALLs, each with a set of RANGEs and an END, and fuse their RANGEs. We do this now in rangeify with substitution, but the substitution makes us traverse the entire graph again. That's really slow, and we ended up writing a bunch of hacks for it. I'm getting back to Hong Kong on Friday, and for the next few months I'm going to sit down and work through every one of these cases.

##### **Geohot** [[00:33:24](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=2004)]
There is so much duplicated code in qualify, prepare, and rangeify that only exists because other things aren't doing their jobs as well as they could. We should be able to do incredibly late fusion. These transformations should be almost lossless. Not lossless to the point that we could recover the movement ops, but enough that we could still do fusion after inserting STOREs and CALLs.

Right now, we can only do fusion while things are still STAGEs. As soon as we rewrite them to STORE, it's over. We need to stop thinking that way. Imagine two complete kernels in the graph, and then imagine being able to look into them and still perform kernel fusion. Kernel fusion shouldn't have to happen early.

My classic tinygrad analogy is an hourglass with a thick middle. A lot of things in the front end come down to the spec. Then there's middleware that processes things within the spec, followed by instruction selection on the back end. Kernel fusion should be part of the thick middle. There shouldn't be a special stage; there should just be STOREs and RANGEs that we can inspect.

Imagine one kernel storing to a buffer and the next loading from it. If the indexing of that STORE and LOAD is the same, you can make the buffer small and store to the same buffer repeatedly, as long as the two CALLs run serially inside the same loop.

##### **Geohot** [[00:35:10](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=2110)]
That's what I've been working on. I don't think there are many patterns here, and I think we're getting close with the spec. I added COPY to the spec and removed CONTIGUOUS from it.

RANGE and END seem very good. I had a long conversation with GPT about whether I wanted CALL to end a RANGE, and I don't. It would help a little with scoping. It would be nice if the RANGEs were scoped as arguments on the CALL, because then they wouldn't need numbers; their positions on the CALL would tell you their scope. But giving RANGEs numbers isn't a big deal, and it all works within the current spec.

I committed `amd_call_matmul`, and I have another version that actually creates the CALL ops. It all works. There were a few hacks for weak dtypes that we need to think about, along with whether CALLs used as syntactic sugar should be allowed to have returns.

Right now, returns from CALLs use unbound buffers as positional arguments, followed by a STORE inside the CALL body. We could add syntactic sugar so you don't need the STORE and can just return the value. It's much better than all the tuple machinery that's been gone for a while.

##### **Geohot** [[00:36:30](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=2190)]
The key thing to realize about the new rangeify is that qualify is simple and rangeify is simple. Qualify pulls out the PARAMs of bound BUFFERs. Rangeify does the movement-op processing. What's missing is the simplification layer, but I think that can be simple too.

If you do it well, qualify and rangeify become much simpler because you can say, "Whatever, I'll simplify that later." Trying to simplify things prematurely is responsible for a lot of the current complexity in those stages.

##### **Geohot** [[00:37:16](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=2236)]
Also, tinygrad shouldn't be slow. Why does it take a minute to start an LLM? It shouldn't. It used to be slow because we compiled kernels serially, but now we compile them in parallel. The remaining time is all rangeify and scheduling-graph overhead. That should be fast too.

You want to decide early where to insert CONTIGUOUSes, STAGEs, or whatever you call the points that create buffers. You can be liberal and insert a buffer anywhere that seems reasonable, then fuse them later because that fusion is cheap.

Check out `amd_call_matmul` and let me know whether the syntax makes sense. I think it's considerably easier to read than `amd_copy_matmul`, and it isn't hypothetical; the example actually works.

##### **Chenyu** [[00:38:14](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=2294)]
Okay. I'll have AI explain this to me later.

##### **Geohot** [[00:38:21](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=2301)]
Go through it. I think it's actually good. I tried using `with` blocks, but you can't quite use them because there's no way to return something from a `with` block. Instead, you can define the functions inside and capture everything in the closure. It's nice.

##### **Chenyu** [[00:38:42](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=2322)]
Cool. Looks good. Anything else?

##### **Geohot** [[00:38:52](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=2332)]
No.

##### **Chenyu** [[00:38:55](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=2335)]
Okay. Next is HCQ2.

##### **Nimlgen** [[00:39:01](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=2341)]
We have multi-machine working now. This week I've also been doing cleanups. I removed all the classes from HCQ2, so it now uses the default `Compiled` class and the default host allocator, which is shared by NPY, PYTHON, and CPU.

The whole RDMA path in HCQ2 is controlled by SDMA. When you need to make a copy, SDMA copies the descriptor into the RDMA queue and launches the RDMA operation.

I'm still investigating the speed. The all-reduce in the LLaMA run currently takes about 150 milliseconds, which looks high. Based on the bandwidth calculation, it should take about half that, so I'm still looking into it.

##### **Nimlgen** [[00:40:44](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=2444)]
Before that, I wanted to explain the future direction. It's currently implemented on the old Remote layer. Now that I have the training run, I'll start optimizing it.

I also want to remove the MMU setup from AMD and NV. I think we can use a static mapping on each machine. At least for now, because we still need host memory, we can pre-map every GPU and some amount of host memory and send the page table once. That should help startup time too.

##### **Geohot** [[00:41:45](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=2505)]
Unless there are other reasons to do that, I wouldn't worry too much about that optimization. You're proposing that all the GPUs share the same page-table mapping, right?

##### **Nimlgen** [[00:41:55](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=2515)]
Yeah.

##### **Geohot** [[00:41:58](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=2518)]
It's cool, but is everything moved over to HCQ2?

##### **Nimlgen** [[00:42:07](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=2527)]
No. The backends that HCQ1 didn't cover are still left.

##### **Geohot** [[00:42:20](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=2540)]
By the way, great work getting the run done. I owe you a bonus.

I don't think we should spend time optimizing it if we're not going to hit the two-machine GPT-OSS target. I saw the link you sent, and it looked like the scaling was worse than one, as though it was slower than a single machine. Is that still true, or was there something wrong with that run?

##### **Nimlgen** [[00:42:56](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=2576)]
The step time is about 1.5x better, so we have roughly 50% scaling.

##### **Geohot** [[00:43:10](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=2590)]
Then why was the total wall time 2:03?

##### **Nimlgen** [[00:43:16](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=2596)]
That was the startup time and the BEAM search.

##### **Geohot** [[00:43:24](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=2604)]
Why wasn't the BEAM search cached?

##### **Nimlgen** [[00:43:28](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=2608)]
It was just my first run.

##### **Geohot** [[00:43:31](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=2611)]
Okay, you just didn't have a cached BEAM search. That's easy. I'm already pretty happy with our time. I'd be fine submitting that because we have no speed requirement, then putting the time into moving everything off HCQ1. That second step included about 30 minutes of BEAM search.

When you get to Hong Kong, I want to work on specifying on a CALL where something runs. When you say you're using the SDMA engine to copy a buffer, we need to be able to interchange freely between running that copy on the SDMA engine and running it on the CUs. Right now, we don't have a good way to do that. We just have hacks where a COPY op means SDMA and the absence of one means CUs.

We need a way to say, "Copy from this buffer to that buffer, both on `AMD:1`, but use the CUs on `AMD:2` to do it." You can see how it could be done.

What remains to clean up in HCQ1, and when can we delete all that code?

##### **Nimlgen** [[00:45:27](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=2727)]
We deleted HCQ1 from the main repository; it's in `extra`. I can remove a lot of graph logic if I switch Metal, CL, and CUDA over.

##### **Geohot** [[00:45:45](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=2745)]
Once you switch Metal, CL, and CUDA, is there anything left outside HCQ2?

##### **Nimlgen** [[00:45:53](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=2753)]
Those are the non-HCQ backends right now.

##### **Geohot** [[00:46:15](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=2775)]
We want to move all of them to HCQ2. HCQ2 needs to be able to express Metal, CL, and CUDA, though I'm not completely sure what that means. The important part is that we no longer have classes like `HCQBuffer`; it's just `Buffer`.

##### **Nimlgen** [[00:46:37](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=2797)]
That part is already in master.

##### **Geohot** [[00:46:44](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=2804)]
But how is it in master if CUDA isn't on HCQ2? We shouldn't be allowed to have backends that aren't HCQ2.

##### **Nimlgen** [[00:46:56](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=2816)]
The `Buffer` used to have all these subtypes that held backend information. Now that information is all in `Buffer`. CUDA returns its CUDA pointer through the storage encapsulated by `Buffer`, so it still works. But I'll switch those backends to HCQ2. It should work.

##### **Geohot** [[00:47:33](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=2853)]
Why do you think you're getting only 50% of the network bandwidth?

##### **Nimlgen** [[00:47:42](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=2862)]
Ideal scaling is obviously 2x, but we're getting 1.5x when comparing one machine with two machines.

##### **Geohot** [[00:47:58](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=2878)]
That's for the whole LLaMA trainer. What is the all-reduce time and bandwidth?

##### **Nimlgen** [[00:48:11](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=2891)]
It was good. I'll post the numbers because I don't remember them, but all links were utilized at full speed. Maybe I can tweak the algorithm a bit.

##### **Geohot** [[00:48:31](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=2911)]
If there's a bottleneck, we should fix it. But if we're getting a good all-reduce time, this is the same generic problem we have across tinygrad: scheduling between compute and communication.

##### **Nimlgen** [[00:48:57](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=2937)]
There may be one limitation, but I need to profile it. For RDMA, both sides currently have to issue send and receive operations. We could potentially use a one-sided write so only one RDMA side needs to issue it, but then it isn't obvious how to signal completion.

We could do it NVIDIA-style, or USB-style, by sending four bytes at the end to mark the transaction complete. That's a lot of logic, though. When I profiled it with Mellanox, the latency for the current approach wasn't that high.

##### **Geohot** [[00:49:56](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=2996)]
You mean the same trick I used on USB: have the SDMA engine or compute engine poll for a few bytes?

##### **Nimlgen** [[00:50:06](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=3006)]
Yeah.

##### **Geohot** [[00:50:15](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=3015)]
We should think about this from first principles: how we want synchronization to work in general as we push further. Right now, we have almost ad hoc scheduling between SDMA and the GPUs, but it should be much more flexible.

We're using one timeline signal through the whole thing. Maybe that's fine, or maybe we want more fine-grained synchronization. We'll have to look at the bottlenecks.

##### **Chenyu** [[00:51:02](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=3062)]
Also, I reverted one of your latest changes because it had bugs.

##### **Nimlgen** [[00:51:07](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=3067)]
Yeah, I saw that.

##### **Chenyu** [[00:51:11](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=3071)]
Cool. Anything else?

##### **Nimlgen** [[00:51:20](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=3080)]
No.

##### **Chenyu** [[00:51:22](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=3082)]
Okay. Comma and RDNA, are we happy?

##### **Chrism** [[00:51:33](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=3093)]
I believe so. I noticed they bumped tinygrad and then reverted the bump. But I know Harald is working on removing `compile_modeld.py` entirely and moving that work into tinygrad, so I imagine they're aware of the issue.

I've given them ample opportunity to complain to me about any problems they might be having, and I haven't heard any complaints. It sounds like something they're trying to fix on their end.

##### **Chenyu** [[00:52:09](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=3129)]
I also see his draft PR to update the compile scripts. That would be nice.

##### **Chrism** [[00:52:20](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=3140)]
Yeah, I'm looking forward to that.

##### **Chenyu** [[00:52:28](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=3148)]
Any comments on the assembly backend?

##### **Geohot** [[00:52:38](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=3158)]
I see an `INS is CALL` draft PR. I think that's the main thing we have to land first.

That first line is a NOOP. That might be fine. I see what the NOOP is doing. What happens if the CALL is opaque and we don't actually have a body? A NOOP is like a fake CALL body.

The real test for this, Nim and Raine, if you ever listen to this, is to do lambda application of the CALLs and make sure the result is still the correct program. This makes the transition to assembly reversible. We perform instruction selection and create all these CALLs, but if you lambda-apply them by removing the CALLs and substituting their bodies back into the graph, you should get a functioning program again.

We can make that an end-to-end loopback test for every assembly backend. It would be very good at finding bugs.

Do people understand what `INS is CALL` means?

##### **Chenyu** [[00:54:38](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=3278)]
Kind of.

##### **Geohot** [[00:54:44](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=3284)]
On the `arg` of the CALL, we'll have the instruction encoding: how you actually emit it on the processor. But in the body of the CALL, at source zero, we have an implementation of that instruction. Clearly every instruction can be implemented, because that's how our RDNA emulator works.

The RDNA emulator goes even further and loads from and saves to VGPRs. This version would be without explicit VGPRs. It would just have PARAMs that can come from other instructions or wherever the register value originates.

##### **Chenyu** [[00:55:20](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=3320)]
Why is it source zero?

##### **Geohot** [[00:55:24](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=3324)]
Because it's the CALL body. A CALL has its body at source zero and its arguments from source one onward.

##### **Chenyu** [[00:55:33](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=3333)]
But it isn't really a source, right? I don't know, call it `body` or whatever. Sometimes this is difficult. We have a lot of code that reads `src`, and `src` can be segmented into as many as three different regions. We also have weird index maps that identify which region each source belongs to.

##### **Geohot** [[00:56:19](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=3379)]
There are two things we can do to improve that. One is to use syntactic sugar that treats things like algebraic data types. We should add one now: a helper property called `body` in `ops.py`. It would assert that the op is a CALL and return `src[0]`. Everywhere that currently accesses `src[0]` could access `.body` instead. That effectively gives us algebraic data types and type safety.

##### **Chenyu** [[00:56:47](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=3407)]
That might be a good start, but there are also cases that use the slice from one onward. Maybe it's fine.

##### **Geohot** [[00:57:00](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=3420)]
We should never have ops with multiple variable-length segments. Think about Python arguments: you can have fixed arguments and then `*args`, which consumes the remaining arguments, but you can't have two separate `*args` groups.

I look at the spec a lot, and I don't think there's anything wrong with it. We just need syntactic sugar to make the code easier to read. We could even make direct access illegal or rename it `_src`.

What's really bad is a structure where the first M sources mean one thing, the next N mean another, and `arg` tells you the value of M. That's when it gets bad, but we don't have anything like that.

##### **Chenyu** [[00:58:00](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=3480)]
That's very bad, and we shouldn't have it. I think what we have is fine. The issue may be that we're changing the spec, so the numbered source fields change sometimes. Once the spec has stabilized and is correct, we can add whatever syntactic sugar we want.

##### **Geohot** [[00:58:24](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=3504)]
I'm already in favor of adding `.body`. I don't love `.args`, because it's too easy to confuse with `.arg`.

##### **Chenyu** [[00:58:38](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=3518)]
Definitely don't reuse a name to mean different things. That would be even more confusing, including for AI.

##### **Geohot** [[00:58:46](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=3526)]
Okay. `.body` is fine. We can add that now. I'll let you decide.

##### **Chenyu** [[00:58:53](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=3533)]
Cool. We'll start with `.body`. I think this is much better. Let's hope assembly will be nicer soon.

On bounties, I don't think this has been useful at all.

##### **Geohot** [[00:59:17](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=3557)]
I just closed the issue that was the source of all those associative-scan PRs. There was an issue saying there was a bounty, and people had their AI agents look through the issues. It was all spam.

##### **Chrism** [[00:59:36](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=3576)]
Makes sense.

##### **Geohot** [[00:59:39](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=3579)]
I don't spend much time on it, maybe three minutes a day closing PRs, so it isn't a big deal. But so far all we've gotten is spam. The only remotely good thing we've gotten is the GPU Ocelot submission. Let me see how that looks.

I think we'll get something useful out of the GPU Ocelot work.

##### **Chenyu** [[01:00:09](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=3609)]
Okay, sounds good. I think that's it for this meeting. Anything else?

I think we'll stick to this time for a while before we change it again.

##### **Geohot** [[01:00:32](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=3632)]
Yeah. Thanks for moving it. Sorry, I was so tired last night.

##### **Chenyu** [[01:00:36](https://www.youtube.com/watch?v=sdXQQRk2BRc&t=3636)]
No problem. That's it for this meeting. Thank you, everyone. See you next week. Bye.
