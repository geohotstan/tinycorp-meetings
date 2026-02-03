# 2025-11-04 Meeting

### Meeting Agenda

**Time:** 9am Monday San Diego time, 1am Hong Kong time
- CDNA4/RDNA3 SQTT in VIZ, same view as RGP
- apple usb gpu without SIP bypass. i bought 3x 5060 for mac CI machines
- why is progress on tinykittens so slow? if it can't do a SOTA gemm, we should look elsewhere
- LLaMA trainer using custom_kernel to get memory usage to acceptable place, figure out what kernels we need to write
- openpilot regressions
- other bounties

### Audio

[Youtube Link](https://www.youtube.com/watch?v=gmY_RjZsYys)

### Highlights

- **[CDNA4/RDNA3 SQTT in VIZ](#chenyu-000031)**: The SQTT (Shader Quality and Thread Trace) table is now merged and viewable in VIZ, showing detailed instruction-level data like cycles, stalls, and latency. The next steps are to match the latency hiding metrics of AMD's RGP profiler and move the SQTT decoder into the main tinygrad repository.
- **[Apple USB GPU CI without SIP](#sieds-lykles-000857)**: To get the Apple USB GPUs working on CI machines without disabling System Integrity Protection (SIP), a signed binary is required to allow Python to connect to the driver kit. The team will also set up three new 5060 GPUs for the Mac CI machines.
- **[LLVM Pipe Support](#chenyu-001104)**: With real hardware now available for Mac CI, the team discussed removing the LLVM pipe software renderer. The consensus is to move the code into a test-only fixture rather than deleting it, which cleans up the main code path while preserving hardware-independent CI tests.
- **[tinykittens Performance](#chenyu-001502)**: Progress on tinykittens is considered slow as it has not yet achieved state-of-the-art GEMM performance, particularly on consumer GPUs like the 4090. The focus is shifting from optimizing GEMM to implementing a flash attention kernel.
- **[Custom Kernels for LLaMA Trainer](#chenyu-001928)**: To reduce the memory footprint of the LLaMA trainer, custom kernels are necessary. The key kernels needed are flash attention forward and backward. Writing the softmax backward component as a single kernel in UOps is the current challenge.
- **[Openpilot Regressions](#sieds-lykles-002253)**: Two regressions are under investigation: an ONNX model parsing failure, which is likely due to a change in how comma.ai serves LFS files, and a performance regression caused by the removal of a block reordering optimization in the new linearizer.
- **[Clan2Py Bounty Update](#chenyu-002709)**: The bounty to generate Python bindings from C headers is progressing. Remaining tasks include handling Objective-C, resolving a Windows issue, and fixing MyPy errors. A potential switch from MyPy to the faster and stricter Pyre type checker is being considered.
- **[FP8 BERT Training Bounty](#chenyu-003217)**: A contributor is working on training BERT with FP8. Initial tests show a ~5% speed improvement, but the training loss stalls. The immediate goal is to fix the convergence issues on a single GPU.
- **[Whisper Bounty Update](#chenyu-003639)**: For the Whisper bounty, the recommended next step is to create a functional web demo. This would allow the initial implementation to be reviewed and merged, with support for longer audio files to be added later.
- **[Guidance on Bounties (Tensor.pool, PyTorch)](#chenyu-003853)**: Chenyu provided guidance for bounty hunters: for the PyTorch backend, contributors must re-enable the currently skipped CI tests to prove their fix works. For the `tensor.pool` removal, the goal is to unify the two convolution code paths without regressing performance, not just remove the `if` block.
- **[Future Meetings and CommaCon](#chenyu-003956)**: The weekly meeting time will likely remain the same going forward. TinyCorp will have a booth at the CommaCon conference on Saturday, and several team members plan to attend.

### Transcript
##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=gmY_RjZsYys&t=0)]
So I think we don't have George today.

##### **Chenyu** [[00:00:04](https://www.youtube.com/watch?v=gmY_RjZsYys&t=4)]
So here's a list of all the things that he left.

##### **Chenyu** [[00:00:08](https://www.youtube.com/watch?v=gmY_RjZsYys&t=8)]
I think we can go through this and then add things

##### **Chenyu** [[00:00:15](https://www.youtube.com/watch?v=gmY_RjZsYys&t=15)]
for probably the short meeting.

##### **Chenyu** [[00:00:18](https://www.youtube.com/watch?v=gmY_RjZsYys&t=18)]
So let's start it.

##### **Sieds Lykles** [[00:00:23](https://www.youtube.com/watch?v=gmY_RjZsYys&t=23)]
A little SQTT stuff in this.

##### **Chenyu** [[00:00:31](https://www.youtube.com/watch?v=gmY_RjZsYys&t=31)]
I merged the SQTT table in this.

##### **Chenyu** [[00:00:35](https://www.youtube.com/watch?v=gmY_RjZsYys&t=35)]
So right now if you run with viz equals one, you can actually see the SQTT stuff.

##### **Chenyu** [[00:00:42](https://www.youtube.com/watch?v=gmY_RjZsYys&t=42)]
I'll post a picture of it on the channel.

##### **Chenyu** [[00:00:46](https://www.youtube.com/watch?v=gmY_RjZsYys&t=46)]
So but it's basically just whatever our decoder gave right now.

##### **Chenyu** [[00:00:54](https://www.youtube.com/watch?v=gmY_RjZsYys&t=54)]
That's it.

##### **Sieds Lykles** [[00:00:55](https://www.youtube.com/watch?v=gmY_RjZsYys&t=55)]
Yeah.

##### **Chenyu** [[00:00:55](https://www.youtube.com/watch?v=gmY_RjZsYys&t=55)]
Yeah.

##### **Chenyu** [[00:00:56](https://www.youtube.com/watch?v=gmY_RjZsYys&t=56)]
So you can see

##### **Chenyu** [[00:00:58](https://www.youtube.com/watch?v=gmY_RjZsYys&t=58)]
how many actual cycles each instruction takes,

##### **Chenyu** [[00:01:04](https://www.youtube.com/watch?v=gmY_RjZsYys&t=64)]
how much it stalled and how much there was latency.

##### **Chenyu** [[00:01:08](https://www.youtube.com/watch?v=gmY_RjZsYys&t=68)]
So latency is like the difference between

##### **Sieds Lykles** [[00:01:11](https://www.youtube.com/watch?v=gmY_RjZsYys&t=71)]
decoding the instruction and waiting for resources

##### **Chenyu** [[00:01:14](https://www.youtube.com/watch?v=gmY_RjZsYys&t=74)]
to be able to actually use the instruction, like waiting for the register or whatever.

##### **Chenyu** [[00:01:21](https://www.youtube.com/watch?v=gmY_RjZsYys&t=81)]
So yeah, I think next steps after this are to match the

##### **Chenyu** [[00:01:26](https://www.youtube.com/watch?v=gmY_RjZsYys&t=86)]
AMG profiler.

##### **Chenyu** [[00:01:29](https://www.youtube.com/watch?v=gmY_RjZsYys&t=89)]
Is to figure out how we're going to show the latency hiding metrics.

##### **Chenyu** [[00:01:39](https://www.youtube.com/watch?v=gmY_RjZsYys&t=99)]
And yeah.

##### **Sieds Lykles** [[00:01:45](https://www.youtube.com/watch?v=gmY_RjZsYys&t=105)]
It's pretty much it on that side.

##### **Chenyu** [[00:01:48](https://www.youtube.com/watch?v=gmY_RjZsYys&t=108)]
And if Nemo-Chan wants to add anything.

##### **Chenyu** [[00:01:59](https://www.youtube.com/watch?v=gmY_RjZsYys&t=119)]
No, nothing to it, to SQTT.

##### **Chenyu** [[00:02:02](https://www.youtube.com/watch?v=gmY_RjZsYys&t=122)]
So for PMC, I think that's not the priority for now.

##### **Chenyu** [[00:02:07](https://www.youtube.com/watch?v=gmY_RjZsYys&t=127)]
But actually counters differ a lot between GFX 9 and GFX 11, 12.

##### **Chenyu** [[00:02:17](https://www.youtube.com/watch?v=gmY_RjZsYys&t=137)]
So yeah, just to warn you.

##### **Sieds Lykles** [[00:02:20](https://www.youtube.com/watch?v=gmY_RjZsYys&t=140)]
Let me see.

##### **Chenyu** [[00:02:22](https://www.youtube.com/watch?v=gmY_RjZsYys&t=142)]
Yeah.

##### **Chenyu** [[00:02:25](https://www.youtube.com/watch?v=gmY_RjZsYys&t=145)]
I'm just trying to keep in mind that this is going to be a pretty busy session.

##### **Chenyu** [[00:02:28](https://www.youtube.com/watch?v=gmY_RjZsYys&t=148)]
Yeah, go ahead.

##### **Chenyu** [[00:02:29](https://www.youtube.com/watch?v=gmY_RjZsYys&t=149)]
Does this work for both CDNA4 and RDNA3 now?

##### **Chenyu** [[00:02:36](https://www.youtube.com/watch?v=gmY_RjZsYys&t=156)]
I think, I mean, yeah, I think.

##### **Sieds Lykles** [[00:02:42](https://www.youtube.com/watch?v=gmY_RjZsYys&t=162)]
So that kind of works for both, and I think UI as well.

##### **Chenyu** [[00:02:51](https://www.youtube.com/watch?v=gmY_RjZsYys&t=171)]
I was thinking post a comment on where that I can test later.

##### **Chenyu** [[00:02:56](https://www.youtube.com/watch?v=gmY_RjZsYys&t=176)]
I imagine running that comment on like TinyBox red will work.

##### **Chenyu** [[00:03:02](https://www.youtube.com/watch?v=gmY_RjZsYys&t=182)]
Just run with with with SQTT equals one.

##### **Chenyu** [[00:03:07](https://www.youtube.com/watch?v=gmY_RjZsYys&t=187)]
We'll show.

##### **Chenyu** [[00:03:16](https://www.youtube.com/watch?v=gmY_RjZsYys&t=196)]
SQTT equals one.

##### **Sieds Lykles** [[00:03:18](https://www.youtube.com/watch?v=gmY_RjZsYys&t=198)]
Okay, I see that in test.

##### **Chenyu** [[00:03:29](https://www.youtube.com/watch?v=gmY_RjZsYys&t=209)]
What's rgp?

##### **Chenyu** [[00:03:34](https://www.youtube.com/watch?v=gmY_RjZsYys&t=214)]
rgp you mean?

##### **Chenyu** [[00:03:37](https://www.youtube.com/watch?v=gmY_RjZsYys&t=217)]
It's the AMD thing.

##### **Chenyu** [[00:03:39](https://www.youtube.com/watch?v=gmY_RjZsYys&t=219)]
Yeah.

##### **Chenyu** [[00:03:42](https://www.youtube.com/watch?v=gmY_RjZsYys&t=222)]
That's the latency hiding metrics.

##### **Sieds Lykles** [[00:03:46](https://www.youtube.com/watch?v=gmY_RjZsYys&t=226)]
Yes.

##### **Chenyu** [[00:03:47](https://www.youtube.com/watch?v=gmY_RjZsYys&t=227)]
Yeah.

##### **Chenyu** [[00:03:47](https://www.youtube.com/watch?v=gmY_RjZsYys&t=227)]
So basically, like, not all latency is bad, not all stalls are bad.

##### **Chenyu** [[00:03:55](https://www.youtube.com/watch?v=gmY_RjZsYys&t=235)]
Because sometimes the CPUs hide latency, hide network latency, and then GPUs hide memory

##### **Chenyu** [[00:04:03](https://www.youtube.com/watch?v=gmY_RjZsYys&t=243)]
latency with issuing a bunch of ALU instructions and then waiting for them later.

##### **Chenyu** [[00:04:12](https://www.youtube.com/watch?v=gmY_RjZsYys&t=252)]
So it's actually very important for a correct.

##### **Sieds Lykles** [[00:04:16](https://www.youtube.com/watch?v=gmY_RjZsYys&t=256)]
We.

##### **Chenyu** [[00:04:17](https://www.youtube.com/watch?v=gmY_RjZsYys&t=257)]
I'm just going to show you this view of the counter data to know if the hardware is actually.

##### **Chenyu** [[00:04:24](https://www.youtube.com/watch?v=gmY_RjZsYys&t=264)]
Blocked by that low instruction.

##### **Chenyu** [[00:04:28](https://www.youtube.com/watch?v=gmY_RjZsYys&t=268)]
Because you're always going to have like some amount of.

##### **Chenyu** [[00:04:31](https://www.youtube.com/watch?v=gmY_RjZsYys&t=271)]
Loneness.

##### **Chenyu** [[00:04:32](https://www.youtube.com/watch?v=gmY_RjZsYys&t=272)]
It's just a matter of if you can pipeline things correctly.

##### **Sieds Lykles** [[00:04:36](https://www.youtube.com/watch?v=gmY_RjZsYys&t=276)]
That's a real key that this is going to unlock.

##### **Chenyu** [[00:04:38](https://www.youtube.com/watch?v=gmY_RjZsYys&t=278)]
And help us figure out how to pipeline stuff correctly.

##### **Chenyu** [[00:04:43](https://www.youtube.com/watch?v=gmY_RjZsYys&t=283)]
And you're saying.

##### **Chenyu** [[00:04:45](https://www.youtube.com/watch?v=gmY_RjZsYys&t=285)]
The.

##### **Chenyu** [[00:04:45](https://www.youtube.com/watch?v=gmY_RjZsYys&t=285)]
Current tools.

##### **Chenyu** [[00:04:47](https://www.youtube.com/watch?v=gmY_RjZsYys&t=287)]
Already report list number.

##### **Sieds Lykles** [[00:04:49](https://www.youtube.com/watch?v=gmY_RjZsYys&t=289)]
That's correct.

##### **Chenyu** [[00:04:51](https://www.youtube.com/watch?v=gmY_RjZsYys&t=291)]
And our goal is to match that.

##### **Chenyu** [[00:04:54](https://www.youtube.com/watch?v=gmY_RjZsYys&t=294)]
I would hope it's correct.

##### **Chenyu** [[00:04:57](https://www.youtube.com/watch?v=gmY_RjZsYys&t=297)]
But yeah, they already have some things for these that.

##### **Chenyu** [[00:05:02](https://www.youtube.com/watch?v=gmY_RjZsYys&t=302)]
I would imagine that's.

##### **Chenyu** [[00:05:04](https://www.youtube.com/watch?v=gmY_RjZsYys&t=304)]
What can we tell if it's correct or not?

##### **Sieds Lykles** [[00:05:08](https://www.youtube.com/watch?v=gmY_RjZsYys&t=308)]
My plan is to write assembly and count the instructions.

##### **Chenyu** [[00:05:13](https://www.youtube.com/watch?v=gmY_RjZsYys&t=313)]
Count the cycles.

##### **Chenyu** [[00:05:14](https://www.youtube.com/watch?v=gmY_RjZsYys&t=314)]
Compare them.

##### **Chenyu** [[00:05:15](https://www.youtube.com/watch?v=gmY_RjZsYys&t=315)]
Yeah.

##### **Chenyu** [[00:05:15](https://www.youtube.com/watch?v=gmY_RjZsYys&t=315)]
Like with micro benchmarking.

##### **Chenyu** [[00:05:19](https://www.youtube.com/watch?v=gmY_RjZsYys&t=319)]
That seems to be the only way.

##### **Sieds Lykles** [[00:05:21](https://www.youtube.com/watch?v=gmY_RjZsYys&t=321)]
An animal that posted something about.

##### **Chenyu** [[00:05:24](https://www.youtube.com/watch?v=gmY_RjZsYys&t=324)]
The decoder being wrong wife.

##### **Chenyu** [[00:05:26](https://www.youtube.com/watch?v=gmY_RjZsYys&t=326)]
Four cycles.

##### **Chenyu** [[00:05:28](https://www.youtube.com/watch?v=gmY_RjZsYys&t=328)]
Which is kind of scary, but hopefully we can hear out.

##### **Chenyu** [[00:05:31](https://www.youtube.com/watch?v=gmY_RjZsYys&t=331)]
All those bugs then.

##### **Chenyu** [[00:05:33](https://www.youtube.com/watch?v=gmY_RjZsYys&t=333)]
It's done.

##### **Sieds Lykles** [[00:05:34](https://www.youtube.com/watch?v=gmY_RjZsYys&t=334)]
Okay.

##### **Chenyu** [[00:05:35](https://www.youtube.com/watch?v=gmY_RjZsYys&t=335)]
So it's.

##### **Chenyu** [[00:05:35](https://www.youtube.com/watch?v=gmY_RjZsYys&t=335)]
Two separate things.

##### **Chenyu** [[00:05:36](https://www.youtube.com/watch?v=gmY_RjZsYys&t=336)]
First is.

##### **Chenyu** [[00:05:37](https://www.youtube.com/watch?v=gmY_RjZsYys&t=337)]
Understand.

##### **Chenyu** [[00:05:38](https://www.youtube.com/watch?v=gmY_RjZsYys&t=338)]
The numbers and the reports is correct.

##### **Sieds Lykles** [[00:05:41](https://www.youtube.com/watch?v=gmY_RjZsYys&t=341)]
And the second is to match the number in this.

##### **Chenyu** [[00:05:44](https://www.youtube.com/watch?v=gmY_RjZsYys&t=344)]
Yes.

##### **Chenyu** [[00:05:46](https://www.youtube.com/watch?v=gmY_RjZsYys&t=346)]
All right.

##### **Chenyu** [[00:05:48](https://www.youtube.com/watch?v=gmY_RjZsYys&t=348)]
See.

##### **Chenyu** [[00:05:49](https://www.youtube.com/watch?v=gmY_RjZsYys&t=349)]
Well.

##### **Chenyu** [[00:05:52](https://www.youtube.com/watch?v=gmY_RjZsYys&t=352)]
That's good.

##### **Sieds Lykles** [[00:05:54](https://www.youtube.com/watch?v=gmY_RjZsYys&t=354)]
Anything else to add on this topic?

##### **Chenyu** [[00:06:02](https://www.youtube.com/watch?v=gmY_RjZsYys&t=362)]
So the only thing I'd like to discuss if we want to keep these flags

##### **Chenyu** [[00:06:07](https://www.youtube.com/watch?v=gmY_RjZsYys&t=367)]
like now to use sq2t in PMC, you need to use separate flags.

##### **Chenyu** [[00:06:14](https://www.youtube.com/watch?v=gmY_RjZsYys&t=374)]
So maybe we want to hide these features behind these with high

##### **Chenyu** [[00:06:19](https://www.youtube.com/watch?v=gmY_RjZsYys&t=379)]
levels like three or four.

##### **Chenyu** [[00:06:29](https://www.youtube.com/watch?v=gmY_RjZsYys&t=389)]
I would keep the sq2t separate just because.

##### **Sieds Lykles** [[00:06:35](https://www.youtube.com/watch?v=gmY_RjZsYys&t=395)]
I mean right now we have like a dependency from extra just to use

##### **Chenyu** [[00:06:39](https://www.youtube.com/watch?v=gmY_RjZsYys&t=399)]
sq2t.

##### **Chenyu** [[00:06:43](https://www.youtube.com/watch?v=gmY_RjZsYys&t=403)]
Yeah.

##### **Chenyu** [[00:06:47](https://www.youtube.com/watch?v=gmY_RjZsYys&t=407)]
Actually, I think that's bad.

##### **Chenyu** [[00:06:49](https://www.youtube.com/watch?v=gmY_RjZsYys&t=409)]
We need to move these into the main tiny crowd.

##### **Chenyu** [[00:06:54](https://www.youtube.com/watch?v=gmY_RjZsYys&t=414)]
Decoder.

##### **Sieds Lykles** [[00:06:54](https://www.youtube.com/watch?v=gmY_RjZsYys&t=414)]
Yeah.

##### **Chenyu** [[00:06:55](https://www.youtube.com/watch?v=gmY_RjZsYys&t=415)]
Agree.

##### **Chenyu** [[00:07:01](https://www.youtube.com/watch?v=gmY_RjZsYys&t=421)]
Is it bad in is in like bad or anything stopping us from just like

##### **Chenyu** [[00:07:08](https://www.youtube.com/watch?v=gmY_RjZsYys&t=428)]
moving into men?

##### **Chenyu** [[00:07:14](https://www.youtube.com/watch?v=gmY_RjZsYys&t=434)]
No, I think we can just move it.

##### **Chenyu** [[00:07:17](https://www.youtube.com/watch?v=gmY_RjZsYys&t=437)]
Is this some old and file?

##### **Sieds Lykles** [[00:07:19](https://www.youtube.com/watch?v=gmY_RjZsYys&t=439)]
I see lots of yeah, this is auto-generate mostly.

##### **Chenyu** [[00:07:23](https://www.youtube.com/watch?v=gmY_RjZsYys&t=443)]
Yeah.

##### **Chenyu** [[00:07:24](https://www.youtube.com/watch?v=gmY_RjZsYys&t=444)]
So we need to move these into after John and yeah, and just clean

##### **Chenyu** [[00:07:29](https://www.youtube.com/watch?v=gmY_RjZsYys&t=449)]
up rock pie because actually initially that was kind of like the

##### **Chenyu** [[00:07:36](https://www.youtube.com/watch?v=gmY_RjZsYys&t=456)]
test tool to parse these cutity sitting something to clean up before

##### **Chenyu** [[00:07:43](https://www.youtube.com/watch?v=gmY_RjZsYys&t=463)]
moving it.

##### **Sieds Lykles** [[00:07:45](https://www.youtube.com/watch?v=gmY_RjZsYys&t=465)]
Yeah, I noticed that with that file whenever the decoder crashes, we

##### **Chenyu** [[00:07:50](https://www.youtube.com/watch?v=gmY_RjZsYys&t=470)]
can't control C from Python.

##### **Chenyu** [[00:07:57](https://www.youtube.com/watch?v=gmY_RjZsYys&t=477)]
That's kind of a like I have to kill the process whenever that happens.

##### **Chenyu** [[00:08:05](https://www.youtube.com/watch?v=gmY_RjZsYys&t=485)]
That's the only instability of seeing this parser.

##### **Chenyu** [[00:08:16](https://www.youtube.com/watch?v=gmY_RjZsYys&t=496)]
Okay.

##### **Chenyu** [[00:08:18](https://www.youtube.com/watch?v=gmY_RjZsYys&t=498)]
Anyway, so sounds like the plan is all sq2t into man.

##### **Sieds Lykles** [[00:08:27](https://www.youtube.com/watch?v=gmY_RjZsYys&t=507)]
Do one of you want to take this one?

##### **Chenyu** [[00:08:30](https://www.youtube.com/watch?v=gmY_RjZsYys&t=510)]
Then the list match RGP and verify RGP is good.

##### **Chenyu** [[00:08:45](https://www.youtube.com/watch?v=gmY_RjZsYys&t=525)]
Cool.

##### **Chenyu** [[00:08:47](https://www.youtube.com/watch?v=gmY_RjZsYys&t=527)]
Okay.

##### **Chenyu** [[00:08:49](https://www.youtube.com/watch?v=gmY_RjZsYys&t=529)]
Next one.

##### **Chenyu** [[00:08:51](https://www.youtube.com/watch?v=gmY_RjZsYys&t=531)]
Another item that I know very little of.

##### **Sieds Lykles** [[00:08:57](https://www.youtube.com/watch?v=gmY_RjZsYys&t=537)]
So in the current state is we got some entitlement, but we are not

##### **Chenyu** [[00:09:01](https://www.youtube.com/watch?v=gmY_RjZsYys&t=541)]
going to get entitlement to open anything.

##### **Chenyu** [[00:09:04](https://www.youtube.com/watch?v=gmY_RjZsYys&t=544)]
I guess everything.

##### **Chenyu** [[00:09:07](https://www.youtube.com/watch?v=gmY_RjZsYys&t=547)]
Yeah, so

##### **Chenyu** [[00:09:09](https://www.youtube.com/watch?v=gmY_RjZsYys&t=549)]
we don't have entitlement to

##### **Chenyu** [[00:09:13](https://www.youtube.com/watch?v=gmY_RjZsYys&t=553)]
to allow any clients.

##### **Sieds Lykles** [[00:09:16](https://www.youtube.com/watch?v=gmY_RjZsYys&t=556)]
So python can't connect to our driver kit.

##### **Chenyu** [[00:09:21](https://www.youtube.com/watch?v=gmY_RjZsYys&t=561)]
So in the solution here is just to

##### **Chenyu** [[00:09:25](https://www.youtube.com/watch?v=gmY_RjZsYys&t=565)]
like have some binary which is signed and python will connect to our driver

##### **Chenyu** [[00:09:30](https://www.youtube.com/watch?v=gmY_RjZsYys&t=570)]
kit.

##### **Chenyu** [[00:09:31](https://www.youtube.com/watch?v=gmY_RjZsYys&t=571)]
Why are these

##### **Chenyu** [[00:09:33](https://www.youtube.com/watch?v=gmY_RjZsYys&t=573)]
assigned application?

##### **Sieds Lykles** [[00:09:36](https://www.youtube.com/watch?v=gmY_RjZsYys&t=576)]
So yeah, I'll investigate this.

##### **Chenyu** [[00:09:39](https://www.youtube.com/watch?v=gmY_RjZsYys&t=579)]
Yeah.

##### **Chenyu** [[00:09:45](https://www.youtube.com/watch?v=gmY_RjZsYys&t=585)]
I'll hook up the 3x 5060 sometime today.

##### **Chenyu** [[00:10:00](https://www.youtube.com/watch?v=gmY_RjZsYys&t=600)]
Oh, while you do that, can you also figure out why the USB GPU was not

##### **Chenyu** [[00:10:06](https://www.youtube.com/watch?v=gmY_RjZsYys&t=606)]
working for one of the tiny Mac one or something?

##### **Chenyu** [[00:10:13](https://www.youtube.com/watch?v=gmY_RjZsYys&t=613)]
Oh, is it broken on one of the Macs?

##### **Sieds Lykles** [[00:10:17](https://www.youtube.com/watch?v=gmY_RjZsYys&t=617)]
I saw I disabled one of it from CI because of that.

##### **Chenyu** [[00:10:21](https://www.youtube.com/watch?v=gmY_RjZsYys&t=621)]
I see.

##### **Chenyu** [[00:10:23](https://www.youtube.com/watch?v=gmY_RjZsYys&t=623)]
It probably just needs a replug.

##### **Chenyu** [[00:10:28](https://www.youtube.com/watch?v=gmY_RjZsYys&t=628)]
Yeah, I think that was the conclusion we had last time, but I forget to ask

##### **Chenyu** [[00:10:31](https://www.youtube.com/watch?v=gmY_RjZsYys&t=631)]
comma people to do this.

##### **Chenyu** [[00:10:33](https://www.youtube.com/watch?v=gmY_RjZsYys&t=633)]
I was saying earlier already.

##### **Sieds Lykles** [[00:10:34](https://www.youtube.com/watch?v=gmY_RjZsYys&t=634)]
Maybe you can do that.

##### **Chenyu** [[00:10:37](https://www.youtube.com/watch?v=gmY_RjZsYys&t=637)]
So I will do it.

##### **Chenyu** [[00:10:39](https://www.youtube.com/watch?v=gmY_RjZsYys&t=639)]
Yeah.

##### **Chenyu** [[00:10:42](https://www.youtube.com/watch?v=gmY_RjZsYys&t=642)]
Yeah, just do that.

##### **Chenyu** [[00:10:42](https://www.youtube.com/watch?v=gmY_RjZsYys&t=642)]
And enable and

##### **Chenyu** [[00:10:46](https://www.youtube.com/watch?v=gmY_RjZsYys&t=646)]
making sure it works.

##### **Sieds Lykles** [[00:10:52](https://www.youtube.com/watch?v=gmY_RjZsYys&t=652)]
Okay.

##### **Chenyu** [[00:10:55](https://www.youtube.com/watch?v=gmY_RjZsYys&t=655)]
Cool.

##### **Chenyu** [[00:10:56](https://www.youtube.com/watch?v=gmY_RjZsYys&t=656)]
Sounds good.

##### **Chenyu** [[00:10:57](https://www.youtube.com/watch?v=gmY_RjZsYys&t=657)]
Wait about the

##### **Chenyu** [[00:10:58](https://www.youtube.com/watch?v=gmY_RjZsYys&t=658)]
the Apple like USB GPU and CI.

##### **Chenyu** [[00:11:04](https://www.youtube.com/watch?v=gmY_RjZsYys&t=664)]
Would it be reasonable to remove LLVM pipe support from Mesa if we can do that?

##### **Sieds Lykles** [[00:11:10](https://www.youtube.com/watch?v=gmY_RjZsYys&t=670)]
If we can test Mesa and CI.

##### **Chenyu** [[00:11:13](https://www.youtube.com/watch?v=gmY_RjZsYys&t=673)]
Using knack now because I feel like there's a lot of like frustration associated with LLVM pipe and

##### **Chenyu** [[00:11:20](https://www.youtube.com/watch?v=gmY_RjZsYys&t=680)]
you know, it would make the code simpler as well.

##### **Chenyu** [[00:11:30](https://www.youtube.com/watch?v=gmY_RjZsYys&t=690)]
I think no because it's benchmarking not CI like yeah.

##### **Chenyu** [[00:11:35](https://www.youtube.com/watch?v=gmY_RjZsYys&t=695)]
Okay.

##### **Chenyu** [[00:11:38](https://www.youtube.com/watch?v=gmY_RjZsYys&t=698)]
So I mean if you are saying let's

##### **Sieds Lykles** [[00:11:43](https://www.youtube.com/watch?v=gmY_RjZsYys&t=703)]
I am not sure.

##### **Chenyu** [[00:11:47](https://www.youtube.com/watch?v=gmY_RjZsYys&t=707)]
So I guess if it's only for testing then we should see if it is something that can be separated.

##### **Chenyu** [[00:11:56](https://www.youtube.com/watch?v=gmY_RjZsYys&t=716)]
Like maybe put a script or some

##### **Chenyu** [[00:12:01](https://www.youtube.com/watch?v=gmY_RjZsYys&t=721)]
some additional test only class in extra or something.

##### **Chenyu** [[00:12:05](https://www.youtube.com/watch?v=gmY_RjZsYys&t=725)]
So let us not including tiny bread and doesn't interfere when people use it similar to how we test some.

##### **Chenyu** [[00:12:13](https://www.youtube.com/watch?v=gmY_RjZsYys&t=733)]
Of the

##### **Sieds Lykles** [[00:12:16](https://www.youtube.com/watch?v=gmY_RjZsYys&t=736)]
I don't know if we still have any of these but

##### **Chenyu** [[00:12:19](https://www.youtube.com/watch?v=gmY_RjZsYys&t=739)]
my point is if it's only there because we don't have a real machine to test.

##### **Chenyu** [[00:12:24](https://www.youtube.com/watch?v=gmY_RjZsYys&t=744)]
I think the general direction is

##### **Chenyu** [[00:12:27](https://www.youtube.com/watch?v=gmY_RjZsYys&t=747)]
anything we can move out of men tiny bread.

##### **Chenyu** [[00:12:30](https://www.youtube.com/watch?v=gmY_RjZsYys&t=750)]
We want to move it out.

##### **Chenyu** [[00:12:31](https://www.youtube.com/watch?v=gmY_RjZsYys&t=751)]
So let the

##### **Sieds Lykles** [[00:12:33](https://www.youtube.com/watch?v=gmY_RjZsYys&t=753)]
so that a legit use case won't be interfere with like least setups.

##### **Chenyu** [[00:12:38](https://www.youtube.com/watch?v=gmY_RjZsYys&t=758)]
But yeah, yeah, ideally we still want this code pass and things.

##### **Chenyu** [[00:12:42](https://www.youtube.com/watch?v=gmY_RjZsYys&t=762)]
To be tested in CI and not and it doesn't need a real machine.

##### **Chenyu** [[00:12:48](https://www.youtube.com/watch?v=gmY_RjZsYys&t=768)]
What's the general direction?

##### **Chenyu** [[00:12:51](https://www.youtube.com/watch?v=gmY_RjZsYys&t=771)]
Okay, that makes sense.

##### **Chenyu** [[00:12:52](https://www.youtube.com/watch?v=gmY_RjZsYys&t=772)]
Yeah, the reason I say that is because there's no reason that an end user would ever want to use llvmpipe because it's just going to be worse than that LLVM back end.

##### **Sieds Lykles** [[00:12:59](https://www.youtube.com/watch?v=gmY_RjZsYys&t=779)]
But yeah, that makes sense.

##### **Chenyu** [[00:13:02](https://www.youtube.com/watch?v=gmY_RjZsYys&t=782)]
I think a small I think some like small part of it running.

##### **Chenyu** [[00:13:10](https://www.youtube.com/watch?v=gmY_RjZsYys&t=790)]
Having a code being man is fine.

##### **Chenyu** [[00:13:12](https://www.youtube.com/watch?v=gmY_RjZsYys&t=792)]
I think we also have led for

##### **Chenyu** [[00:13:15](https://www.youtube.com/watch?v=gmY_RjZsYys&t=795)]
or the

##### **Chenyu** [[00:13:17](https://www.youtube.com/watch?v=gmY_RjZsYys&t=797)]
other emulated back end.

##### **Sieds Lykles** [[00:13:19](https://www.youtube.com/watch?v=gmY_RjZsYys&t=799)]
Yeah, there's like a test slash mock GPU or something like that.

##### **Chenyu** [[00:13:22](https://www.youtube.com/watch?v=gmY_RjZsYys&t=802)]
Maybe I can move it in there.

##### **Chenyu** [[00:13:24](https://www.youtube.com/watch?v=gmY_RjZsYys&t=804)]
So something some test picture like glad would be nice.

##### **Chenyu** [[00:13:28](https://www.youtube.com/watch?v=gmY_RjZsYys&t=808)]
Yeah.

##### **Chenyu** [[00:13:30](https://www.youtube.com/watch?v=gmY_RjZsYys&t=810)]
Cool.

##### **Chenyu** [[00:13:35](https://www.youtube.com/watch?v=gmY_RjZsYys&t=815)]
Okay.

##### **Sieds Lykles** [[00:13:37](https://www.youtube.com/watch?v=gmY_RjZsYys&t=817)]
Guess that's for this one.

##### **Chenyu** [[00:13:39](https://www.youtube.com/watch?v=gmY_RjZsYys&t=819)]
Do we have anything from the USB GPU channel?

##### **Chenyu** [[00:13:45](https://www.youtube.com/watch?v=gmY_RjZsYys&t=825)]
Oh,

##### **Chenyu** [[00:13:46](https://www.youtube.com/watch?v=gmY_RjZsYys&t=826)]
oh,

##### **Chenyu** [[00:13:47](https://www.youtube.com/watch?v=gmY_RjZsYys&t=827)]
we're here anymore.

##### **Chenyu** [[00:13:48](https://www.youtube.com/watch?v=gmY_RjZsYys&t=828)]
Do you have any comment on there's person asking question in

##### **Sieds Lykles** [[00:13:53](https://www.youtube.com/watch?v=gmY_RjZsYys&t=833)]
some of the special universe

##### **Chenyu** [[00:13:56](https://www.youtube.com/watch?v=gmY_RjZsYys&t=836)]
or GPU GPU USB?

##### **Chenyu** [[00:14:08](https://www.youtube.com/watch?v=gmY_RjZsYys&t=848)]
No comments reading.

##### **Chenyu** [[00:14:09](https://www.youtube.com/watch?v=gmY_RjZsYys&t=849)]
I mean, yeah, we can try.

##### **Chenyu** [[00:14:13](https://www.youtube.com/watch?v=gmY_RjZsYys&t=853)]
I mean, it's it's interesting why like the Linux reports that it can

##### **Chenyu** [[00:14:21](https://www.youtube.com/watch?v=gmY_RjZsYys&t=861)]
that it has some bars, but after that you cannot resize these bars.

##### **Sieds Lykles** [[00:14:30](https://www.youtube.com/watch?v=gmY_RjZsYys&t=870)]
Yeah.

##### **Chenyu** [[00:14:32](https://www.youtube.com/watch?v=gmY_RjZsYys&t=872)]
Okay.

##### **Chenyu** [[00:14:32](https://www.youtube.com/watch?v=gmY_RjZsYys&t=872)]
Yeah, I'll take a look into this.

##### **Chenyu** [[00:14:34](https://www.youtube.com/watch?v=gmY_RjZsYys&t=874)]
No comments yet.

##### **Chenyu** [[00:14:44](https://www.youtube.com/watch?v=gmY_RjZsYys&t=884)]
Just just comment something on this too.

##### **Chenyu** [[00:14:49](https://www.youtube.com/watch?v=gmY_RjZsYys&t=889)]
It's probably good enough.

##### **Sieds Lykles** [[00:14:52](https://www.youtube.com/watch?v=gmY_RjZsYys&t=892)]
Okay.

##### **Chenyu** [[00:14:55](https://www.youtube.com/watch?v=gmY_RjZsYys&t=895)]
Uh, cool.

##### **Chenyu** [[00:14:56](https://www.youtube.com/watch?v=gmY_RjZsYys&t=896)]
Next is tiny kitten.

##### **Chenyu** [[00:14:59](https://www.youtube.com/watch?v=gmY_RjZsYys&t=899)]
It's tiny kitten.

##### **Chenyu** [[00:15:00](https://www.youtube.com/watch?v=gmY_RjZsYys&t=900)]
Good.

##### **Chenyu** [[00:15:00](https://www.youtube.com/watch?v=gmY_RjZsYys&t=900)]
Is it fast?

##### **Sieds Lykles** [[00:15:01](https://www.youtube.com/watch?v=gmY_RjZsYys&t=901)]
And we use it.

##### **Chenyu** [[00:15:02](https://www.youtube.com/watch?v=gmY_RjZsYys&t=902)]
Slender kittens is not fast.

##### **Chenyu** [[00:15:05](https://www.youtube.com/watch?v=gmY_RjZsYys&t=905)]
We can't get good GEMM performance out of it.

##### **Chenyu** [[00:15:07](https://www.youtube.com/watch?v=gmY_RjZsYys&t=907)]
I don't know how much of that is just down to me not tuning.

##### **Chenyu** [[00:15:12](https://www.youtube.com/watch?v=gmY_RjZsYys&t=912)]
Any of the block sizes.

##### **Chenyu** [[00:15:17](https://www.youtube.com/watch?v=gmY_RjZsYys&t=917)]
All right.

##### **Sieds Lykles** [[00:15:18](https://www.youtube.com/watch?v=gmY_RjZsYys&t=918)]
Okay.

##### **Chenyu** [[00:15:19](https://www.youtube.com/watch?v=gmY_RjZsYys&t=919)]
Also don't know how many more of the GEMM tricks.

##### **Chenyu** [[00:15:23](https://www.youtube.com/watch?v=gmY_RjZsYys&t=923)]
I'm missing the GEMM that I wrote using Thunder kittens.

##### **Chenyu** [[00:15:30](https://www.youtube.com/watch?v=gmY_RjZsYys&t=930)]
Uh, totally publish like any of the numbers.

##### **Chenyu** [[00:15:35](https://www.youtube.com/watch?v=gmY_RjZsYys&t=935)]
Not for 4090.

##### **Chenyu** [[00:15:38](https://www.youtube.com/watch?v=gmY_RjZsYys&t=938)]
The Thunder kittens is very much focused on.

##### **Sieds Lykles** [[00:15:41](https://www.youtube.com/watch?v=gmY_RjZsYys&t=941)]
H100 and B200.

##### **Chenyu** [[00:15:46](https://www.youtube.com/watch?v=gmY_RjZsYys&t=946)]
And there is now very little support for anything below that.

##### **Chenyu** [[00:15:51](https://www.youtube.com/watch?v=gmY_RjZsYys&t=951)]
And especially on the consumer side.

##### **Chenyu** [[00:15:58](https://www.youtube.com/watch?v=gmY_RjZsYys&t=958)]
Okay.

##### **Chenyu** [[00:16:00](https://www.youtube.com/watch?v=gmY_RjZsYys&t=960)]
So I know George is going back soon.

##### **Chenyu** [[00:16:04](https://www.youtube.com/watch?v=gmY_RjZsYys&t=964)]
So maybe you can just you who can discuss any ideas for how to progress on this front.

##### **Sieds Lykles** [[00:16:12](https://www.youtube.com/watch?v=gmY_RjZsYys&t=972)]
So I don't know how much I think I don't know how much time I want to waste more on looking at the GEMM performance.

##### **Chenyu** [[00:16:21](https://www.youtube.com/watch?v=gmY_RjZsYys&t=981)]
So I've switched to just copying the flash attention example over to you ops.

##### **Chenyu** [[00:16:29](https://www.youtube.com/watch?v=gmY_RjZsYys&t=989)]
Have a PR for that currently.

##### **Chenyu** [[00:16:35](https://www.youtube.com/watch?v=gmY_RjZsYys&t=995)]
I see.

##### **Chenyu** [[00:16:36](https://www.youtube.com/watch?v=gmY_RjZsYys&t=996)]
Okay.

##### **Chenyu** [[00:16:38](https://www.youtube.com/watch?v=gmY_RjZsYys&t=998)]
Yeah, I think that's.

##### **Sieds Lykles** [[00:16:42](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1002)]
Uh, anyway, we can discuss later in person.

##### **Chenyu** [[00:16:46](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1006)]
So the conclusion is.

##### **Chenyu** [[00:16:50](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1010)]
We don't know if it works well on 4090.

##### **Chenyu** [[00:16:56](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1016)]
I mean, the main thing is I think most of the Thunder kittens abstractions are correct.

##### **Chenyu** [[00:17:02](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1022)]
Hey.

##### **Chenyu** [[00:17:08](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1028)]
It's just the speed stuff.

##### **Sieds Lykles** [[00:17:11](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1031)]
I think there's one thing that we can't do with Thunder kittens, but I don't know how important it is.

##### **Chenyu** [[00:17:21](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1041)]
But.

##### **Chenyu** [[00:17:22](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1042)]
At the same.

##### **Chenyu** [[00:17:25](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1045)]
I mean, said you can look at the max memory example.

##### **Chenyu** [[00:17:31](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1051)]
Okay.

##### **Chenyu** [[00:17:33](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1053)]
Uh.

##### **Sieds Lykles** [[00:17:40](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1060)]
Anyway.

##### **Chenyu** [[00:17:44](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1064)]
Okay.

##### **Chenyu** [[00:17:48](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1068)]
Okay.

##### **Chenyu** [[00:17:52](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1072)]
So you say the next step is you have the flash and tension kernel.

##### **Chenyu** [[00:17:57](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1077)]
Let's copy.

##### **Chenyu** [[00:17:58](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1078)]
Yeah.

##### **Sieds Lykles** [[00:17:59](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1079)]
The goal this week is just to get the flash attention kernel running.

##### **Chenyu** [[00:18:04](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1084)]
Yeah.

##### **Chenyu** [[00:18:04](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1084)]
But it also won't be fast, right?

##### **Chenyu** [[00:18:07](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1087)]
Because it has like three gym three GEMMs inside.

##### **Chenyu** [[00:18:15](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1095)]
Yes.

##### **Chenyu** [[00:18:16](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1096)]
Okay.

##### **Sieds Lykles** [[00:18:17](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1097)]
I mean, there's hits 136.

##### **Chenyu** [[00:18:19](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1099)]
So.

##### **Chenyu** [[00:18:22](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1102)]
It's not like slow.

##### **Chenyu** [[00:18:25](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1105)]
Okay.

##### **Chenyu** [[00:18:26](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1106)]
It's just not mixing out the GPU fast.

##### **Chenyu** [[00:18:31](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1111)]
Cool.

##### **Sieds Lykles** [[00:18:32](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1112)]
I guess generally for me.

##### **Chenyu** [[00:18:34](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1114)]
For these kind of a task is find some scripts that people other people write.

##### **Chenyu** [[00:18:41](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1121)]
So it is fast and try to match that.

##### **Chenyu** [[00:18:44](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1124)]
So if you are saying there's it's not fast with tiny kids and then maybe we should check something else for benchmark.

##### **Chenyu** [[00:18:53](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1133)]
But having some kind of flash attention also sounds good.

##### **Chenyu** [[00:18:57](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1137)]
So maybe we'll go from there.

##### **Sieds Lykles** [[00:19:00](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1140)]
Yeah.

##### **Chenyu** [[00:19:00](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1140)]
Yeah.

##### **Chenyu** [[00:19:01](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1141)]
I think that's more useful right now.

##### **Chenyu** [[00:19:05](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1145)]
Cool.

##### **Chenyu** [[00:19:08](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1148)]
Okay.

##### **Chenyu** [[00:19:11](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1151)]
Next one is kind of similar.

##### **Sieds Lykles** [[00:19:14](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1154)]
I to use the custom kernel to basically put a customer kernel in the scale that product attention.

##### **Chenyu** [[00:19:23](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1163)]
And see if the memory usage is good.

##### **Chenyu** [[00:19:28](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1168)]
This is probably on me.

##### **Chenyu** [[00:19:30](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1170)]
I would have figured this out.

##### **Chenyu** [[00:19:35](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1175)]
I post a question somewhere in theory.

##### **Chenyu** [[00:19:38](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1178)]
Do you know how to write a average thing in you up?

##### **Sieds Lykles** [[00:19:49](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1189)]
I think the jam is.

##### **Chenyu** [[00:19:52](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1192)]
So few things we would need flash attention backwards and very hard to write and I think the.

##### **Chenyu** [[00:20:01](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1201)]
One requirement for that is to write a softmax backward.

##### **Chenyu** [[00:20:05](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1205)]
And then I don't really know how to write a softmax backward in one kernel using you up.

##### **Chenyu** [[00:20:11](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1211)]
So that's something I will figure out or at least isolate a case now.

##### **Chenyu** [[00:20:15](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1215)]
Do I I don't think it's possible.

##### **Sieds Lykles** [[00:20:18](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1218)]
Oh.

##### **Chenyu** [[00:20:22](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1222)]
I want to write the X divided by some X kernel in one kernel or because fuse doesn't work anymore after range.

##### **Chenyu** [[00:20:30](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1230)]
If I.

##### **Chenyu** [[00:20:36](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1236)]
So it's either I was thinking if I write is similar to the old single single kernels of Max way.

##### **Chenyu** [[00:20:45](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1245)]
Basically you lift another.

##### **Chenyu** [[00:20:48](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1248)]
You expand another dimension to do reduce later.

##### **Sieds Lykles** [[00:20:52](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1252)]
I was hoping there's a different way to do that.

##### **Chenyu** [[00:20:55](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1255)]
Oh, I think I will look into or I'll just ask her to later when I meet him.

##### **Chenyu** [[00:21:04](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1264)]
And so I think.

##### **Chenyu** [[00:21:08](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1268)]
For the kernels we really need is flash attention forward flash attention backward.

##### **Chenyu** [[00:21:13](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1273)]
I think forward we have a much better understanding and the memory usage should be content.

##### **Chenyu** [[00:21:20](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1280)]
If it's seeing like a single kernel with like multiple output.

##### **Sieds Lykles** [[00:21:24](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1284)]
I worry less about that land the backward kernel.

##### **Chenyu** [[00:21:28](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1288)]
I think people say it's a finicky.

##### **Chenyu** [[00:21:30](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1290)]
And we should at least start with the softmax backward.

##### **Chenyu** [[00:21:34](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1294)]
See if it can be represented with the ranch stuff.

##### **Chenyu** [[00:21:38](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1298)]
Issue there is.

##### **Chenyu** [[00:21:41](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1301)]
It's not really an element wise operation on ranch.

##### **Sieds Lykles** [[00:21:46](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1306)]
It's a kind of a function of the identity metrics and ranch.

##### **Chenyu** [[00:21:52](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1312)]
So not clear there yet.

##### **Chenyu** [[00:21:55](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1315)]
I guess let's look at main focus for this week for me.

##### **Chenyu** [[00:22:01](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1321)]
I think I just realized because we didn't submit mlpref this round.

##### **Chenyu** [[00:22:05](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1325)]
We cannot see other people's submission until they are released.

##### **Chenyu** [[00:22:09](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1329)]
I also don't know if other people has better out there than anything like that.

##### **Sieds Lykles** [[00:22:17](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1337)]
Yeah.

##### **Chenyu** [[00:22:21](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1341)]
I think it's November already.

##### **Chenyu** [[00:22:24](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1344)]
Oh before end of this year is getting fast.

##### **Chenyu** [[00:22:28](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1348)]
less fashion attention and at least have something less training

##### **Chenyu** [[00:22:33](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1353)]
maybe a smaller drama or we should start with like trend bigger LLMs

##### **Chenyu** [[00:22:48](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1368)]
Let's list item, the next is open on pilot regressions

##### **Sieds Lykles** [[00:22:53](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1373)]
I posted on Onyx channel earlier, I think the parsing issue is really not a parsing issue

##### **Chenyu** [[00:23:00](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1380)]
I think maybe Karma just changed the way they upload LFS file

##### **Chenyu** [[00:23:04](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1384)]
now it's not part of the release

##### **Chenyu** [[00:23:06](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1386)]
so if you download from the URL, you would just download a pointer page

##### **Chenyu** [[00:23:10](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1390)]
and that's why parsers fail

##### **Chenyu** [[00:23:15](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1395)]
maybe we can do better

##### **Sieds Lykles** [[00:23:20](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1400)]
I don't know, because it's proto, I don't know

##### **Chenyu** [[00:23:22](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1402)]
so you don't really

##### **Chenyu** [[00:23:24](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1404)]
you cannot really parse and say this is not valid

##### **Chenyu** [[00:23:30](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1410)]
so maybe we can do better for error

##### **Chenyu** [[00:23:35](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1415)]
error propagation, but in this case if you compare

##### **Chenyu** [[00:23:38](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1418)]
if you download the same thing and try to parse it with Onyx

##### **Sieds Lykles** [[00:23:43](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1423)]
or parser, you get similar errors

##### **Chenyu** [[00:23:45](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1425)]
so I don't think it's a big deal

##### **Chenyu** [[00:23:49](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1429)]
follow speed regression

##### **Chenyu** [[00:23:52](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1432)]
I have an isolated script that shows why it becomes slower

##### **Chenyu** [[00:23:57](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1437)]
so this is the regression after the linearizer

##### **Chenyu** [[00:24:00](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1440)]
and it's basically the same thing because it removes the block reorder

##### **Sieds Lykles** [[00:24:06](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1446)]
and block reorder sometimes makes things faster and sometimes makes things slower

##### **Chenyu** [[00:24:09](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1449)]
in this case it's much slower because I post it in the fast tiny graph channel

##### **Chenyu** [[00:24:19](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1459)]
so currently it's doing some read image

##### **Chenyu** [[00:24:23](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1463)]
then do some ALU on that image

##### **Chenyu** [[00:24:25](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1465)]
then read another image

##### **Chenyu** [[00:24:27](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1467)]
things like that

##### **Sieds Lykles** [[00:24:28](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1468)]
while it's faster to just initiate bunch of loads of read image

##### **Chenyu** [[00:24:34](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1474)]
then following up by ALU

##### **Chenyu** [[00:24:37](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1477)]
imagine it's doing something smarter there

##### **Chenyu** [[00:24:41](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1481)]
I try a bit, I try to play with the priority a bit here

##### **Chenyu** [[00:24:48](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1488)]
it's really good

##### **Chenyu** [[00:24:49](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1489)]
it's really weird sometimes it's faster but the output is wrong

##### **Sieds Lykles** [[00:24:53](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1493)]
and after the new linearizer

##### **Chenyu** [[00:24:57](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1497)]
I don't know much about if it's still valid to just change the order of stuff in the block

##### **Chenyu** [[00:25:04](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1504)]
because it looks like it's not

##### **Chenyu** [[00:25:06](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1506)]
that's something I'll probably also follow up when I am in office

##### **Chenyu** [[00:25:11](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1511)]
unless people want to try this

##### **Chenyu** [[00:25:13](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1513)]
I have the script and you can manually change the order for the

##### **Sieds Lykles** [[00:25:18](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1518)]
generated source code layer to get the faster version

##### **Chenyu** [[00:25:26](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1526)]
yeah so I think that's the two OpenPython regressions

##### **Chenyu** [[00:25:30](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1530)]
one is the URL

##### **Chenyu** [[00:25:33](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1533)]
I'll probably talk to Wukama people later to see

##### **Chenyu** [[00:25:37](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1537)]
what do they recommend

##### **Chenyu** [[00:25:38](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1538)]
I imagine it's not a problem for them on device

##### **Sieds Lykles** [[00:25:41](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1541)]
because they probably just download a model and load it differently

##### **Chenyu** [[00:25:45](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1545)]
but it's slightly annoying because now there's

##### **Chenyu** [[00:25:48](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1548)]
I don't see an easy way for us to upgrade

##### **Chenyu** [[00:25:51](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1551)]
the benchmark to ping to 0.10.1

##### **Chenyu** [[00:25:54](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1554)]
without finding the GitLab LFS URL and use that

##### **Chenyu** [[00:25:59](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1559)]
but that's not tied to a release

##### **Sieds Lykles** [[00:26:01](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1561)]
that's slightly annoying

##### **Chenyu** [[00:26:09](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1569)]
I'll take a look at this

##### **Chenyu** [[00:26:14](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1574)]
sure don't waste too much time on this

##### **Chenyu** [[00:26:16](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1576)]
it's fine for the things we currently have on CA

##### **Chenyu** [[00:26:18](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1578)]
in worst case it's not that bad to pull the GitLab LFS URL

##### **Chenyu** [[00:26:29](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1589)]
yeah I mean we used to do that

##### **Sieds Lykles** [[00:26:31](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1591)]
but it's just it's no longer tied to a release

##### **Chenyu** [[00:26:33](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1593)]
and it's slightly annoying

##### **Chenyu** [[00:26:38](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1598)]
yeah

##### **Chenyu** [[00:26:40](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1600)]
okay I think for now the UIO is fine

##### **Chenyu** [[00:26:43](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1603)]
Kama has no problems running the models

##### **Chenyu** [[00:26:46](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1606)]
so I think the speed is still more important here

##### **Sieds Lykles** [[00:26:55](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1615)]
okay

##### **Chenyu** [[00:26:57](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1617)]
next is Underbounties

##### **Chenyu** [[00:27:03](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1623)]
what do we have?

##### **Chenyu** [[00:27:05](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1625)]
do we have update for Clan2Py?

##### **Chenyu** [[00:27:09](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1629)]
yep that's still going

##### **Chenyu** [[00:27:10](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1630)]
there's like three things that are left to figure out

##### **Sieds Lykles** [[00:27:13](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1633)]
so there's the MetalObject.js

##### **Chenyu** [[00:27:16](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1636)]
and the Objective-C stuff

##### **Chenyu** [[00:27:16](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1636)]
which I'm reading about

##### **Chenyu** [[00:27:17](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1637)]
it shouldn't be too bad

##### **Chenyu** [[00:27:18](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1638)]
the only thing I'm thinking about is whether or not we want to verify that in CI

##### **Chenyu** [[00:27:24](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1644)]
but the Mac CI runners should have all of the header files

##### **Sieds Lykles** [[00:27:27](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1647)]
I mean I think they should

##### **Chenyu** [[00:27:29](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1649)]
I don't I imagine they do

##### **Chenyu** [[00:27:32](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1652)]
and then there's something wrong with Windows as well

##### **Chenyu** [[00:27:35](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1655)]
and then also I posted about this in the TinyGrad Dev Channel

##### **Chenyu** [[00:27:40](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1660)]
but I'm getting a whole bunch of MyPy errors

##### **Chenyu** [[00:27:43](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1663)]
because I made a

##### **Sieds Lykles** [[00:27:45](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1665)]
it's a long story

##### **Chenyu** [[00:27:46](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1666)]
but I had to subclass ctype structure

##### **Chenyu** [[00:27:50](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1670)]
and for whatever reason MyPy can't see through the subclass

##### **Chenyu** [[00:27:55](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1675)]
but interestingly Pyrefly can see through it

##### **Chenyu** [[00:27:58](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1678)]
and Pyrefly is also faster

##### **Chenyu** [[00:28:00](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1680)]
so I was asking about whether or not that would be a reasonable thing to switch to

##### **Sieds Lykles** [[00:28:04](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1684)]
but yeah it's good progress

##### **Chenyu** [[00:28:06](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1686)]
I think it should

##### **Chenyu** [[00:28:06](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1686)]
generally for this

##### **Chenyu** [[00:28:08](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1688)]
as long as you can show that

##### **Chenyu** [[00:28:12](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1692)]
it's really

##### **Chenyu** [[00:28:12](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1692)]
it's really seeing through it

##### **Sieds Lykles** [[00:28:15](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1695)]
and not just bypass in this case

##### **Chenyu** [[00:28:17](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1697)]
I think it's generally a good idea to switch to a faster and modern infra

##### **Chenyu** [[00:28:22](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1702)]
like how we pretty much replaced PyLint with Ruff

##### **Chenyu** [[00:28:27](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1707)]
so

##### **Chenyu** [[00:28:30](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1710)]
just see if you can show

##### **Chenyu** [[00:28:33](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1713)]
show that by switching to this

##### **Sieds Lykles** [[00:28:37](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1717)]
maybe it's fine if it doesn't match all of MyPy features

##### **Chenyu** [[00:28:42](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1722)]
but it cannot be

##### **Chenyu** [[00:28:43](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1723)]
it cannot be like dropping a lot

##### **Chenyu** [[00:28:45](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1725)]
and that's why it's faster

##### **Chenyu** [[00:28:47](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1727)]
yeah yeah

##### **Chenyu** [[00:28:48](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1728)]
no they claim that

##### **Sieds Lykles** [[00:28:50](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1730)]
that it has feature parity

##### **Chenyu** [[00:28:52](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1732)]
or it's actually stricter than MyPy

##### **Chenyu** [[00:28:54](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1734)]
and actually when you run it right now

##### **Chenyu** [[00:28:57](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1737)]
on the TinyGrad codebase

##### **Chenyu** [[00:28:58](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1738)]
it gives you 7000 errors

##### **Chenyu** [[00:29:00](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1740)]
so you know adding it would probably take a little bit to get it to work

##### **Sieds Lykles** [[00:29:04](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1744)]
but yeah I'll try and verify that it's actually seeing through the meta class

##### **Chenyu** [[00:29:11](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1751)]
yeah generally

##### **Chenyu** [[00:29:12](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1752)]
I think I also tried like

##### **Chenyu** [[00:29:14](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1754)]
something from Microsoft before

##### **Chenyu** [[00:29:16](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1756)]
or something

##### **Chenyu** [[00:29:17](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1757)]
so I can believe that there are

##### **Sieds Lykles** [[00:29:19](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1759)]
some other errors that's currently bypassed by MyPy

##### **Chenyu** [[00:29:24](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1764)]
MyPy is slow

##### **Chenyu** [[00:29:25](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1765)]
so

##### **Chenyu** [[00:29:27](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1767)]
in general

##### **Chenyu** [[00:29:28](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1768)]
we want faster like tooling

##### **Chenyu** [[00:29:31](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1771)]
and

##### **Sieds Lykles** [[00:29:31](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1771)]
just show

##### **Chenyu** [[00:29:33](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1773)]
it already seems to be faster

##### **Chenyu** [[00:29:35](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1775)]
so just show that it's like

##### **Chenyu** [[00:29:38](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1778)]
really on priority

##### **Chenyu** [[00:29:39](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1779)]
or if there's a

##### **Chenyu** [[00:29:42](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1782)]
like trade-off

##### **Sieds Lykles** [[00:29:43](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1783)]
at least we understand the trade-off

##### **Chenyu** [[00:29:46](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1786)]
otherwise I think we are generally supportive to like Unreal or tools

##### **Chenyu** [[00:29:51](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1791)]
okay

##### **Chenyu** [[00:29:52](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1792)]
okay

##### **Chenyu** [[00:29:53](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1793)]
the other thing I was wondering about is

##### **Chenyu** [[00:29:54](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1794)]
if there's a lot of stuff blocked on

##### **Sieds Lykles** [[00:29:56](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1796)]
getting autogen to work

##### **Chenyu** [[00:29:58](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1798)]
then maybe I should just finish up autogen and then

##### **Chenyu** [[00:30:00](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1800)]
do the pyre

##### **Chenyu** [[00:30:02](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1802)]
pyrefly stuff later

##### **Chenyu** [[00:30:03](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1803)]
but

##### **Chenyu** [[00:30:04](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1804)]
I don't know if that's true

##### **Sieds Lykles** [[00:30:06](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1806)]
I don't know

##### **Chenyu** [[00:30:07](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1807)]
NemoGen can decide this

##### **Chenyu** [[00:30:16](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1816)]
so

##### **Chenyu** [[00:30:17](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1817)]
I think if it's not a big deal

##### **Chenyu** [[00:30:26](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1826)]
then maybe just

##### **Chenyu** [[00:30:28](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1828)]
separate the issue

##### **Sieds Lykles** [[00:30:30](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1830)]
we can always use

##### **Chenyu** [[00:30:32](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1832)]
the upgrade MyPy

##### **Chenyu** [[00:30:34](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1834)]
or use something

##### **Chenyu** [[00:30:35](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1835)]
different later

##### **Chenyu** [[00:30:36](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1836)]
feel free to skip things

##### **Chenyu** [[00:30:38](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1838)]
that

##### **Sieds Lykles** [[00:30:39](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1839)]
just justify and make it

##### **Chenyu** [[00:30:42](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1842)]
your own

##### **Chenyu** [[00:30:42](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1842)]
yes

##### **Chenyu** [[00:30:43](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1843)]
yeah

##### **Chenyu** [[00:30:43](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1843)]
and if

##### **Chenyu** [[00:30:44](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1844)]
if it's a big deal

##### **Sieds Lykles** [[00:30:46](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1846)]
then we

##### **Chenyu** [[00:30:47](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1847)]
reconvene and see if we want to use a different type factor

##### **Chenyu** [[00:30:50](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1850)]
yeah

##### **Chenyu** [[00:30:51](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1851)]
the alternative thing that I thought about doing is

##### **Chenyu** [[00:30:53](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1853)]
you can generate

##### **Chenyu** [[00:30:54](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1854)]
pyi files

##### **Sieds Lykles** [[00:30:55](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1855)]
and that

##### **Chenyu** [[00:30:56](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1856)]
you know

##### **Chenyu** [[00:30:57](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1857)]
like you basically have a separate file that has all the types

##### **Chenyu** [[00:30:59](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1859)]
that doesn't

##### **Chenyu** [[00:30:59](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1859)]
get executed

##### **Chenyu** [[00:31:00](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1860)]
but it

##### **Sieds Lykles** [[00:31:01](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1861)]
MyPy reads it to try and understand what's going on

##### **Chenyu** [[00:31:04](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1864)]
and

##### **Chenyu** [[00:31:04](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1864)]
so generating

##### **Chenyu** [[00:31:05](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1865)]
the auto generating those as well would fix MyPy

##### **Chenyu** [[00:31:09](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1869)]
yeah

##### **Chenyu** [[00:31:10](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1870)]
I think

##### **Sieds Lykles** [[00:31:12](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1872)]
adding type stops in general is not a good idea

##### **Chenyu** [[00:31:15](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1875)]
it's just harder to maintain

##### **Chenyu** [[00:31:16](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1876)]
I think the goal for having type checker is to make development faster

##### **Chenyu** [[00:31:20](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1880)]
and more smooth

##### **Chenyu** [[00:31:21](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1881)]
and not adding too much more work

##### **Chenyu** [[00:31:23](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1883)]
okay

##### **Sieds Lykles** [[00:31:24](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1884)]
so

##### **Chenyu** [[00:31:25](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1885)]
so that's why

##### **Chenyu** [[00:31:26](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1886)]
if

##### **Chenyu** [[00:31:26](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1886)]
if it's like

##### **Chenyu** [[00:31:28](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1888)]
easy to understand

##### **Chenyu** [[00:31:29](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1889)]
easy to reproduce

##### **Sieds Lykles** [[00:31:30](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1890)]
and fix

##### **Chenyu** [[00:31:31](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1891)]
sometimes feel free to just like

##### **Chenyu** [[00:31:33](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1893)]
skip a few

##### **Chenyu** [[00:31:34](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1894)]
like type checking

##### **Chenyu** [[00:31:35](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1895)]
I think that's fine

##### **Chenyu** [[00:31:36](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1896)]
okay

##### **Sieds Lykles** [[00:31:37](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1897)]
that makes sense

##### **Chenyu** [[00:31:39](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1899)]
just making sure it's justified

##### **Chenyu** [[00:31:40](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1900)]
and not being lazy

##### **Chenyu** [[00:31:41](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1901)]
because

##### **Chenyu** [[00:31:42](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1902)]
I'm the person who has been like removing all the random cast

##### **Chenyu** [[00:31:45](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1905)]
that is wrong in the

##### **Sieds Lykles** [[00:31:46](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1906)]
in the repo

##### **Chenyu** [[00:31:47](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1907)]
so

##### **Chenyu** [[00:31:49](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1909)]
yeah

##### **Chenyu** [[00:31:50](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1910)]
yeah

##### **Chenyu** [[00:31:50](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1910)]
now I get it

##### **Chenyu** [[00:31:51](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1911)]
yeah

##### **Sieds Lykles** [[00:31:52](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1912)]
okay

##### **Chenyu** [[00:31:54](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1914)]
great

##### **Chenyu** [[00:31:55](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1915)]
yeah

##### **Chenyu** [[00:31:56](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1916)]
other auto gen stuff

##### **Chenyu** [[00:31:57](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1917)]
feel free to

##### **Chenyu** [[00:31:58](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1918)]
just add

##### **Sieds Lykles** [[00:32:00](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1920)]
okay

##### **Chenyu** [[00:32:00](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1920)]
you just see that moving forward

##### **Chenyu** [[00:32:04](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1924)]
okay

##### **Chenyu** [[00:32:07](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1927)]
you want

##### **Chenyu** [[00:32:08](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1928)]
did you want to add something

##### **Chenyu** [[00:32:12](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1932)]
hi

##### **Sieds Lykles** [[00:32:14](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1934)]
hi

##### **Chenyu** [[00:32:17](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1937)]
last week I fixed some f

##### **Chenyu** [[00:32:21](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1941)]
fp8 tends to cost speed issue

##### **Chenyu** [[00:32:26](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1946)]
and now I'm start doing

##### **Chenyu** [[00:32:28](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1948)]
bird train

##### **Chenyu** [[00:32:30](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1950)]
replace few layers

##### **Sieds Lykles** [[00:32:33](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1953)]
to fp8

##### **Chenyu** [[00:32:35](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1955)]
so

##### **Chenyu** [[00:32:37](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1957)]
the speed

##### **Chenyu** [[00:32:39](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1959)]
goes up

##### **Chenyu** [[00:32:42](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1962)]
like 5%

##### **Chenyu** [[00:32:44](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1964)]
but

##### **Sieds Lykles** [[00:32:46](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1966)]
the loss

##### **Chenyu** [[00:32:49](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1969)]
then goes down

##### **Chenyu** [[00:32:50](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1970)]
after it

##### **Chenyu** [[00:32:51](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1971)]
reach

##### **Chenyu** [[00:32:52](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1972)]
reach 4

##### **Chenyu** [[00:32:53](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1973)]
still working on it

##### **Sieds Lykles** [[00:32:58](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1978)]
okay

##### **Chenyu** [[00:32:59](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1979)]
you say you have

##### **Chenyu** [[00:33:01](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1981)]
training script

##### **Chenyu** [[00:33:02](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1982)]
that use fpa to train bird

##### **Chenyu** [[00:33:07](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1987)]
yeah

##### **Chenyu** [[00:33:08](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1988)]
currently I

##### **Sieds Lykles** [[00:33:09](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1989)]
I trained

##### **Chenyu** [[00:33:11](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1991)]
the

##### **Chenyu** [[00:33:12](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1992)]
using

##### **Chenyu** [[00:33:13](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1993)]
one gpu

##### **Chenyu** [[00:33:14](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1994)]
one gpu

##### **Chenyu** [[00:33:15](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1995)]
didn't

##### **Sieds Lykles** [[00:33:19](https://www.youtube.com/watch?v=gmY_RjZsYys&t=1999)]
didn't find the

##### **Chenyu** [[00:33:20](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2000)]
broken

##### **Chenyu** [[00:33:21](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2001)]
corner

##### **Chenyu** [[00:33:24](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2004)]
okay

##### **Chenyu** [[00:33:25](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2005)]
one gpu is fine

##### **Chenyu** [[00:33:27](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2007)]
so

##### **Sieds Lykles** [[00:33:28](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2008)]
I guess I

##### **Chenyu** [[00:33:30](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2010)]
I

##### **Chenyu** [[00:33:33](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2013)]
first

##### **Chenyu** [[00:33:34](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2014)]
I get it

##### **Chenyu** [[00:33:35](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2015)]
right

##### **Chenyu** [[00:33:36](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2016)]
using

##### **Sieds Lykles** [[00:33:37](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2017)]
one gpu

##### **Chenyu** [[00:33:38](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2018)]
then

##### **Chenyu** [[00:33:40](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2020)]
to

##### **Chenyu** [[00:33:40](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2020)]
I

##### **Chenyu** [[00:33:41](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2021)]
I

##### **Chenyu** [[00:34:12](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2052)]
right time

##### **Sieds Lykles** [[00:34:14](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2054)]
as already

##### **Chenyu** [[00:34:20](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2060)]
but

##### **Chenyu** [[00:34:22](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2062)]
right time

##### **Chenyu** [[00:34:40](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2080)]
so

##### **Chenyu** [[00:34:42](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2082)]
master should be using, I don't know, flow 16.

##### **Chenyu** [[00:34:45](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2085)]
Then try FP8 and measure the speed,

##### **Sieds Lykles** [[00:34:52](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2092)]
and also measure the loss curve.

##### **Chenyu** [[00:34:58](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2098)]
Yes.

##### **Chenyu** [[00:35:01](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2101)]
Sounds good.

##### **Chenyu** [[00:35:04](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2104)]
I see an AMD FP8 PR.

##### **Chenyu** [[00:35:09](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2109)]
You want that?

##### **Chenyu** [[00:35:13](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2113)]
Which one?

##### **Sieds Lykles** [[00:35:14](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2114)]
1, 2, 6, 3, 1.

##### **Chenyu** [[00:35:30](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2130)]
1, 2, 6, 3, 1.

##### **Chenyu** [[00:35:43](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2143)]
Anyway, it's one of your PR.

##### **Chenyu** [[00:35:45](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2145)]
You can check it later to see if you still need it.

##### **Chenyu** [[00:35:52](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2152)]
OK, let's move on.

##### **Chenyu** [[00:35:56](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2156)]
Good note, I didn't see any update.

##### **Sieds Lykles** [[00:35:59](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2159)]
It should be not changing at all.

##### **Chenyu** [[00:36:08](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2168)]
What else?

##### **Chenyu** [[00:36:11](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2171)]
Metal components.

##### **Chenyu** [[00:36:12](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2172)]
Compiler.

##### **Chenyu** [[00:36:12](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2172)]
Oh, so I realized the 3.14 BIM error was metal only,

##### **Chenyu** [[00:36:20](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2180)]
and seems to be the way we use metal compiler that's

##### **Sieds Lykles** [[00:36:24](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2184)]
causing issue.

##### **Chenyu** [[00:36:24](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2184)]
I don't really know what's happening,

##### **Chenyu** [[00:36:26](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2186)]
but it doesn't seem to be an issue for TinyGrip proper.

##### **Chenyu** [[00:36:36](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2196)]
OK.

##### **Chenyu** [[00:36:39](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2199)]
There's an update for Whisper.

##### **Chenyu** [[00:36:48](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2208)]
I mean, the output looks fine.

##### **Sieds Lykles** [[00:36:49](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2209)]
I don't know.

##### **Chenyu** [[00:36:50](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2210)]
Is there a demo or a website that we can try?

##### **Chenyu** [[00:37:03](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2223)]
Yeah, because it's two bounties, right?

##### **Chenyu** [[00:37:05](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2225)]
Like, one is having a Whisper in TinyGrip and just running

##### **Chenyu** [[00:37:11](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2231)]
in a web browser.

##### **Chenyu** [[00:37:12](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2232)]
So I think it's a good idea to have a website demo.

##### **Sieds Lykles** [[00:37:13](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2233)]
So if that's good, we can start to review and merge

##### **Chenyu** [[00:37:16](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2236)]
those code first.

##### **Chenyu** [[00:37:19](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2239)]
Then for it to handle much longer videos and stuff

##### **Chenyu** [[00:37:24](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2244)]
can be separate.

##### **Chenyu** [[00:37:26](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2246)]
I mean, up to you to decide how do you want to paste this.

##### **Chenyu** [[00:37:29](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2249)]
But this has also been for a while.

##### **Sieds Lykles** [[00:37:32](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2252)]
So it's probably a good idea to have something smaller that's

##### **Chenyu** [[00:37:35](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2255)]
been merged and improved.

##### **Chenyu** [[00:37:42](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2262)]
I don't think other things are being worked on.

##### **Chenyu** [[00:37:50](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2270)]
Oh, can we have a script that has 100 on next model?

##### **Chenyu** [[00:37:54](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2274)]
Do we have it already?

##### **Chenyu** [[00:38:04](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2284)]
My point is it can be separate as long as you have something

##### **Sieds Lykles** [[00:38:09](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2289)]
that's already working.

##### **Chenyu** [[00:38:11](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2291)]
I'm excited.

##### **Chenyu** [[00:38:12](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2292)]
I think we can add this one with WebGPU and it's

##### **Chenyu** [[00:38:15](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2295)]
an improvement over current stuff.

##### **Chenyu** [[00:38:18](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2298)]
Currently, we don't have anything.

##### **Chenyu** [[00:38:19](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2299)]
So anything you have is an improvement.

##### **Sieds Lykles** [[00:38:21](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2301)]
Then that's part of the bounty.

##### **Chenyu** [[00:38:24](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2304)]
And the other part is the performance

##### **Chenyu** [[00:38:25](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2305)]
over very long audio.

##### **Chenyu** [[00:38:33](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2313)]
OK.

##### **Chenyu** [[00:38:36](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2316)]
Great.

##### **Chenyu** [[00:38:39](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2319)]
Oh.

##### **Sieds Lykles** [[00:38:40](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2320)]
Onyx.

##### **Chenyu** [[00:38:43](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2323)]
Other bounty.. so I think all the flash attention ones is kind of on the main TinyGrid team.

##### **Chenyu** [[00:38:53](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2333)]
I see several attempts for remove tensor.pool alternative, and pretty much everyone is doing the same thing that's not working.

##### **Chenyu** [[00:39:04](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2344)]
So don't do that.

##### **Chenyu** [[00:39:05](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2345)]
For the PyTorch backend one, you should be able to re-enable the PyTorch test in CI, and that should be passing to start with.

##### **Chenyu** [[00:39:16](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2356)]
Any attempt to fix that and claim all the tests passed is because those tests are currently skipped in CI.

##### **Sieds Lykles** [[00:39:28](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2368)]
What else do we have?

##### **Chenyu** [[00:39:33](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2373)]
Uh..

##### **Chenyu** [[00:39:43](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2383)]
Anyway, if this meeting has any other questions or things to add, you can ask in general channel or look at for this meeting.

##### **Chenyu** [[00:39:56](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2396)]
I think starting from next week, we'll probably keep meeting at this time if it works for everyone, because we are back to the United States and we can do this.

##### **Chenyu** [[00:40:05](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2405)]
We cannot wake up to production for you.

##### **Chenyu** [[00:40:11](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2411)]
Okay.

##### **Sieds Lykles** [[00:40:26](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2426)]
So I don't see anything else.

##### **Chenyu** [[00:40:28](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2428)]
I think that's it for this meeting.

##### **Chenyu** [[00:40:32](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2432)]
Next.

##### **Chenyu** [[00:40:33](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2433)]
So this..

##### **Chenyu** [[00:40:34](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2434)]
Saturday is CommaCon, commerce conference, and I think TinyCorp has a booth.

##### **Chenyu** [[00:40:44](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2444)]
I will be there, George will be there, and some other people, Wolfberry will also be there.

##### **Sieds Lykles** [[00:40:49](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2449)]
People will be there.

##### **Chenyu** [[00:41:02](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2462)]
I mean, if performance regressed significantly, that means it's not running the same kernel.

##### **Chenyu** [[00:41:10](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2470)]
So that doesn't meet the bounty requirements.

##### **Chenyu** [[00:41:13](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2473)]
The bounty requirement is to keep the kernels the same.

##### **Chenyu** [[00:41:18](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2478)]
You might need to change the kernel.

##### **Chenyu** [[00:41:20](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2480)]
You might need to change part of the kernel path so that the two variants give you the same kernel output, but it cannot be significantly slower.

##### **Sieds Lykles** [[00:41:34](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2494)]
That make sense?

##### **Chenyu** [[00:41:36](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2496)]
Okay.

##### **Chenyu** [[00:41:36](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2496)]
So..

##### **Chenyu** [[00:41:40](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2500)]
Yeah.

##### **Chenyu** [[00:41:41](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2501)]
The goal of that bounty is not just remove that if block that I can already do, and I'm sure I already did.

##### **Chenyu** [[00:41:48](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2508)]
And that's why everyone is copying that.

##### **Sieds Lykles** [[00:41:51](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2511)]
The goal is to realize why unfold is not working.

##### **Chenyu** [[00:41:55](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2515)]
That's one.

##### **Chenyu** [[00:41:56](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2516)]
And see what's caused the difference.

##### **Chenyu** [[00:42:00](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2520)]
I know there are some parameters that's slightly permuted.

##### **Chenyu** [[00:42:05](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2525)]
So I think let's..

##### **Chenyu** [[00:42:06](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2526)]
We will fix it, but I'm not sure.

##### **Sieds Lykles** [[00:42:08](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2528)]
And that's why it's a bounty.

##### **Chenyu** [[00:42:17](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2537)]
Great.

##### **Chenyu** [[00:42:18](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2538)]
Yeah, I think..

##### **Chenyu** [[00:42:19](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2539)]
No, I think the unfold thing is just because some are probably not handled correctly, and there's an off-by-one somewhere.

##### **Chenyu** [[00:42:31](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2551)]
But yeah.

##### **Chenyu** [[00:42:32](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2552)]
Basically, the goal is to merge the two branches into one.

##### **Sieds Lykles** [[00:42:36](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2556)]
into one so that it generates the same kernel regardless of your dilation and stripe

##### **Chenyu** [[00:42:45](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2565)]
so that's a goal of that bounty

##### **Chenyu** [[00:42:54](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2574)]
uh see anything else so I think that's the meeting for this week

##### **Chenyu** [[00:43:00](https://www.youtube.com/watch?v=gmY_RjZsYys&t=2580)]
uh thank you everyone and see you next week
