# 2026-04-07 Meeting

### Meeting Agenda

**Time:** new meeting #12, 4/6 9pm Monday San Diego time
- company update, Exa Box pre-order, TinyRed eGPU
- FP8 MLPerf, `function`, profiling loop
- agentic loop, x86 review, assembly and UOp kernels
- `DEV` interfaces, semicolon syntax, remote
- USB GPU custom firmware, Chestnut, USB4
- `ctypes.Structure`, read-only memory views, Tensor cleanups
- remote training, `ext4`, NVMe, Exa Box single-GPU flow
- DSP support, other issues, bounties, any Comma complaints


### Audio

[Youtube Link](https://www.youtube.com/watch?v=ksHFf4DqGcs)

### Highlights

### Transcript
##### **Geohot** [[00:00:00](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=0)]
All right, let's get started.

##### **Geohot** [[00:00:03](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3)]
So we don't have a list today. Chenyu is jet lagged, so I will try my best without the list. I'll start with company update. We launched the Exa Box pre-order. We haven't gotten an Exa Box pre-order yet, obviously. But I got a few DMs from interesting people who might want to buy one. So, you know, I'm not going to take phone calls until someone actually sends the money. You got to do that. Otherwise, other people will waste your time. And always remember that it is cheaper for other people to waste your time than for you to try to waste theirs, because we are a tiny corp.

##### **Geohot** [[00:00:46](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=46)]
Yeah, so that's the main company update thing.

##### **Geohot** [[00:00:51](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=51)]
I think the other company update is that we're getting ready to ship the TinyRed eGPU. The eGPU got tons of traction this week. People are really excited about the Mac thing. I saw at least two people actually replicate it. They did complain that it was slow, though, and that's something we should talk about. We should talk about how to make it not slow. So I'm just going to look at people's sprint reports, and we'll just go down the list. All right, so let's start with Qazalin.

##### **Geohot** [[00:01:26](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=86)]
Your sprint stuff: the FP8 matmul and the auto research.

##### **Qazalin** [[00:01:35](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=95)]
Yeah, so I'll start with FP8. I'm not sure if Wozeparrot wants to split the work.

##### **Geohot** [[00:01:46](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=106)]
Yeah, we can.

##### **Geohot** [[00:01:50](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=110)]
The FP8 matmul is merged.

##### **Qazalin** [[00:01:52](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=112)]
Oh, yeah. The rest of the latency is around non-FP8 stuff.

##### **Geohot** [[00:02:07](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=127)]
Okay. What can we do about that stuff?

##### **Qazalin** [[00:02:13](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=133)]
The FP8 quantize stuff?

##### **Geohot** [[00:02:16](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=136)]
Yeah, I mean, what is that doing? Why is that not built into the matmul? I guess it can't be built into the matmul, but if that's what's really slow...

##### **Wozeparrot** [[00:02:29](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=149)]
I think it's a good idea to start with the FP8 matmul, so I'm fixing some of that. One of the main things is the current FP8 implementation that I have that trains to convergence: there's FP32 master weights, then we keep the bfloat16 weights, and then we quantize on the forward pass to FP8. Something I'm doing now is moving that weight storage to be FP8 directly, and you only quantize in the optimizer.

##### **Geohot** [[00:02:54](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=174)]
Yeah, okay. That sounds a lot better. I mean... Yeah. We should also be able to just like if the gradients are in FP8, we should also be able to do this all on the CPU. Yeah.

##### **Wozeparrot** [[00:03:06](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=186)]
For a 405B, we can do that.

##### **Geohot** [[00:03:09](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=189)]
Yeah, I guess. Actually, none of it has to be on the CPU except the master weights. You can keep the master weights on the CPU.

##### **Wozeparrot** [[00:03:14](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=194)]
Okay.

##### **Geohot** [[00:03:14](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=194)]
But yeah, my point is that this should be entirely done. Right. So the only thing if you imagine the 405B communications pass, right, because communications are slower than everything else, you would imagine the communication is just the FP8 gradients and then getting back FP8 weights.

##### **Geohot** [[00:03:32](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=212)]
Is that possible? Gradients are non-FP8?

##### **Geohot** [[00:03:42](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=222)]
Why not?

##### **Wozeparrot** [[00:03:43](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=223)]
For bfloat16.

##### **Geohot** [[00:03:45](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=225)]
Wait, but so we're only using the FP8 matmul on the forward pass?

##### **Wozeparrot** [[00:03:48](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=228)]
No. So the gradient gets requantized to FP8 for the matmul. For everything else, it needs to be bfloat16.

##### **Geohot** [[00:03:58](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=238)]
Okay, what is what is AMD stock implementation doing?

##### **Wozeparrot** [[00:04:01](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=241)]
This is AMD's implementation. I copied AMD's implementation as closely as possible.

##### **Geohot** [[00:04:07](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=247)]
Okay. And then we have to look: I don't want to submit MLPerf with a six-hour time. I want to submit to MLPerf with, at worst, a three-hour time. We can't really be that much slower than AMD's stock thing. Okay, so they're doing the same stuff.

##### **Wozeparrot** [[00:04:26](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=266)]
Yes. Bfloat16 gradients, FP8 backward GEMM, FP8 forward GEMM.

##### **Geohot** [[00:04:35](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=275)]
Okay, so the sorry, go ahead.

##### **Wozeparrot** [[00:04:40](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=280)]
Some other like minor things is when you do max for the FP8 quantize that max is local per device and is not all reduced. So I'm testing that now too.

##### **Geohot** [[00:05:00](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=300)]
Okay, cool.

##### **Geohot** [[00:05:02](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=302)]
Yeah, and I want to make sure that we're always using `function`. What's the startup time of the trainer? I want the startup time to be under 10 seconds.

##### **Geohot** [[00:05:19](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=319)]
I think we already spent 10 seconds initializing GPUs.

##### **Geohot** [[00:05:26](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=326)]
No, we don't know if the GPUs are already initialized. We don't. Sure, if we have to download the firmware, that's fine.

##### **Geohot** [[00:05:42](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=342)]
Still, I want this to be I want this to boot up in about 10 seconds. I want to be able to do like a whole profiling run. Of a couple steps in like a minute.

##### **Wozeparrot** [[00:05:51](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=351)]
It's pretty fast. It's like 30 seconds right now. From running the command to the first kernel being run.

##### **Geohot** [[00:05:58](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=358)]
Hmm, that's without function.

##### **Wozeparrot** [[00:06:01](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=361)]
This is with `function`. I have a PR for `function`.

##### **Geohot** [[00:06:05](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=365)]
Okay, if you have `function` and you've confirmed that all the saving stuff actually works, because I don't really have tests for that.

##### **Wozeparrot** [[00:06:11](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=371)]
Uh, it seems to work like the memory goes up. And the time goes down. Yeah.

##### **Geohot** [[00:06:17](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=377)]
Yeah, but does that? Yeah. You should just check the total number of ops. Let's see if it matches.

##### **Wozeparrot** [[00:06:22](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=382)]
Yeah.

##### **Geohot** [[00:06:23](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=383)]
Like, we're saving everything. Yeah. I also want to add some tests for that. I didn't really test it. I mean, I think I tested the basic functionality, but I didn't test it in anything fancy. I tested the basic functionality that it will save things if you put them there, but I didn't test the more complicated cases.

##### **Geohot** [[00:06:41](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=401)]
Okay, that seems like progress is being made here. Um, is there any other kernels that we need?

##### **Nimlgen** [[00:06:46](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=406)]
Yeah.

##### **Wozeparrot** [[00:06:54](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=414)]
Uh, maybe we can look into a fused RMS norm dropout residual kernel. It doesn't seem like most people are training with this. How much time are we wasting there?

##### **Geohot** [[00:07:07](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=427)]
All right. So I'm looking at the, uh, I'm looking at that breakdown, uh, cause all the breakdown you put in, uh, uh, is that still correct?

##### **Nimlgen** [[00:07:16](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=436)]
Yeah.

##### **Geohot** [[00:07:19](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=439)]
That was with function.

##### **Qazalin** [[00:07:20](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=440)]
I didn't comment on it.

##### **Geohot** [[00:07:24](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=444)]
Yeah. I mean, we should really be testing. If you compare the two, I don't know if your first one had `function` or no `function`, but you can see that one of them is doing 2240 matmuls and the other one's doing 3136 matmuls.

##### **Nimlgen** [[00:07:51](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=471)]
So that's going to be a little bit more complicated than the first one was.

##### **Geohot** [[00:07:51](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=471)]
Uh, can we also fix, why is the estimated training time wrong?

##### **Wozeparrot** [[00:07:55](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=475)]
Uh, that goes off the configured max steps. I'll put in like an estimated number of steps and that should fix it.

##### **Geohot** [[00:08:01](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=481)]
Okay, great. Wait, but how come it got slower between the two branches? I see two screenshots here. One says 14,000 hours and one says 20,000 hours.

##### **Geohot** [[00:08:30](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=510)]
Um, okay.

##### **Geohot** [[00:08:31](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=511)]
So what's our total time to, to, to run that profile or what's our total wall time to do that?

##### **Geohot** [[00:08:42](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=522)]
I think it takes like four or five minutes to do a benchmark.

##### **Geohot** [[00:08:47](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=527)]
Yeah. What can we do to improve that? I'm seeing this second step is taking 180 seconds.

##### **Geohot** [[00:08:54](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=534)]
Why is it taking 180 seconds? I don't know if you run with beam, but I always run my profile with beam.

##### **Geohot** [[00:09:05](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=545)]
I do not. Wait, you have to run the profile with beam. The timing is kind of useless if it wasn't running with beam.

##### **Geohot** [[00:09:27](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=567)]
Okay.

##### **Geohot** [[00:09:29](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=569)]
The main thing I want you to work on is getting that profile under a minute. I want to be able to benchmark in under a minute, and I want to be able to see that in VIZ. Most of your work should just continue to match AMD perfectly. Every place we match AMD is good. We know that AMD is fast enough. If we can get two hours, if we can match AMD, I'm super happy. We don't have to do better than them.

##### **Wozeparrot** [[00:09:57](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=597)]
We're three X off right now. Less than three X off.

##### **Geohot** [[00:10:01](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=601)]
Uh, do we know? And then the one that you have training now is you're confident that it's a hundred percent correct for MLPerf?

##### **Wozeparrot** [[00:10:09](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=609)]
Uh, yes, it should be correct for MLPerf if we just use `run_and_time`.

##### **Geohot** [[00:10:15](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=615)]
Okay. We just use `run_and_time`. Okay.

##### **Geohot** [[00:10:17](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=617)]
Uh, great. So yeah, we just got to get this to go faster. Use `function`. We got to get startup times down. Qazalin, Wozeparrot, these are your top priorities for the next week. Nothing else is more important than getting this to be fast. We're closing in on the MLPerf deadline. I want to get a really good time on this, and I want to make sure that we have really good tooling around it, because the speed at which we can iterate on a benchmark profile is going to determine our final speed. So we need that to be under a minute. I'm not going to sit there and wait longer than a minute for something to profile, because that's the time that you context-switch to something else. The dream would be if that was like 20 seconds and then it would be super easy to reprofile, make a change, reprofile, make a change, reprofile. That's the loop we have to get people in.

##### **Wozeparrot** [[00:11:14](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=674)]
Well, then if it's that fast, you can get agents to do it too.

##### **Geohot** [[00:11:17](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=677)]
That too. Yeah, getting agents to do this would be amazing. Forget making matmuls fast on RDNA, whatever. I care about getting this loop to be fast.

##### **Geohot** [[00:11:28](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=688)]
Let's get this loop to be agentic.

##### **Geohot** [[00:11:34](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=694)]
Yeah.

##### **Qazalin** [[00:11:36](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=696)]
For the matmul, I can share my experience a little bit. It's basically that they're not good at writing assembly.

##### **Geohot** [[00:11:47](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=707)]
They're not good at that. I think this is kind of hopeless. I think what I'm going to do is review that Thompson resubmitted the x86 PR. I think the x86 PR has a pretty good jumping-off point for a lot of this. This is what I said to Jay Suarez too: we want tinygrad to be able to handle the entire spectrum from torch-like operations all the way down to assembly instructions, and you should be able to code at any point on that spectrum. Obviously, by definition, the assembly instruction contains all the speed. If you're coding assembly, there is some configuration of assembly instructions that will give you the speed. Then as you move back up toward torch, you're losing speed at different points. Effectively, the way to think about this is that you're constraining the search space. You have this whole search space of all possible programs that run on the GPU, and then there's all the programs that tinygrad can generate from the beginning. We want to figure out where in the translation the speed is being lost.

I think agents will get a lot better once the assembler handles some low-level monotony stuff automatically, like register allocation. By the way, there are even lower layers than RDNA. If you think of PTX to SASS, RDNA is somewhere in between those two. PTX doesn't do register allocation, but SASS is doing things like explicitly managing pipeline stalls, which are automatic on RDNA GPUs. That's really interesting. There's a whole spectrum here, and we can think about at what level the agents will best be able to code.

But yeah, for now let's focus on the agentic loop. That actually matters to us for the LLaMA app. It'd be amazing if we can get this to be agentic and fast. I think we can beat AMD. And then for some of these other kernels, like these `R32_32_4`-type kernels, I wonder if we can make them a lot faster by coding them in something like the way I coded flash attention, by coding some UOp thing. We don't have to go all the way down to a custom kernel in HIP or anything like that. We can just do these things in the UOp way and it would be fast.

##### **Geohot** [[00:14:27](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=867)]
Great. Any other thoughts on this kind of stuff?

##### **Geohot** [[00:14:34](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=874)]
Oh, by the way, was it real that the agents could break the GPUs?

##### **Qazalin** [[00:14:40](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=880)]
Yes, it did take down tiny R11. I have the kernel for it, but it couldn't reproduce. What do you mean by took down? Oh, it's just like machine stopped, and I had to.

##### **Geohot** [[00:15:00](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=900)]
Machine stopped? Yeah, it's just a machine. A kernel panic?

##### **Qazalin** [[00:15:09](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=909)]
I mean, yeah, `TinyR11` went down.

##### **Geohot** [[00:15:12](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=912)]
Well, OK. So you're aware that right now the AMD GPU is still inserted, right?

##### **Qazalin** [[00:15:17](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=917)]
It's not inserted.

##### **Geohot** [[00:15:19](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=919)]
I just ran `rocm-smi` on the machine. It's inserted.

##### **Qazalin** [[00:15:24](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=924)]
On R11 right now? Because I reset it.

##### **Geohot** [[00:15:26](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=926)]
I just ran `rocm-smi` on the machine. It's inserted.

##### **Qazalin** [[00:15:31](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=931)]
Yeah, it resets when I power reset.

##### **Geohot** [[00:15:35](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=935)]
We should blacklist it. We should blacklist it. Just any agent can do it. Yeah, let's blacklist AMD GPU. Because there should be absolutely no way. I can't believe that there's some way that it brought the machine down without the driver.

##### **Nimlgen** [[00:15:51](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=951)]
Actually, it was hardware fault. So the CPU complained about cache.

##### **Geohot** [[00:16:00](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=960)]
So wait. Oh, so there's a problem with tiny R11's hardware that we need to fix.

##### **Geohot** [[00:16:09](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=969)]
I'm not sure about that.

##### **Nimlgen** [[00:16:13](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=973)]
OK. I mean, we need a way to reproduce that. Because maybe something broken was sent from the GPU itself to the CPU. And because of that, cache was not coherent.

##### **Geohot** [[00:16:29](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=989)]
OK, so interesting note. Right now I ran `rocm-smi`, and it's complaining about some device 1. It's saying N/A for device 1. I mean, that's a brand new computer. It might have issues.

##### **Geohot** [[00:16:42](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1002)]
Could we be running through provisioning and everything?

##### **Wozeparrot** [[00:16:47](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1007)]
Yeah, I actually ran this one twice because this had issues before. I would not be surprised.

##### **Geohot** [[00:16:53](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1013)]
Oh, you think? OK, yeah. Yeah, yeah, yeah. Let's just fix the hardware if the machine has hardware issues and stuff. Because yeah, I can't believe. You say the CPU complained that the cache wasn't coherent. Ah, it sounds like a bad CPU a lot more than the GPU did something to me. Can you like? What? What do you think the GPU could do to do that?

##### **Nimlgen** [[00:17:21](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1041)]
Um. Maybe can't do that. I know because they just sent like this loop request. And I don't know if it's broken. I don't know. I mean, we've seen something similar on the Mac. As well. So when we just disconnecting GPU, some better requests and like. Yeah.

##### **Geohot** [[00:17:51](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1071)]
Oh, well, yeah, but that's because the Mac kernel is interacting with the driver.

##### **Nimlgen** [[00:18:00](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1080)]
Oh, yeah, but actually it was the hardware fault as well.

##### **Geohot** [[00:18:05](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1085)]
I see what you're saying. OK, I have a theory. So right now, that GPU that's saying N/A, that might be a bad GPU. Yeah. I could totally believe that a hardware fault on the PCI connection to the GPU, even if that hardware fault is on the GPU side, could bring a CPU down. See what I'm saying? If the issue is at the deep protocol layer, right, if the issue is at the PCI protocol layer, I could totally believe that brings a CPU down. I just can't believe that anything in-band in PCI could bring a CPU down.

##### **Geohot** [[00:18:50](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1130)]
I know. I want, I think it's such an amazing world right now.

##### **Wozeparrot** [[00:18:56](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1136)]
Yeah, yeah, yeah. It seems fixed now, which is suspicious.

##### **Geohot** [[00:19:01](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1141)]
Okay, there's stuff complaining about the MES ring buffer being full in `dmesg`.

##### **Geohot** [[00:19:22](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1162)]
I see the computer just rebooted. Yeah, it looks like there's some bad GPU or something, right? Because no one tried to run anything on that machine, right? No? I think the GPU in port 86 is broken. Is that the GPU that said down for me? I mean, I don't know. I just see that in `dmesg`.

##### **Geohot** [[00:19:56](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1196)]
But yeah, my point is that right after the reboot, it was complaining about that MES fail-to-respond thing.

##### **Geohot** [[00:20:03](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1203)]
I mean, that's got to be hardware, right? Because we haven't even touched anything.

##### **Nimlgen** [[00:20:10](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1210)]
I think `rocm-smi` just reports this kind of randomly, because I've seen this on the other machines as well.

##### **Geohot** [[00:20:26](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1226)]
So it's only one of the GPUs that's doing that.

##### **Geohot** [[00:20:36](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1236)]
And it is that same GPU. I mean, so the devices on the GPU are in the order of they are on the PCIe bus.

##### **Nimlgen** [[00:20:45](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1245)]
In the ROCm SMI, I think it might not.

##### **Geohot** [[00:20:53](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1253)]
I'm going to send a hard reboot to the machine right now, and we'll see if it comes up with any MES errors. But I think this is a hardware bug, and I think we should fix it regardless. Oh, the reboot? Yeah, cool. How do I trigger it? So I'm in tinybox...

##### **Wozeparrot** [[00:21:15](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1275)]
In `tinybox-access`, do `infra-reboot` and then a machine name.

##### **Geohot** [[00:21:27](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1287)]
No, `tiny-r11`. Oh, that's weird. I'm going to redeploy that. We'll try it at the end of the meeting.

##### **Geohot** [[00:21:45](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1305)]
Yeah, we'll have a way so nobody will have to ping anyone in Discord anymore. We told everyone in the `tinybox-access` channel not to spam reboots. It's not like if you do spam reboots you'll just get banned from your `tinybox-access` channel; I don't think it's a very big deal. It's better than giving people access to all the BMCs, but yeah, we have access to rebooting the machines out of band. We're a cloud provider now. We're a cloud provider. You can reboot the machines out of band. Discord-based cloud provider. All right, cool. How is the dev stuff coming? So I see that the interface stuff was merged.

##### **Chrism** [[00:22:29](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1349)]
Yeah, yeah. So the only thing from there that isn't merged yet is the semicolon syntax where you can specify multiple devices. So I've got to do that. And then the other thing is that mock actually needs to be an interface for it to be able to be used as like mock plus, you know, AMD or whatever. And similar. But yeah, I mean, USB works right now. You put USB plus, you know, AMD.

##### **Geohot** [[00:23:00](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1380)]
Right.

##### **Chrism** [[00:23:02](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1382)]
Yeah.

##### **Geohot** [[00:23:03](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1383)]
How about the semicolon syntax?

##### **Chrism** [[00:23:07](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1387)]
Yeah. Sorry, you mean to specify which device number?

##### **Geohot** [[00:23:11](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1391)]
Well, yeah. How do I specify the device number? How do I specify also for the semicolon so I can specify multiple, like find different renderers to devices and stuff?

##### **Nimlgen** [[00:23:19](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1399)]
Yeah.

##### **Chrism** [[00:23:19](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1399)]
So that all works like we discussed. For right now, you still have to do `HCQ_VISIBLE_DEVICES` for selecting a device. I need to fix that, but that'll be like a semicolon after the interface. We kind of mentioned this before: it's a little awkward with remote, because remote is like `hostname:ip:port:device_number`. The only thing I saw as an issue is that right now the way remote works is that you do `remote=<hostname>:<ip>`, and then previously it's also used to specify `AMD_IFACE=PCI`, so I don't know. It's sort of like remote PCI.

##### **Geohot** [[00:24:14](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1454)]
Right? Yeah, I mean I also see some complaint in tinybox access about AMSMI being broken.

##### **Geohot** [[00:24:21](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1461)]
Oh, all right. I didn't see it trying to access something with remote. I'm not sure about that. Oh, is `TinyR5` the machine you're experimenting on with the remote stuff?

##### **Nimlgen** [[00:24:55](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1495)]
Yeah, yeah. That should be a simple fix.

##### **Geohot** [[00:25:00](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1500)]
Cool. Okay, maybe this is unrelated to the `DEV` change. Oh yeah, good. I'm glad that's coming along. Has Comma switched to the new tinygrad yet?

##### **Chrism** [[00:25:10](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1510)]
Yep. And they added us back to the auto bump list of packages. So it should be every Monday we get bumped.

##### **Geohot** [[00:25:21](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1521)]
Great. We are almost ready to deploy a custom firmware where it all works. I want to hand off the actual deployment of this to you to make sure that Comma integrates with it well. The custom firmware currently doesn't work for USB4, and I think the PCIe link speed is only 1x, but I'm not even sure we care.

##### **Geohot** [[00:25:48](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1548)]
The USB is fast.

##### **Geohot** [[00:25:50](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1550)]
Cool. Yeah, I got both paths working. Again, I want to hand the integration of this off to you. Also, the testing of the Chestnut hardware: I posted about this on Comma Slack. Basically, it's browning out during USB PD negotiation, and that makes it really hard for me to sniff USB4. So yeah, just make sure that gets communicated right to Comma.

##### **Chrism** [[00:26:23](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1583)]
Yeah, yeah. I saw Ro respond a little bit about that, but I will bring that up again.

##### **Wozeparrot** [[00:26:31](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1591)]
Interestingly, the boards I've tested have been super stable on USB4.

##### **Geohot** [[00:26:36](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1596)]
Well, they're stable on USB4, but the problem is the PD negotiation is triggering a reset of the device. So it actually just happens to work. It resets the thing and then it just happens to come back, but we're just getting lucky. It's timing.

##### **Nimlgen** [[00:26:55](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1615)]
I see.

##### **Geohot** [[00:26:55](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1615)]
And that's why they're stable once they're up, but I've had to unplug it and replug it a few times to get it to negotiate correctly, because there's basically a race condition where PD is browning out the microcontroller. It's browning out the ASM.

##### **Wozeparrot** [[00:27:10](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1630)]
Yeah, I've noticed that too. I wasn't sure what it was.

##### **Geohot** [[00:27:13](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1633)]
The signal integrity seems good. Once it's up on USB4, it seems fine. But the problem is that USB PD negotiation sends this thing called a hard reset, which resets the PD. This turns the power off on the VBUS rail for a tiny amount of time. I think the stock controllers, like the normal ASM chip things, have enough capacitance to buffer through this. I have no idea how long this pulse is. I don't have an oscilloscope here or anything to check. Chris, I just wanted to make sure that the USB GPU gets rolled out to Comma and all that unpickling stuff should

##### **Chrism** [[00:28:05](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1685)]
be super fast now. Cool. So it has been merged. You had `CUSTOM=1` in

##### **Geohot** [[00:28:13](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1693)]
tinygrad now? I got rid of `CUSTOM=1`. I'll merge that today and then I'll hand it off. Yeah, in order to flash it, I'll put some instructions in the README of the firmware. I got rid of `CUSTOM=1`. I just added to the vendor string that it's custom firmware, like the USB descriptor string. So when you do `lsusb`, it shows up as custom

##### **Chrism** [[00:28:34](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1714)]
firmware. It's pretty nice, actually. Okay, great. So it'll just automatically detect if they're on the latest firmware and then... Yeah, that should never have been

##### **Geohot** [[00:28:44](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1724)]
a flag. Yeah, so it just shows up. Okay. And then, yeah, to flash them,

##### **Chrism** [[00:28:52](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1732)]
we're just going to flash them the same old way. Yeah, yeah, yeah. There's just a script.

##### **Geohot** [[00:28:59](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1739)]
Yeah, yeah, yeah. So you can flash them. You can build the firmware. The new firmware is three and a half kilobytes, and I did all sorts of stability and fuzzing tests with it yesterday. It's super stable. So basically, Dan, I know you worked on this a bit too, and I know we discussed this. I actually went and did it. There's now two extra control transfers in the custom firmware. The old method still works, with `E4` and `E5` and bitbanging the PCIe registers, but bitbanging the PCIe registers is stupidly slow. So what I did was I added an `F0` control message, which then lets you send bulk transfers in and out to rapidly submit TLPs to the PCIe engine. This will let you read and write anywhere in PCIe. However, it's still pretty slow because the TLPs are only four bytes, so each transaction on the PCIe bus is only four bytes. That might go faster if I fix the Gen 1 link issue, but it's still pretty slow.

But I also have the fast path working. The fast path is the `F2` command, which sets up DMA. There is 512 KB of SRAM on the ASM chip, and the `F2` command will enable a bulk transfer that goes directly from a single bulk transfer to all 512 KB of SRAM. If you're on USB 3 Gen 2, this will go at 700 MB/s. The really hard thing, the thing that took me days and days and days, is getting the opposite path to work. So you can set up the DMA controller to do a read of this SRAM, but you set it up and then the bulk-in just doesn't work. I couldn't figure out why. The USB request to actually do the read just hangs.

It turns out that there's hardware in the ASM chip that detects writes: it snoops the bus and detects writes to the completion queue. But this is actually kind of nice, because you can use the GPU SDMA to just SDMA a single byte to the completion queue, and that will automatically trigger the readback path from USB. The USB readback path will trigger when it gets the SDMA to the completion queue, and you don't have to clear it or anything. It's really simple. Just any write at all to the completion queue area works. There's a special register to specify where that completion queue area is. Once you set this up correctly, you can just DMA out at the same 700 MB/s. So that's going to require a change to tinygrad. Nimlgen, once this is in, if you could make that change, if we're on the custom firmware...

##### **Geohot** [[00:32:07](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1927)]
Yeah, you see what I mean?

##### **Geohot** [[00:32:11](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1931)]
Yeah, yeah.

##### **Nimlgen** [[00:32:13](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1933)]
Cool.

##### **Geohot** [[00:32:14](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1934)]
I remember we discussed this, and you were like, "I don't see how to get the other path to work." After I wasted four straight days on this and wrote a super sophisticated emulator, it turns out all you have to do is poke the completion queue.

##### **Geohot** [[00:32:29](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1949)]
Like from the GPU side.

##### **Geohot** [[00:32:32](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1952)]
Yeah, I see.

##### **Geohot** [[00:32:36](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1956)]
Yeah, I have that `sram_verify` script. It implements it.

##### **Geohot** [[00:32:42](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1962)]
But yeah, there's just a magic address you have to write to, and you can rewrite the same address over and over again. You don't have to clear it, nothing. It actually snoops the bus. So we don't have to do that hack anymore with reading out `F0`. I think the detection of the custom thing can be temporary, and we can remove the other path, and I think this can refactor a whole bunch of stuff. Nimlgen, I'll leave that refactoring to you, and Chrism, I'll leave the deployment of this to Comma to you.

##### **Chrism** [[00:33:17](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=1997)]
Yeah, sounds good. The other thing is the `ctypes.Structure` PR. I have a draft PR open on this. I don't know, I'm not super thrilled with it, but it is faster and it does support read-only structures, which is kind of nice. Nimlgen, you had mentioned that this would make a big difference for the PCI interfaces. So if that's worth doing, I can definitely clean it up a little more. But yeah, I think that's the main thing that I'm going to do. It's also a little faster, which is good.

##### **Geohot** [[00:34:01](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2041)]
I don't totally understand this. Is this a fast path? Or is this the only path?

##### **Chrism** [[00:34:06](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2046)]
No. So one of the things in there is that to be able to do the read-only memory views, you have to poke at `ctypes.pythonapi` to be able to get the addresses out. For instance, previously we had those little comments right before we did our `mv_address` in `tinygrad/helpers`, that were like, "Oh, it'd be nice if this supported read-only memory views." So this is the way to do that, to actually be able to get the address of a read-only memory view. And the other thing is just, I don't know, it's not really a fast path, because it's just handling each case properly. It's a little more complicated, though.

##### **Geohot** [[00:34:51](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2091)]
I object get buffer. Yeah.

##### **Chrism** [[00:34:55](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2095)]
Yeah, no, that's pretty brutal. That's the part that I am a little bit like,

##### **Geohot** [[00:34:59](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2099)]
yeah.

##### **Geohot** [[00:35:03](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2103)]
Interesting. But that's so self-referential. I mean, Python `ctypes` is itself... yeah, exactly. It's fast. I mean, those are pretty stable APIs, I think.

##### **Chrism** [[00:35:18](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2118)]
Yeah, yeah. No, they're part of the Python stable API. All that stuff is solidified. Since Python 3.11, that struct is guaranteed to never change size or change layout. Yeah, I mean, especially if it's really good for the PCI iface to be able to use read-only structs, I think it might be worth it.

##### **Geohot** [[00:35:41](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2141)]
Well, I mean, we want that. I want that path to be super fast for Comma. Supporting the eGPU on Comma... look, I just spent the last week or two working 12 hours a day on this stupid firmware. Again, this wasn't for USB4 before; this is for USB3. But I think it's worth it, because this is also related to getting that agentic path for improving LLaMA working really fast and reliably. Make it really easy to just do one command: boom, profile your whole LLaMA; okay, fix it; okay, boom, try it again. The less friction any of these things have, the more they're going to be done by developers.

I think you can extend this point even further. I don't run Tiny Corp so that I can get personally rich. I think getting personally rich is actually fairly worthless. And I don't mean this in some altruistic way; I'm a very selfish, self-centered person. But the problem with focusing on just getting yourself rich is: you could be the richest guy in the world, but if you live in a war zone, your life's terrible. The way the future looks good is if local AI becomes the dominant path, and it never becomes the dominant path through ideology. We're never going to be able to tell people "don't use the cloud, the cloud is bad." That's never going to work. You need to make your product more convenient and simpler to use than the cloud.

The same thing is true of tinygrad. The way we're going to get adoption on tinygrad has nothing to do with telling people, "Oh look, it's ideologically pure. Look, you can modify it yourself, and it's short, and it doesn't depend on large companies maintaining it out of goodwill." None of that matters. The only thing that matters is how simple and convenient these tasks are to do, how fast the REPL is, how low-friction there is. That's why we make a lot of the decisions we make. The reason that we don't have any dependencies is because dependencies break. Dependencies break all the time, and then all the dependencies aren't at the right version, and you're like, sure, sure, sure, you can work around this with a tool, you can work around this with NPM. But then what you encourage is a dependency on a library called `is-even`, right? We don't want that. You get whatever you encourage. Look at MLIR: MLIR encouraged the creation of dialects, and now people complain there are too many dialects. You can look at what Torch depends on: Torch depends on this ATen API, so it encouraged the use of this ATen API, and now you get tons of ATen methods. What tinygrad encourages is deletion. Every time we can take something and just delete thinking about it, the more we win.

And the USB GPU needs to be just as easy to use for Comma as the QCOM path. If they're not willing to put any more time into, "Oh my god, it's USB3. Oh, that doesn't work. Oh, I gotta set this flag," we've lost. The way Comma is going to end up shipping big models is by having a completely trivial switch between `QCOM=1` and `AMD=1`, and no one at Comma ever has to think about it. Speed's all the same. You never have to think about bulk-in and bulk-out or anything like that. That's all dealt with for you, and it's dealt with in a way that doesn't increase complexity. With all these things, what we actually want to do is drill down to what the actual simplest way to do everything is. It's only if it's simple and frictionless that anybody will actually use this. Look, I'm super mad about Apple and having to submit that stupid thing. If this was just for us, I'd just be like, "Just disable SIP on all the Macs." It doesn't even do anything.

##### **Geohot** [[00:40:18](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2418)]
But it's not. We need to deliver something that is convenient and easy, because that's the only way Tiny Corp, tinygrad, and local AI in general are ever going to win. So yeah, that's kind of what I worked on this week.

##### **Geohot** [[00:40:41](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2441)]
This week, I'm going to work on Qwen upstreaming, and I'm going to work on the x86 review. I think we're finally there with that, and we can start moving into this assembly stuff. Oh, cool. I also forgot remote stuff. How is remote stuff going?

##### **Geohot** [[00:40:58](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2458)]
Are we training on two machines yet?

##### **Nimlgen** [[00:41:07](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2467)]
No, I haven't tried training, but we can do all-reduce, and the link speed is about 10 or 10.5 GB/s. For training, I haven't tested that yet. I see the main blocker as loading data from disks, because currently I just have two remote clients set up in my setup, and in this case right now it will just use remote to load from the disks over remote.

##### **Geohot** [[00:41:54](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2514)]
How do we deal with this in general? How do we deal with data loading in general being slow? Why is remote using the disks slow?

##### **Nimlgen** [[00:42:03](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2523)]
I mean, it's slow simply because of the speed. I think we're limited to 100. Maybe 200 megabytes a second.

##### **Geohot** [[00:42:25](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2545)]
I think the physical link is only 100 gigabit. That should be a lot more than 100 megabytes a second.

##### **Nimlgen** [[00:42:39](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2559)]
I know. I'll test that. But actually, we kind of think of remote as the control lane, but in the current setup it's not. Because we don't have an NVMe driver and NVMe disks, we'll send data over it.

##### **Geohot** [[00:42:58](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2578)]
I mean, I think the right solution here is the NVMe disks. The NVMe disks right now are formatted

##### **Geohot** [[00:43:09](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2589)]
ext4. Yes.

##### **Geohot** [[00:43:14](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2594)]
Yeah. I mean, `ext4` is very simple, actually. If all you want to do is read from a filesystem, the complexity is not that much bigger than zip or tar or GGUF or something. So I have an `ext4` gist. Which trainer are you running that's having this problem with the access?

##### **Nimlgen** [[00:43:43](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2623)]
I think any will have it, but again, I haven't trained anything yet.

##### **Geohot** [[00:43:51](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2631)]
No, sure. I'm just thinking long-term. I think the way that we want to deal with this is that we want tinygrad to implement `ext4`, and we want to unload the NVMe driver from the kernel. `ext4` is simple. So right now, you just have some kind of remote disk protocol that's running syscalls on the other side?

##### **Nimlgen** [[00:44:20](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2660)]
I think that's not the case.

##### **Geohot** [[00:44:21](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2661)]
No, we don't have anything like that. How's it working? Sorry, I haven't read the code.

##### **Nimlgen** [[00:44:28](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2668)]
No, I mean, we have remote, and remote only controls the PCI.

##### **Geohot** [[00:44:33](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2673)]
Yeah, but right now I can train `beautiful_mnist` on a remote machine. How is that working?

##### **Nimlgen** [[00:44:40](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2680)]
Yeah, it will load weights from your local machine to the remote machine over remote.

##### **Geohot** [[00:44:47](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2687)]
Oh, I see. So it's using disk locally. It's loading them onto CPU and then it's doing remote CPU?

##### **Geohot** [[00:45:04](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2704)]
No. How is it? Explain to me all the steps.

##### **Nimlgen** [[00:45:10](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2710)]
Okay. So to do the copying, we have system memory, which is kind of like pinned memory. The system memory gets allocated on the remote machine, and you basically have the remote function write into that system memory. That's basically what we do over remote.

##### **Geohot** [[00:45:36](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2736)]
So you copy...

##### **Geohot** [[00:45:39](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2739)]
I see. Is that path fast?

##### **Geohot** [[00:45:46](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2746)]
I think no. It's...

##### **Geohot** [[00:45:50](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2750)]
Oh, I know.

##### **Geohot** [[00:45:51](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2751)]
Okay.

##### **Geohot** [[00:45:54](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2754)]
Yeah.

##### **Geohot** [[00:45:55](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2755)]
I see. So this is going over... yeah, yeah. I'm reading the code now. So what you're doing is basically... but it is going over the remote link.

##### **Geohot** [[00:46:06](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2766)]
It's going over that TCP link, right?

##### **Geohot** [[00:46:10](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2770)]
Yeah. Yeah, okay.

##### **Geohot** [[00:46:11](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2771)]
So this is what we want to avoid.

##### **Geohot** [[00:46:14](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2774)]
I see a few different ways that we can avoid it, of varying complexity. I think the first one we want to support, probably the simplest one here before we think about `ext4` and NVMe drivers and stuff, is like this: I have two machines. I have my driver machine and my remote machine. So my driver machine should be able to allocate a chunk of CPU memory that my remote GPUs

##### **Geohot** [[00:46:42](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2802)]
can then access quickly over the Mellanox. Can we do that? Can you repeat it?

##### **Nimlgen** [[00:47:03](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2823)]
Yeah, we can allocate the CPU memory, which is kind of system memory, and we can use Mellanox over it.

##### **Geohot** [[00:47:05](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2825)]
Yeah. So I think the way to make disk fast, at least for now, is this: long-term we should do an NVMe driver and `ext4`, but before that, on your host machine you allocate a chunk of CPU memory. You do a copy from the disk into that CPU memory, which should happen at pretty much full NVMe speed using `io_uring`. And then on your remote machine, you use the Mellanox to copy from that CPU memory

##### **Geohot** [[00:47:47](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2867)]
into the remote GPU.

##### **Nimlgen** [[00:47:54](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2874)]
Yeah, the only problem is that we kind of have only one interface supported now. So basically what I'm doing is I have two remotes. One of them is just `localhost`, but still the control process is the separate one.

##### **Geohot** [[00:48:15](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2895)]
Yeah, yeah, yeah. I agree that it should definitely be like that. But what you can do there is: I think the controller process, the non-remote, can be the one that actually submits the `liburing` requests to the disk. In fact, we should probably refactor disk a little bit more generally. I think there are paths in disk right now which are creating some CPU buffers that are then being ping-ponged and copied fast to the GPU. But currently `liburing` does not support

##### **Geohot** [[00:48:46](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2926)]
direct copies from the disk to the GPU.

##### **Nimlgen** [[00:48:50](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2930)]
Correct?

##### **Geohot** [[00:48:53](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2933)]
It does now.

##### **Geohot** [[00:48:56](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2936)]
It does now?

##### **Geohot** [[00:48:57](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=2937)]
It does on Linux 7.0. Oh, Linux 7.0. I mean, regardless, this is the kind of thing that we're going to have to support anyway. And we probably want to do this at an earlier level of the graph, right? So whenever you see a copy in the graph from disk to GPU, it's not really an allowed copy path. The way to make this stuff really generic is that it inserts a CPU copy. But the key thing about that CPU copy is it shouldn't need to allocate, say, a gigabyte on the CPU if you're reading a gigabyte. It's the same exact rangeify that we use everywhere else. It's the same exact form of double-buffering ping-pong that you want to use in a GEMM kernel, right? The kernel should basically be a copy from the disk through the CPU to the GPU. And then you could imagine that same thing working remotely, where you have your controller process copying it to CPU RAM that's allocated by the controller process, and then whether you have the remote that's actually on the same machine or the remote that's on the faraway machine, they should both be able to DMA quickly from that chunk of CPU memory.

##### **Geohot** [[00:50:13](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3013)]
Does this work?

##### **Nimlgen** [[00:50:14](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3014)]
Yeah. Yeah. Yeah.

##### **Geohot** [[00:50:19](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3019)]
Yeah. Yeah. Yeah, yeah.

##### **Geohot** [[00:50:26](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3026)]
Yeah, I mean, in the `liburing` stuff now, we have some kind of ping-pong buffer, if I recall correctly. We have some amount of preallocated pinned memory. What we want to do is genericize that. See what I mean?

##### **Geohot** [[00:50:54](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3054)]
Oh. I mean, it's range-ify, really. That transformation that says don't do... So you're copying your gigabyte from the disk to the GPU, right? That same transformation that says don't allocate a full gigabyte on the CPU is the exact same transformation that does A plus B plus C as a single kernel with locality instead of doing A plus B into a huge buffer and then plus C from that huge buffer.

##### **Geohot** [[00:51:25](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3085)]
So yeah, I mean, tinygrad eventually, at some point, needs to unify these things. Yeah, but I think the... oh, go ahead.

##### **Nimlgen** [[00:51:45](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3105)]
Yeah, I think the prereq for this is to remove `ExecItem`, because that's currently the level where we do the decision.

##### **Geohot** [[00:51:57](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3117)]
Yeah. Cool. I see that on your sprinkles.

##### **Nimlgen** [[00:52:07](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3127)]
All right.

##### **Geohot** [[00:52:12](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3132)]
So yeah, the update I see from Chenyu is that, as he's working on mixing in the tensor cleanups, he has something where he's auto-detaching the softmax. I don't fully even understand how this works. I thought the detach was actually part of the algorithm, but if it's not part of the algorithm, even better. And then the split accumulation ALU optimization should be moved. We always knew this. There's this thing in tensor where if you're doing a big accumulation, let's say you're just doing a sum of a gigabyte block, the way to do this is not to dispatch a single CU that adds up everything in the gigabyte. It's to first sum it to, like, a 4 KB block and then sum that 4 KB block. That's way, way, way faster. So yeah, Chenyu's working on moving that out of `tensor.py`.

##### **Geohot** [[00:53:09](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3189)]
It should never have been in tensor.py. So that's good.

##### **Geohot** [[00:53:18](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3198)]
Yeah, we'll finish up the custom USB stuff. Everyone has their tasks on that. And then everyone has their tasks on the LLaMA trainer, the continued JIT refactor, and getting remote training to work in a sustainable way. And I'm really pitching the Exa Box as a single GPU. Gotta make sure the software is there. I think it'll feel really cool to just dispatch. And then the other thing kind of related to this is the discussion about it taking 10 seconds to boot the GPUs. Well, it takes 10 seconds to boot the GPUs because it boots them sequentially. So yeah, I think the first step is to move the driver into tinygrad, and then it should be pretty easy to have tinygrad dispatch this all in parallel. So yeah, I'm glad that I almost wrapped up the custom firmware. USB4 should be built.

##### **Wozeparrot** [[00:54:28](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3268)]
Sorry. Do you know if the ASM supports USB 3.2 Gen 2x2?

##### **Geohot** [[00:54:35](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3275)]
Um... Maybe. I don't have a computer that supports that.

##### **Wozeparrot** [[00:54:42](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3282)]
Your H... I think the ZBook Ultra supports it on the USB4 ports.

##### **Geohot** [[00:54:48](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3288)]
Oh, on the USB4 ports. If I disabled USB4.

##### **Wozeparrot** [[00:54:52](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3292)]
If you just don't authorize the device, it should drop to Gen 2x2.

##### **Geohot** [[00:54:58](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3298)]
Um... Cool.

##### **Geohot** [[00:54:59](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3299)]
Yeah, I'll try it. I've been testing on the TinyBox with the Gen 4 motherboard; that one only supports 5 Gbit.

##### **Wozeparrot** [[00:55:10](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3310)]
I believe so.

##### **Geohot** [[00:55:13](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3313)]
Yeah, I only see 5 Gbit on that one. And then I see 10 Gbit on another HP laptop here. It's an older Ryzen 8640U, a Hawk Point, and that one gets me 10.

##### **Geohot** [[00:55:29](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3329)]
But yeah, I mean, I think that the chip supports... Does the chip support it? I didn't have to do anything to configure that.

##### **Geohot** [[00:55:39](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3339)]
Um...

##### **Geohot** [[00:55:41](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3341)]
That was just all automatic.

##### **Wozeparrot** [[00:55:43](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3343)]
Go ahead.

##### **Geohot** [[00:55:45](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3345)]
That was just all automatic.

##### **Wozeparrot** [[00:55:48](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3348)]
I'm assuming the chip supports it if it supports USB4. I don't really see a reason for it to not support it, considering it's just USB3 Gen 2x1, but with an extra lane.

##### **Geohot** [[00:56:01](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3361)]
Well, yeah, then it probably does.

##### **Geohot** [[00:56:04](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3364)]
There might be some in there. I don't know. If you want to read the custom firmware, I'll link it. I'm very proud of it. AI didn't write it at all. AI just loves to add things. But then again, you can't just blame AI for this, because the stock firmware also adds tons and tons and tons of stuff. There are so many registers that I have no idea what they do, and I don't even know why you'd want them.

##### **Geohot** [[00:56:35](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3395)]
Which is kind of scary, because I'm sure they do something.

##### **Geohot** [[00:56:41](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3401)]
Uh... But yeah, that's the full firmware.

##### **Geohot** [[00:56:46](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3406)]
Pretty short.

##### **Geohot** [[00:56:48](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3408)]
Yeah, short.

##### **Geohot** [[00:56:49](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3409)]
Pretty short. Just for things that need speed, I put them in the firmware. For the flasher, I didn't bother to put the flasher in the firmware.

##### **Geohot** [[00:56:59](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3419)]
I just put the flasher in a file called `e4flash.py`.

##### **Geohot** [[00:57:08](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3428)]
And `e4flash.py` just flashes for you

##### **Geohot** [[00:57:14](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3434)]
using the peeks and pokes.

##### **Geohot** [[00:57:19](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3439)]
Oh, this Flasher without bootloader?

##### **Nimlgen** [[00:57:22](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3442)]
Yep.

##### **Geohot** [[00:57:22](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3442)]
Yep.

##### **Geohot** [[00:57:26](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3446)]
It's all AI-written, but it works. It flashes with the bootloader, but the thing that I couldn't make it do, and I tried for a few hours, is reboot without the FTDI. I haven't found a way to make the chip reboot without the FTDI or unplugging and replugging it, and the stock one can't do this either.

So what the bootloader does is: the firmware doesn't actually run from the SPI flash. I believe this can be confirmed with an oscilloscope, that it reads the entire firmware from the SPI flash in the bootloader to some secret code-page RAM, and then it runs out of this code RAM, out of `IDATA` or whatever. So I can read from `IDATA` and that all works, but that's unrelated to the SPI flash. So I can reflash it, and I can reboot the chip. There's a register which will do a reset, but that reset doesn't retrigger the bootloader. So I haven't found any way to retrigger the bootloader and retrigger the read. You actually have to unplug it and plug it back in after you reflash.

##### **Geohot** [[00:58:37](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3517)]
It's a little bit annoying.

##### **Geohot** [[00:58:40](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3520)]
Yeah, and then the USB4 thing: I have a whole emulator that makes finding stuff super easy. The way that Claude wrote that flash was I just run the emulator and run the flash through the emulator. The way the emulator works is that it proxies every MMIO read and write over the serial port to the device, which is actually amazing that it works, and it makes seeing things super easy. So that's how I figured out all the NVMe stuff. I got the NVMe drive to boot in this emulator where I'm actually running on a soft 8051 core written in Python, and then I'm proxying all the MMIO. So yeah, it makes debugging things super easy, but because of the PD brownout issue, I can't fix that with USB4. But once we fix the PD brownout issue, the emulator should just work, and then it's easy to see what registers you need.

##### **Nimlgen** [[00:59:38](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3578)]
Cool. Cool.

##### **Geohot** [[00:59:46](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3586)]
Anything else?

##### **Nimlgen** [[00:59:47](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3587)]
Yes.

##### **Geohot** [[00:59:55](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3595)]
I'm talking to Comma about wanting to have DSP support at some point.

##### **Chrism** [[01:00:01](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3601)]
Oh, but I don't know.

##### **Geohot** [[01:00:03](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3603)]
How much is Comma willing to pay for the DSP support? They want to run the whole model on the DSP.

##### **Wozeparrot** [[01:00:11](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3611)]
You mean the whole model? The driving model. Why? Unclear.

##### **Chrism** [[01:00:17](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3617)]
Well, okay, this was Harold at lunch. He was like, "All the cool kids these days are running their models on the DSP, so we gotta do that too." I don't know if it was fully thought out.

##### **Geohot** [[01:00:32](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3632)]
Yeah, yeah, Tiny Corp can help for a price. No, it should be a lot easier now. I mean, it's worth it for somebody to go back into that old DSP stuff and modernize it all. I don't know who's excited about that project, but Chris, you're excited about that project.

##### **Chrism** [[01:00:54](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3654)]
Yeah, yeah. Well, I don't know if I'll have a chance to take a look at it this week, but I think it'd be

##### **Geohot** [[01:01:00](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3660)]
No, no, not this week. I'm saying next sprint. Maybe we can get the DSP back up for Comma. Actually, I think it's a good project for you because it's similar to the image stuff.

##### **Chrism** [[01:01:10](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3670)]
The trick to getting speed on the DSP is basically just putting things in the buffers in the right place.

##### **Geohot** [[01:01:18](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3678)]
You need padding. But once you have like the padding, it's all pretty easy.

##### **Geohot** [[01:01:23](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3683)]
Yeah.

##### **Geohot** [[01:01:25](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3685)]
Yeah, and the lowering path. So I think it's a good project. I think it's a good next project.

##### **Nimlgen** [[01:01:28](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3688)]
Right.

##### **Geohot** [[01:01:28](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3688)]
At Comma, we'll get their DSP support. Yeah. We put a lot of effort into it. We have a custom DSP boot path. We avoid so much of the Qualcomm crap. I think also I'm not sure we ever found a way to not require the test sigs, but there's definitely a way, because the thing that generates the test sig doesn't go to a Qualcomm server. We just need some automated way to generate that test sig in tinygrad. I don't care about signed Qualcomm stuff, but for Comma you still need this fake sig. I think we can just add something to tinygrad to generate them. It's probably three lines of OpenRSA.

##### **Chrism** [[01:02:16](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3736)]
Yeah. I don't really know anything about this sig thing. So I'd have to read about it. But yeah.

##### **Geohot** [[01:02:21](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3741)]
Yeah. I think the DSP is a good next project. Let's make sure we wrap up the `ctypes` thing and the other one nicely. I mean, the eGPU is way more important to me than the DSP. They might say they want the DSP, but I don't care about their 3 TOPS int8 models. I care about their 200 teraflop.

##### **Chrism** [[01:02:47](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3767)]
No, I think it's more important than them. Yeah. Yeah.

##### **Nimlgen** [[01:02:49](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3769)]
Yeah. Yeah. Yeah.

##### **Geohot** [[01:02:50](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3770)]
Yeah. Their models are too small. Comma's models are so small. Very sad. They need to be way bigger. FSD has bigger models and it's better, and we need bigger models.

##### **Geohot** [[01:03:01](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3781)]
Great. Oh, anything else? We good? All right, that's this meeting. Thanks, everyone.

##### **Nimlgen** [[01:03:10](https://www.youtube.com/watch?v=ksHFf4DqGcs&t=3790)]
Thank you.
