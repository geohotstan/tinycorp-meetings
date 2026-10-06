# 2026-10-06 Meeting

### Meeting Agenda

**Time:** new meeting #40, 10/6 12pm Hong Kong time
- company update
- CALL, UIR, course
- MLPerf
- HCQ2
- CI
- assembly
- bounties, Comma, RDNA


### Audio

[Youtube Link](https://www.youtube.com/watch?v=eojuJ_9for8)

### Highlights

### Transcript
##### **Wozeparrot** [[00:00:00](https://www.youtube.com/watch?v=eojuJ_9for8&t=0)]
Okay, we'll start with the company update.

##### **Geohot** [[00:00:03](https://www.youtube.com/watch?v=eojuJ_9for8&t=3)]
Cool. Yeah, so we have a course. I'm 90% confident it's going to be spring semester at CMU. I think CMU is the right place to do this, the top-ranked CS school in the world. We'll expose a lot of people to tinygrad ideas. That's the main thing.

##### **Geohot** [[00:00:39](https://www.youtube.com/watch?v=eojuJ_9for8&t=39)]
No real communication with AMD recently. They're working on what our new contract is going to be. And on the secret project, we hopefully have an announcement next week. Hopefully, if it's ready and we have everything ready, we'll be announcing a new product. So yeah, that's it.

##### **Wozeparrot** [[00:01:09](https://www.youtube.com/watch?v=eojuJ_9for8&t=69)]
Cool. Moving on to CALL, UIR, and I guess just your stuff.

##### **Geohot** [[00:01:14](https://www.youtube.com/watch?v=eojuJ_9for8&t=74)]
Cool. The main thing I worked on was UIR. Hopefully it's been sufficiently shoved everywhere so you can all see it. When you use viz now, instead of having pyrender, which was some janky Python code that might reconstruct the thing, it's now a text-based format that looks like LLVM IR: UIR. It's a text-based representation of a UOp graph.

##### **Geohot** [[00:01:45](https://www.youtube.com/watch?v=eojuJ_9for8&t=105)]
I think we're going to start seeing this in a lot more places. This is also going to replace the pickling of UOps. Instead of pickling and ending up with who knows what, we'll be using UIR as an interchange format. If you think about saving a JIT, you'll be able to save a JIT as a safetensors file. I checked this morning: you can add metadata to safetensors. There'll be a UIR section of the metadata, and then a safetensors file becomes a self-runnable neural network. You could even imagine this someday replacing ONNX because it's a lot simpler than ONNX. You just have the UIR, which tells you how to execute the model, and the buffer slots will just be the slots in the safetensors file. I'll add that stuff.

##### **Geohot** [[00:02:40](https://www.youtube.com/watch?v=eojuJ_9for8&t=160)]
I've also been working on the course, and the course is leading me to a bunch of minor spec cleanups. I got one merged yesterday: we used to put extra sources on the RANGE to specify dependencies, but I've switched that to AFTER. You can actually use AFTER on a CONST now. You're like, 'Well, what does AFTER on a CONST mean? A CONST doesn't change.' Yeah, but it still has the same basic meaning. What AFTER means is that the things in src[1:] run before source zero is passed through the AFTER. You can see how that's the same semantics as the RANGE thing.

##### **Geohot** [[00:03:29](https://www.youtube.com/watch?v=eojuJ_9for8&t=209)]
It's not a buffer. It's not a versioned CONST, obviously, but I think we can use it for that. I'm also working on cleaning up BUFFER, PARAM, and ALLOC to put the size in a source instead of putting the size in the args, because I think we do want PARAMs to support symbolic sizes.

##### **Geohot** [[00:04:00](https://www.youtube.com/watch?v=eojuJ_9for8&t=240)]
If you think about what this CALL API can become, you could imagine writing entire convolutions and GEMMs with CALL. You can write a generic convolution that's a CALL, then put in an X and a W and a bunch of parameters. They all have to check out; they all have to be consistent. If I have a symbolic parameter, that symbolic parameter sure better match the rest of the arguments. So, still minor changes to this.

##### **Geohot** [[00:04:38](https://www.youtube.com/watch?v=eojuJ_9for8&t=278)]
Overall, I want to really, really clean up UIR. I want everything to be nailed down and kind of perfect. I think there are many things that we just never have to change again. It'll be with us for a long time.

##### **Wozeparrot** [[00:04:56](https://www.youtube.com/watch?v=eojuJ_9for8&t=296)]
Cool. Anything else?

##### **Geohot** [[00:04:58](https://www.youtube.com/watch?v=eojuJ_9for8&t=298)]
No, but if you're at CMU, you're going to have a course to sign up for. The course will not be recorded. It's a one-time and one-time-only thing. It's a real event in the physical world, because everything that goes online just gets fed to the machines these days. This is the anti-streaming.

##### **Wozeparrot** [[00:05:29](https://www.youtube.com/watch?v=eojuJ_9for8&t=329)]
Okay, moving on to my stuff. I did the initial submission for both GPT-OSS runs, so we're submitted for two-machine and single-machine GPT-OSS. Single-machine is 117 minutes, and two-machine is 67.2 minutes. I know for dual-machine we wanted under 66.

##### **Geohot** [[00:05:53](https://www.youtube.com/watch?v=eojuJ_9for8&t=353)]
I mean, I think it's fine.

##### **Wozeparrot** [[00:05:56](https://www.youtube.com/watch?v=eojuJ_9for8&t=356)]
The time that we have is under 66, but we converge a little faster than RCP, so they apply a scaling factor of 1.02 to our time.

##### **Nimlgen** [[00:06:07](https://www.youtube.com/watch?v=eojuJ_9for8&t=367)]
I see. Ideally we should land like NVIDIA: they have three runs at 18 evals and seven at 19. Do we have that, or do we have more at 18 evals?

##### **Wozeparrot** [[00:06:23](https://www.youtube.com/watch?v=eojuJ_9for8&t=383)]
I just ran ten runs in a row. I don't know if we want to; we could be cherry-picking runs.

##### **Geohot** [[00:06:28](https://www.youtube.com/watch?v=eojuJ_9for8&t=388)]
I'm happy with what we got. AMD wanted us to strive for 66. That's not the hard gate in the contract; the hard gate is 71. We got them two extra minutes on the single machine, so there's one penalty minute on the two machines. I'm totally fine with the times. Let's just get the LLaMA one submitted.

##### **Wozeparrot** [[00:06:52](https://www.youtube.com/watch?v=eojuJ_9for8&t=412)]
Yeah, so the main one is LLaMA. My current ten LLaMA runs average to 101.2 minutes. The target is under 101. On the updated branch, it doesn't run: it'll run, and somewhere midway it hangs in eval.

##### **Geohot** [[00:07:10](https://www.youtube.com/watch?v=eojuJ_9for8&t=430)]
I definitely want to fix that bug. Again, 101.2 is fine. What's our two-machine LLaMA?

##### **Wozeparrot** [[00:07:18](https://www.youtube.com/watch?v=eojuJ_9for8&t=438)]
I thought our target for one machine was under something. I don't know what's in the contract.

##### **Geohot** [[00:07:24](https://www.youtube.com/watch?v=eojuJ_9for8&t=444)]
No, there's no target. LLaMA is not...

##### **Wozeparrot** [[00:07:26](https://www.youtube.com/watch?v=eojuJ_9for8&t=446)]
Two-machine is two hours. The main problem with two-machine is that setup takes an hour by itself, which is over the 30-minute setup time limit.

##### **Geohot** [[00:07:37](https://www.youtube.com/watch?v=eojuJ_9for8&t=457)]
Okay, we have to fix this. 101.2 is totally fine for single-machine. Let's get that submitted. For two-machine, I just want us to have something that's not embarrassing. Under 60 minutes, let's say. We can't submit something to the board where we get 120 with two machines and 101 with one. We still have a little bit of time. Let's fix whatever we need to get two-machine LLaMA under 60. Is that a reasonable target?

##### **Wozeparrot** [[00:08:22](https://www.youtube.com/watch?v=eojuJ_9for8&t=502)]
Yeah. I think our current fastest is 90 minutes.

##### **Geohot** [[00:08:29](https://www.youtube.com/watch?v=eojuJ_9for8&t=509)]
Yeah, this is embarrassing.

##### **Wozeparrot** [[00:08:33](https://www.youtube.com/watch?v=eojuJ_9for8&t=513)]
That's not accounting for setup time either. If you shift the 30 minutes of extra setup time into the actual runtime, it's like two hours.

##### **Geohot** [[00:08:42](https://www.youtube.com/watch?v=eojuJ_9for8&t=522)]
Okay, we've got to fix this. What can we do? Everyone who worked on LLaMA?

##### **Nimlgen** [[00:08:54](https://www.youtube.com/watch?v=eojuJ_9for8&t=534)]
I think we definitely should fix it. I'll fix the setup speed, the setup time. For the runtime, I don't know about 60 minutes, but I think 70 should be reasonably easy to get. The main problem is the overlapping issue again. For GPT-OSS, I basically had a pass where I manually reshuffled some kernels. It's pretty easy to do for LLaMA as well and get a reasonable time.

##### **Geohot** [[00:09:33](https://www.youtube.com/watch?v=eojuJ_9for8&t=573)]
Our scaling factor for GPT-OSS is 57%. If you take 67 divided by 117, that's 57%. So 57% of 101 is like 58. I really do want to get it there. It makes tinygrad look bad if we're scaling that poorly across two machines.

##### **Nimlgen** [[00:10:01](https://www.youtube.com/watch?v=eojuJ_9for8&t=601)]
Yeah. Okay, I'll take that.

##### **Wozeparrot** [[00:10:05](https://www.youtube.com/watch?v=eojuJ_9for8&t=605)]
When I was running two-machine LLaMA, it's BS32, but gradient accumulation is still on. I don't know if that was intended.

##### **Nimlgen** [[00:10:20](https://www.youtube.com/watch?v=eojuJ_9for8&t=620)]
I didn't change any of that.

##### **Geohot** [[00:10:24](https://www.youtube.com/watch?v=eojuJ_9for8&t=624)]
We might want to, though. What are we gradient-accumulating to normally?

##### **Wozeparrot** [[00:10:28](https://www.youtube.com/watch?v=eojuJ_9for8&t=628)]
To a global batch size of 32. We can just do 32 across two machines.

##### **Geohot** [[00:10:35](https://www.youtube.com/watch?v=eojuJ_9for8&t=635)]
Yeah, maybe we can just turn gradient accumulation off. I really do want to get...

##### **Wozeparrot** [[00:10:38](https://www.youtube.com/watch?v=eojuJ_9for8&t=638)]
Without gradient accumulation, I found that with a global batch size of 64 it was unstable.

##### **Geohot** [[00:10:47](https://www.youtube.com/watch?v=eojuJ_9for8&t=647)]
Yeah, I think it's fine, I guess, if we do 32.

##### **Wozeparrot** [[00:10:54](https://www.youtube.com/watch?v=eojuJ_9for8&t=654)]
32 matches our single-machine runs, in terms of knowing that this will converge.

##### **Geohot** [[00:11:02](https://www.youtube.com/watch?v=eojuJ_9for8&t=662)]
Yeah, I don't know if we're wasting tons of time syncing then. I don't know what the overhead is. Okay, but we have till the 16th; we have ten days. Let's really try to get it under 60 minutes.

##### **Nimlgen** [[00:11:22](https://www.youtube.com/watch?v=eojuJ_9for8&t=682)]
Yeah.

##### **Geohot** [[00:11:23](https://www.youtube.com/watch?v=eojuJ_9for8&t=683)]
Again, just so tinygrad looks good. Otherwise it looks like we have some problem with our scaling. Some small penalty for scaling is fine, but even 70 minutes, it's like, really, you can't scale across GPUs? Are we good with 101.2? Did you ever get much better than that?

##### **Wozeparrot** [[00:11:51](https://www.youtube.com/watch?v=eojuJ_9for8&t=711)]
That's on par with the best.

##### **Geohot** [[00:11:53](https://www.youtube.com/watch?v=eojuJ_9for8&t=713)]
Okay, 101.2 for single-machine. Let's get that submitted.

##### **Wozeparrot** [[00:11:55](https://www.youtube.com/watch?v=eojuJ_9for8&t=715)]
Okay, I'll submit that right after the meeting.

##### **Geohot** [[00:12:01](https://www.youtube.com/watch?v=eojuJ_9for8&t=721)]
What's NVIDIA's time?

##### **Wozeparrot** [[00:12:08](https://www.youtube.com/watch?v=eojuJ_9for8&t=728)]
Have they submitted already this round?

##### **Geohot** [[00:12:11](https://www.youtube.com/watch?v=eojuJ_9for8&t=731)]
Oh no, I mean the last one.

##### **Geohot** [[00:12:26](https://www.youtube.com/watch?v=eojuJ_9for8&t=746)]
Oh, one hour, twenty minutes. Yeah, 101 is fine.

##### **Wozeparrot** [[00:12:36](https://www.youtube.com/watch?v=eojuJ_9for8&t=756)]
Okay, that's all for MLPerf. HCQ2?

##### **Nimlgen** [[00:12:45](https://www.youtube.com/watch?v=eojuJ_9for8&t=765)]
I've been adding functions and binaries into HCQ2. It's done; it looks cleaner now.

##### **Geohot** [[00:13:02](https://www.youtube.com/watch?v=eojuJ_9for8&t=782)]
So CL is...

##### **Nimlgen** [[00:13:06](https://www.youtube.com/watch?v=eojuJ_9for8&t=786)]
Yeah, CL is still to do. I'll probably do it this week after the LLaMA fixes.

##### **Geohot** [[00:13:21](https://www.youtube.com/watch?v=eojuJ_9for8&t=801)]
Did you see all those compiler warnings? What are those?

##### **Nimlgen** [[00:13:25](https://www.youtube.com/watch?v=eojuJ_9for8&t=805)]
Yeah, I've fixed those. I think I fixed them all. I haven't seen any new ones, only the one you posted.

##### **Geohot** [[00:13:47](https://www.youtube.com/watch?v=eojuJ_9for8&t=827)]
How close are we? Is CL the last one, or are there more?

##### **Nimlgen** [[00:13:53](https://www.youtube.com/watch?v=eojuJ_9for8&t=833)]
CL, and I think Python and CPU. I'm not sure about Python and CPU because we still need the old API for them to submit the HCQ program itself.

##### **Geohot** [[00:14:14](https://www.youtube.com/watch?v=eojuJ_9for8&t=854)]
That might be fine. I'm not exactly sure what it means for Python and CPU to become HCQ2.

##### **Nimlgen** [[00:14:33](https://www.youtube.com/watch?v=eojuJ_9for8&t=873)]
Yeah, so also with functions...

##### **Geohot** [[00:14:37](https://www.youtube.com/watch?v=eojuJ_9for8&t=877)]
When I look at CUDA now, I see there's no more CUDAProgram. So CUDAProgram is just gone?

##### **Nimlgen** [[00:14:46](https://www.youtube.com/watch?v=eojuJ_9for8&t=886)]
Yeah. There's bufferize, which allocates the program using the CUDA APIs and hands the handle to the runtime, to the C program.

##### **Geohot** [[00:15:09](https://www.youtube.com/watch?v=eojuJ_9for8&t=909)]
I see. Okay, so this is pm_bufferize.

##### **Nimlgen** [[00:15:15](https://www.youtube.com/watch?v=eojuJ_9for8&t=915)]
Yeah, there's the function that actually does the module loading.

##### **Geohot** [[00:15:23](https://www.youtube.com/watch?v=eojuJ_9for8&t=923)]
I see the function returns a buffer. Does CUDA let you execute any buffer as a program?

##### **Nimlgen** [[00:15:35](https://www.youtube.com/watch?v=eojuJ_9for8&t=935)]
No, it doesn't. Basically, this buffer just contains one integer, which is the handle, kind of the pointer.

##### **Geohot** [[00:15:58](https://www.youtube.com/watch?v=eojuJ_9for8&t=958)]
I see. But is it a buffer?

##### **Nimlgen** [[00:16:06](https://www.youtube.com/watch?v=eojuJ_9for8&t=966)]
In tinygrad it's the buffer supplied as the argument, but in CUDA it's not; it's just a handle.

##### **Geohot** [[00:16:15](https://www.youtube.com/watch?v=eojuJ_9for8&t=975)]
I also see functools.cache on there, so those never get freed.

##### **Nimlgen** [[00:16:22](https://www.youtube.com/watch?v=eojuJ_9for8&t=982)]
Yeah, all our programs are never freed.

##### **Geohot** [[00:16:29](https://www.youtube.com/watch?v=eojuJ_9for8&t=989)]
The thing I worry about is that ideally, and maybe this isn't possible in the CUDA API, I want programs to use the same lifecycle management as buffers. Is this how it is in NV and stuff?

##### **Nimlgen** [[00:16:49](https://www.youtube.com/watch?v=eojuJ_9for8&t=1009)]
No, I can just remove the cache, and it should be like that.

##### **Geohot** [[00:16:54](https://www.youtube.com/watch?v=eojuJ_9for8&t=1014)]
I'm not that worried about CUDA. I'm more worried about NV.

##### **Nimlgen** [[00:17:00](https://www.youtube.com/watch?v=eojuJ_9for8&t=1020)]
Currently there's an explicit cache for the programs, but it's removable.

##### **Geohot** [[00:17:09](https://www.youtube.com/watch?v=eojuJ_9for8&t=1029)]
The other thing is that I've struggled to make that change once I get to the HCQ layer, where parameters are just normal inputs to the program. Right now we have a whole bunch of extra logic to bind the parameters to the program, when there really shouldn't be. I'm not sure exactly what has to change for this. Every time I've tried to do it, I struggle once I get to HCQ. Maybe I just need to sit down and try harder.

##### **Nimlgen** [[00:17:58](https://www.youtube.com/watch?v=eojuJ_9for8&t=1078)]
You can show me your PR, and maybe I can polish that part.

##### **Geohot** [[00:18:07](https://www.youtube.com/watch?v=eojuJ_9for8&t=1087)]
Okay. So ops_amd works with both devices. That all seems good. We have HIP and CUDA, and they're very short. Oh, HIP is still the old way?

##### **Nimlgen** [[00:18:29](https://www.youtube.com/watch?v=eojuJ_9for8&t=1109)]
Yeah, it's not even exposed, really. It's used for debugging. It's the old one.

##### **Geohot** [[00:18:38](https://www.youtube.com/watch?v=eojuJ_9for8&t=1118)]
HIP needs to become like CUDA. HIP and CUDA are so similar. I almost wonder if they can entirely share code.

##### **Nimlgen** [[00:19:01](https://www.youtube.com/watch?v=eojuJ_9for8&t=1141)]
Yeah, I'll think about that. I think it's possible.

##### **Nimlgen** [[00:19:13](https://www.youtube.com/watch?v=eojuJ_9for8&t=1153)]
Also, we now have error handling for HCQ2. I don't know if they're happier now.

##### **Chrism** [[00:19:20](https://www.youtube.com/watch?v=eojuJ_9for8&t=1160)]
The thing they were complaining about most recently is when you unplug power from the Chestnut, apparently it just hangs forever. If that's fixed, then they're happy. I believe that fixes all their errors.

##### **Nimlgen** [[00:19:37](https://www.youtube.com/watch?v=eojuJ_9for8&t=1177)]
Okay.

##### **Chrism** [[00:19:41](https://www.youtube.com/watch?v=eojuJ_9for8&t=1181)]
I haven't tested that. I don't know if you have.

##### **Nimlgen** [[00:19:50](https://www.youtube.com/watch?v=eojuJ_9for8&t=1190)]
Okay, I'll test that better. I've tested the general error handling for USB. We can now reset USB as well. If the GPU is wedged, you shouldn't have to replug it; tinygrad can recover it.

##### **Geohot** [[00:20:11](https://www.youtube.com/watch?v=eojuJ_9for8&t=1211)]
Are you toggling the PCIe power for that, or the ATX?

##### **Nimlgen** [[00:20:17](https://www.youtube.com/watch?v=eojuJ_9for8&t=1217)]
No, we just reset the GPU. We recover it with an IP reset, and the same for the USB library.

##### **Geohot** [[00:20:31](https://www.youtube.com/watch?v=eojuJ_9for8&t=1231)]
What kind of power reset?

##### **Nimlgen** [[00:20:39](https://www.youtube.com/watch?v=eojuJ_9for8&t=1239)]
IP reset, I mean the blocks of the GPU, like SDMA and compute.

##### **Geohot** [[00:20:47](https://www.youtube.com/watch?v=eojuJ_9for8&t=1247)]
Oh, I see.

##### **Nimlgen** [[00:20:48](https://www.youtube.com/watch?v=eojuJ_9for8&t=1248)]
So it's not about power.

##### **Geohot** [[00:20:51](https://www.youtube.com/watch?v=eojuJ_9for8&t=1251)]
Can you also get this merged? I posted in HCQ if you want to clean that up. The MI350P startup time is really slow because the mmap is really slow.

##### **Nimlgen** [[00:21:18](https://www.youtube.com/watch?v=eojuJ_9for8&t=1278)]
I don't know if you want to write it how GPT wrote it.

##### **Geohot** [[00:21:24](https://www.youtube.com/watch?v=eojuJ_9for8&t=1284)]
It's kind of meh. I think it should just be generic. I don't know if there needs to be another wrapper class.

##### **Nimlgen** [[00:21:35](https://www.youtube.com/watch?v=eojuJ_9for8&t=1295)]
Yeah, okay, I'll take a look.

##### **Chrism** [[00:21:38](https://www.youtube.com/watch?v=eojuJ_9for8&t=1298)]
The deal with the Comma stuff is that their philosophy is, if there's any weird flakiness going on with the GPU, they just fall back to the Qualcomm. They just need to be able to detect whether something happened. Previously, the issue was that it would hang, and they had no way of knowing that there was some weirdness going on.

##### **Geohot** [[00:21:57](https://www.youtube.com/watch?v=eojuJ_9for8&t=1317)]
Okay. Speaking of resets, if you can find any way to reset the MI350P: when I did the port, it seemed even harder to reset than the MI350X. It's so easy to get into a bad state. I wonder if you can find something, or if there even is a way. I had the LLMs look at the kernel, and they couldn't really find anything. I don't know.

##### **Nimlgen** [[00:22:33](https://www.youtube.com/watch?v=eojuJ_9for8&t=1353)]
Okay. Also, I'm thinking about whether the memory planner should use ALLOC. Currently, for the arena buffer, we use Ops.BUFFER. Should we switch that to ALLOC? That would simplify JIT a lot, because we could just delete the linear and free all the buffers.

##### **Geohot** [[00:22:54](https://www.youtube.com/watch?v=eojuJ_9for8&t=1374)]
Oh yeah, absolutely. All the intermediates in the function call should absolutely switch to ALLOC.

##### **Nimlgen** [[00:23:05](https://www.youtube.com/watch?v=eojuJ_9for8&t=1385)]
Okay.

##### **Geohot** [[00:23:07](https://www.youtube.com/watch?v=eojuJ_9for8&t=1387)]
That was kind of planned. When you do an ALLOC, it has to be in the scope of CALL. The idea of ALLOC is that it doesn't survive the scope of the CALL; it's just for one run. I'm totally fine with the JIT hitting the LRU cache every time to reallocate that thing. We can delete the stupid stuff in the JIT that says free_intermediates. Ideally we just want to do that every time, even at a tiny performance hit. It'd be great to just hit the LRU allocator.

##### **Geohot** [[00:23:51](https://www.youtube.com/watch?v=eojuJ_9for8&t=1431)]
Great. Glad the HCQ2 journey is... Anything else?

##### **Nimlgen** [[00:24:03](https://www.youtube.com/watch?v=eojuJ_9for8&t=1443)]
No, that's it for me.

##### **Wozeparrot** [[00:24:06](https://www.youtube.com/watch?v=eojuJ_9for8&t=1446)]
Moving on to CI.

##### **Chrism** [[00:24:09](https://www.youtube.com/watch?v=eojuJ_9for8&t=1449)]
The big thing I've been working on is the queue time: the time between when you submit your job and when it actually starts executing. This required some work that we were going to have to do anyway to get GPU runners working, so it was worth doing. It turns out the built-in GARM provider is not very good, so it's good to have our own, because we'll need it anyway for GPU runners.

##### **Chrism** [[00:24:45](https://www.youtube.com/watch?v=eojuJ_9for8&t=1485)]
Right now it takes about 25 seconds between submitting and the job actually starting, which is not great. I think I can probably shave another five seconds off that, and then it won't feel so horrible. That's where we're at. It turns out we're doing all this stupid stuff as we boot the kernel, like waiting a second for a framebuffer that's never going to appear. It's dumb. We should just not do that.

##### **Chrism** [[00:25:22](https://www.youtube.com/watch?v=eojuJ_9for8&t=1522)]
The other stuff I did: the DEV syntax for specifying the arch works now. We just need to re-enable the HCQ2 runner. I think that needs some credentials.

##### **Geohot** [[00:25:39](https://www.youtube.com/watch?v=eojuJ_9for8&t=1539)]
You can create the credentials.

##### **Chrism** [[00:25:43](https://www.youtube.com/watch?v=eojuJ_9for8&t=1543)]
I haven't tried to do that, but I'll try.

##### **Geohot** [[00:25:44](https://www.youtube.com/watch?v=eojuJ_9for8&t=1544)]
If not, you should be a maintainer of CI on GitHub.

##### **Chrism** [[00:25:51](https://www.youtube.com/watch?v=eojuJ_9for8&t=1551)]
All right. Anyway, re-enable that.

##### **Geohot** [[00:25:55](https://www.youtube.com/watch?v=eojuJ_9for8&t=1555)]
Okay, so we've got to do something about this.

##### **Chrism** [[00:25:58](https://www.youtube.com/watch?v=eojuJ_9for8&t=1558)]
Yeah. Is this against master?

##### **Geohot** [[00:26:06](https://www.youtube.com/watch?v=eojuJ_9for8&t=1566)]
This is a Namespace runner on one of my PRs.

##### **Chrism** [[00:26:10](https://www.youtube.com/watch?v=eojuJ_9for8&t=1570)]
How rebased is it? The change to no longer run HCQ2 mock GPU with Python also sped up a lot of these, I noticed.

##### **Geohot** [[00:26:24](https://www.youtube.com/watch?v=eojuJ_9for8&t=1584)]
Oh, interesting.

##### **Chrism** [[00:26:33](https://www.youtube.com/watch?v=eojuJ_9for8&t=1593)]
It didn't speed it up a lot, but it did a bit, so it's not quite eight minutes anymore.

##### **Geohot** [[00:26:39](https://www.youtube.com/watch?v=eojuJ_9for8&t=1599)]
How fast is it?

##### **Chrism** [[00:26:40](https://www.youtube.com/watch?v=eojuJ_9for8&t=1600)]
I don't remember.

##### **Nimlgen** [[00:26:42](https://www.youtube.com/watch?v=eojuJ_9for8&t=1602)]
I don't know if you've noticed, but I also switched the runtime from Python to CPU.

##### **Chrism** [[00:26:48](https://www.youtube.com/watch?v=eojuJ_9for8&t=1608)]
Yeah, that's what I was saying. That made a difference.

##### **Nimlgen** [[00:26:52](https://www.youtube.com/watch?v=eojuJ_9for8&t=1612)]
Oh, okay.

##### **Geohot** [[00:26:55](https://www.youtube.com/watch?v=eojuJ_9for8&t=1615)]
You're using CPU. Are you using Clang or LLVM?

##### **Nimlgen** [[00:27:00](https://www.youtube.com/watch?v=eojuJ_9for8&t=1620)]
Clang.

##### **Geohot** [[00:27:01](https://www.youtube.com/watch?v=eojuJ_9for8&t=1621)]
LLVM is a lot faster. We should probably switch. I really want the HCQ backend to be LLVM in general, if LLVM is available. It should work in both, because the problem with Clang is that you're forking. Every time this thing has to fork and create a new process, you're spending basically 50 milliseconds on every Clang invocation. LLVM, especially if you disable LLVM optimizations, is all in-process, so it's only about five milliseconds. I think that will improve things a lot if we switch HCQ2 to LLVM.

##### **Chrism** [[00:27:40](https://www.youtube.com/watch?v=eojuJ_9for8&t=1660)]
Yeah, and probably in a lot of cases we don't care; we're just running stuff on CPU because we're running on CPU.

##### **Geohot** [[00:27:47](https://www.youtube.com/watch?v=eojuJ_9for8&t=1667)]
I think we should move the default HCQ to LLVM, but if LLVM's not available, it should work with Clang as well.

##### **Chrism** [[00:28:02](https://www.youtube.com/watch?v=eojuJ_9for8&t=1682)]
The other thing I looked at was cancelling this try_compile thing. Rather than doing it with a signal, you can do it with a thread.

##### **Geohot** [[00:28:14](https://www.youtube.com/watch?v=eojuJ_9for8&t=1694)]
A watchdog thread?

##### **Chrism** [[00:28:16](https://www.youtube.com/watch?v=eojuJ_9for8&t=1696)]
No, you actually run the compiler in the thread, and if it doesn't finish within a certain amount of time, the main thread says, 'Okay, forget about that.'

##### **Geohot** [[00:28:26](https://www.youtube.com/watch?v=eojuJ_9for8&t=1706)]
That sounds good.

##### **Chrism** [[00:28:27](https://www.youtube.com/watch?v=eojuJ_9for8&t=1707)]
The issue is when PARALLEL=0. It's kind of hard to deal with this. I don't think it's possible to kill the thread. There's no thread cancellation mechanism. For instance, if you were in LLVM and hanging forever, like a while-true loop, I think it's impossible to cancel that if it's running in some thread. It has to have a cancellation point, right?

##### **Geohot** [[00:29:12](https://www.youtube.com/watch?v=eojuJ_9for8&t=1752)]
Can I send a signal to it?

##### **Chrism** [[00:29:14](https://www.youtube.com/watch?v=eojuJ_9for8&t=1754)]
No, the signal won't be handled. It gets handled by the CPython signal handler, then stored: once we return from the C DLL, we'll handle it.

##### **Geohot** [[00:29:29](https://www.youtube.com/watch?v=eojuJ_9for8&t=1769)]
There's got to be some way to do this.

##### **Chrism** [[00:29:33](https://www.youtube.com/watch?v=eojuJ_9for8&t=1773)]
I'll look a little bit more.

##### **Geohot** [[00:29:34](https://www.youtube.com/watch?v=eojuJ_9for8&t=1774)]
There's got to be some way.

##### **Chrism** [[00:29:36](https://www.youtube.com/watch?v=eojuJ_9for8&t=1776)]
The other thing I was thinking was, instead of PARALLEL=0, actually use PARALLEL=1.

##### **Geohot** [[00:29:44](https://www.youtube.com/watch?v=eojuJ_9for8&t=1784)]
PARALLEL=1, and then it always runs in another process.

##### **Chrism** [[00:29:48](https://www.youtube.com/watch?v=eojuJ_9for8&t=1788)]
Yeah, there's only one worker process. The problem with that is...

##### **Geohot** [[00:29:58](https://www.youtube.com/watch?v=eojuJ_9for8&t=1798)]
What's the issue? Well, your PARALLEL=1 is actually two processes, right?

##### **Chrism** [[00:30:04](https://www.youtube.com/watch?v=eojuJ_9for8&t=1804)]
Yes.

##### **Geohot** [[00:30:05](https://www.youtube.com/watch?v=eojuJ_9for8&t=1805)]
What runs currently when you do PARALLEL is the entire codegen path goes into the parallel process. For viz, we have to support PARALLEL=0 and make sure all those rewrites stay in-process. The compiler can always go somewhere else.

##### **Chrism** [[00:30:25](https://www.youtube.com/watch?v=eojuJ_9for8&t=1825)]
Yeah, I see. I was really only looking at this in the BEAM code.

##### **Geohot** [[00:30:38](https://www.youtube.com/watch?v=eojuJ_9for8&t=1838)]
Okay, I can think about this. I'll take this over if you can make CI not take seven and a half minutes. And are there still failures? I want to get one of those signs: 'Six days since a spurious CI failure.'

##### **Chrism** [[00:30:58](https://www.youtube.com/watch?v=eojuJ_9for8&t=1858)]
Get the traffic light from...

##### **Geohot** [[00:31:00](https://www.youtube.com/watch?v=eojuJ_9for8&t=1860)]
That'll always be green. That's impossible, but we can definitely get a sign. You see them on all the worksites here. Unlike the ones in America that I think are fake, here they have one like, 'Four days since there was an accident.'

##### **Chrism** [[00:31:11](https://www.youtube.com/watch?v=eojuJ_9for8&t=1871)]
I'll look at these some more. I noticed some HCQ2 flakiness earlier. I haven't looked super carefully, but there's this frustrating macOS one that's been around forever, which is impacting interactivity.

##### **Geohot** [[00:31:26](https://www.youtube.com/watch?v=eojuJ_9for8&t=1886)]
Oh, that one. I haven't seen a lot of those, and that only seems to happen when the Mac is doing something.

##### **Chrism** [[00:31:33](https://www.youtube.com/watch?v=eojuJ_9for8&t=1893)]
Yeah, like animating the background or something.

##### **Geohot** [[00:31:36](https://www.youtube.com/watch?v=eojuJ_9for8&t=1896)]
It's got to animate the background. It's very important. Windows XP used to freeze the whole kernel when you would minimize a window. That window-minimize animation would freeze the whole kernel for about 200 milliseconds.

##### **Chrism** [[00:31:52](https://www.youtube.com/watch?v=eojuJ_9for8&t=1912)]
Anyway, that's it.

##### **Geohot** [[00:32:11](https://www.youtube.com/watch?v=eojuJ_9for8&t=1931)]
You cut out at the end there.

##### **Qazalin** [[00:32:14](https://www.youtube.com/watch?v=eojuJ_9for8&t=1934)]
So, I worked on...

##### **Geohot** [[00:32:17](https://www.youtube.com/watch?v=eojuJ_9for8&t=1937)]
Wait, you cut out at the end.

##### **Chrism** [[00:32:18](https://www.youtube.com/watch?v=eojuJ_9for8&t=1938)]
Oh, I cut out? What did you miss?

##### **Geohot** [[00:32:23](https://www.youtube.com/watch?v=eojuJ_9for8&t=1943)]
I heard 'that,' and then...

##### **Chrism** [[00:32:25](https://www.youtube.com/watch?v=eojuJ_9for8&t=1945)]
Oh, I was saying, 'That's it.'

##### **Wozeparrot** [[00:32:26](https://www.youtube.com/watch?v=eojuJ_9for8&t=1946)]
Okay. Moving on to Sam.

##### **Qazalin** [[00:32:33](https://www.youtube.com/watch?v=eojuJ_9for8&t=1953)]
I worked on this stuff. I also merged CALL in codegen last week. Right now, CALLs can render codegen, and BINARY can also render. I know HCQ has been using it. I'm going to use it for assembly, to lift assembly into UOps.

##### **Geohot** [[00:32:58](https://www.youtube.com/watch?v=eojuJ_9for8&t=1978)]
With the binaries, that's super nice. Names. It looks like real, high-quality C code now. Do you have compile_efficientnet?

##### **Qazalin** [[00:33:18](https://www.youtube.com/watch?v=eojuJ_9for8&t=1998)]
I do not. I didn't work on compile_efficientnet at all. Should I make that a priority?

##### **Geohot** [[00:33:27](https://www.youtube.com/watch?v=eojuJ_9for8&t=2007)]
Yeah, I think so. As opposed to what?

##### **Qazalin** [[00:33:30](https://www.youtube.com/watch?v=eojuJ_9for8&t=2010)]
Well, I worked on assembly stuff.

##### **Geohot** [[00:33:36](https://www.youtube.com/watch?v=eojuJ_9for8&t=2016)]
Is that a BINARY? Oh, that's so nice. Look at that. So nice.

##### **Qazalin** [[00:33:42](https://www.youtube.com/watch?v=eojuJ_9for8&t=2022)]
I'm looking at the UIR. UIR is so nice.

##### **Geohot** [[00:33:48](https://www.youtube.com/watch?v=eojuJ_9for8&t=2028)]
Can LLVM do this? Does this work?

##### **Qazalin** [[00:33:51](https://www.youtube.com/watch?v=eojuJ_9for8&t=2031)]
I don't know. Nimlgen merged it, I think. I didn't do it.

##### **Geohot** [[00:33:56](https://www.youtube.com/watch?v=eojuJ_9for8&t=2036)]
What's HCQ_RUNTIME_DEV? Is it going to work?

##### **Qazalin** [[00:34:04](https://www.youtube.com/watch?v=eojuJ_9for8&t=2044)]
Python and CPU work. I'm not sure about LLVM.

##### **Geohot** [[00:34:09](https://www.youtube.com/watch?v=eojuJ_9for8&t=2049)]
Python works. Let's see if that actually did...

##### **Nimlgen** [[00:34:12](https://www.youtube.com/watch?v=eojuJ_9for8&t=2052)]
To use LLVM, you should switch the device's CPU compiler to LLVM.

##### **Geohot** [[00:34:19](https://www.youtube.com/watch?v=eojuJ_9for8&t=2059)]
Oh, I can't do HCQ_RUNTIME_DEV=CPU:LLVM? It did something.

##### **Nimlgen** [[00:34:27](https://www.youtube.com/watch?v=eojuJ_9for8&t=2067)]
I'm not sure that works.

##### **Geohot** [[00:34:29](https://www.youtube.com/watch?v=eojuJ_9for8&t=2069)]
Is there a flag for this?

##### **Chrism** [[00:34:34](https://www.youtube.com/watch?v=eojuJ_9for8&t=2074)]
I don't know of a flag for this, but I think he was saying DEV=CPU:LLVM.

##### **Geohot** [[00:34:39](https://www.youtube.com/watch?v=eojuJ_9for8&t=2079)]
That's not what I want. What is the syntax?

##### **Chrism** [[00:34:48](https://www.youtube.com/watch?v=eojuJ_9for8&t=2088)]
DEV equals, in quotes, the device you actually want to run on, semicolon, CPU:LLVM.

##### **Geohot** [[00:34:52](https://www.youtube.com/watch?v=eojuJ_9for8&t=2092)]
The device I want to run on, semicolon, CPU:LLVM?

##### **Chrism** [[00:34:58](https://www.youtube.com/watch?v=eojuJ_9for8&t=2098)]
Yes.

##### **Geohot** [[00:35:00](https://www.youtube.com/watch?v=eojuJ_9for8&t=2100)]
All right, that's probably right. Failed to render an INDEX...

##### **Chrism** [[00:35:06](https://www.youtube.com/watch?v=eojuJ_9for8&t=2106)]
Oh, that sets the default compiler, I see.

##### **Geohot** [[00:35:09](https://www.youtube.com/watch?v=eojuJ_9for8&t=2109)]
Yeah, it's getting 'failed to render' on the device INDEX. The syntax I want to work, if possible...

##### **Nimlgen** [[00:35:23](https://www.youtube.com/watch?v=eojuJ_9for8&t=2123)]
Or HCQ_RUNTIME_DEV should be in DEV somewhere.

##### **Geohot** [[00:35:28](https://www.youtube.com/watch?v=eojuJ_9for8&t=2128)]
I don't know if HCQ_RUNTIME_DEV should be in DEV.

##### **Chrism** [[00:35:33](https://www.youtube.com/watch?v=eojuJ_9for8&t=2133)]
It depends on whether it's something people would frequently set.

##### **Geohot** [[00:35:37](https://www.youtube.com/watch?v=eojuJ_9for8&t=2137)]
No, this should not be something people frequently set. The only reason I want to switch it to CPU LLVM is that I think we're spending a lot of time launching processes to compile ten-line Clang programs. We can just use LLVM and it'll be way faster. Sorry, go ahead.

##### **Qazalin** [[00:36:00](https://www.youtube.com/watch?v=eojuJ_9for8&t=2160)]
I worked on UIR. Now, if you click on the UIR, you can see the linked UOp light up. UIR is pretty nice. LLMs are very good at using it, right? I tried with GLM today; it just read the UIR. The viz CLI is completely switched to UIR. I used to have a hand-rolled UOp printer, so I deleted all that.

##### **Qazalin** [[00:36:36](https://www.youtube.com/watch?v=eojuJ_9for8&t=2196)]
I worked on SQTT for about a day. This is the new shot of SQTT.

##### **Geohot** [[00:36:52](https://www.youtube.com/watch?v=eojuJ_9for8&t=2212)]
So this is zoomed in?

##### **Qazalin** [[00:36:54](https://www.youtube.com/watch?v=eojuJ_9for8&t=2214)]
Yeah, that's a wave. You can see the barriers.

##### **Geohot** [[00:36:57](https://www.youtube.com/watch?v=eojuJ_9for8&t=2217)]
We're good, right, until we get to that ridiculous prologue.

##### **Qazalin** [[00:37:01](https://www.youtube.com/watch?v=eojuJ_9for8&t=2221)]
Yeah, the ridiculous prologue. I also added wave ends. This is eight waves in one picture.

##### **Geohot** [[00:37:14](https://www.youtube.com/watch?v=eojuJ_9for8&t=2234)]
What do you mean, wave end?

##### **Qazalin** [[00:37:16](https://www.youtube.com/watch?v=eojuJ_9for8&t=2236)]
If you zoom in, you see a little black line? Those lines are wave ends, the wave termination.

##### **Geohot** [[00:37:27](https://www.youtube.com/watch?v=eojuJ_9for8&t=2247)]
Wait, that's doing wave termination stuff?

##### **Qazalin** [[00:37:30](https://www.youtube.com/watch?v=eojuJ_9for8&t=2250)]
Yes. It ended up being that the idle time is actually in the wave termination and the wave start.

##### **Geohot** [[00:37:38](https://www.youtube.com/watch?v=eojuJ_9for8&t=2258)]
Why does it not just loop?

##### **Qazalin** [[00:37:40](https://www.youtube.com/watch?v=eojuJ_9for8&t=2260)]
Because it needs to store back.

##### **Geohot** [[00:37:43](https://www.youtube.com/watch?v=eojuJ_9for8&t=2263)]
What? Why does it actually terminate the wave? You see what I'm saying?

##### **Qazalin** [[00:37:48](https://www.youtube.com/watch?v=eojuJ_9for8&t=2268)]
Like launching a persistent kernel and just keeping it?

##### **Geohot** [[00:37:51](https://www.youtube.com/watch?v=eojuJ_9for8&t=2271)]
It's not hyper-persistent. Instead of using the GPU launcher to launch the eight waves, why don't I just put a for loop?

##### **Qazalin** [[00:37:58](https://www.youtube.com/watch?v=eojuJ_9for8&t=2278)]
Yeah, I was surprised. Those blank lines aren't in the middle of the wave; they're at the end.

##### **Geohot** [[00:38:08](https://www.youtube.com/watch?v=eojuJ_9for8&t=2288)]
Once we have anything that can work on assembly, turning that into a for loop is going to help.

##### **Qazalin** [[00:38:13](https://www.youtube.com/watch?v=eojuJ_9for8&t=2293)]
GPT did an analysis, and 30% of idle time is in the wave ends.

##### **Geohot** [[00:38:23](https://www.youtube.com/watch?v=eojuJ_9for8&t=2303)]
That's still not going to fix the stores and the launches.

##### **Qazalin** [[00:38:27](https://www.youtube.com/watch?v=eojuJ_9for8&t=2307)]
That's the point: the idles are happening because of the stores, because the wave has nothing else to hide. Whenever you see green...

##### **Geohot** [[00:38:37](https://www.youtube.com/watch?v=eojuJ_9for8&t=2317)]
You just mean this tiny thing here, right? During those stores themselves, you can't be using the MFMA.

##### **Qazalin** [[00:38:43](https://www.youtube.com/watch?v=eojuJ_9for8&t=2323)]
The next wave can, but you can't really launch the next wave without ending the previous one. That's why we end up with a ridiculous MFU.

##### **Geohot** [[00:38:58](https://www.youtube.com/watch?v=eojuJ_9for8&t=2338)]
You did a good job. Work more on assembly.

##### **Qazalin** [[00:39:08](https://www.youtube.com/watch?v=eojuJ_9for8&t=2348)]
I'm hoping by the end of this week I can have some syntax for expressing assembly kernels without register allocation. Once we have that, express the control flow using BACKEDGE and loops and express the registers with ALLOC. Then I should be able to actually write the kernel.

##### **Geohot** [[00:39:46](https://www.youtube.com/watch?v=eojuJ_9for8&t=2386)]
Is this ready to merge?

##### **B1tg** [[00:39:48](https://www.youtube.com/watch?v=eojuJ_9for8&t=2388)]
Yes.

##### **Geohot** [[00:39:50](https://www.youtube.com/watch?v=eojuJ_9for8&t=2390)]
Let's see. I merged the Tensor.empty thing yesterday.

##### **B1tg** [[00:40:04](https://www.youtube.com/watch?v=eojuJ_9for8&t=2404)]
The load thing was fixed.

##### **Geohot** [[00:40:10](https://www.youtube.com/watch?v=eojuJ_9for8&t=2410)]
That's still going to CPU, but that's not going to be a blocker. This is still calling shard, which is totally fine; that's just going to have a shard of one. Got it. Pass in an empty shard map otherwise. Cool, that's fixed. If GPT says it's good, I think we're good. So the all-reduces are all implicit now?

##### **B1tg** [[00:40:45](https://www.youtube.com/watch?v=eojuJ_9for8&t=2445)]
Yeah, using the tinygrad native reduce.

##### **Geohot** [[00:40:58](https://www.youtube.com/watch?v=eojuJ_9for8&t=2458)]
I'm reviewing this. We're finally adding LLM shards back, so we can delete the old LLaMA 3 thing in extra. I think it might be time for that to be deleted. We can move everything to this. I'll merge this if GPT says it's good. Do you want to see how the time compares to the LLaMA 3 one for that BEAM test in CI?

##### **B1tg** [[00:41:32](https://www.youtube.com/watch?v=eojuJ_9for8&t=2492)]
You mean compare the speed?

##### **Geohot** [[00:41:39](https://www.youtube.com/watch?v=eojuJ_9for8&t=2499)]
Some of these LLM benchmarks, this one, I think, and maybe this one?

##### **Chrism** [[00:41:50](https://www.youtube.com/watch?v=eojuJ_9for8&t=2510)]
The first one.

##### **Geohot** [[00:41:51](https://www.youtube.com/watch?v=eojuJ_9for8&t=2511)]
It should be the first one. I think this might be using the old LLaMA 3. It'd be great to move it to the new sharded one.

##### **B1tg** [[00:42:01](https://www.youtube.com/watch?v=eojuJ_9for8&t=2521)]
I think we should add the prefill speed to this.

##### **Geohot** [[00:42:07](https://www.youtube.com/watch?v=eojuJ_9for8&t=2527)]
Previous speed?

##### **B1tg** [[00:42:09](https://www.youtube.com/watch?v=eojuJ_9for8&t=2529)]
Prefill.

##### **Qazalin** [[00:42:11](https://www.youtube.com/watch?v=eojuJ_9for8&t=2531)]
Prefill.

##### **Geohot** [[00:42:12](https://www.youtube.com/watch?v=eojuJ_9for8&t=2532)]
Oh, prefill speed. Yes, definitely. We definitely need to add prefill speed. We should have some syntax for benchmark where we can specify prefill and then rollout. Right now we do BENCHMARK=5. Maybe we should put a prefill length in front of that. It'll do a prefill of that length. That seems to be the way a lot of these things are written. I really liked the way RKNN did that.

##### **Geohot** [[00:42:52](https://www.youtube.com/watch?v=eojuJ_9for8&t=2572)]
They basically have seq_len and new_tokens, so that's prefill and decode. It should be backwards compatible: I could still do BENCHMARK=5 and it'll just go.

##### **B1tg** [[00:43:11](https://www.youtube.com/watch?v=eojuJ_9for8&t=2591)]
Do we want to put the benchmark in the CLI or in extra?

##### **Geohot** [[00:43:17](https://www.youtube.com/watch?v=eojuJ_9for8&t=2597)]
In the CLI. It stays backwards compatible, so BENCHMARK=5 is five decode tokens. There's an implicit zero, right? Same as BENCHMARK=0,5. You can also benchmark...

##### **Chrism** [[00:43:53](https://www.youtube.com/watch?v=eojuJ_9for8&t=2633)]
There's some weird stuff where, if you don't have Jinja installed, you get better performance. Maybe I changed this, but it certainly used to be true. When you benchmarked, it was deciding whether to put in the system prompt.

##### **Geohot** [[00:44:12](https://www.youtube.com/watch?v=eojuJ_9for8&t=2652)]
Oh yeah, benchmark should disable that.

##### **Chrism** [[00:44:18](https://www.youtube.com/watch?v=eojuJ_9for8&t=2658)]
Maybe I changed that. There's a flag in there now to always disable it. I think it does.

##### **Geohot** [[00:44:29](https://www.youtube.com/watch?v=eojuJ_9for8&t=2669)]
Yeah, that template handler. I think this is good. Thanks for cleaning it up.

##### **B1tg** [[00:44:43](https://www.youtube.com/watch?v=eojuJ_9for8&t=2683)]
This week I'll do some speedups. First, prefill speed is very slow now, only 500 tokens per second. I think it can be 800 or 1,000.

##### **Geohot** [[00:45:09](https://www.youtube.com/watch?v=eojuJ_9for8&t=2709)]
What I found with trying to make prefill faster is that a lot of it has to do with your chunk size. We can already make it faster if we increase the chunk size. You just run into issues sometimes. Maybe those bugs are fixed now; they might have just been bugs. It'd be great to get prefill into the benchmark and onto the board. What gets measured gets managed.

##### **Geohot** [[00:45:41](https://www.youtube.com/watch?v=eojuJ_9for8&t=2741)]
Cool. Anything else?

##### **Wozeparrot** [[00:45:45](https://www.youtube.com/watch?v=eojuJ_9for8&t=2745)]
Anything else? Okay. Is Comma happy?

##### **Chrism** [[00:45:53](https://www.youtube.com/watch?v=eojuJ_9for8&t=2753)]
I believe so. The thing they were complaining about was what happens when you unplug the USB GPU. There was some excitement about maybe switching to IR3, especially considering it's faster, but I don't think they're spending much time on the Qualcomm stuff.

##### **Geohot** [[00:46:21](https://www.youtube.com/watch?v=eojuJ_9for8&t=2781)]
I locked the bounty for a Qualcomm compiler, or rather a Qualcomm emulator. It's a little bit AI slop, but I would say it's not more AI slop than the AMD emulator. It uses NumPy to emulate. It's not that fast, but it's fast enough to run a lot of the tests. It seems to support all the instructions.

##### **Qazalin** [[00:47:04](https://www.youtube.com/watch?v=eojuJ_9for8&t=2824)]
Wait, why NumPy?

##### **Geohot** [[00:47:06](https://www.youtube.com/watch?v=eojuJ_9for8&t=2826)]
What else do you want to use? tinygrad?

##### **Qazalin** [[00:47:08](https://www.youtube.com/watch?v=eojuJ_9for8&t=2828)]
Yeah.

##### **Geohot** [[00:47:09](https://www.youtube.com/watch?v=eojuJ_9for8&t=2829)]
That'd be nice. I don't know.

##### **Qazalin** [[00:47:18](https://www.youtube.com/watch?v=eojuJ_9for8&t=2838)]
The AMD one does.

##### **Geohot** [[00:47:20](https://www.youtube.com/watch?v=eojuJ_9for8&t=2840)]
The AMD one does, yeah. It's easy enough to convert. I don't know, I'm okay with NumPy. I'm not going to block the bounty on that as long as it's fast enough to actually run things. It looks like a lot of tests are passing. With a bunch of cleanups, we can get that merged. The important thing I wanted to test is that it has to be fast enough to run the openpilot model. If it's 15 milliseconds on the hardware, I'm fine with it being ten seconds on the emulator. But it should be ten seconds, not ten minutes.

##### **Geohot** [[00:48:01](https://www.youtube.com/watch?v=eojuJ_9for8&t=2881)]
How cool is that? We can run the openpilot model through the whole thing with IR3. We can actually compile it too. We already do compile it, though...

##### **Chrism** [[00:48:16](https://www.youtube.com/watch?v=eojuJ_9for8&t=2896)]
No, we don't, because of the ONNX bullshit. We actually don't compile it.

##### **Geohot** [[00:48:25](https://www.youtube.com/watch?v=eojuJ_9for8&t=2905)]
You mean the null ONNX thing?

##### **Chrism** [[00:48:27](https://www.youtube.com/watch?v=eojuJ_9for8&t=2907)]
Yeah.

##### **Geohot** [[00:48:29](https://www.youtube.com/watch?v=eojuJ_9for8&t=2909)]
That'll be great. I'm excited for that.

##### **Geohot** [[00:48:48](https://www.youtube.com/watch?v=eojuJ_9for8&t=2928)]
What's RDNA?

##### **Wozeparrot** [[00:48:51](https://www.youtube.com/watch?v=eojuJ_9for8&t=2931)]
I'm trying to remember. That was from last week. It's more assembly stuff, the RDNA assembly bounty. I think it's legacy stuff that's been carried forward.

##### **Geohot** [[00:49:07](https://www.youtube.com/watch?v=eojuJ_9for8&t=2947)]
The assembly backend? Oh yeah, the assembly backend. Raine's not here. There are PRs for that getting merged. There's a hack in the x86 backend which needs to be fixed, not hacked around more. x86 used this hack to do callee-saved registers. I shouldn't have let TThompson get away with that. I did, and now it causes trouble.

##### **Geohot** [[00:49:50](https://www.youtube.com/watch?v=eojuJ_9for8&t=2990)]
We're going to have a twelve-GPU 9700 computer pretty soon. This is part of the new product launch coming next week. We have to finish the software, but it should be capable of running GLM Flash and DeepSeek Flash across twelve of those GPUs.

##### **Chrism** [[00:50:25](https://www.youtube.com/watch?v=eojuJ_9for8&t=3025)]
Where are the twelve going to go? Where's the machine going to go?

##### **Geohot** [[00:50:29](https://www.youtube.com/watch?v=eojuJ_9for8&t=3029)]
In our office? We'll put it in our office. It should be quiet. It can sit next to my existing tinybox.

##### **Chrism** [[00:50:41](https://www.youtube.com/watch?v=eojuJ_9for8&t=3041)]
Where's it going to go? It's tall and scary.

##### **Geohot** [[00:50:48](https://www.youtube.com/watch?v=eojuJ_9for8&t=3048)]
I don't know where we have space right now.

##### **Chrism** [[00:50:54](https://www.youtube.com/watch?v=eojuJ_9for8&t=3054)]
They're actually putting a real wall up in that room.

##### **Geohot** [[00:50:57](https://www.youtube.com/watch?v=eojuJ_9for8&t=3057)]
Oh, they're putting a real wall up?

##### **Chrism** [[00:50:59](https://www.youtube.com/watch?v=eojuJ_9for8&t=3059)]
Yeah. The real wall project has been on the table for a long time. It didn't happen last weekend, but now it's happening.

##### **Geohot** [[00:51:09](https://www.youtube.com/watch?v=eojuJ_9for8&t=3069)]
Oh, Yassine was using the customer tinybox? We're shipping those out. If you're one of the three tinybox orders, I'm sorry they've taken so long. We're on top of it. The really annoying thing is that now there's KYC for GPUs. If you're trying to buy glassware to make meth, they've got to investigate. You're trying to buy GPUs to make LLMs, and they've got to investigate. They're a controlled substance. It's really not us.

##### **Geohot** [[00:51:45](https://www.youtube.com/watch?v=eojuJ_9for8&t=3105)]
I think we have your GPUs now, and the machines are getting built and tested. We've got a whole bunch of orders for the tinybox pro RTXs. By the way, I think we have to raise the price again. I'm really not increasing our margins. If anything, our margins are worse. They keep raising the price of these RTX 6000 cards. We've gotten a whole bunch of orders for the $200,000 machine. If you're one of those orders, your order will ship soon.

##### **Chrism** [[00:52:24](https://www.youtube.com/watch?v=eojuJ_9for8&t=3144)]
They are going out.

##### **Wozeparrot** [[00:52:26](https://www.youtube.com/watch?v=eojuJ_9for8&t=3146)]
Great. I'm going through the backlog of provisioning them.

##### **Geohot** [[00:52:32](https://www.youtube.com/watch?v=eojuJ_9for8&t=3152)]
We've put a lot of effort into the thermals for those things too, so that should be good.

##### **Chrism** [[00:52:40](https://www.youtube.com/watch?v=eojuJ_9for8&t=3160)]
Yassine was...

##### **Geohot** [[00:52:41](https://www.youtube.com/watch?v=eojuJ_9for8&t=3161)]
What's up?

##### **Chrism** [[00:52:43](https://www.youtube.com/watch?v=eojuJ_9for8&t=3163)]
Yassine was making the PDUs very unhappy.

##### **Geohot** [[00:52:48](https://www.youtube.com/watch?v=eojuJ_9for8&t=3168)]
Yassine was breaking our PDUs?

##### **Chrism** [[00:52:50](https://www.youtube.com/watch?v=eojuJ_9for8&t=3170)]
He didn't break them, but they were flashing.

##### **Geohot** [[00:52:58](https://www.youtube.com/watch?v=eojuJ_9for8&t=3178)]
One of the groups was overcurrent.

##### **Geohot** [[00:53:03](https://www.youtube.com/watch?v=eojuJ_9for8&t=3183)]
[Unclear remark about Anthropic.]

##### **Chrism** [[00:53:08](https://www.youtube.com/watch?v=eojuJ_9for8&t=3188)]
Wait, really?

##### **Geohot** [[00:53:10](https://www.youtube.com/watch?v=eojuJ_9for8&t=3190)]
Yeah. Apparently it's a pretty good deal. I almost signed up for Claude, but I really don't want to use Claude Code. I don't want to install that spyware on my computer. If there's a good workaround for...

##### **Geohot** [[00:53:32](https://www.youtube.com/watch?v=eojuJ_9for8&t=3212)]
[Unclear exchange.] I don't know if that's more expensive or less expensive.

##### **Geohot** [[00:53:45](https://www.youtube.com/watch?v=eojuJ_9for8&t=3225)]
I got a new price for our RTX 6000s, and they're very expensive, and they need compliance. Maybe we don't have to raise prices, because the price doesn't seem like it went up. That's a lot of compliance.

##### **Wozeparrot** [[00:54:15](https://www.youtube.com/watch?v=eojuJ_9for8&t=3255)]
Any update on NPUs?

##### **Geohot** [[00:54:20](https://www.youtube.com/watch?v=eojuJ_9for8&t=3260)]
What NPUs? The Rockchip ones?

##### **Wozeparrot** [[00:54:24](https://www.youtube.com/watch?v=eojuJ_9for8&t=3264)]
Rockchip.

##### **Geohot** [[00:54:26](https://www.youtube.com/watch?v=eojuJ_9for8&t=3266)]
We met with the guy working on the Rockchip port last week. It didn't look performant. When a lot of people focus on ports, they're thinking about making sure every op works, and this doesn't necessarily make for a very useful port. What's generally more useful is to focus on Qwen3.8 and make it fast, or Qwen3.6. You should be able to run an LLM at the memory-bandwidth limit. If you can't, what are you not doing right? Prefill and decode in LLMs are better benchmarks than total completeness. Someone else did an NPU port, and it didn't look performant either.

##### **Geohot** [[00:55:20](https://www.youtube.com/watch?v=eojuJ_9for8&t=3320)]
If someone out there listens to this and works at a company with an NPU: stop shipping your crappy vendor software, ship tinygrad. We're open to contracts to make it fast for you. The Rockchip guy derived the way to make it fast. Rockchip has a 32-by-32 accumulate-in-place, which looks kind of like Apple's AMX. tinygrad has complete support for this; you just need to write it. I'm very happy that we can now write kernels that are fast for things, and that this is totally separate from the whole frontend/lowering thing.

##### **Geohot** [[00:56:10](https://www.youtube.com/watch?v=eojuJ_9for8&t=3370)]
I think that's all for this meeting.

##### **Wozeparrot** [[00:56:13](https://www.youtube.com/watch?v=eojuJ_9for8&t=3373)]
Thank you, everyone, for joining.

##### **Geohot** [[00:56:16](https://www.youtube.com/watch?v=eojuJ_9for8&t=3376)]
Thanks, everyone.
