# 2026-03-03 Meeting

### Meeting Agenda

**Time:** 9am Monday San Diego time
- company update
- comma issues
- IMAGE=1
- CALL/BUFFER_VIEW, sym llm
- assign, setitem, disk
- drivers
- llama
- VIZ
- other issue, bounties

### Audio

[Youtube Link](https://www.youtube.com/watch?v=0VOafsXYdNA)

### Highlights

- **[Company Update](#geohot-000021)**: Tinygrad is getting traction on Twitter; people are using it for different projects (including connecting WebGPU pieces), though it’s still seen as “slow” compared to Torch for serious workloads.
- **[Hardware/Cost Headwinds](#geohot-000139)**: Tinybox parts (especially RAM) have gotten dramatically more expensive; GPU pricing and availability are shifting (e.g., “Blackwell” prices up; comments about limited 5090 availability).
- **[Product Direction](#geohot-000441)**: Clear product vision: sell inference boxes “under your desk” aimed at running coding assistants (mentions Claude Code / OpenCode) and needing easy tokens/sec messaging.
- **[Comma Issues: CI & Perf Guardrails](#chenyu-000635)**: Plan is to run Comma-related checks in CI to prevent regressions; focus on the most important request first, and keep thresholds relaxed (e.g., allow up to ~2× before failing) rather than tight % deltas.
- **[Owner Assigned for Comma Requests](#geohot-000852)**: Chrism is assigned as the point-person to triage and maintain the Comma account; Comma requests are prioritized above other work items.
- **[IMAGE=1 Kernel Count Progress + Indexing Bottleneck](#chrism-000931)**: IMAGE=1 kernels reduced to ~125 (IMAGE=2 ~123); remaining performance gap is largely indexing/shape heuristics, not small kernel micro-differences.
- **[VIZ/Disassembly Blocker on Qualcomm](#chrism-000959)**: Disassembly in VIZ broke when compilation moved onto-device; renderer can’t compile without device access, so workflow needs adjustment (likely manual compile path).
- **[Render API / Multi-Device Use Case](#chrism-001518)**: Key target is Comma’s split-device workflow (e.g., LLVM for AMD + Qualcomm CL for Qualcomm) and ensuring the API is correct and usable; cross-compiling mixed kernels is acknowledged as inherently complex.
- **[Next 2 Weeks: llm.py + JIT Replacement via `call`](#geohot-001746)**: Geohot plans to focus on `llm.py`, possibly replacing parts of JIT; `call` is working well, improves VIZ readability, and should work for training once remaining bugs are fixed.
- **[Buffer-view & Memory Planning](#geohot-002049)**: Buffer-view is positioned as the foundation for moving the memory planner into the graph: unify internal buffers into one backing buffer with views; clarify that `.contiguous` doesn’t imply a new buffer (use `.clone`/`assign` for new buffers).
- **[Realize=0: Run LLM Directly from GGUF for Speed](#geohot-002233)**: Plan to prefer `realize=0` so the LLM runs straight from GGUF (fewer copies, higher tokens/sec because it’s memory-bandwidth bound); buffer-view is needed so offsets stay outside compiled kernels and avoid recompiles.
- **[Driver Updates: MI300/MI350 Stability + Timeouts](#nimlgen-002156)**: MI350 stability improved (line recovery, usable with agents); implementing “kill long-run kernels” via a timeout/recovery path; still investigating performance gaps (warmup/clocking).
- **[Memory Planner Project Ownership](#geohot-002534)**: Nimlgen will start on moving the memory planner to operate on the graph; longer-term direction includes moving HTQ command-buffer compilation into the graph output.
- **[Llama Training Deadline + Must-Have Activation Checkpointing](#geohot-004649)**: Deadline urgency called out (“~10 weeks”); current runs are several GB over memory; activation checkpointing is required, and `call` is framed as the mechanism to enable it cleanly.
- **[Kick Off a 70B Training Smoke Run](#geohot-004921)**: Plan to start a 70B training run for a small number of steps to surface issues early and make speed/memory problems more representative and parallelizable.
- **[SQTT Gift + VIZ/Profiler Improvements](#geohot-005315)**: AMD’s SQTT tooling is now open-sourced; plan is to switch to AMD’s naming/enums across CDNA/RDNA3/RDNA4; VIZ improvements include expandable call graphs and faster profiling that now runs on Llama without OOM.
- **[Cleanup & PR Hygiene + Bounties](#geohot-005754)**: Request to close old PRs; CDNA bounty is close but must run key assembly/hip-kernels; ongoing emphasis on staying on top of external contributors.
- **[Cache Keys: Hash and Save All Context](#geohot-005936)**: For schedule/beam cache keys, decision trend is to include all relevant context and hash it to reduce misuse and confusion from partial context capture.

### Transcript
##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=0VOafsXYdNA&t=0)]
Hi, everyone. So for the logistic, I think next week is some weird daylight saving stuff. We will figure out the exact time. I will also be in Hong Kong, so we will see.

##### **Chrism** [[00:00:16](https://www.youtube.com/watch?v=0VOafsXYdNA&t=16)]
Great.

##### **Chenyu** [[00:00:17](https://www.youtube.com/watch?v=0VOafsXYdNA&t=17)]
But yeah, that's for next week. We're going to start with company updates.

##### **Geohot** [[00:00:21](https://www.youtube.com/watch?v=0VOafsXYdNA&t=21)]
Yeah, a lot of Tinygrad is starting to get some traction on Twitter. A lot of people using it for a lot of different things.

##### **Chenyu** [[00:00:30](https://www.youtube.com/watch?v=0VOafsXYdNA&t=30)]
Say more.

##### **Geohot** [[00:00:33](https://www.youtube.com/watch?v=0VOafsXYdNA&t=33)]
Now people are using it. Like some guy used it to connect some web GPU stuff together.

##### **Chenyu** [[00:00:41](https://www.youtube.com/watch?v=0VOafsXYdNA&t=41)]
I saw two people complaining it's too slow.

##### **Geohot** [[00:00:45](https://www.youtube.com/watch?v=0VOafsXYdNA&t=45)]
Well, yeah, it's too slow. Oh, that was people using tiny boxes. With Tinygrad, I can now do federated training.

##### **Chenyu** [[00:00:57](https://www.youtube.com/watch?v=0VOafsXYdNA&t=57)]
There was at least one person. Who claimed they used Tinygrad for prototype because it works for prototype. Then once it's good, they move to torch.

##### **Geohot** [[00:01:09](https://www.youtube.com/watch?v=0VOafsXYdNA&t=69)]
Yeah, well, it's slow.

##### **Chrism** [[00:01:13](https://www.youtube.com/watch?v=0VOafsXYdNA&t=73)]
Okay.

##### **Geohot** [[00:01:14](https://www.youtube.com/watch?v=0VOafsXYdNA&t=74)]
Um, yeah, no, I'm working on, so I'm working on LLM. I mean, that's kind of, we get a, we get a sell these things as like LLM inference boxes. We have to figure out how to get the most tokens per second easily on these things, because. Now there's actually people who want to like use LLM. Did I use LLM?

##### **Geohot** [[00:01:35](https://www.youtube.com/watch?v=0VOafsXYdNA&t=95)]
Great.

##### **Geohot** [[00:01:39](https://www.youtube.com/watch?v=0VOafsXYdNA&t=99)]
Uh, yeah. I don't know. Everything's very expensive. All the tiny box parts are RAM is so expensive. It's like $500 for one stick. In October it was $98.

##### **Geohot** [[00:01:55](https://www.youtube.com/watch?v=0VOafsXYdNA&t=115)]
And now it's 500. Yeah. Yeah.

##### **Geohot** [[00:02:02](https://www.youtube.com/watch?v=0VOafsXYdNA&t=122)]
Um, and video raised the price of the black wells. AMD hasn't seriously raised the price yet, but it's cause they're on the GDR six is easier to get. BDDR seven and DDR five have really gotten a huge price hike. Um, and video is not making any more 50 nineties apparently.

##### **Geohot** [[00:02:27](https://www.youtube.com/watch?v=0VOafsXYdNA&t=147)]
Oh yeah.

##### **Geohot** [[00:02:28](https://www.youtube.com/watch?v=0VOafsXYdNA&t=148)]
I mean, prices go up. So, uh, people are finally like, like, you know what it is. It's not even tiny grant. I see people saying they're using their tiny box to run things.

##### **Chenyu** [[00:02:40](https://www.youtube.com/watch?v=0VOafsXYdNA&t=160)]
Oh, I be happy. I thought it's a good how we're I mean, are they complaining? Penny bucks is too slow.

##### **Geohot** [[00:02:50](https://www.youtube.com/watch?v=0VOafsXYdNA&t=170)]
No, no, no, no. Tiny gratitude is slow, but tiny box is very good. Yeah.

##### **Chenyu** [[00:02:54](https://www.youtube.com/watch?v=0VOafsXYdNA&t=174)]
It's good. You're so good to be you. Uh, especially. Yeah. The black ones, not the red box.

##### **Geohot** [[00:03:03](https://www.youtube.com/watch?v=0VOafsXYdNA&t=183)]
I'm not the red box. Those don't work, but, uh, when 3.5, four, three 97 B and the F people are running quite well on the V two black and doing a better job than Opus in many categories.

##### **Chenyu** [[00:03:17](https://www.youtube.com/watch?v=0VOafsXYdNA&t=197)]
Yeah. Learning model.

##### **Geohot** [[00:03:20](https://www.youtube.com/watch?v=0VOafsXYdNA&t=200)]
Awesome. Won't randomly degrade to crap like Opus when they run out of capacity.

##### **Chenyu** [[00:03:28](https://www.youtube.com/watch?v=0VOafsXYdNA&t=208)]
No, I try. I try our. I swear. You're going to undo into Indoreggs for strategically esasalent routing showing worse than serve

##### **Geohot** [[00:03:35](https://www.youtube.com/watch?v=0VOafsXYdNA&t=215)]
This one is great when you're wrong, character usage calm, safe.

##### **Chrism** [[00:03:41](https://www.youtube.com/watch?v=0VOafsXYdNA&t=221)]
Cool Yeah.

##### **Geohot** [[00:03:46](https://www.youtube.com/watch?v=0VOafsXYdNA&t=226)]
So, uh, so the latency on our italics.

##### **Chrism** [[00:03:51](https://www.youtube.com/watch?v=0VOafsXYdNA&t=231)]
We, um, we'll do it better than ever commonly.

##### **Geohot** [[00:03:54](https://www.youtube.com/watch?v=0VOafsXYdNA&t=234)]
Not lagging as much as I did, Stan. Okay. Bring it back to as I get. I can't hear you on recording. Can you take the camera off your ass and answer that? I'm working on fully symbolic LLM. And we have a product. People always ask for the tiny box, so like how many tokens per second? And I'm like, oh, I'm not going to benchmark it in VLLM.

##### **Geohot** [[00:04:24](https://www.youtube.com/watch?v=0VOafsXYdNA&t=264)]
We probably still don't have a good solution for MOU. For MOU? Yeah. Just because of the sort thing? I don't think that's that hard.

##### **Chenyu** [[00:04:37](https://www.youtube.com/watch?v=0VOafsXYdNA&t=277)]
Oh, I don't know what's the curve bottleneck, but it's not fast.

##### **Geohot** [[00:04:41](https://www.youtube.com/watch?v=0VOafsXYdNA&t=281)]
I know, but I don't think anyone's really looked into it. I don't think that the problem is MOU specific. I think that we have a bunch of other things to fix in the LLM example first. Before we get to MOU, if prefill takes 15 seconds, that's way too long. OK. Yeah. But we have a product. We have a clear product vision. I don't know about training. I could talk about all that stuff. But the clear product vision is we sell boxes that run Claude code under your desk.

##### **Geohot** [[00:05:16](https://www.youtube.com/watch?v=0VOafsXYdNA&t=316)]
Claude code? Well, OpenCode. OpenCode's actually better. I use OpenCode with Claude to the dismay of Claude people.

##### **Chrism** [[00:05:27](https://www.youtube.com/watch?v=0VOafsXYdNA&t=327)]
Cool.

##### **Geohot** [[00:05:29](https://www.youtube.com/watch?v=0VOafsXYdNA&t=329)]
Yeah. OpenCode with the box under your desk. Great. Sounds good. OK.

##### **Chenyu** [[00:05:40](https://www.youtube.com/watch?v=0VOafsXYdNA&t=340)]
Do we get any new complaints per comma? Have we fixed their old complaint?

##### **Chrism** [[00:05:47](https://www.youtube.com/watch?v=0VOafsXYdNA&t=347)]
No.

##### **Chenyu** [[00:05:48](https://www.youtube.com/watch?v=0VOafsXYdNA&t=348)]
Happy?

##### **Chrism** [[00:05:50](https://www.youtube.com/watch?v=0VOafsXYdNA&t=350)]
Yeah. So, I mean, Armand gave me a thing to put in CI. I don't know. At least should be putting this in benchmarks and stuff.

##### **Chrism** [[00:06:08](https://www.youtube.com/watch?v=0VOafsXYdNA&t=368)]
I'm glad I have a full confessed to looking at homework with these dumb familia is available using CI.

##### **Chenyu** [[00:06:35](https://www.youtube.com/watch?v=0VOafsXYdNA&t=395)]
Yeah, I think the general principle is we definitely want to see it running in CI. And we decide. Because sometimes it's like we do very stupid things that regress their need. Let those we should fix. And then the next is, are they happy with the current state? No, we can discuss with them. Otherwise, we just don't regress. And I think that's good enough.

##### **Geohot** [[00:07:07](https://www.youtube.com/watch?v=0VOafsXYdNA&t=427)]
Well, so if we just put it in timings, nobody's going to look at it. I think we should have assertions for time. But the assertion should not be 10% more. There should be like 2x more.

##### **Chenyu** [[00:07:16](https://www.youtube.com/watch?v=0VOafsXYdNA&t=436)]
Yeah. It's like you can put a more relaxed on the 2x.

##### **Chrism** [[00:07:23](https://www.youtube.com/watch?v=0VOafsXYdNA&t=443)]
Yeah. Yeah, yeah. Let's just run it a couple of times and make sure it's not super high. It's just a little bit of experience.

##### **Chenyu** [[00:07:32](https://www.youtube.com/watch?v=0VOafsXYdNA&t=452)]
That's probably fine. It can start with like 2x, as Stuart said.

##### **Geohot** [[00:07:35](https://www.youtube.com/watch?v=0VOafsXYdNA&t=455)]
Something like sensible. Yeah. OK. People loading speed. And compile time. I mean, yeah, we have to like get a nice profile

##### **Geohot** [[00:07:54](https://www.youtube.com/watch?v=0VOafsXYdNA&t=474)]
and get a breakdown of what they mean by compile time. They manage to run model.

##### **Chrism** [[00:08:00](https://www.youtube.com/watch?v=0VOafsXYdNA&t=480)]
Yeah. Yeah. I mean, apparently it works. Yeah, I don't know. I actually need to ask a little bit more details

##### **Chrism** [[00:08:09](https://www.youtube.com/watch?v=0VOafsXYdNA&t=489)]
about what they mean by compile time. Because right now, like Arman gave me a script that, well, it wraps a lot more than what I would consider compiling. But it's the amount of time to generate the pickle.

##### **Chenyu** [[00:08:20](https://www.youtube.com/watch?v=0VOafsXYdNA&t=500)]
Yeah, so we just need to distinguish between what's acceptable for them and what's good to have. And we need to try. And if they try very hard to make it work, then if they want to go above and optimize those things in tiny bits, we'll come.

##### **Chrism** [[00:08:37](https://www.youtube.com/watch?v=0VOafsXYdNA&t=517)]
Yeah. I mean, my impression was that the compile time is much more of a nice to have thing, whereas the pickle loading is like very ..

##### **Chenyu** [[00:08:45](https://www.youtube.com/watch?v=0VOafsXYdNA&t=525)]
So usually when comma asks for three things, just find the most important one and start from there.

##### **Chrism** [[00:08:52](https://www.youtube.com/watch?v=0VOafsXYdNA&t=532)]
Yeah.

##### **Geohot** [[00:08:52](https://www.youtube.com/watch?v=0VOafsXYdNA&t=532)]
Yeah. So Chris, from now on, you are responsible for maintaining the comma account. OK. So any comma requests go straight to you.

##### **Chrism** [[00:09:03](https://www.youtube.com/watch?v=0VOafsXYdNA&t=543)]
OK.

##### **Geohot** [[00:09:03](https://www.youtube.com/watch?v=0VOafsXYdNA&t=543)]
And then you triage them, figure out what we're going to do. And they're higher priority than image equals 1. They're higher priority than anything else. Now we have a clear role.

##### **Chenyu** [[00:09:13](https://www.youtube.com/watch?v=0VOafsXYdNA&t=553)]
And also ask them just open the issue. It's always easier if it's written down, not just verbally say, please do this, so that no one will do.

##### **Chrism** [[00:09:23](https://www.youtube.com/watch?v=0VOafsXYdNA&t=563)]
Yeah. OK.

##### **Chenyu** [[00:09:27](https://www.youtube.com/watch?v=0VOafsXYdNA&t=567)]
OK. Next. Chris, still yours?

##### **Chrism** [[00:09:31](https://www.youtube.com/watch?v=0VOafsXYdNA&t=571)]
Yeah. Yeah. So I mean, this morning I merged something that gets the number of kernels for image equals 1 down to 125. Image equals 2 gets 123. I know what the last two are, but I don't know. When I profiled it, it was like 0.05 milliseconds difference.

##### **Geohot** [[00:09:53](https://www.youtube.com/watch?v=0VOafsXYdNA&t=593)]
I don't care. It's not slower.

##### **Chrism** [[00:09:54](https://www.youtube.com/watch?v=0VOafsXYdNA&t=594)]
OK.

##### **Chrism** [[00:09:57](https://www.youtube.com/watch?v=0VOafsXYdNA&t=597)]
But. OK. Yeah.

##### **Chrism** [[00:09:59](https://www.youtube.com/watch?v=0VOafsXYdNA&t=599)]
So the big difference right now is all down to indexing. And so it's a little frustrating because the like, pushing the CL compiler to compile in the device means that the disassembly doesn't work in Qualcomm anymore. Like you can't do it. You can't view disassembly in Viz anymore. So I just need to look like I should have to compile it manually.

##### **Geohot** [[00:10:21](https://www.youtube.com/watch?v=0VOafsXYdNA&t=621)]
Why can't you do the disassembly in Viz?

##### **Chrism** [[00:10:24](https://www.youtube.com/watch?v=0VOafsXYdNA&t=624)]
Because the disassembler is on, the disassemble function is on the renderer. But the renderer doesn't have the device.

##### **Geohot** [[00:10:31](https://www.youtube.com/watch?v=0VOafsXYdNA&t=631)]
So therefore, I can't compile. So I can't do anything. Oh. You get that common device working?

##### **Chrism** [[00:10:39](https://www.youtube.com/watch?v=0VOafsXYdNA&t=639)]
I did. I mean, mostly I was just switching.

##### **Geohot** [[00:10:42](https://www.youtube.com/watch?v=0VOafsXYdNA&t=642)]
It works.

##### **Chrism** [[00:10:43](https://www.youtube.com/watch?v=0VOafsXYdNA&t=643)]
It does work.

##### **Chrism** [[00:10:43](https://www.youtube.com/watch?v=0VOafsXYdNA&t=643)]
Correct.

##### **Geohot** [[00:10:44](https://www.youtube.com/watch?v=0VOafsXYdNA&t=644)]
Yeah. And has it done the burnout?

##### **Chrism** [[00:10:46](https://www.youtube.com/watch?v=0VOafsXYdNA&t=646)]
It didn't for me.

##### **Geohot** [[00:10:48](https://www.youtube.com/watch?v=0VOafsXYdNA&t=648)]
That's it.

##### **Chrism** [[00:10:49](https://www.youtube.com/watch?v=0VOafsXYdNA&t=649)]
The thing that's different, though, is that this one's running like the display server, whereas the other one is running just some more

##### **Chrism** [[00:10:55](https://www.youtube.com/watch?v=0VOafsXYdNA&t=655)]
just like a PNG. But there's nothing.

##### **Chrism** [[00:10:58](https://www.youtube.com/watch?v=0VOafsXYdNA&t=658)]
There's nothing.

##### **Chrism** [[00:10:59](https://www.youtube.com/watch?v=0VOafsXYdNA&t=659)]
There's no difference there. The one that we have also. Yeah, but this one's running all this stuff. We should run all that stuff.

##### **Geohot** [[00:11:08](https://www.youtube.com/watch?v=0VOafsXYdNA&t=668)]
All that stuff is good. runs all that.

##### **Chrism** [[00:11:13](https://www.youtube.com/watch?v=0VOafsXYdNA&t=673)]
Yeah, it is different from what's currently on the other devices. The call for it will be different. Do you want to use the G2 3D UI?

##### **Geohot** [[00:11:23](https://www.youtube.com/watch?v=0VOafsXYdNA&t=683)]
Oh. I was like, . But yeah, any case.

##### **Chrism** [[00:11:32](https://www.youtube.com/watch?v=0VOafsXYdNA&t=692)]
Yeah, that's the big difference is that indexing and .. OK.

##### **Chenyu** [[00:11:37](https://www.youtube.com/watch?v=0VOafsXYdNA&t=697)]
Yeah. Have you checked if all the D type ALU are doing in the desired D type? Because I saw that the old image has a hack that says basically the D type promotion doesn't work if it's like, oh, I'm going to do an image half. Instead of upgrading the image half to floats, I think it does some hack to emote the other thing to half. So by not doing that, you might be doing .. And we lost.

##### **Geohot** [[00:12:12](https://www.youtube.com/watch?v=0VOafsXYdNA&t=732)]
We can't hear anything.

##### **Chenyu** [[00:12:15](https://www.youtube.com/watch?v=0VOafsXYdNA&t=735)]
So I think for, can you hear me now?

##### **Geohot** [[00:12:21](https://www.youtube.com/watch?v=0VOafsXYdNA&t=741)]
Hello?

##### **Chrism** [[00:12:23](https://www.youtube.com/watch?v=0VOafsXYdNA&t=743)]
.

##### **Geohot** [[00:12:23](https://www.youtube.com/watch?v=0VOafsXYdNA&t=743)]
. . Maybe his internet .. Hello? Hello? . . For the current year. Hi. Other people hear me talk? Can other people hear talking? I can hear you talk. . I can hear both of you. OK, good. But you can hear Chen Yu. Hi. Yeah. Oh, fine. I can hear both of you. OK, I'll try rejoining.

##### **Chrism** [[00:13:01](https://www.youtube.com/watch?v=0VOafsXYdNA&t=781)]
.

##### **Geohot** [[00:13:02](https://www.youtube.com/watch?v=0VOafsXYdNA&t=782)]
Yeah, I don't know. OK.

##### **Chrism** [[00:13:06](https://www.youtube.com/watch?v=0VOafsXYdNA&t=786)]
Well, you got cut off when you were talking about some image hack.

##### **Chenyu** [[00:13:11](https://www.youtube.com/watch?v=0VOafsXYdNA&t=791)]
Yeah, so image half, I think when it does ALU to a float, instead of upcast the image half to float, I think there was a half. somewhere that the most let float to have. So you do more stuff in. I don't know how does that work in image one.

##### **Chrism** [[00:13:34](https://www.youtube.com/watch?v=0VOafsXYdNA&t=814)]
Wait, so you're thinking, OK, wait, so this is to ensure that the math actually happens in, oh, I see. Yeah, yeah, yeah.

##### **Geohot** [[00:13:40](https://www.youtube.com/watch?v=0VOafsXYdNA&t=820)]
The math should happen in float.

##### **Chrism** [[00:13:41](https://www.youtube.com/watch?v=0VOafsXYdNA&t=821)]
Yeah, yeah, yeah. I will double check this, but I'm almost certain

##### **Chrism** [[00:13:47](https://www.youtube.com/watch?v=0VOafsXYdNA&t=827)]
that all the math is happening in float.

##### **Chrism** [[00:13:50](https://www.youtube.com/watch?v=0VOafsXYdNA&t=830)]
Cool.

##### **Chrism** [[00:13:52](https://www.youtube.com/watch?v=0VOafsXYdNA&t=832)]
I mean, I've looked through the generated code, and it appears that it's all happening in float.

##### **Geohot** [[00:13:58](https://www.youtube.com/watch?v=0VOafsXYdNA&t=838)]
That GPU is entirely bottlenecked by the memory path, the cache feed.

##### **Chrism** [[00:14:05](https://www.youtube.com/watch?v=0VOafsXYdNA&t=845)]
Yeah, and also the Qualcomm CL compiler sometimes very frequently breaks as soon as you try and do math in half.

##### **Chrism** [[00:14:10](https://www.youtube.com/watch?v=0VOafsXYdNA&t=850)]
Yeah, yeah, you're right.

##### **Chrism** [[00:14:11](https://www.youtube.com/watch?v=0VOafsXYdNA&t=851)]
So I'm almost certain it's all happening in float.

##### **Chenyu** [[00:14:17](https://www.youtube.com/watch?v=0VOafsXYdNA&t=857)]
So it's basically just indexing, not cancel all.

##### **Chrism** [[00:14:24](https://www.youtube.com/watch?v=0VOafsXYdNA&t=864)]
Yeah, so the shapes that the image equals one thing, like the shapes for the image buffers, they're not the same. It's flat, right?

##### **Chenyu** [[00:14:32](https://www.youtube.com/watch?v=0VOafsXYdNA&t=872)]
What's that? Sorry? For now, it's like a very flat shape.

##### **Chrism** [[00:14:37](https://www.youtube.com/watch?v=0VOafsXYdNA&t=877)]
Well, it tries to choose the most optimal one based on how many valid it can remove and also how complicated the indexing math ends up being. But they're not identical. And it seems to be. Like. Yeah. I don't know. I need to find a better heuristic for this,

##### **Geohot** [[00:14:53](https://www.youtube.com/watch?v=0VOafsXYdNA&t=893)]
because clearly this one is not optimal.

##### **Chrism** [[00:14:58](https://www.youtube.com/watch?v=0VOafsXYdNA&t=898)]
OK.

##### **Geohot** [[00:15:04](https://www.youtube.com/watch?v=0VOafsXYdNA&t=904)]
Sounds good. Anything else? I think that's it.

##### **Chenyu** [[00:15:14](https://www.youtube.com/watch?v=0VOafsXYdNA&t=914)]
Anything for the render API?

##### **Chrism** [[00:15:18](https://www.youtube.com/watch?v=0VOafsXYdNA&t=918)]
Yeah. I mean, so we just have to think more about the use case here. I think the biggest example is Comma's use case, where they're running some stuff on one device and some stuff on another device. So we just have to really make sure we support that well. And that's basically, OK, well, I want to use LLVM for the AMD stuff, but I want to use Qualcomm CL for the Qualcomm stuff. But just making sure that we have a good, you know, like, a good, good, good, good, good, good, good, good, good, good, good API that makes sense and is easy to use for this use case. I mean, one of the questions is, like, OK, well, what if you have, like, you know, two different GPUs? Like, you have two AMD GPUs, but there are two different models on your system. Like, how do we want to handle that? And so this seems like a much more rare use case, but it's something that we're worried about handling, then that's the bigger question. I think overall, most of the stuff I've proposed in the tip is sound, but I mean, it's a matter of, like, testing out use cases and making sure that they all make sense within this case. Yeah, I mean, one of the questions is also, like, OK, so if you're cross compiling and you want to cross compile some kernels for AMD and some kernels for Qualcomm or something like this, then you kind of end up with a, like, that pattern is very complicated, I think.

##### **Chrism** [[00:16:48](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1008)]
And I think that's the one use case where it's not correct.

##### **Chrism** [[00:16:55](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1015)]
But yeah.

##### **Geohot** [[00:16:59](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1019)]
I don't know how common that pattern is.

##### **Chrism** [[00:17:02](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1022)]
No matter what, that pattern is going to be complicated.

##### **Chenyu** [[00:17:04](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1024)]
I think we have good .. The important thing is to make the separation that no matter how complicated the pattern is, down to exact items, things are, like, expressed correctly. Then higher level, how do you make sure, how do you flag those things properly and pipe it through?

##### **Geohot** [[00:17:27](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1047)]
Yeah. Yeah. It's going to be use case dependent.

##### **Chrism** [[00:17:29](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1049)]
For sure. Yeah, yeah. I mean, correctness is obviously the most important factor. But yeah. I mean, yeah, yeah.

##### **Geohot** [[00:17:38](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1058)]
OK. Sounds good. Pete?

##### **Chenyu** [[00:17:43](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1063)]
Next is George, your stuff.

##### **Geohot** [[00:17:46](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1066)]
Yeah. So I'm going to work the next two weeks on llm.py. And this might also include the JIT replacement. So call worked pretty well now. It has its own set of foot guns. But they're less bad than the JIT foot guns. And call also finally makes the, like, viz stuff very viewable. You can, like, view the llm. And it shows you, like, beat forward attention, beat forward attention. It works for training as well. But you have to fix the bug in. Yeah. So once there's the only bug, it works for training. It doesn't work with the hip kittens attention because of how when you can't save the forwards for later, you have to extract them from the call. You have to, like, your backwards function can't assume that the parameters are fixed. Yeah. Well, that's fixed.

##### **Chenyu** [[00:18:49](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1129)]
Since you mentioned this, for worst-parity, can you make sure the spec works for the llama trainer?

##### **Geohot** [[00:18:59](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1139)]
I think I posted somewhere.

##### **Chenyu** [[00:19:01](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1141)]
Currently, if you run it with spec equals to 2, it doesn't pass. And I was reading the call and some end issue. That was the only problem.

##### **Geohot** [[00:19:12](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1152)]
OK. So spec equals 1 passes, but not spec equals 2. Oh. How about with Tiny Kitten? How about with hip kittens?

##### **Chenyu** [[00:19:19](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1159)]
Tiny Kitten. Yeah. The training thing.

##### **Geohot** [[00:19:22](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1162)]
Oh, I don't expect Tiny Kittens to work with spec equals 2. No, no. It will not work with spec equals 2. No, no.

##### **Chenyu** [[00:19:26](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1166)]
So I don't know. The issue is I think there is some bug in how the end is written there. And so we either need to properly support that with a test or something. Otherwise, it's very hard to make scheduler change because it would just break.

##### **Geohot** [[00:19:44](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1184)]
What do you mean end?

##### **Chenyu** [[00:19:48](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1188)]
The way Tiny Kitten ends range or some spec error. And if you try to change things and simplify stuff, everything can pass, but just breaks for Tiny Kitten.

##### **Geohot** [[00:20:02](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1202)]
OK. Maybe spec equals 2 should pass for that. We should just, yeah, make it in the Bs as a lot of things. Oh. Oh.

##### **Chrism** [[00:20:11](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1211)]
Oh.

##### **Chenyu** [[00:20:12](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1212)]
Oh. I think our priority is to make that work, get our MLPerf stuff. But you can see this makes prefactoring clean up very difficult.

##### **Geohot** [[00:20:20](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1220)]
Well, but do we even need to support Tiny Kittens? No.

##### **Chenyu** [[00:20:23](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1223)]
Yeah.

##### **Geohot** [[00:20:25](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1225)]
Oh.

##### **Chenyu** [[00:20:27](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1227)]
Then don't pull that in test?

##### **Geohot** [[00:20:29](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1229)]
Yeah, I think maybe remove Tiny Kittens from tests. HipKittens is what we're using for ..

##### **Chenyu** [[00:20:37](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1237)]
I see. OK, OK. Then feel free to remove that. I will do more clean up.

##### **Chrism** [[00:20:42](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1242)]
All right. OK.

##### **Chenyu** [[00:20:45](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1245)]
Buffer-view. You like Buffer-view?

##### **Geohot** [[00:20:49](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1249)]
Buffer-view has always been in there. I didn't create a new thing. I just use it more. And yes, I mean buffer view is a buffer. Eventually, the really important use case of Buffer-view is that Buffer-view is how you do the memory planner. We need to move the memory planner into the graph. And what the memory planner basically does is take a whole call, look at all of the internal buffers and say, this should all be one buffer and everything should just have different views into it. So we definitely like buffer view. Then, yeah, I mean, I think that we can be more explicit in tests confirming that a flight is, a flight.contiguous is not a new buffer. Because contiguous does not mean a new buffer. Contiguous just means contiguous in memory. And what that means, if you want a new buffer, use clone. If you want a new buffer, use assign. Use assign to empty. You can do .clone, .clone. That's going to create two new buffers. But if you do .contiguous, .contiguous, it'll only eventually create one or zero new buffers.

##### **Chenyu** [[00:22:02](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1322)]
.clone, .clone only creates one because the middle one immediately got GC.

##### **Geohot** [[00:22:09](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1329)]
The middle one gets GC. No, it doesn't. Why not? Why would it get GC? All right. I'm 80% sure .clone, .clone is going to create two buffers.

##### **Chenyu** [[00:22:30](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1350)]
Okay, probably I'm thinking about something else.

##### **Chrism** [[00:22:32](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1352)]
Okay.

##### **Geohot** [[00:22:33](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1353)]
Yeah, I mean, because what .clone is, like, it's very nice. The thing about like assign and buffer view is we've always had these things, but we've kind of, we've kind of half supported them. And I really like this project of making them well supported. And so buffer view is a potential, is a potential rewrite of movement ops that is a contiguous view into a buffer. It has a size and an offset. And a gtype. It can also be a bitcast. Size, gtype, and offset. Yeah, and the reason that you want to use it is so there's a flag for LLM called realize. And if you set realize equals zero, it will run the LLM straight out of the ggup. So we don't have to make any copies. We don't do expand to float 16 anymore. It runs out of the ggup and it's also now faster. You get more tokens per second running out of the ggup than you do if you convert to float 16.

##### **Chenyu** [[00:23:32](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1412)]
Yeah, because it's all memory bandwidth bound.

##### **Geohot** [[00:23:36](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1416)]
Because it's largely memory bandwidth bound. I mean, we're not doing, so the out of the ggup, ones with beam are still only getting us like 30% of the memory bandwidth in my system, but that's not too bad. Yeah, I'm not sure what the real, I'm not sure what like the LLM CVP ones got. But yeah, so I'm going to remove the realize equals one. It's going to be all realize equals zero. And then if you're doing realize equals zero and you're slicing from the ggup, you need to have buffer view or else every convolution gets recompiled. With the offset baked into it. Or every gem gets recompiled, the offset baked into it, right? Because it's just offsets into the ggup and you want to make sure that offset stays outside of the compiled thing. So there's two ways to basically do that. One way would be with a new symbolic variable that does a symbolic shrink. Or the other way is with buffer. And I think buffer is a good way to do it. Yeah, and then it's just, yeah, it behaves like a buffer. It's clean. It worked on most devices. The ones that doesn't work on whatever, you get more copies.

##### **Chrism** [[00:24:51](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1491)]
That's good.

##### **Geohot** [[00:24:54](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1494)]
All similar on this week, next week. I'll fix up the mixture of experts thing. And my goal is at the end of the week to get big quen running on, end of the sprint to get big quen running on.

##### **Geohot** [[00:25:09](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1509)]
So I'm going to go to the next. I'm OK. I should be. Symbolical working?

##### **Geohot** [[00:25:21](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1521)]
Yeah. I mean, symbolic's good. There's a few. I mean, symbolic is actually great. So I merged yesterday up that removes a lot of the, we used to have all these asserts for where things were into uops. Again, this was something we kind of like half supported. But now you can remove them and they almost all just work.

##### **Chenyu** [[00:25:42](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1542)]
So I'm going to go back to the last one. When does it not work?

##### **Geohot** [[00:25:46](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1546)]
So like in flash attention, head dims can't be symbolic because we use math.square root. It's dumb crap like that, but nothing.

##### **Chenyu** [[00:25:58](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1558)]
Oh, but those should just change, and they should just work, right?

##### **Geohot** [[00:26:01](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1561)]
Yeah, I think so. You could, I mean, yeah, I guess you could change tensor square. Sure.

##### **Chrism** [[00:26:08](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1568)]
Cool. OK.

##### **Geohot** [[00:26:16](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1576)]
Sounds good. OK.

##### **Chenyu** [[00:26:20](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1580)]
Next is my stuff. I think the very beautiful change is to remove the pending global map and multiple wrong schedule. And now it's all just a magic rewrite of after. Yay! And map.

##### **Chrism** [[00:26:39](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1599)]
Yeah.

##### **Chenyu** [[00:26:43](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1603)]
So probably to fix the rest of the clone issue, I need to think about it. But we might need another map in that function. So it would be 2.

##### **Geohot** [[00:26:55](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1615)]
Another map in what function?

##### **Chenyu** [[00:26:57](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1617)]
No, no. Not map. Another apply map to tensors in assign.

##### **Geohot** [[00:27:04](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1624)]
I think you need 2.

##### **Chenyu** [[00:27:07](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1627)]
Yeah. So for the current case, the map, which is, I think, is 2. Yeah. So the case we mentioned needs test clone and swap.

##### **Geohot** [[00:27:15](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1635)]
Yeah.

##### **Chenyu** [[00:27:16](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1636)]
Fix that.

##### **Geohot** [[00:27:20](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1640)]
Yeah. Yeah. I mean, you see what I did. So I marked that test as expected failure, because it was actually testing for the wrong thing.

##### **Chenyu** [[00:27:27](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1647)]
Yeah. I already merged the change to use clone.

##### **Chrism** [[00:27:31](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1651)]
OK.

##### **Geohot** [[00:27:32](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1652)]
Oh, you changed to use clone. Oh, I got it. Yeah, yeah, yeah.

##### **Chenyu** [[00:27:35](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1655)]
But to fix, to really fix that, and I have another, like, five different cases. That's a more advanced version of that. Yeah. I think it needs another way to check, making sure the order is correct. Because always do the after is very aggressive, and it will break the previous assign, basically.

##### **Geohot** [[00:27:57](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1677)]
Well, so we have a problem right now. And I'm going to need to fix this about the after thing. So I tried switching the KV cache in LLM just to use assign now. Instead of using that hard-coded after thing. And it doesn't work in a call. Because in a call, that after is not resolved by the tensor thing. So I need to fix this at call. But I wonder if this works out to kind of be the same problem. What I need to work out at call is to pull the after out of the call.

##### **Chenyu** [[00:28:29](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1709)]
Oh, yeah. I think I hit another thing in call when I was fixing something. Because call is kind of a block. And just skip first. And resolve later. Oh, that was the, for now, there's a duplicated rules to remove, detach, and continue to this backward. That's part of the reason.

##### **Geohot** [[00:28:53](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1733)]
Yeah.

##### **Chenyu** [[00:28:54](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1734)]
Because there's something left in the call that later, you only see that later in rangeify.

##### **Geohot** [[00:28:59](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1739)]
Yeah, there's a bit of cleanup that still needs to be done here. Failing test cases for it would be great. So just to talk about what call is. Yeah. So call, nothing inside of a call can ever be put back into the tensor graph. Like the uopt inside of call cannot be referenced by the big graph.

##### **Geohot** [[00:29:21](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1761)]
That's the definition of call. That's a very interesting definition. Why? Like it's scoping.

##### **Geohot** [[00:29:45](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1785)]
So there's the global scope and there's a call scope. And most of these times, the scopes are the same. But they're not the same when the big tensor graph, tensors can only exist at top level scope. Once something goes into a call, any buffers that are in there. So it replaces all global buffers with params. And any buffers that exist inside the call are scoped to the call.

##### **Geohot** [[00:30:20](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1820)]
So the after thing gets a little bit annoying

##### **Geohot** [[00:30:22](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1822)]
because we have this thing that rewrites the afters in the big graph back to the tensor graph. But if that's inside of a call, it won't get rewritten. So what I need to do is write logic in call to bring that after to the big graph so that it gets rewritten.

##### **Geohot** [[00:30:43](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1843)]
OK. And you're aware of the issue and knows how to fix that?

##### **Geohot** [[00:30:49](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1849)]
Yeah, I'm aware what that issue is. But I just wonder if that's kind of related. Maybe it's not. Maybe it's not. I didn't understand why the swap thing doesn't work.

##### **Chenyu** [[00:30:58](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1858)]
Well, the swap thing is just you make a clone, let's say, assign. But they also got basically the same thing but it got replaced again in the actual assign call. But you cannot. It's like some complicated dependent on tracking.

##### **Chrism** [[00:31:17](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1877)]
Yeah.

##### **Geohot** [[00:31:17](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1877)]
I'll leave that to you. Yeah.

##### **Chenyu** [[00:31:20](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1880)]
Cool. Set item, I think it's very clean now. I also support the back-core for set item. It's not the slice version because assign itself doesn't have derivative. But use a where and add. And then we can do the back-core of let. So we just support it, test it. It should all match Torch. We support more cases that Torch doesn't support.

##### **Geohot** [[00:31:49](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1909)]
Wait. So is there a flag to switch between the two versions or something?

##### **Chenyu** [[00:31:54](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1914)]
There's no derivative for assign. So if you set.

##### **Chrism** [[00:31:58](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1918)]
No, I.

##### **Chenyu** [[00:31:58](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1918)]
So it depends on if your set requires or not.

##### **Geohot** [[00:32:02](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1922)]
Oh. Oh.

##### **Geohot** [[00:32:05](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1925)]
Oh.

##### **Chrism** [[00:32:05](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1925)]
Oh. Oh. Oh. Oh.

##### **Geohot** [[00:32:07](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1927)]
Oh. I want to ideally always use the one that supports required to grad and then rewrite the other one later because you can change required to grad.

##### **Chenyu** [[00:32:16](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1936)]
Yeah. But the issue is that the compute is very different.

##### **Geohot** [[00:32:23](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1943)]
But . No, we don't.

##### **Chenyu** [[00:32:26](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1946)]
It's like when you do a slice set item, only the slice is being considered.

##### **Geohot** [[00:32:33](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1953)]
I mean, yeah. So the way that like probably maybe the right way to deal. With this is to have it do the. Do the. Like aware and then you can use that where and then you can later on when you compile the kernel not like there's some rulings of ball to remove that.

##### **Chrism** [[00:32:56](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1976)]
And.

##### **Geohot** [[00:32:57](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1977)]
Like there's a rule in symbolic to remove anywhere you do aware. I don't know. But I don't really like the idea that it chooses a compute path based on requires grad.

##### **Sieds Lykles** [[00:33:07](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1987)]
Um.

##### **Geohot** [[00:33:12](https://www.youtube.com/watch?v=0VOafsXYdNA&t=1992)]
It's fine for now. Maybe it's not the highest priority thing but. Like the right way to deal with a lot of stuff is in the tensor graph,

##### **Geohot** [[00:33:28](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2008)]
we want the version that's differentiable to be there. And then once we rewrite it, once we're through that, once we're in graph rewrite, we can then change it to versions that are faster with compute. Um, this is the same way like unique constants were like unique constants are required in the tensor graph in order to fix the. It's an issue with derivatives.

##### **Geohot** [[00:33:49](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2029)]
But as soon as we get down to the compilation stuff, we can remove them. Okay. Yeah, let me close. It's very exciting that we have an item derivative. Yeah, work that can't do that.

##### **Chenyu** [[00:34:10](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2050)]
SAMUEL GREENBERG сразу ARCHIVER As you see. You can see the grain. There we go. How do we do this? Has it changed anything, huh?

##### **Geohot** [[00:34:33](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2073)]
Well. Yeah, I think. I think his had done it all right.

##### **Chenyu** [[00:34:37](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2077)]
Basically, it's like assign or copy to the buffer view. So if let pass just work, I think this should work. It's mostly blocked on a few bitcasts because bitcasts at level is not free.

##### **Geohot** [[00:34:52](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2092)]
It should be. We should be able to make the buffer view thing also support bitcasts.

##### **Chenyu** [[00:34:58](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2098)]
So previously, we don't have that because we don't have a good way to represent its contiguous. I think for now, its contiguous is just that function returns a non-value. Then we can just use that.

##### **Geohot** [[00:35:13](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2113)]
Great. That's also why I worked on the buffer view stuff. I mean, that should eventually be... I tried to unify them a bit more, but I just wrote that function instead. But yeah, you can see how that becomes desk. I really like that the Claude summary said our KV pattern is natural and it's not a function. It's kind of efficient.

##### **Geohot** [[00:35:37](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2137)]
Great.

##### **Chenyu** [[00:35:39](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2139)]
Yeah, I think our scheduler has a lot of potential. Always good to keep things flexible. I also fixed the tinyFS, but it's removing CI or something because it's broken. We can... I don't know. If we want to keep that working, then fix that.

##### **Geohot** [[00:36:03](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2163)]
I also added some unit tests, so hopefully that's good enough. Sorry, say that again? So tinyFS,

##### **Chenyu** [[00:36:13](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2173)]
the real test is disabled now, I think. Because the network... Oh, yeah, I just... Yeah, yeah, yeah.

##### **Geohot** [[00:36:21](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2181)]
Yeah, because R2 is broken.

##### **Chrism** [[00:36:24](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2184)]
Okay.

##### **Geohot** [[00:36:25](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2185)]
Okay. That's my part. Next, driver.

##### **Chrism** [[00:36:32](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2192)]
Driver.

##### **Nimlgen** [[00:36:36](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2196)]
Yeah, so MI300... Sorry, MI350. So actually, I think the stability is fixed. I mean, we now have hyper sets working on MI350, and both 300 and 350 now support some line recovery. So it should be pretty usable with agents. Yeah, also, now we have more CAM. You know, a CI to test different interfaces and all these things. And also, I've implemented, like they... With all this fast recovery, it's now possible to support kernel machines. It's possible to implement, like, killing long-run kernels in Beam. It works, and it's a bit faster now.

##### **Geohot** [[00:37:36](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2256)]
That works on normal, like, RDNA cards too.

##### **Nimlgen** [[00:37:43](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2263)]
Yeah, only with AM.

##### **Geohot** [[00:37:46](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2266)]
Only with AM. Cool. I see keywords being passed to call now.

##### **Geohot** [[00:37:54](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2274)]
Oh, you're passing a timeout.

##### **Geohot** [[00:37:57](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2277)]
Yeah.

##### **Geohot** [[00:37:58](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2278)]
I see. Yeah.

##### **Geohot** [[00:38:02](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2282)]
Yeah, that's probably the right place to put that. Is the timeout done by Python, or is the timeout done by the GPO?

##### **Nimlgen** [[00:38:16](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2296)]
Timeout is, so in AM, like in HTQ, it's Python timeout. It's like the normal timeout path we used to have, like with HTQ timeout. So it will timeout, and after that, it will recover.

##### **Geohot** [[00:38:32](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2312)]
It will recover. All right, cool. Does the, uh? Yeah.

##### **Nimlgen** [[00:38:41](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2321)]
Yeah, so for the beam timings, I know I didn't spend much time. I tried to play with clocks on MI300. So actually, I don't know. I still see this gap without warmup. And I know. I can get the fixed clock for the GFX score, but not for UCL and other things. So I'll still look into this.

##### **Geohot** [[00:39:28](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2368)]
Do you have a repro of that speed? Yeah.

##### **Chrism** [[00:39:32](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2372)]
We'll have our temporals shaking down

##### **Chrism** [[00:39:33](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2373)]
for a second.

##### **Chrism** [[00:39:34](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2374)]
foot on, I don't know why I'm finding this. I'm not going to take it, but I'm starting to have some challenges right now.

##### **Geohot** [[00:39:40](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2380)]
Like thermzähly stinky, Spotlight. You want to do the, uh, Savmostop this. 美що

##### **Nimlgen** [[00:40:02](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2402)]
Like again, Lama 8B training with AMD GPU slower than AM.

##### **Geohot** [[00:40:08](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2408)]
Yeah, why? Like 2X I'm hearing.

##### **Geohot** [[00:40:15](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2415)]
I know, I'll take a look. Same pass. Yeah, they should. Yeah. Did the Apple driver work?

##### **Nimlgen** [[00:40:33](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2433)]
I haven't Nvidia card to test it, but I can sign it. And this new profile looks promising because it has the correct format.

##### **Geohot** [[00:40:47](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2447)]
Right.

##### **Geohot** [[00:40:48](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2448)]
But they didn't give us AMD, they just gave us Nvidia. Yeah.

##### **Geohot** [[00:40:57](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2457)]
Yeah, I mean, we can complain to them if it actually works. We can probably get it. Can we sign it with two if they give us one with each?

##### **Nimlgen** [[00:41:10](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2470)]
Actually, I don't know how, but I think I've seen something like that on the Apple forums, that it's possible to do that. No idea.

##### **Geohot** [[00:41:24](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2484)]
But yeah, no, we should test that. Can you test it with the... Can you test it remotely on Tiny Mac 3? Yeah.

##### **Geohot** [[00:41:33](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2493)]
Oh, yeah, yeah, yeah. I'll do that, yeah. Great. Yeah, that. Anyone else have driver issues? They look tough. And I just kept crashing it. What? During Beam? What do you mean, crashing?

##### **Geohot** [[00:41:55](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2515)]
I would like Beam kernel, and then my entire GPU would crash.

##### **Geohot** [[00:42:00](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2520)]
Yeah, that happens. That happens to me sometimes, too. I don't know why that is. Quite annoying. Yeah. I mean, we should get what? Strix Halo Bench?

##### **Chrism** [[00:42:14](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2534)]
Yeah.

##### **Geohot** [[00:42:17](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2537)]
Yeah, I'll do that. You need tokens for the thing? Yeah, I run your demo. Okay.

##### **Geohot** [[00:42:26](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2546)]
Let's see. Yeah. So what are... Ammo also says that the... Yeah. The decoder is still... The HVAC decoder is still a lot slower.

##### **Geohot** [[00:42:39](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2559)]
Do we expect that or no? I'll post the message from Comma. Oh, actually, yeah.

##### **Nimlgen** [[00:43:12](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2592)]
I think it's regressed. I should have asserted. Yeah, it's 800 FPS now, benchmark now.

##### **Geohot** [[00:43:20](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2600)]
Yeah. I mean, so this is the...

##### **Chrism** [[00:43:28](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2608)]
You know, I can't remember.

##### **Geohot** [[00:43:33](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2613)]
I think I can't remember. I don't remember that. We can get that back to... Back to speed. And then the other thing...

##### **Geohot** [[00:43:43](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2623)]
I want to move the memory planner to operate on, like, the graph.

##### **Geohot** [[00:43:51](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2631)]
I think you can do that. Yeah. It didn't work.

##### **Chrism** [[00:44:00](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2640)]
That's cool.

##### **Geohot** [[00:44:01](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2641)]
See what I mean by that? Yeah, yeah.

##### **Geohot** [[00:44:06](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2646)]
I wanted to operate on the graph, and I wanted to ideally operate on both graphs. So it should operate on the graph of a call, but also the graph of a local. A defined local should also work with the same memory planner.

##### **Geohot** [[00:44:30](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2670)]
I think I still have to do a refactor

##### **Geohot** [[00:44:33](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2673)]
where instead of using defined local, I use buffer. But yeah, maybe at this sprint, you want to work on moving the memory planner to the graph. And the other advantage to moving memory planner to the graph is it shouldn't be related to the JIT. I don't know if it's related to the JIT. I guess it's not related to the JIT right now. I guess the only thing that's really related to the JIT is HTQ, which should also get moved to the scheduler.

##### **Geohot** [[00:45:05](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2705)]
Do you feel confident doing those moves? Yeah. You don't sound excited about it.

##### **Nimlgen** [[00:45:19](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2719)]
No, I am. I think I'll start with memory. Memory planner.

##### **Chrism** [[00:45:22](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2722)]
Okay.

##### **Geohot** [[00:45:31](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2731)]
Memory planner it is.

##### **Geohot** [[00:45:34](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2734)]
Yeah, no, I mean, I want to get to a point. I think the memory planner, and I think the project that I see you moving to in the next couple months is moving the HTQ command buffer compilation into the graph so that the graph just outputs. Yeah.

##### **Geohot** [[00:45:51](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2751)]
Like we've graph rewrited up with a command queue. Yeah. Yeah. Why is it not like that? Why is it not like that?

##### **Chrism** [[00:46:07](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2767)]
Yeah.

##### **Geohot** [[00:46:08](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2768)]
Because we still have the exec item. Yeah, but. Okay. Oh, we'll get there.

##### **Geohot** [[00:46:16](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2776)]
We have to do it. But, you know, I mean, currently we're still doing this traditional, like, this old school lowering pass, which operates on these linearized schedule items. But I put all the prerequisite stuff in there now that you just get a linear on kernel. And that linear on kernels can be compiled directly into graph.

##### **Geohot** [[00:46:36](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2796)]
So I'll come back. Anything else for driver?

##### **Chrism** [[00:46:47](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2807)]
No.

##### **Geohot** [[00:46:49](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2809)]
Okay. Next we have Lama. Now you just realize it's 10 weeks to a deadline. When's that line? And weeks. 10 weeks. No, it's two and a half months. Not even two months. Yeah, that's 10 weeks. Um, as of right now, four or five, we does not fit. We're like five VECs off memory.

##### **Geohot** [[00:47:26](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2846)]
We have all the tricks training APs that are needed for four or five bit offloading and then offloading intensive parallel threading works. And I think the big thing that I think would help is we need to have activation checkpoint. We cannot do this without activation. It's like, just not possible. We're materializing the expanded. And we can't be doing that because that takes up way too much. Um, so if you start using call, uh, this will happen for you because nothing. So when the derivative of call never can reference anything inside the call, I wrap the entire FFN function. Um, and yeah, you want to, you want to write tests for these? You want to start looking into it, but yeah, so the, the derivative of call, the function on call is treated as like a black box for the derivative.

##### **Chrism** [[00:48:23](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2903)]
Okay.

##### **Geohot** [[00:48:24](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2904)]
So the derivative of call computes the compute multiple calls that are the inverse of that. Um, yeah. So that the call is basically what you want for activation checkpoint. Um, and that should also help you. Yeah. Understand the memory. It's better. Yeah. That could be the only memory. We absolutely need to be taking four or five steps by the end of this event. Yeah. Yeah.

##### **Geohot** [[00:48:53](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2933)]
X is the parse that's on GPU. Yes. Can we run 70 B? Hmm. Possibly. I don't know. I haven't tried.

##### **Chenyu** [[00:49:08](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2948)]
That's one six. Probably. It's just good to run something with that high of low to make sure like, no, it's not very. Yeah. I think. Yeah.

##### **Geohot** [[00:49:21](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2961)]
We should kick off a 70 B pick up 70 B training run.

##### **Chenyu** [[00:49:24](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2964)]
Yeah. Let it run like 10 steps and it should reveal a lot of things that we can work in parallel earlier.

##### **Geohot** [[00:49:34](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2974)]
Okay. Um, but yeah, call should basically give you activation checkpointing. Yeah. There's some other stuff like we could do sequence parallelism, but that requires scatter reduce that we don't have. We have scattered reduce. That's the opposite of embedding, but, um, you need a cross, not it's like all device scatter. Do we have to do that to fit it? No, I don't think we need that if we have that. Okay.

##### **Geohot** [[00:49:58](https://www.youtube.com/watch?v=0VOafsXYdNA&t=2998)]
Great. Let's avoid that. And, um, multi seems to make big buffers on every device. There might be bugs in multi. Oh, there's definitely bugs in multi. Isolate them where it does wrong.

##### **Chenyu** [[00:50:17](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3017)]
If you, if you find. A smaller example for you, I would take a look.

##### **Geohot** [[00:50:21](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3021)]
Okay.

##### **Chrism** [[00:50:25](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3025)]
Cool.

##### **Geohot** [[00:50:27](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3027)]
Okay.

##### **Chenyu** [[00:50:28](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3028)]
So let's get 70 beach like test work. A few steps should be good enough. Then we can start.

##### **Geohot** [[00:50:36](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3036)]
I mean, why don't you turn a 70 bit? Oh, exactly. Maybe you're fit. No. X longer than you agree. Yeah. Let's go.

##### **Chenyu** [[00:50:52](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3052)]
We just need a few steps and we can start to complain.

##### **Geohot** [[00:50:56](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3056)]
Well, yeah, we could, let's train 70 B let's 70 be training. And then that's going to be more representative of the, uh, of the timing. So we can all work on the speed of it.

##### **Geohot** [[00:51:04](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3064)]
Okay. Definitely. Okay. Next we have this. Oh, wait, this. I guess. Use often. Yeah. I wrote. I don't think it's right. It's like you partial, you allocate a big buffer for all the grads and you're powerful. Assign. Yeah. Not entirely. Yeah.

##### **Chenyu** [[00:51:50](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3110)]
So I haven't tried. It might need my current fix, but if you have a smaller repro that you show is wrong, let me know. I will fix.

##### **Chrism** [[00:51:59](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3119)]
Yeah.

##### **Chenyu** [[00:52:00](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3120)]
I think now assigning into a buffer view should be correct.

##### **Geohot** [[00:52:06](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3126)]
So, so let's show work in principle. And if not, there's box on there. Okay. Sorry. Uh, this is the engine working right away for Loma. What's the ad engine. Yeah.

##### **Qazalin** [[00:52:33](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3153)]
The ad function.

##### **Geohot** [[00:52:38](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3158)]
The assembly.

##### **Qazalin** [[00:52:40](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3160)]
Oh yeah.

##### **Geohot** [[00:52:41](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3161)]
Yeah.

##### **Chrism** [[00:52:42](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3162)]
Okay.

##### **Geohot** [[00:52:45](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3165)]
It's still slow. Okay.

##### **Chrism** [[00:52:47](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3167)]
So. Yeah.

##### **Geohot** [[00:52:48](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3168)]
That one shape is slow. Yeah. Well, that one shade.

##### **Qazalin** [[00:52:55](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3175)]
I mean, I had the disabled.

##### **Geohot** [[00:52:59](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3179)]
It's it's we don't hit an MP and we don't, it's super negative one four or five anyway. Yeah. I'm not worried about this. Um, but yeah. Uh, well you, you got a gift for SQTT. Uh, they finally open source that.

##### **Qazalin** [[00:53:15](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3195)]
Yay. Yay. It's very nice.

##### **Geohot** [[00:53:18](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3198)]
It's pretty good too. Yeah. They have, they have basically that enum you were trying to figure out. That's all just done. Uh, our names are not bad. Our RDNA three names are not bad, but there's our better. Um, so yeah, if you want the project, this sprint of moving all our SQTT stuff to, uh, the stuff from their repo and making sure it works, but CDNA, RDNA three and RDNA four.

##### **Geohot** [[00:53:42](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3222)]
Oh, good. Yeah. I'll take that.

##### **Chrism** [[00:53:45](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3225)]
Okay.

##### **Geohot** [[00:53:46](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3226)]
What else on this? Uh, I don't know.

##### **Chrism** [[00:53:49](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3229)]
I don't know.

##### **Qazalin** [[00:53:49](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3229)]
Um, this has call graph. Individual call graphs expand and collapse.

##### **Geohot** [[00:53:57](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3237)]
Yeah. It looks quite good. I can click on them. I also added to call the, uh, the little hash. You can tell if two things are the same without having to expand them.

##### **Geohot** [[00:54:10](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3250)]
Um, but yeah, no overall, it seems good.

##### **Geohot** [[00:54:14](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3254)]
Uh, I did a visiting this week too. I fixed, uh, I, I, I, I, I, I, I, I, I, I, I, I, I, I, I, I, I, I, I, I, I, I, I, I, I, I, I fixed DAG, right? I fixed all the recursion errors and DAG, right? And by me, I mean, Claude.

##### **Geohot** [[00:54:24](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3264)]
Yeah. Ask you to do for the three things, update everything to use AMD's names. You want to differ in this? Oh, the differ. Yeah.

##### **Geohot** [[00:54:44](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3284)]
I don't know. Uh, that's we'll design that in person. Yeah. I think, uh, that's, that's, I'm not sure exactly what it should look like.

##### **Geohot** [[00:54:51](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3291)]
Yeah. Yeah.

##### **Qazalin** [[00:54:56](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3296)]
As cutity also got a little upgrade. No, I got inspiration from Kira. Can see the trace on the side, all the instructions.

##### **Geohot** [[00:55:07](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3307)]
I've tried it. Cool. Um, yeah, no, I noticed that the profiler is faster too. It's definitely noticeable.

##### **Qazalin** [[00:55:14](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3314)]
Yep. Profile runs on Lama without out of memory.

##### **Geohot** [[00:55:17](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3317)]
Yeah. Yeah.

##### **Chrism** [[00:55:28](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3328)]
So I'm going to do it.

##### **Geohot** [[00:55:30](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3330)]
Anything else that are going to work on next? It's just SQTT. Mostly.

##### **Qazalin** [[00:55:42](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3342)]
Uh, I did some cleanups on the assembly CD and agent. I'll do more. Okay.

##### **Geohot** [[00:55:51](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3351)]
Have we cleaned up across the code base on all the places where like, still doing like weird hacks to compile assembly.

##### **Qazalin** [[00:55:59](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3359)]
Oh, I clean them up. Yeah.

##### **Geohot** [[00:56:02](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3362)]
There's none left. There's none left. Still using like old, weird gaps.

##### **Qazalin** [[00:56:05](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3365)]
Uh, there is one for the test GPU crashes. Honestly, like I couldn't even run those tests on our exhibition. Right. pass, but they can still change it.

##### **Geohot** [[00:56:21](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3381)]
It's an extra. You shouldn't change it. Everything that's Yeah, you shouldn't change it if you can't run it. That's the only one that's left. MMA peak is good and clean now. OK, cool.

##### **Qazalin** [[00:56:46](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3406)]
Yeah. There's also your first attempt at sqtt parse. That one is also using the old path. I'm not sure if you want to keep that file.

##### **Chrism** [[00:56:56](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3416)]
Just delete that.

##### **Qazalin** [[00:56:58](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3418)]
All right, I'll delete that. Yeah, those two are the only ones that use the old YAML parse.

##### **Geohot** [[00:57:05](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3425)]
Yeah, just print just for cleaning up sqtt,

##### **Geohot** [[00:57:09](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3429)]
using the gif AMD gave us, making all the names right. OK, so I'm going to do this. Sounds good. OK, so I want to review this. Mm-hmm. Oh, you can't review the later file. Yeah, I'll review it after the meeting. Yeah, this looks all right.

##### **Chrism** [[00:57:48](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3468)]
OK.

##### **Geohot** [[00:57:54](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3474)]
Anything else? We have an issue. Not really. The PR, we have a lot of PR open. Everyone, please close both PRs. Bounties, I think the cDNA one's kind of close. OK, great. The new cDNA one is? Yeah, so good cDNA one. So .

##### **Qazalin** [[00:58:31](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3511)]
Oh, I hope. Should the cDNA one also test the assembly gem and the hip cadence?

##### **Geohot** [[00:58:37](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3517)]
Oh, yeah. Yeah, it has to run on those. If it can't run on those, it's not ready. Yeah, I complained to the guy. Yeah, I saw you complain to the guy. Just stay on top of them.

##### **Chenyu** [[00:58:54](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3534)]
What do we want to do with all the cache key for schedule cache and BIM cache with all the context smarts that we can have?

##### **Geohot** [[00:59:07](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3547)]
I don't know.

##### **Chenyu** [[00:59:09](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3549)]
Because we currently only keep some of it and not all of it. And it's very easy to misuse. Yeah.

##### **Geohot** [[00:59:19](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3559)]
Well, we should save it all, I guess. Is it big? Just add all of them.

##### **Chrism** [[00:59:27](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3567)]
Yeah.

##### **Chenyu** [[00:59:28](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3568)]
Depends on how we want to set it. It's like, do we read the dictionary and just add everything? Or we encode lots of things?

##### **Geohot** [[00:59:36](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3576)]
We should hash it, yeah.

##### **Geohot** [[00:59:38](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3578)]
Hash it, and then we can handle all the context. Yeah. Oh, OK. I guess. OK.

##### **Chrism** [[00:59:48](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3588)]
Yeah.

##### **Chrism** [[00:59:49](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3589)]
The person who is most confused or misused, this one would be bad enough to fix it.

##### **Geohot** [[00:59:58](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3598)]
Which one? I mean, someone will eventually fix it. Yeah.

##### **Chrism** [[01:00:04](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3604)]
If it's bothering someone, add that context there. I'm not going to write about those.

##### **Chrism** [[01:00:09](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3609)]
Cool.

##### **Chenyu** [[01:00:12](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3612)]
OK. Sounds good. I think that's it for this meeting. Thank you, everyone. See you next week. See you in Hong Kong. Bye bye.

##### **Geohot** [[01:00:21](https://www.youtube.com/watch?v=0VOafsXYdNA&t=3621)]
Bye.
