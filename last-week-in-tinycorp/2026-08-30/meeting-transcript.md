# 2026-08-30 Meeting

### Meeting Agenda

**Time:** new meeting #35, 8/30 9am Monday San Diego time
- company update
- hcq2
- gptoss
- llama training
- CI infra
- rangeify, IR spec
- CONST weak dtype
- bounties, rdna3, comma happiness

### Audio

[YouTube Link](https://www.youtube.com/watch?v=PVkWak7QG-s)

### Highlights

- **[Company Update](#geohot-000004)**: Hong Kong office air conditioning fixed; AMD secret project shipped on EXW pickup terms; two more tinybox Pros with RTX cards sold at good margin (customers want to run GLM).
- **[Exa Box](#geohot-000113)**: Racks and cooling system in design; core challenge is heat exchanger sizing (full-rack vs half-rack) and placement; a Chinese company claims it can build the system and is preferred after bad experiences with American vendors; direct hiring efforts going poorly.
- **[HCQ2 CI Performance](#nimlgen-000311)**: CI is ~2.5x slower overall under HCQ2 and test_dtype is 3x slower; slowness attributed to fixed backend overhead on the many small test kernels; large schedules perform fine relative to rangeify.
- **[HCQ2 Single Control Program](#geohot-001831)**: Hard constraint set—one compiled control program per schedule containing all waits, regardless of device count; the program should be named "timeline"; queue submission remains a simple, single-threaded, linear program dispatched from Python.
- **[CPU Threading Removal](#geohot-002106)**: CPU threading to be ripped out of BEAM and main tinygrad; Python is not a dispatcher; parallel multi-device submission deemed premature optimization ahead of Exa Box.
- **[Broadcom VF](#nimlgen-002822)**: Broadcom network driver merged; AMD virtual function driver blocked because GIM resets the GPU after seconds without the real RLC scheduler queue; reproducible on a single GPU and flagged as possibly higher priority than HCQ2 to enable a DigitalOcean run.
- **[NOLOCALS Removal](#chrism-003129)**: Chrism's PR to remove NOLOCALS will be merged despite a small performance regression; NOLOCALS called an expensive feature that shouldn't block HCQ2 work.
- **[GPT-OSS Training](#wozeparrot-003257)**: Next run targets ~800ms per step after Flash Attention kernel optimization and removal of MoE elementwise kernels; MoE GEMM kernels (HipKittens, FP8) remain below 20% MFU; GEMM kernel optimization is the next target.
- **[LLaMA Training](#qazalin-003604)**: New best time of 1 hour 53 minutes achieved by squeezing the existing GEMMs; no GEMM exceeds 40% MFU; comms work still pending.
- **[CI & GARM](#chrism-004519)**: Decision to stay on GitHub; GARM chosen for self-hosted runners supporting both GitHub and Gitea; CI target is under 3 minutes; comma 3Xs to be replaced with comma fours; NVIDIA GPU passthrough into VMs works via PCIe bus attachment.
- **[Rangeify Spec](#geohot-005148)**: Spec advanced—PARAM (inherited from higher scope) replaces long-lived buffers in the big graph while BUFFER is local to a CALL scope; RETURNED, TUPLE, and GETTUPLE removed; UNSHARD becomes END; UOp count down to 70.
- **[UOp dtype & x86](#chenyu-005714)**: dtype removed as a UOp attribute—CONSTs now carry weak dtypes and CUSTOM/CODE/INS hold dtype in their args; half of the x86 renderer (dead vectorized code) to be removed since x86 is correctness-only.
- **[Flux MLPerf](#flata-010147)**: Correctness run failed with NaN plus a JIT argument mismatch during eval; without BEAM the run is ~9 seconds per step over 30,000+ steps (~2.5 days)—too long to debug; MLPerf submission still the target.
- **[RDNA3 Backend](#raine-010332)**: CI is passing with correctness verified on small kernels; scaling to hardware exposed renderer state and register allocation issues (dispatch hangs when hitting the 256-register cap); Geohot directed that DEFINE_REG should mean preallocated named registers, not memory.


### Transcript
##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=PVkWak7QG-s&t=0)]
We start with company updates.

##### **Geohot** [[00:00:04](https://www.youtube.com/watch?v=PVkWak7QG-s&t=4)]
The Hong Kong office has good air conditioning now. That happened this week, so that's exciting. What else? The secret project from AMD supposedly shipped, although the shipping terms are EXW, which apparently means we have to pick them up. But I don't know where to pick them up, so there's that. We sold two more tinybox Pros with the RTX cards. I think people want them because they can run GLM. They're a huge pain to build, but that's priced in. We do make good money on those, so that's good. What else? That's pretty much it. Any update on the Exa Box?

##### **Geohot** [[00:01:13](https://www.youtube.com/watch?v=PVkWak7QG-s&t=73)]
Yeah, we're trying to hire people. Last week we were discussing that it might just be better to contract one of the Chinese companies that has experience doing this. We're trying to build out the Exa Box, the actual racks and the cooling system. We'll see. We're trying to hire someone to do it too, but that has been going very mediocre. Harold's had a whole bunch of calls, and they're bad. That's unfortunate. But there's a Chinese company that basically says they can just do it. It's terrible working with the American companies.

The tricky thing is figuring out how to get heat out of the box. That's the whole challenge. You have to buy these heat exchangers. How much space are the heat exchangers going to take up? Do you want them to cover the racks, or do you want them in the middle of the racks? I don't really want them to cover the racks because that sounds annoying.

##### **Geohot** [[00:02:28](https://www.youtube.com/watch?v=PVkWak7QG-s&t=148)]
They're in the middle of the racks, but then how big are they? Are they a full rack wide or half a rack wide? There's an American company that says you can use half a rack of stuff to pull out a rack's worth of heat, and I don't know if that makes sense. The ones the Chinese make are full-rack, but they say they can make a half-size one. I don't know if I believe them. When I'm back in China, I'll go visit the people.

##### **Chenyu** [[00:02:57](https://www.youtube.com/watch?v=PVkWak7QG-s&t=177)]
Okay, that sounds fun. Cool.

##### **Chenyu** [[00:03:02](https://www.youtube.com/watch?v=PVkWak7QG-s&t=182)]
Let's move on. We'll start with HCQ2.

##### **Nimlgen** [[00:03:11](https://www.youtube.com/watch?v=PVkWak7QG-s&t=191)]
We still have HCQ1, so I'm pretty sad about that. The main blocker right now is switching CI and keeping it fast. After you reverted the benchmark, I tried to enable everything in CI, and it is really slow. There are a lot of small tests, they're all different, and all of them go through HCQ compile. I'm focusing on optimizing for these small programs.

##### **Geohot** [[00:03:50](https://www.youtube.com/watch?v=PVkWak7QG-s&t=230)]
We shouldn't spend time making things fast if we're trading complexity for speed. Are we making anything more complex to get this speed?

##### **Nimlgen** [[00:04:04](https://www.youtube.com/watch?v=PVkWak7QG-s&t=244)]
No. I think HCQ2 should be simpler. I rewrote what I think is the ugliest part, and I'll continue to simplify it. I don't think complexity is the issue.

##### **Chenyu** [[00:04:25](https://www.youtube.com/watch?v=PVkWak7QG-s&t=265)]
How slow is it?

##### **Nimlgen** [[00:04:31](https://www.youtube.com/watch?v=PVkWak7QG-s&t=271)]
test_dtype is the most annoying, and it's about three times slower. The whole CI is about two and a half times slower.

##### **Nimlgen** [[00:04:52](https://www.youtube.com/watch?v=PVkWak7QG-s&t=292)]
I'll optimize that. My current plan is to keep in mind the amount of UOps we have. Some passes generate a lot of UOps, which makes it slower. It's basically fine for large schedules compared to rangeify. In tests we have small kernels, and rangeify is pretty fast, but the backend overhead is the same for small kernels as it is for big kernels. That's why it's not 30% slower like it was before, but three times slower.

##### **Geohot** [[00:05:44](https://www.youtube.com/watch?v=PVkWak7QG-s&t=344)]
I want you to think about everything from the perspective of when we start to build our own operating system to run on the GPUs. We're eventually going to have our own kernel that runs on all 96 of the RDNA3 cores, and that kernel will parse whatever our MEC format, PM4 format, or queue format is. Each core will parse it individually. What's slow? How could it be three times slower? Think about the size of compiling a kernel versus compiling the HCQ2 stuff.

##### **Nimlgen** [[00:06:46](https://www.youtube.com/watch?v=PVkWak7QG-s&t=406)]
It's mostly in Python. I've been emitting a lot of UOps for the patches and for expanding the PM4 packets.

##### **Geohot** [[00:07:06](https://www.youtube.com/watch?v=PVkWak7QG-s&t=426)]
I'm looking at the recent rewrite PR. I see this function called seal_call, and it's creating all these UOps. It's in ops_amd, in HCQ2. What does seal_call do? Why do we need it?

##### **Nimlgen** [[00:08:42](https://www.youtube.com/watch?v=PVkWak7QG-s&t=522)]
The encode pass generates a linear sequence of all the PM4 packets. Some of them have UOps because they need patches. A UOp can be GETADDR of PARAM zero for kernel arguments, for example. seal_call splits the patches we apply at runtime from the ones we apply at link time. It also rewrites the runtime patches as a loop, because if you put all the UOps sequentially, all the lowering into C is really slow.

##### **Geohot** [[00:10:11](https://www.youtube.com/watch?v=PVkWak7QG-s&t=611)]
What is the loop? Why do I need a loop?

##### **Nimlgen** [[00:10:16](https://www.youtube.com/watch?v=PVkWak7QG-s&t=616)]
It's to apply patches to the command buffer based on your input arguments.

##### **Geohot** [[00:10:24](https://www.youtube.com/watch?v=PVkWak7QG-s&t=624)]
That shouldn't have to be compiled every time. There should be one universal patcher program that compiles once. I'm looking at an HCQ2 lowering now, and I don't see any loops.

##### **Nimlgen** [[00:11:02](https://www.youtube.com/watch?v=PVkWak7QG-s&t=662)]
It can be the same program, but the cache before HCQ compile doesn't work for different programs because its key includes the program itself.

##### **Geohot** [[00:11:23](https://www.youtube.com/watch?v=PVkWak7QG-s&t=683)]
I also don't see the source of the submitter anymore.

##### **Geohot** [[00:11:52](https://www.youtube.com/watch?v=PVkWak7QG-s&t=712)]
I really worry about these changes that make it faster. I think they're adding complexity and putting stuff in Python that shouldn't be in Python, but should really be in UOps. Where did the code go? Run with AMD. I thought AMD was going to be the default, but here's another footgun in tinygrad: if this import fails, it'll silently fall back to CPU. Okay, now I see these HCQ submits.

##### **Geohot** [[00:13:01](https://www.youtube.com/watch?v=PVkWak7QG-s&t=781)]
Why are there five submits?

##### **Nimlgen** [[00:13:11](https://www.youtube.com/watch?v=PVkWak7QG-s&t=791)]
We have a finalizer, reset, and fence, which are for synchronization.

##### **Geohot** [[00:13:18](https://www.youtube.com/watch?v=PVkWak7QG-s&t=798)]
That's fine, but why? I can see there being two. I can see one per device. I don't understand why there are five.

##### **Nimlgen** [[00:13:34](https://www.youtube.com/watch?v=PVkWak7QG-s&t=814)]
The naming is bad, but one is the actual submit, three are reset, fence, and finalizer, and the last one should be the batch submitter in C.

##### **Geohot** [[00:13:49](https://www.youtube.com/watch?v=PVkWak7QG-s&t=829)]
I don't understand why there's more than one per device. There could be one for all the devices. There's no reason these are different. This was all done from a single schedule, right? Why are there five?

##### **Nimlgen** [[00:14:17](https://www.youtube.com/watch?v=PVkWak7QG-s&t=857)]
The first two are probably the fence and reset. They're separate programs because we need to maintain order between them if we submit them in parallel with threads.

##### **Geohot** [[00:14:35](https://www.youtube.com/watch?v=PVkWak7QG-s&t=875)]
Why can't that be done inside the program? Imagine this running on a GPU operating system. Whatever synchronization mechanism you're using, why can't that just be in the UOps? Am I missing something?

##### **Nimlgen** [[00:15:05](https://www.youtube.com/watch?v=PVkWak7QG-s&t=905)]
I'm not sure what UOps you mean.

##### **Geohot** [[00:15:08](https://www.youtube.com/watch?v=PVkWak7QG-s&t=908)]
You're going to submit these things. Something's going to be submitted to the CPU, and something's going to be submitted to the GPU. Also, how come when I do DEBUG=2, I don't see the HCQ programs running anymore? Is there a flag for that? And for some reason they all have three. This needs to stop. Every week it's, "I've changed a whole bunch of stuff that makes it faster." I really think this is just making things more complex, and they don't need to be.

##### **Geohot** [[00:16:06](https://www.youtube.com/watch?v=PVkWak7QG-s&t=966)]
Why is it five programs? Let's start there. I understand there's a fence and that you want to synchronize things, but I don't understand why they're separate programs. Why is that done in Python?

##### **Nimlgen** [[00:16:33](https://www.youtube.com/watch?v=PVkWak7QG-s&t=993)]
They're compiled as separate programs.

##### **Geohot** [[00:16:37](https://www.youtube.com/watch?v=PVkWak7QG-s&t=997)]
Why? I don't understand why it's not all one program.

##### **Nimlgen** [[00:17:00](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1020)]
Okay, I'll think about that. It's not one program because, currently, if we want to send things in threads, we need separate programs.

##### **Geohot** [[00:17:20](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1040)]
We should just revert all of CPU threading. The way we're doing CPU threading is not the way it should be done. Python is not a dispatcher. The way you do threading is to have 16 kernels, 16 threads spinning and waiting on a semaphore. Your control program triggers that semaphore, and then the programs go. So why do I need five programs?

##### **Nimlgen** [[00:18:24](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1104)]
Yeah, I see. I'll think about that.

##### **Geohot** [[00:18:31](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1111)]
Let's make that a hard constraint. There should be one control program that handles everything, one control program per schedule, no matter how many devices you're running it on. That control program contains all the waits.

##### **Nimlgen** [[00:19:21](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1161)]
It's actually already like that. If you open the last program, the last HCQ submit in HCQ compile, it's the one C submitter that pushes all these programs to the CPU.

##### **Geohot** [[00:19:37](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1177)]
So it's the bottom HCQ submit? This one?

##### **Nimlgen** [[00:19:53](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1193)]
Yeah. It prebuilds the queue with the addresses of all these programs and pushes it into the CPU worker with all the arguments.

##### **Geohot** [[00:20:19](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1219)]
The CPU workers should never talk to the GPU. I don't know if that's what's happening now. The CPU device is overloaded: there's the CPU device that does compute, and then there's the CPU device that does submissions. Those should be totally separate. There should be no way to run a multithreaded submitting function.

##### **Nimlgen** [[00:20:56](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1256)]
That removes a lot of annoyance, but don't we want to submit to GPUs in parallel?

##### **Geohot** [[00:21:06](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1266)]
Can we just delete all CPU threading for now to make things simpler? We don't need this feature. Let's rip CPU threading out of BEAM and main tinygrad for now. I think this is creating complexity, and there are things about it that have always created complexity. We don't really need this feature. Do we need it for anything?

##### **Chrism** [[00:21:38](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1298)]
I don't think so.

##### **Geohot** [[00:21:41](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1301)]
Let's take that out of master tinygrad right now and never think about it again. Think about where this is eventually going to go. We're eventually going to have an operating system. Right now GPUs have a central dispatcher, something like the MEC doing central dispatch. We should remove all of that and just have kernels that sit spinning, or sleeping if they can, on GPU or CPU cores and wait for jobs to come in. But this should never be confused with queue submission logic, which should always be a simple, single-threaded program dispatched from Python.

##### **Nimlgen** [[00:22:42](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1362)]
That looks simpler.

##### **Geohot** [[00:22:48](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1368)]
It should be one compilation that drives the entire schedule, regardless of what device it's on. If you want to keep the submission queue and CPU runners in different threads, that's fine, whatever is simpler there. It doesn't have to be multithreaded. There can be a separate control thread and compute thread.

##### **Nimlgen** [[00:23:30](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1410)]
So we remove submitting several devices in parallel?

##### **Geohot** [[00:23:43](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1423)]
Yeah, don't worry about that at all.

##### **Nimlgen** [[00:23:45](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1425)]
Okay.

##### **Geohot** [[00:23:46](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1426)]
Why do you think you need that?

##### **Nimlgen** [[00:23:48](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1428)]
For Exa Box, if we have a lot of GPUs.

##### **Geohot** [[00:23:57](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1437)]
I don't think we should be thinking about this yet. It's premature optimization. If you're submitting to GPUs, this stuff should be lightning fast. There's an antipattern we should never have: submit to one, wait for one; submit to two, wait for two; submit to three, wait for three. It should be submit to one, two, and three, then wait for one, two, and three. All of that can be single-threaded, and I think it can scale to a thousand things with no problem. Do you agree?

##### **Nimlgen** [[00:25:04](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1504)]
Yeah. For PM4, definitely, because it has indirect buffers and it's really fast to copy them. AQL is annoying, and SDMA is probably annoying. SDMA has indirect buffers, but I remember it having issues for no reason.

##### **Geohot** [[00:25:39](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1539)]
Even if it's not indirect, how large are these buffers?

##### **Nimlgen** [[00:26:00](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1560)]
I don't know off the top of my head, but I guess several megabytes.

##### **Geohot** [[00:26:09](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1569)]
And you're saying you have to rebuild several megabytes every submission?

##### **Nimlgen** [[00:26:14](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1574)]
No, that's prebuilt.

##### **Geohot** [[00:26:18](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1578)]
Okay, and you have to patch it.

##### **Nimlgen** [[00:26:22](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1582)]
Yes, but you also need to copy it into the ring.

##### **Geohot** [[00:26:33](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1593)]
Copy it into the ring? Because there's no indirect buffer? That's bad. There's no way to say, "Run this existing buffer." PM4 lets you do that, but not SDMA and AQL.

##### **Nimlgen** [[00:26:50](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1610)]
SDMA also has that command. AQL doesn't. But we had issues with SDMA, maybe alignment or some other problem.

##### **Geohot** [[00:27:04](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1624)]
AQL doesn't support indirect buffers?

##### **Nimlgen** [[00:27:09](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1629)]
Three months ago it didn't. I can check the latest ROCm.

##### **Geohot** [[00:27:18](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1638)]
I can't believe AMD likes that AQL crap.

##### **Nimlgen** [[00:27:20](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1640)]
When I read the HIP graph, they didn't use any indirect buffers for AQL.

##### **Geohot** [[00:27:32](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1652)]
Regardless, we need to get HCQ2 merged, and we need to massively simplify this stuff. We should not be thinking about building CPU programs that submit in a CPU thread queue. We should compile a single program that controls the whole thing. That should be strictly better than what we have right now. Right now it's a Python program doing submission. A compiled C program, even if it's single-threaded, is going to crush Python.

##### **Nimlgen** [[00:28:07](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1687)]
Runtime is good even now. The problem is elsewhere, but okay.

##### **Geohot** [[00:28:13](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1693)]
I get what you're saying. Let's simplify this. I want every schedule to be compiled as a single program.

##### **Nimlgen** [[00:28:22](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1702)]
Okay. On the other items, the Broadcom driver is merged. The AM driver for virtual functions is a bit annoying because it seems to want the real RLC queue. GIM resets the GPU after several seconds without this scheduler queue. I don't want to copy all these things from AMD because it's a lot. I tried to reuse our user queue and point the RLC scheduler to it, but no luck yet. I'll try to find something better.

##### **Geohot** [[00:29:18](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1758)]
Let's focus on getting HCQ2 merged. I imagine the Broadcom stuff is different between the current path and HCQ2. Let's get HCQ2 merged, including all the network-card stuff. Again, this should all be a completely single-threaded linear program. When we use counters, our synchronization strategy is fundamentally not graph-based; it's a linear-program synchronization strategy.

We shouldn't prematurely optimize for fancier runtime management when our synchronization is still a line. My understanding is that even the fanciest megakernel stuff is still doing single-line synchronization. What do we call the synchronization where there's a single number and everything waits for that number?

##### **Nimlgen** [[00:30:46](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1846)]
A timeline signal.

##### **Geohot** [[00:30:47](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1847)]
Timeline signal. Timeline is the perfect word. That program should be called timeline.

##### **Nimlgen** [[00:31:06](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1866)]
I also tried to remove NOLOCALS. I know it's only about eight lines of hand-coded code, but it's seven or ten percent slower depending on the model. I'm not sure about that. It's the real hand-coded part.

##### **Chrism** [[00:31:29](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1889)]
I had a PR open that did this. I don't know if you saw it. It's not the same performance, but it's pretty close. There's one thing that's broken, but I don't think it's too bad.

##### **Geohot** [[00:31:40](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1900)]
Can you just get that merged?

##### **Chrism** [[00:31:42](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1902)]
Yeah, I can merge it.

##### **Geohot** [[00:31:45](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1905)]
Okay. Chris says we'll remove NOLOCALS. You should never have to deal with that. Focus on making HCQ2 a single compilation. Then NOLOCALS will be gone. I don't care if it's a regression of some percent.

##### **Chrism** [[00:32:07](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1927)]
I mentioned this to them. They were like, "Yeah, whatever."

##### **Geohot** [[00:32:09](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1929)]
They could have paid more for NOLOCALS. NOLOCALS is an expensive feature.

##### **Chenyu** [[00:32:15](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1935)]
Great. Let's move on, and let's try to speed this up a little bit. Next is GPT-OSS.

##### **Wozeparrot** [[00:32:29](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1949)]
I don't have a new run for this week. The box was used over the weekend, so I didn't get to launch one.

##### **Geohot** [[00:32:36](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1956)]
You can kill Kimi.

##### **Wozeparrot** [[00:32:39](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1959)]
Okay. I've been using Kimi too, so it's annoying to kill it.

##### **Geohot** [[00:32:44](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1964)]
We all use Kimi. I have a Kimi API key if you want to use my account. It's just a little slower.

##### **Wozeparrot** [[00:32:57](https://www.youtube.com/watch?v=PVkWak7QG-s&t=1977)]
I'm going to launch a run right after the meeting, and we should be at about 800 milliseconds a step. That's from some Flash Attention kernel optimization and getting rid of the MoE elementwise kernels. The next biggest thing to target is GEMM kernel optimization. The MoE kernels are still pretty slow. I haven't looked into that much.

##### **Geohot** [[00:33:28](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2008)]
How bad are your GEMM kernels? Are you trying to optimize them to LLaMA or beyond LLaMA?

##### **Wozeparrot** [[00:33:34](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2014)]
We need to get them to at least what LLaMA is getting.

##### **Geohot** [[00:33:39](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2019)]
Is what's in AITER good enough, or is what's in AITER not good enough?

##### **Wozeparrot** [[00:33:47](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2027)]
The GEMMs are fine. It's the MoE kernels that aren't. I wasn't able to find any MoE kernels in AITER, or basically anywhere, that have the epilogue and everything else you need for MoE.

##### **Geohot** [[00:34:05](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2045)]
If we need kernels that don't exist, our fastest kernels now, especially once you get into MXFP4, aren't necessarily in those libraries. Are we using FP4 or FP8?

##### **Wozeparrot** [[00:34:25](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2065)]
FP8.

##### **Geohot** [[00:34:26](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2066)]
If we're using FP8, the HipKittens stuff should work.

##### **Wozeparrot** [[00:34:28](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2068)]
Currently it's a HipKittens kernel.

##### **Geohot** [[00:34:32](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2072)]
The MoE kernel? And it's not fast? How slow?

##### **Wozeparrot** [[00:34:43](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2083)]
Under 20% MFU.

##### **Geohot** [[00:34:48](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2088)]
How about the exposed communication stuff?

##### **Wozeparrot** [[00:34:54](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2094)]
I haven't really looked into that because I thought LLaMA was already looking into comms.

##### **Geohot** [[00:35:04](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2104)]
We'll see what LLaMA came up with for comms. I think the LLaMA comms thing is broken. Is this on master?

##### **Wozeparrot** [[00:35:17](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2117)]
No, I still have stuff to merge into master.

##### **Chenyu** [[00:35:27](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2127)]
So we should have a faster run after landing those changes, around 800 milliseconds? We can discuss more about splitting machine loads and making progress on LLaMA. Anything else for GPT-OSS? No? Okay, next is LLaMA.

##### **Qazalin** [[00:35:58](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2158)]
We got one hour and 53 minutes. That's the new time.

##### **Geohot** [[00:36:02](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2162)]
We got a new time?

##### **Qazalin** [[00:36:04](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2164)]
Yeah, one hour and 53 minutes. I said it wasn't going to be faster, but I actually got some wins with the existing GEMMs. Here's the comparison with last week. The GEMMs are still ridiculously bad. Nothing is above 40% MFU.

##### **Geohot** [[00:36:35](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2195)]
That looks a ton better than last week. It looks way faster.

##### **Qazalin** [[00:36:38](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2198)]
It's the best I could get. I squeezed every bit of performance out of the existing stuff we have.

##### **Geohot** [[00:36:51](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2211)]
Nimlgen, how close are we on the VF? Were there actual bugs in it, or are there bugs in the LLaMA runner?

##### **Nimlgen** [[00:37:16](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2236)]
No, I mean GIM resetting the GPU. That's not LLaMA.

##### **Geohot** [[00:37:29](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2249)]
What's resetting the GPU?

##### **Nimlgen** [[00:37:33](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2253)]
The host is resetting the GPU.

##### **Geohot** [[00:37:39](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2259)]
Oh, interesting.

##### **Nimlgen** [[00:37:40](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2260)]
It does that because it doesn't like the RLC scheduler. We don't use that in the AM driver, but it wants to have the KIQ running and valid.

##### **Geohot** [[00:38:02](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2282)]
You can replicate this on our computer, no problem? Do you need eight GPUs to replicate it, or is one enough?

##### **Nimlgen** [[00:38:22](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2302)]
One is enough. Even tiny AMD2 is fine.

##### **Geohot** [[00:38:30](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2310)]
Great. You're welcome to use tiny AMD2 all you want. This might be even higher priority than HCQ2. I want to get a run on DigitalOcean as soon as we can. Is there anything else I can do to help? Would it help to have a DigitalOcean machine that we ran long-term?

##### **Nimlgen** [[00:39:02](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2342)]
No, it's good for now.

##### **Geohot** [[00:39:05](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2345)]
All right, cool. Qazalin, how is the new VIZ stuff coming?

##### **Qazalin** [[00:39:09](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2349)]
The new VIZ stuff? I've been working on tiny H3 and looking at VIZ.

##### **Geohot** [[00:39:17](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2357)]
Great. You can use that. That's your computer.

##### **Qazalin** [[00:39:20](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2360)]
It's pretty good. It's very nice. It reboots so fast and comes back up so fast after rebooting. I did need to reboot it a bunch of times, though. This is the current state of VIZ.

##### **Geohot** [[00:39:36](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2376)]
That needs a lot of work. There's not really just one wave, right?

##### **Qazalin** [[00:39:43](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2383)]
There is one traced wave. We only trace that wave and mask the other ones. I couldn't find a way around that. It's kind of a bummer because then you can't show wave specialization, but it's fine because the kernel isn't wave-specialized.

##### **Geohot** [[00:40:01](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2401)]
Why can't I see the other waves? Who masks the waves?

##### **Qazalin** [[00:40:13](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2413)]
We mask the SIMDs.

##### **Geohot** [[00:40:19](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2419)]
SIMDs aren't waves. Is there really only one wave, and it's just on the SIMDs?

##### **Qazalin** [[00:40:23](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2423)]
Yes. They allocate the entire VGPR and accumulator VGPR space to one wave.

##### **Geohot** [[00:40:38](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2438)]
They basically take over that wave. How do they hide any latency? They don't? They just issue everything? GPUs don't work like this. How do they hide latency between loads and ALU?

##### **Qazalin** [[00:41:01](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2461)]
You can still have multiple waves running at the same time, just not on that SIMD.

##### **Geohot** [[00:41:13](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2473)]
I don't think so. What's the local size for that GEMM, the local size for the MXFP4 GEMM? I think there's a bug. There has to be more than one wave, whether it's doing multi-wave work or because of occupancy. You're telling me occupancy is only a single wave? I guess I could believe that, but you have to do latency hiding with waves.

##### **Qazalin** [[00:42:17](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2537)]
I think what I saw was that there's only one wave that's traced.

##### **Geohot** [[00:42:33](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2553)]
Only one wave that's what?

##### **Qazalin** [[00:42:38](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2558)]
That's traced in SQTT.

##### **Geohot** [[00:42:39](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2559)]
Then we have some misconfiguration. There are four waves. We have to really improve VIZ.

##### **Qazalin** [[00:43:03](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2583)]
There are more problems, like overlaps. I don't quite know how to look at them. The VALU and SALU issue at the same time. I talked with the LLMs about this. rocprof does dispatch patching, and we don't want that.

##### **Geohot** [[00:43:28](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2608)]
Try it in rocprof and see what it looks like. I don't understand: there are four waves, so there can't just be one wave.

##### **Qazalin** [[00:43:35](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2615)]
I'll try it with rocprof. I think we match the instruction stream, but we don't match the timestamps.

##### **Geohot** [[00:43:51](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2631)]
The timestamp stuff has a lot of hacks, and I'm not actually that worried about it. I mean more that if there's one wave with one program counter, you can't hide latency between loads and ALUs. I can't believe it does that.

##### **Geohot** [[00:44:23](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2663)]
All right, VIZ work, and we'll try to get a DigitalOcean run as soon as we possibly can. Maybe I'll give you access to the DigitalOcean account. Be aware that it's expensive, but use it at your discretion. You can spin up a machine and do a run there so we can actually beat AMD's time as soon as the VF stuff is ready.

##### **Qazalin** [[00:45:08](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2708)]
Sounds good.

##### **Chenyu** [[00:45:15](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2715)]
Next, CI.

##### **Chrism** [[00:45:19](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2719)]
I think we're going to stay on GitHub. That was the decision. I'm going to look into getting self-hosted runners for GitHub working. It looks like GARM is probably the way to go. I got setup_tinygrad to be quite fast on the Gitea runners, so I don't see any reason it would be different for GARM VMs. Rather than building a Docker image, I need to build a VM image, which should be relatively straightforward.

I also made some benchmark changes and tried to split up openpilot a little more. It should be even faster if we remove all the comma 3Xs from CI and replace them with comma fours. Then we can have a whole bunch of comma four runners, and it should go by very fast. It was mostly cleaning up how we do CI so it's easier to make setup_tinygrad fast.

##### **Chrism** [[00:46:35](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2795)]
I'm going to try to get everything below three minutes. That's probably the realistic CI goal. I also got the NVIDIA GPU working properly in a VM. For whatever reason, you have to attach it to a PCIe bus, but that fixes it. We should be able to pass devices through into VMs and have everything in VMs, rather than only CPU runners in VMs.

I want to look specifically at how GARM works and see whether we can keep dmesg logs around, or what logs it keeps. That's probably useful rather than tossing them when we toss the VM.

##### **Geohot** [[00:47:26](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2846)]
It should be good about all this. It seemed very nice when I set it up. I want our runners to support both GitHub and Gitea. GARM supports both and listens on both.

##### **Chrism** [[00:47:36](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2856)]
That makes sense. I can start by getting these to run on Gitea, and hopefully it's just a configuration change to get them running on GitHub too.

##### **Geohot** [[00:47:46](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2866)]
We'll have to add GARM to pyinfra and figure out where to run it, probably on the same machine as Gitea.

##### **Chrism** [[00:47:52](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2872)]
That makes sense. The web UI is nice.

##### **Geohot** [[00:47:56](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2876)]
It's great, and it's all one SQLite database. No crazy stuff.

##### **Chrism** [[00:48:03](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2883)]
The only thing that concerned me a little was the architecture of listening for a webhook. It seems complicated, but I guess it works for Namespace.

##### **Geohot** [[00:48:13](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2893)]
It works for Namespace. It's not that complicated. You listen for a webhook. When it gets the webhook, it registers runners, and then GitHub sees that registration and dispatches to your runner. That's it.

##### **Chrism** [[00:48:27](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2907)]
The other thing I read about is how to tell GitHub not to run if, for instance, someone opens a PR and changes the runs-on strategy. I think the only way to prevent that is in the server. GitHub doesn't have configuration for this, so we'll have to figure it out.

##### **Geohot** [[00:48:48](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2928)]
You have a server.

##### **Chrism** [[00:48:51](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2931)]
Yeah. That's mostly it. I'll try to get the NOLOCALS thing merged as well. That should be no problem.

##### **Chenyu** [[00:49:07](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2947)]
Do you think we'll get any real emulator?

##### **Chrism** [[00:49:14](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2954)]
Sorry, real emulator? What do you mean by that?

##### **Chenyu** [[00:49:19](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2959)]
I saw a bunch of people trying to do the QCOM emulator and the new GPU Ocelot.

##### **Chrism** [[00:49:25](https://www.youtube.com/watch?v=PVkWak7QG-s&t=2965)]
Ideally, the new GPU Ocelot looks a lot more like the AMD emulator than just hacking GPU Ocelot to work. I saw a bunch of these hacked-Ocelot PRs. They seem like the sort of thing that works right now, but then we change how the CUDA or PTX renderer works. It starts outputting something that is valid PTX, but the hacked-together GPU Ocelot doesn't support it. The person who claimed the bounty already got the bounty, so they're gone. That's a little bit of a struggle.

##### **Chenyu** [[00:50:18](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3018)]
That was kind of expected. I think even the AMD emulator went through 20 revisions after it merged.

##### **Chrism** [[00:50:28](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3028)]
That's true, but at least the AMD emulator is in the tinygrad codebase. Part of the reason the Ocelot bounty is so hard is that all the Ocelot code is outside tinygrad, none of us knows it very well, and it's all in C++. That's probably not ideal.

##### **Geohot** [[00:50:51](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3051)]
We'll see what happens. I'm hopeful, but we'll see. It would certainly be nice to have a Python Ocelot.

##### **Chenyu** [[00:51:07](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3067)]
Anything else? We also got a bunch of PRs for "kernel args in any input order." I still don't know what those are doing.

##### **Geohot** [[00:51:17](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3077)]
That whole bounty is practically bait. If you paste the bounty into an LLM, it seems to do the wrong thing. It should be clear to anyone who spends 20 minutes trying to understand it, but people don't put in that much effort. It hasn't been too bad to close all the PRs.

##### **Chenyu** [[00:51:42](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3102)]
Okay, moving on. Rangeify?

##### **Geohot** [[00:51:48](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3108)]
No real progress on rangeify, but some big progress on the spec this weekend. I realized that we shouldn't put BUFFERs in the big graph; we should put PARAMs in the big graph. They're PARAMs. When you create a buffer that exists in global scope, it's a PARAM.

Whenever you use BUFFER, it means a locally scoped buffer that can be removed. RETURNED can be removed too. You don't need any of this stuff. It's all either PARAM or BUFFER. PARAM means it is inherited from a higher scope. BUFFER means it's a local buffer that only survives for the current scope of the CALL. When this is done, it'll be simple to reason about.

##### **Chenyu** [[00:52:43](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3163)]
Should a BUFFER know its own scope?

##### **Geohot** [[00:52:48](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3168)]
A BUFFER's scope is defined by its CALL.

##### **Chenyu** [[00:52:52](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3172)]
So the BUFFER itself shouldn't be aware of its scope. It's just a BUFFER.

##### **Geohot** [[00:52:58](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3178)]
It's just a BUFFER. The BUFFER exists in arg zero of CALL, which is the call body. A call body can contain a BUFFER, but that BUFFER cannot be returned or leak out of the call body. It can go inward. If you have another CALL inside that call body, the BUFFER can be an argument to that CALL, and then it appears in the inner body as a PARAM.

You can do this recursively. You can have a CALL inside that CALL with a PARAM as an argument, and then another PARAM inside. PARAM means it comes from a higher scope. BUFFER means it exists only in this scope and further inner scopes, assuming it's passed in. We don't have any kind of closures.

There's BUFFER and PARAM. These are fundamental, and they can remove RETURNED, TUPLE, and GETTUPLE. Instead of RETURNED, just use a BUFFER. We shouldn't be afraid of writing optimizations that remove BUFFERs. When I have something that looks like a BUFFER construction, STORE, and AFTER, that whole BUFFER, STORE, AFTER sequence can be removed. In certain cases you can pass the STORE's input straight through to whatever is downstream. You know it's safe because BUFFER only exists in the current CALL scope.

##### **Chenyu** [[00:54:32](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3272)]
Great.

##### **Geohot** [[00:54:34](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3274)]
There will be more cleanups. It's going to remove RETURNED, which I just added, because RETURNED looks more like BUFFER. TUPLE and GETTUPLE are already gone. Then I thought more about what UNSHARD is, and UNSHARD is just END. That's why it's so tempting to push it down.

Think about what UNSHARD does. I have something with four elements on each device, and I want to turn it into a four-by-four matrix. I END the device range. When I END the device range, I get a four-by-four shape because END reinserts the range at the front. That's not actually a renderable graph. You can't render a graph that has an END for a range you didn't open. You have to make that END end up at the bottom of the graph. You can do this by pushing it or with some rangeify magic; we'll see.

UNSHARD will become END, and only PARAM and BUFFER will exist. In the big graph, all the long-lived buffers aren't BUFFERs, because a BUFFER only exists in local scope. If you want to pass in a buffer from the magical buffer holder in the sky, that's a PARAM. That'll be my week. We should get rid of two more ops. There are only 77 left.

##### **Chenyu** [[00:56:12](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3372)]
We still have 77?

##### **Geohot** [[00:56:15](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3375)]
Well, we still have 70. It's down. It's shrinking.

##### **Chenyu** [[00:56:20](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3380)]
Yes, I'm aware. Cool. Sounds good.

##### **Geohot** [[00:56:25](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3385)]
We should make that graph and figure out when we're going to get to zero. Not zero, but what is it going to bottom out at? I don't know.

##### **Chenyu** [[00:56:42](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3402)]
We'll see. I think it's nice that the spec text, the PDF, is getting closer and closer to the actual codebase. I find that pretty useful. I also saw you added PARAM args.

##### **Geohot** [[00:57:04](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3424)]
RETURNED is going away. We're just going to have PARAM and BUFFER, and they're both going to have PARAM args.

##### **Chenyu** [[00:57:14](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3434)]
Great. Anything else? No? Moving on. dtype is gone. CONSTs now all have weak dtypes, and there's no more pushing dtypes left and right. dtype is no longer a UOp attribute. For CUSTOM, CODE, and INS, it's just shoved into the arg. We can worry about spec'ing those better later, but I think it's pretty nice now.

##### **Geohot** [[00:57:52](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3472)]
That's a huge victory. It's amazing that you got rid of dtype. Every one of my clean-room rewrites of tinygrad has never had dtype. It's great that it's actually done.

##### **Chenyu** [[00:58:08](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3488)]
We need someone to work more on x86 or assembly. I'm pretty sure half of x86 is dead now. All the vectorized code is dead.

##### **Geohot** [[00:58:29](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3509)]
The vector stuff isn't triggering anymore?

##### **Chenyu** [[00:58:32](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3512)]
It was, but the vectorizer was removed afterward, and there's no real test for whether AVX is triggered.

##### **Geohot** [[00:58:41](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3521)]
It never should have been like this. We can rip all of that out. x86 should never have been about speed; it should only have been about correctness.

##### **Chenyu** [[00:58:53](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3533)]
So no objection if I remove half the things that no longer trigger?

##### **Geohot** [[00:58:59](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3539)]
Not at all.

##### **Chenyu** [[00:59:00](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3540)]
Okay. It was kind of annoying. Maybe there's a better way to do the dtype layer, but I realized there was a lot of dead code anyway.

##### **Geohot** [[00:59:11](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3551)]
The only good things that came from the assembly PR were thinking about where we're putting instruction selection and register allocation.

##### **Chenyu** [[00:59:24](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3564)]
I agree. It's nice to have that layer. I'll remove more stuff from it since I have the diff anyway. Next, I'm interested in fixing more ASSIGN stuff. There are still a bunch of things that aren't correct. We have some issues, and I hope now is a better time to fix it again.

##### **Geohot** [[00:59:55](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3595)]
Hopefully the BUFFER/PARAM scoping simplifies a bunch of things there too.

##### **Chenyu** [[01:00:01](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3601)]
Yes, that's my hope. We'll see how this goes.

##### **Chrism** [[01:00:10](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3610)]
I think the copy work also makes a big difference, like the copy compiler.

##### **Chenyu** [[01:00:18](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3618)]
The copy compiler is one. It's also related to disk. That's another. I'll think about this more. I think there's also some big cast cleanup that wasn't really merged. I'll look into what's happening there. These are all kind of related, but not really. I'll see if I can write something better.

Most things on torch.compile are fine. I think they changed some API in the latest version, which is annoying, but I'll do whatever I have to. That's pretty much it. The RDNA3 bounty is happy, I assume.

##### **Geohot** [[01:01:20](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3680)]
Yeah. I probably have a bunch of things to merge.

##### **Chenyu** [[01:01:33](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3693)]
If they're happy, they're good. We have Flata here. Do you have something to say? We'll do Flata, B1tg, and Raine.

##### **Flata** [[01:01:47](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3707)]
The correctness run I did failed. I think it NaNed out, so I need to figure that out. There was also an argument mismatch in the JIT during eval, so I need to look at that. Those are the blockers to making the Flux run happen.

##### **Geohot** [[01:02:07](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3727)]
Are we actually going to be able to submit this to MLPerf?

##### **Flata** [[01:02:12](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3732)]
That's what I'm targeting.

##### **Geohot** [[01:02:14](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3734)]
What's our time looking like?

##### **Flata** [[01:02:17](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3737)]
Not so great right now, because I haven't worked on the BEAM stuff yet. I increased the batch size, but without any BEAM it was about nine seconds per step, so definitely not good for MLPerf.

##### **Geohot** [[01:02:35](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3755)]
How long is the run, order of magnitude?

##### **Flata** [[01:02:40](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3760)]
I think it's more than 30,000 steps.

##### **Geohot** [[01:02:44](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3764)]
I see your run taking two days and 11 hours. Runs like that are extremely difficult to debug.

##### **Flata** [[01:02:54](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3774)]
Right. I'll try to get it down to a much easier run that definitely won't take two days to debug. I'll work on that.

##### **Chenyu** [[01:03:18](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3798)]
Cool. B1tg, did you want to say something? If not, Raine, do you want to say something?

##### **Raine** [[01:03:32](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3812)]
I think it's getting there. CI is all passing. We mostly have correctness on small kernels; it's just scaling it up on hardware. I started running tests like BEAM MNIST and BEAM LLaMA. I was having problems with how I managed renderer state and how many registers I allocated. You can't just set the upper limit to 256. Otherwise, dispatch sometimes hangs and throws memory exceptions because they don't all fit onto a compute unit.

I've been debugging that. It's structural stuff, but I think it should be close to ready this week. I'm cleaning up the bad parts, not adding new features. I'm making sure it all runs properly at higher scales.

##### **Geohot** [[01:04:17](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3857)]
You have this file called mem2reg.py. This kind of stuff shouldn't exist.

##### **Raine** [[01:04:24](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3864)]
How else do we manage REG buffer semantics?

##### **Geohot** [[01:04:29](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3869)]
REG buffers are registers. In assembly, AddrSpace.REG and AddrSpace.ALU are the same thing.

##### **Raine** [[01:04:37](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3877)]
The problem is managing control flow. With LOAD and STORE operations in the UOps, it's modeled as memory, but that doesn't work with SSA form. There has to be a conversion where you turn it into copies. That was really hacky before in the RDNA backend file, so I was trying to clean it up.

##### **Geohot** [[01:04:59](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3899)]
There doesn't have to be any conversion. When you do a LOAD, it loads into registers. Every loop variable is always in a register. If you have more than will fit, you deal with that by spilling. There shouldn't be a pass like this that starts them out as memory. Everything should start as registers, and then in some extreme one-percent case, you can spill.

##### **Raine** [[01:05:28](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3928)]
If you have a LOAD in a loop and then STORE after it, how do you manage that in the backend pass, during instruction selection?

##### **Geohot** [[01:05:38](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3938)]
When you do DEFINE_REG, that should create a bunch of named registers. Or it's BUFFER now. When you do a register BUFFER, those should just be named registers. You can have two pools: a pool of named registers and a pool of random registers.

##### **Raine** [[01:06:01](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3961)]
How do you route it so it knows it's being used backward in program time? How do you route the LOADs and STOREs so register allocation can spill if it needs to provide a value to a back edge?

##### **Geohot** [[01:06:16](https://www.youtube.com/watch?v=PVkWak7QG-s&t=3976)]
You want to preallocate those registers. Every time you use DEFINE_REG, preallocate a set of registers that won't be used for anything else. What if you define two of these and it becomes a lot of registers? That should be dealt with by the memory planner. DEFINE_REG means define registers. It doesn't mean memory. I know that in C it means memory, but in assembly it should mean registers and shouldn't interact with the register allocator.

##### **Raine** [[01:06:55](https://www.youtube.com/watch?v=PVkWak7QG-s&t=4015)]
So every reference to the same index into a buffer writes the exact same named register?

##### **Geohot** [[01:07:01](https://www.youtube.com/watch?v=PVkWak7QG-s&t=4021)]
Yes.

##### **Raine** [[01:07:03](https://www.youtube.com/watch?v=PVkWak7QG-s&t=4023)]
Okay. I was trying to do that before, but it was pretty hacky. I think I can fix it up.

##### **Geohot** [[01:07:08](https://www.youtube.com/watch?v=PVkWak7QG-s&t=4028)]
I don't think it should be hacky. DEFINE_REG is pretty rare; it's used for accumulators. Your accumulator is just defined. Theoretically, you might reduce register pressure if you allocate these things dynamically. In practice, I don't think that will happen, because the accumulator is already at the highest-pressure point of the loop.

Okay, sounds good. I think that's pretty much it. Anything else for the meeting? I don't think so. That's it for this meeting. Thank you, everyone. See you next week.

##### **Chenyu** [[01:07:58](https://www.youtube.com/watch?v=PVkWak7QG-s&t=4078)]
Bye-bye.

##### **Geohot** [[01:07:59](https://www.youtube.com/watch?v=PVkWak7QG-s&t=4079)]
Bye.
