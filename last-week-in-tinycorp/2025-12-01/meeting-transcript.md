# 2025-12-01 Meeting

### Meeting Agenda

**Time:** 9am Monday San Diego time
- company update, AMD contract,
- training loop, LLaMA 8B,
- flash attention,
- VIZ/Profiling,
- nvidia HEVC decode,
- QCOM MESA backend,
- Python speed,
- assemblers?

### Audio

[Youtube Link](https://www.youtube.com/watch?v=S7w_cqqW8BM)

### Highlights

- **[Company Updates](#geohot-000000)**: TinyBox raids are selling and shipping today after resolving power instability issues; two Blackwell orders are also preparing to ship.
- **[Training Loop & MMU Faults](#chenyu-000114)**: Chenyu reports hitting MMU faults on the MI350 during training; Geohot notes a fix was deployed, but intermediate number overflows remain an issue.
- **[Fuse Optimization Strategy](#geohot-000245)**: Plans to separate microsteps into their own JIT and fuse gradient clipping into a single tensor update to drastically reduce kernel count in the LLaMA trainer.
- **[Python Speed Improvements](#geohot-000411)**: Python speed is approximately 3x faster due to fixes in n-squared behavior (specifically in tensor assignment), making 8B model startup fast and 405B reasonable.
- **[Flash Attention Status](#wozeparrot-000559)**: Flash attention PR works for evaluation but encounters MMU faults; the plan is to integrate it into `tensor.py` via `fa=1` and test using Stable Diffusion on MI350x.
- **[SQTT & Visualization](#qazalin-000936)**: Merged software SQTT fixes; running with `viz=2` now correctly displays the timeline of waves and instructions, though aggregate views are currently too slow.
- **[HEVC Decode](#nimlgen-001343)**: Merged a minimal NVIDIA HEVC decoder; currently slow due to scheduling and cloning overhead, with plans to optimize by passing the entire video and history tensors into the JIT.
- **[Qualcomm Zero-Copy](#chenyu-002013)**: Discussing zero-copy implementation from NumPy for Qualcomm to enable merging calibration code into OpenPilot.
- **[Mesa Backend & Image DType](#geohot-002159)**: The open-source Mesa backend for Qualcomm is speed-competitive; long-term plans involve removing `Image` as a DType and treating it as a buffer optimization using texture sampling.
- **[Refactoring Symbolic Rules](#chenyu-003056)**: Proposal to categorize rewrite rules (strict removal, constant return, reassembly) to better manage complexity and avoid breaking specific backend requirements like FP8 casting.
- **[Assembler & RDNA3 Project](#geohot-003533)**: Announcing a long-term project to remove LLVM dependence by moving to assembly, starting with RDNA3, including building a cycle-accurate emulator to handle ALU stalls.
- **[MI300/350 Device Hangs](#b1tg-003849)**: Identified a reproduction script for device hangs and MMU faults on MI300X/MI350 when using multiple GPUs; marked as a top priority fix.
- **[UOP Generated Kernels](#geohot-004519)**: A draft of UOP-generated MaxGemm kernels is working and passing tests, proving the concept of handling complex swizzling within the UOP structure despite being currently slower than hand-coded versions.

### Transcript
##### **Geohot** [[00:00:00](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=0)]
Any company updates? TinyBox raids are selling. We sold like four of them. We haven't actually shipped any yet. We got to make sure they ship today. Yeah, we got to make sure they ship today. We were hitting some.. There's a little bit instability and we.. It's stable now. What was it?

##### **Wozeparrot** [[00:00:19](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=19)]
I think it was just power.

##### **Geohot** [[00:00:21](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=21)]
Did you throttle them?

##### **Wozeparrot** [[00:00:22](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=22)]
Yeah. I also didn't throttle a box and that also passed.

##### **Geohot** [[00:00:30](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=30)]
I see.

##### **Wozeparrot** [[00:00:32](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=32)]
It seems to be some variance between boxes.

##### **Geohot** [[00:00:34](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=34)]
Yeah, yeah. The AMD GPUs might have really high transients. We just might need to clip the transients on them. But.. I mean, yeah, I have one here. Again, these things are like.. We test them in really extreme cases. So they definitely do work. So yeah, raids are going to ship soon. We got two orders for Blackwells. Those are also going to ship soon. We did our first testing with that. I mean, those boxes have two power supplies. So you got plenty of headroom there.

##### **Geohot** [[00:01:04](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=64)]
Yeah. Okay.

##### **Chenyu** [[00:01:14](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=74)]
Moving on to the training loop. I think I will focus on this for this week. What's the current status on this? So when I tried to trans.. When I tried to trans.. When I tried to trans training stuff, I hit the default. My 350, I think other people also hit that.

##### **Qazalin** [[00:01:38](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=98)]
My 350, I think other people also hit that.

##### **Geohot** [[00:01:38](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=98)]
The MMU fault, you mean? The MMU fault, you mean? I think a fix went in this morning. I'm not sure that that's everything. Oh, okay. Nimozen, you have more to say about that?

##### **Nimlgen** [[00:01:55](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=115)]
Actually, no, yeah. I mean, we heard some.. bug in our code base. I'm not sure that's related to the MMU fault. I haven't reproduced it since that. I haven't reproduced it since that. Got it.

##### **Chenyu** [[00:02:09](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=129)]
Yeah, so.. What I was doing this morning was I was training around a big ring or reduce. Then I hit the other thing that we'll discuss in the AMD channel. Some of the intermediate number overflow. Some of the intermediate number overflow. That we also probably want to fix. Because our thing would be pretty much

##### **Geohot** [[00:02:30](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=150)]
hitting all the limits on the machine. George, you mentioned another thing that's slow.

##### **Geohot** [[00:02:45](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=165)]
So, yeah, I mean, if you think it would be helpful, I could work on this this week. So, basically what you want to do, it's the same way that we're going to split out the microsteps into their own JIT. So, you really want to step out, you really want to separate out, like, everything should be like really fuse-optim. So you're doing the gradients, you're doing the gradient clipping in a way that's really slow and generates tons of kernels in the LLaMA Trainer. So what you want to do is you want to basically concatenate all the gradients into one tensor, and then that single tensor can do the update. If it would help, I could write this, but I don't really know how I'd test it, is the problem.

##### **Geohot** [[00:03:31](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=211)]
I mean, if you think you can write it reasonably fast, I can

##### **Chenyu** [[00:03:36](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=216)]
test it.

##### **Geohot** [[00:03:38](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=218)]
Yeah, you know what, I'll spend the next two days on it. I think there's a few things that we might need to optimize to, because it is kind of like in the set-assign kind of area. But, um, like slice-assign? But, yeah, no, we want the microstep to compute the entire gradient, and then after we compute the gradient, like the optimizer should basically

##### **Geohot** [[00:04:04](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=244)]
only be like four kernels.

##### **Geohot** [[00:04:11](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=251)]
Which will have our kernels. Also, there's been a ton of progress on speed. Everything's about 3x faster now. If you try stable diffusion on your Mac, there's been a ton of progress on Python speed in the last two weeks. So yeah, I think we're good on, I don't think we need scan. I mean, we still want scan, but I don't think we need it to do 4 or 5b. 8b starts up pretty fast now, and 4 or 5b, okay, it takes a minute to start. It's an 11-day training run, like that's fine.

##### **Chenyu** [[00:04:40](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=280)]
How about the outer-world range? Do we still want that?

##### **Geohot** [[00:04:44](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=284)]
I mean, we do, but I don't think we need it for the AMD contract. I think that now, I fixed a lot of the stuff. So I fixed like all the n-squared behavior too. So the 4 or 5b was particularly bad because there was n-squared behavior on the layer, and I fixed that last week. This was mostly in this tensor-assigned thing, and I fixed that last week. So it's all, the speeds are all reasonable now. Like the speeds are all within, they're the same as torch, basically. So yeah, sure. Scan would be great, but it's plenty good. And 8b starts up really fast now.

##### **Geohot** [[00:05:19](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=319)]
That's good, okay.

##### **Chenyu** [[00:05:20](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=320)]
I would test all these, see where we are, and probably need to retrain something on a real machine and figure out mmUFold or any driver issue.

##### **Qazalin** [[00:05:33](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=333)]
Cool.

##### **Geohot** [[00:05:34](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=334)]
Yeah, I'll work on that training loop with a built-in FuseOptim. But yeah, I don't really know how to test it. I'll just put it in a different file too. I'll make a LLaMA-train.py.

##### **Chenyu** [[00:05:46](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=346)]
Oh, okay, sounds good.

##### **Geohot** [[00:05:48](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=348)]
I won't talk to the other one, because the other one's tested.

##### **Chenyu** [[00:05:51](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=351)]
Okay.

##### **Geohot** [[00:05:52](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=352)]
Yeah, no problem.

##### **Chenyu** [[00:05:54](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=354)]
Cool. Anything for Flash attention?

##### **Wozeparrot** [[00:05:59](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=359)]
Yeah, if you run the.. On my PR, eval should work with Flash attention. I couldn't actually get it to run because I hit the mmUFold too.

##### **Chenyu** [[00:06:09](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=369)]
Is there any reason.. Is that.. Can you use the same Flash attention on smaller, I don't know, LLaMA-train.py or stable-based fusion? Does that work?

##### **Wozeparrot** [[00:06:21](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=381)]
Yeah, it should work in stable-based fusion too. I mean, yeah. It should work in LLaMA-train because that's variable shape.

##### **Geohot** [[00:06:29](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=389)]
Can you put it in tensor.py?

##### **Wozeparrot** [[00:06:32](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=392)]
I thought about that, but it's very MI350 specific. That's fine. We can put it in tensor.py.

##### **Geohot** [[00:06:40](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=400)]
Yeah, I think that's fine.

##### **Geohot** [[00:06:42](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=402)]
It also imports from extra.

##### **Geohot** [[00:06:46](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=406)]
Yeah, I think all these things are fine.

##### **Geohot** [[00:06:48](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=408)]
If you get it with an mvera and just.. It's just like the Flash attention. Just make it like fa equals one. Yeah, fa equals one will use the fastscale.product attention. I wanted to know if you could do this.

##### **Geohot** [[00:06:59](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=419)]
How long is this? How long is what? How big is this? Code? Oh, I mean it'll just import it. Yeah, that's fine, right? It's just a few lines. Yeah, it's just a few lines

##### **Geohot** [[00:07:16](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=436)]
in tensor.py. Yeah, but it'll just run fastscale.product attention and then we can test it in stable-based fusion. But stable-based fusion is probably a good place to test it.

##### **Chenyu** [[00:07:28](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=448)]
And this is forward?

##### **Wozeparrot** [[00:07:30](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=450)]
This is forward. Backwards is a little more complicated. There's some stuff that we have to save and I'm not sure how to save stuff with the custom.

##### **Geohot** [[00:07:40](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=460)]
Yeah, I can show you how to do that. So, you have two outputs from a kernel or one output from a kernel?

##### **Wozeparrot** [[00:07:48](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=468)]
One kernel has one output, one kernel has two outputs.

##### **Geohot** [[00:07:51](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=471)]
Two outputs is.. That's tricky. As long as you only have one output, you're fine. But even if you want to just save it, yeah, you just probably want to add

##### **Geohot** [[00:08:04](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=484)]
a context and just create a tensor empty that it writes to and then put that in the context for the backwards pass. It'll be very explicit, but it should just work.

##### **Wozeparrot** [[00:08:13](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=493)]
Because backwards is.. There's a pre-kernel for backwards and at least the way we're doing it, there's two kernels that actually compute the gradient.

##### **Geohot** [[00:08:19](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=499)]
Two kernels is no problem. It's just on the forward, when you have a kernel that has two outputs, it's difficult for us to compute the gradient because think of how.. It's closed from two places. So you want to avoid that.

##### **Qazalin** [[00:08:32](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=512)]
Okay.

##### **Geohot** [[00:08:33](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=513)]
What I would do is, if you just have one thing that you want to save, I would just create an empty tensor, put that empty tensor in the forward, and then add that tensor to the callback. Like have the callback just do functuals.raps, or not wraps, but you know the one. Functuals.partial. Yeah, do functuals.partial on the kernel and then you can partially apply that empty tensor. And it'll be explicit, but it'll work. Yeah.

##### **Geohot** [[00:09:02](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=542)]
Yeah, there's that, and then we need to fix the after end.

##### **Geohot** [[00:09:09](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=549)]
Yeah, that's not hard.

##### **SPEAKER_02** [[00:09:11](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=551)]
Yeah.

##### **Geohot** [[00:09:13](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=553)]
The after end is easy, thanks, but do the.. The first thing I would do is get it working in tensor.py and let's get stable diffusion running on the MI350x with flashdash check, because stable diffusion is a great test.

##### **Geohot** [[00:09:24](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=564)]
Yeah.

##### **Qazalin** [[00:09:27](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=567)]
Okay.

##### **Geohot** [[00:09:30](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=570)]
Sounds good. Uh.. Want to do this?

##### **Qazalin** [[00:09:36](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=576)]
I did merge some software, SQTT, and that was fast. Last week it was very slow. That should be fixed with a split up per-sie graph. So if you run with viz equals two, you can see the timeline of the waves and the instructions. Hopefully that's good. Yeah, that's nice.

##### **Geohot** [[00:10:00](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=600)]
You know, I think there's been great improvements. It's getting kind of usable. We still got to do the aggregate view. I think the aggregate view should just be on the click and it should aggregate everything across all the waves.

##### **Qazalin** [[00:10:15](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=615)]
I did that. It's slow.

##### **Geohot** [[00:10:18](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=618)]
RGP limits to 60 waves. Interesting. Uh.. Wait, why is it slow?

##### **Qazalin** [[00:10:29](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=629)]
It's slow to decode. Like it takes Oh, because you're only decoding. to decode all the instructions.

##### **Geohot** [[00:10:36](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=636)]
I see, because you're only decoding when you click on a wave. Okay, never mind. Don't do this. That's annoying.

##### **Qazalin** [[00:10:42](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=642)]
I know. Yeah. It's in the branch. I didn't merge it.

##### **Geohot** [[00:10:45](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=645)]
Yeah, I'm half tempted to rewrite SQTT, trace decoder, and rust. Just get something insanely fast on there. It just like parses these things. I don't know. We shouldn't actually do it. But I think we have enough of it figured out now that we could switch to the non-AMD one. But we don't have it. It works for RDNA4, but it doesn't work for CDNA. My reverse stuff.

##### **Qazalin** [[00:11:08](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=668)]
Mm-hmm. I also get errors for RDNA4.

##### **SPEAKER_02** [[00:11:15](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=675)]
Do you?

##### **Qazalin** [[00:11:16](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=676)]
Yeah, yesterday I got stuff for MDMAT at UOPMAT mall. It's like some offset didn't assert.

##### **Geohot** [[00:11:24](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=684)]
In sqttpart equals one? Yeah.

##### **Qazalin** [[00:11:25](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=685)]
Oh, I see.

##### **Geohot** [[00:11:26](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=686)]
Yeah. Oh, post the way to reproduce that. I'll take a look at that. It's probably something simple. Because it is the same thing. But yeah, this week let's do performance counters. I'm hoping performance counters are lightweight enough

##### **Geohot** [[00:11:41](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=701)]
we could do them with viz equals one. Should be, yeah.

##### **Qazalin** [[00:11:49](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=709)]
I mean, all of them have some overhead of flushing the buffer at the end of every kernel. But other than that, it's..

##### **Geohot** [[00:11:57](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=717)]
What do you mean flushing the buffer? Tracing overhead.

##### **Qazalin** [[00:12:00](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=720)]
So after every kernel, you save the trace into a buffer from the GPU copies out.

##### **Nimlgen** [[00:12:09](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=729)]
With just performance counters? No, I mean, we just treat every counter.

##### **Geohot** [[00:12:15](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=735)]
Oh yeah, that's cheap.

##### **Nimlgen** [[00:12:17](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=737)]
As long as we don't have to do anything like

##### **Geohot** [[00:12:18](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=738)]
3DL2 or anything. Yeah, like reading 20 counters is going to be free, basically.

##### **Nimlgen** [[00:12:24](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=744)]
It's not 20. I mean..

##### **Geohot** [[00:12:27](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=747)]
How many is it?

##### **Nimlgen** [[00:12:28](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=748)]
Some of them are.. Depending on the counter, but some of them are like.. Tracked per seamed.

##### **Geohot** [[00:12:37](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=757)]
So, a bunch of them. Some of them are what? Tracked per seamed.

##### **Nimlgen** [[00:12:43](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=763)]
Like per CU. I mean, like each CU has its own counter.

##### **Geohot** [[00:12:48](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=768)]
Yeah, I mean, I guess we could also do.. Yeah, that again, that's not that many. I don't know. But I would like some performance counters to work with viz equals one. It'd be great if we could just show basic memory overheads with viz equals one as reported by the GPU. Kind of like what our bandwidths are to each L2 bandwidth, L1 bandwidth, and the

##### **Geohot** [[00:13:13](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=793)]
DRAM bandwidth. Cool. I will find out.

##### **Qazalin** [[00:13:23](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=803)]
Cool. Okay.

##### **Geohot** [[00:13:28](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=808)]
I'll HVC decode. Yeah, so I merged..

##### **Nimlgen** [[00:13:43](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=823)]
So, I merged the minimal HVC decoder for NV. So, it's pretty slow without.. Because it's not jitted. Right now. So, the whole time is in scheduling right now.

##### **Geohot** [[00:14:00](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=840)]
What is.. Why is it.. I mean, we kind of need like a framework to deal with these kind of things. It's the same as the copy engine, right?

##### **Geohot** [[00:14:09](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=849)]
Kind of, yeah. I mean..

##### **Nimlgen** [[00:14:20](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=860)]
Yeah, it's not that hard to make the jit. The only problem is that actually, we need to clone after each jit right now. So, that's also kind of slow. Or one wasteful copy. And it'll.. And, like, it has variable-sized inputs to the jit. Because the jit is a variable-sized input. In buffer, different sizes. Like, a chunk is different sized.

##### **Geohot** [[00:14:51](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=891)]
Yeah. So, the way that I would deal with that is I would just pass the entire video into the jit and then put the offset and size in a variable.

##### **Geohot** [[00:15:02](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=902)]
Yeah.

##### **Geohot** [[00:15:06](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=906)]
I wouldn't worry about the clone thing on the output. Because, like, usually you're just gonna, like, do something with the frame. Like, imagine basically the flow of, like, decode a frame, run a model, decode a frame, run a model

##### **Geohot** [[00:15:19](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=919)]
kind of flow. So, it's okay if it writes the frame into the same app.

##### **Geohot** [[00:15:25](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=925)]
Oh, but I guess it's not because you need the history.

##### **Nimlgen** [[00:15:29](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=929)]
Yeah. Yeah. It also will corrupt.

##### **Geohot** [[00:15:34](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=934)]
Yeah. Yeah, then what I would do, I would, like, pass in two tensors into the jit. One that's the whole video and one that's the history tensor.

##### **Geohot** [[00:15:46](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=946)]
Maybe, like, an offset into the history tensor, too. And then a bunch of variables to deal with, like, where the frame is that you want to decode. Yeah. I mean,

##### **Nimlgen** [[00:16:01](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=961)]
I mean, for the history right now, like, the solution I have is just to, like, we know the size of the history, like, the maximum size of the history.

##### **Geohot** [[00:16:10](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=970)]
Yeah.

##### **Nimlgen** [[00:16:10](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=970)]
And it's, like, so, yeah, I just, so, yeah, and just pass all of them, the max size to the jit. So, like, capture all the tensors.

##### **Geohot** [[00:16:25](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=985)]
Yeah, but I see. So, you're, you're, you're, like, passing the history tensor. I see. I see. That's just really good. Yeah, I mean, that seems reasonable. But the way to deal with the variable size thing on the input is just to pass in two variables.

##### **Nimlgen** [[00:16:40](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1000)]
Yeah, okay. We'll do that. And then we, yeah.

##### **Geohot** [[00:16:45](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1005)]
Do you think it's worth doing AMDs? Um,

##### **Nimlgen** [[00:16:51](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1011)]
yeah, I'll take a look into that. Um, yeah. I mean, that, that should be pretty easy to do. So, I think it should be pretty easy to do, like, for the kernel driver. But for AM, like, still, like, we need to enable this UVM VCN, how it's called. VCN, yeah. Got it. Yeah.

##### **Geohot** [[00:17:19](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1039)]
I mean, just for the kernel driver would probably be fine. I just like the idea of whenever we're working on a new abstraction, to have both AMD and NVIDIA, so we know, like, what we need to abstract and what we don't.

##### **Qazalin** [[00:17:32](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1052)]
Yeah.

##### **Geohot** [[00:17:34](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1054)]
Um, and I find,

##### **Geohot** [[00:17:35](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1055)]
I find always, like, doing one teaches me things about the other, too. It's like, you know, NVIDIA has this weird stuff about the memory and the and the VCN, or whatever they call it. Uh,

##### **Geohot** [[00:17:45](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1065)]
I wonder if AMD has similar stuff. Um, but yeah. Absolute

##### **Geohot** [[00:17:53](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1073)]
highest priority is any bugs on, uh, MI350X. All those, all those things. Uh, yeah. If we could somehow reproduce the MMU fault. Um, I think that's the highest priority stuff. But otherwise, yeah. I think good work on the on the HVAC decode and, uh, let's find the right abstractions for it. Let's get it to be fast on the JET. And then let's try to convince Comma to use it.

##### **Geohot** [[00:18:17](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1097)]
I see Herois on the code. You want to ask something? What'd you say? Oh, sorry. Oh, I see Herois on the code.

##### **Chenyu** [[00:18:32](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1112)]
Yes, sir. I heard my name. What was your question? We're building you an

##### **Geohot** [[00:18:37](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1117)]
HVAC decoder. Do you want it?

##### **Chenyu** [[00:18:39](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1119)]
Uh, yeah. I saw it gets exactly the NVIDIA posted speed, so that's pretty good.

##### **Geohot** [[00:18:45](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1125)]
Ah, but we didn't specify if it was C2 or C3.

##### **Chenyu** [[00:18:50](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1130)]
Um, okay. It wasn't a bug. It was just the wrong video. It's just the wrong video.

##### **Nimlgen** [[00:18:59](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1139)]
No, I think I posted the second one, which is..

##### **Geohot** [[00:19:02](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1142)]
Yeah, yeah. Harold and I have a $50 bet about whether we're going to get over 2,000 frames per second.

##### **Chenyu** [[00:19:10](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1150)]
Which was optimistic. You could double NVIDIA's, uh, performance.

##### **Geohot** [[00:19:15](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1155)]
All I said was that I don't think there was a bug, but I think it was actually correct. And it was.

##### **Chenyu** [[00:19:22](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1162)]
Yeah, I mean, that's impr.. It's still, uh, quite a.. I mean, it's faster than what we use, so it actually would be an improvement. But we actually don't get NVIDIA's posted numbers.

##### **Geohot** [[00:19:33](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1173)]
I mean, you should also be able to pretty easily, like, the idea here is that you'd want to move your Segnet into TinyGrad2, and that the decode and Segnet would be together very fast.

##### **Chenyu** [[00:19:44](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1184)]
So, yeah. I mean, yeah, that would all be great. It's not trivial in our current setup to move everything from the decoder to the model runner without taking it off GPU. It'll require some really ugly code.

##### **Geohot** [[00:19:58](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1198)]
But yeah, it would be easy if all you had to do was throw in an HVAC and get Segnet outputs out, right? Yeah, exactly.

##### **Chenyu** [[00:20:03](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1203)]
It would be easier if TinyGrad handled all the GPU stuff, so then we don't have to have, like, four libraries to keep stuff on the GPU.

##### **Geohot** [[00:20:10](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1210)]
Yeah, do you have your latest Segnet Onyx somewhere?

##### **Chenyu** [[00:20:13](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1213)]
I'll post it. Cool. Yeah, the only thing I wanted to show for, if you guys are open to this, is the.. If we can get the zero-copy Qualcomm stuff working, we can merge the calibration stuff in OpenPilot, if you guys have any interest in that. So you want zero-copy from NumPy. NimbleGen, any reason that's hard? From Qualcomm. I have an issue for it, if someone wants to look at it. It's one of the latest TinyGrad issues. That's the last block on merging all that stuff.

##### **Nimlgen** [[00:20:53](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1253)]
Yeah, can you hear me? So yeah, probably that's easy. The only problem.. I know. I'll try to do that to map NumPy memory for QCOM. I think that should be possible,

##### **Chenyu** [[00:21:06](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1266)]
yeah. It should be possible with zero-copy, right? Because it worked with the OpenCL stuff, so I assume it should work. Yeah, if you need anything else from me on that issue,

##### **Geohot** [[00:21:18](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1278)]
let me know. Yeah, so it looks like it's just making FromBlob work on the QCOM backend. Yeah, exactly. Cool. Yeah, so I think this is a higher priority than HVAC decode, but lower priority than any MI or other UI 350 issues. Let's move on to

##### **Chenyu** [[00:21:57](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1317)]
the Mesa backend.

##### **Geohot** [[00:21:59](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1319)]
So yeah, Chris is.. He can listen, but he can't talk in the meeting. So I can kind of fill in for that. Yeah, I mean the Mesa backend looks good. I think we'll get it merged probably this week. Um.. Yeah, I mean it's exciting that we'll have an open source uh.. QACOM backend. It's speed competitive uh.. with the with the QACOM closed source one. Um.. and I think maybe we can do a few small tweaks to it to get it to be better. But I think long term, the project here also is removing index.. removing image from Dtypes. Image should not be a Dtype. The only difference on.. the only difference between image and buffer is the instruction that is used to do the load. Um.. so there's no difference uh.. even really on stores. Uh.. there's no difference on anything except loads. Because if you use the image instruction to do the load, there is a texture cache. And that texture cache is twice as fast as any other memory-ish looking thing on the QACOM GPU. Um.. so that's why we have to use it. But it's really just a.. It's really just.. instead of having a load4 instruction, you use the texture sample for. Um.. and texture sample also gives you this added benefit of doing.. it's two-dimensional, so it does this added benefit of doing this.. doing the.. the indexing math for two dimensions, and it also deals with overflows for you. But again, these are all optimizations that can be applied right at the end. These are not optimizations that have anything to do with what you have in the I think the potential blocker might be..

##### **Chenyu** [[00:24:08](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1448)]
We have many places that try to maintain the image as a solid image, otherwise some other optimization would break it, without where there's a more later optimization that can make it fast.

##### **Geohot** [[00:24:22](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1462)]
Yeah, so we probably have to do it before things like simplify-valid and those kind of things. Um.. but regardless of, like, where we do it, at least it doesn't have to be in tensor.py. Even if we do it as, like, a pretty early rewrite. Like, even if we do it.. I mean, probably the right place to do it is, like, post-range. Like, when you do the upcast, call it, like, image-upcast or something.

##### **Chenyu** [[00:24:43](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1483)]
Oh, you mean those pad2, 4, then do a image-conf thing should be removed?

##### **Geohot** [[00:24:50](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1490)]
Uh, so all the pad2s will stay, just the dtype will go away. Like, the image-conf function in tensor will stay, because the image-conf function in tensor is actually doing two things. And the other thing is an optimization we should work on as well, but it's doing the image dtype. It's also swizzling the data. So, this was the biggest improvement on all the DSP stuff. The whole trick to the DSP is basically putting the data in a format that the DSP can read very quickly. So, like, imagine any time you have, like, a global store and a global load. As long as you permute both sides of that, it's equivalent. So, that's what the image-conf and image-GEMM code in tensor.py is doing. So, we would leave it for that purpose. But all the places that we use dtypes. image

##### **Chenyu** [[00:25:42](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1542)]
we can change basically make image equals to one.

##### **Geohot** [[00:25:47](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1547)]
Yes, exactly. Yes. I mean, that's the simplest way to put it. Yeah. So, we would just actually start by making image equals one fast. Yeah. And then doing those rewrites on the backend silently. There's no disadvantage to using that image texture cache ever.

##### **Geohot** [[00:26:03](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1563)]
So, it's always a winning rewrite. That sounds good.

##### **Qazalin** [[00:26:13](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1573)]
Okay.

##### **Geohot** [[00:26:16](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1576)]
Next.

##### **Chenyu** [[00:26:17](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1577)]
I think Python speed, we talked lots of things. I still remember you mentioned something about moving more stuff to the Python backend. And stuff like that.

##### **Geohot** [[00:26:29](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1589)]
Oh, I mean, when I was talking about moving stuff to the Python backend, I was just saying for things like zlib decode, we could put that in the Python backend so then it would be lazy. These things are, like, they're not important, really. Um, but most of the Python speed stuff, the most egregious things have been dealt with now. Uh, the rangeify is now pretty much back on par with what the old stuff was by adding a bunch of caches. There's the reshape cache and stuff now. I mean, rangeify used to be brutally slow because the reshape would, like, every reshape would be a separate thing. But I just wrote the substitute thing and it works. So, yeah, you're hitting a reshape cache now. You're hitting a divmod cache. So there's a whole bunch of speedups there. I sped up the tensor map thing in tensor.py. The tensor map thing was n squared. I rewrote it to not be n squared. And between basically adding caches that match the old shape tracker view caches and fixing this n squared thing, the Python speed is, like, within the realm of reasonable now.

##### **Qazalin** [[00:27:43](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1663)]
Cool.

##### **Geohot** [[00:27:45](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1665)]
Yeah, I'll definitely merge things to make it faster. So, like, we started off with stable diffusion. Like, stable diffusion was taking, like, 50 seconds. Now it's down to 20 seconds. And I think

##### **Geohot** [[00:27:55](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1675)]
with more work, we can get it down to 10. Yeah, I did, like, a little, like,

##### **Geohot** [[00:28:05](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1685)]
micro-optimization in the graph rewrite that adds, like, another 2% yesterday. I tried some bit field stuff. It wasn't faster. I think now we're getting into the most of the realm of diminishing returns, unless we find big bugs. But really, the way to improve Python speed is just to make the rewrites themselves. Like, just do less rewrites. What do we not need to do?

##### **Chenyu** [[00:28:24](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1704)]
Oh, yes. On that topic. Uh.. Oh, how come.. Oh, sorry. Before more.. less rewrite, I don't see a huge change to LLaMA no JIT. Is it because we are doing too many rewrites?

##### **Geohot** [[00:28:40](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1720)]
Well, so for LLaMA no JIT, it.. uh.. Oh, I guess no JIT, if you're not using variables, it's gonna be slow no matter what. But, like, I do want to write this schedule cache. So the schedule cache should be able to cache entire schedules, and uh.. that will give you, like, half of the JIT behavior for free.

##### **Geohot** [[00:29:03](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1743)]
Yeah, I understand. Yeah. Um.. I don't know.

##### **Geohot** [[00:29:07](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1747)]
I mean, that's one of my, like.. There's a whole bunch of refactors that can be done here. Like, I want to move more stuff to mixins.. Um.. And, like, really make that code good. There's definitely a path now. It's nice how, like, everything is uops. Uops are pure. I think that, like, the old scheduler, you couldn't touch it. The new scheduler, you can touch it. It all kind of behaves how you think it should. It's been a long time since I've hit something where I'm just, like.. I literally have no idea how to do this refactor. There's so many weird broken things. I think we're mostly past that now. And pretty much every time I'm like, oh, I want to refactor, like, you know, the pad op to not pad both sides. Okay, cool. That's going to take me an hour. Like, that's not even.. All that stuff kind of works now. So, that's pretty good. Um, but yeah. So I think that a lot of polish can be done by moving stuff to, like, mixins. And then once that's done, we can look at tensor.py and be like, oh yeah, now the schedule cache is, like, really easy to write. It's just, like, one little thing in there. Um.. And then also refactoring the JIT. The JIT right now, uh, confuses two concerns. It confuses this concern of capturing a function with applying the graph. So we have these graph things on GPUs, which are more like cached command buffers, but that really has nothing to do with the JIT. Uh, so we should separate out all the cached command buffer code. This gets into, like, the HCQ refactors. There's a lot of stuff that can be done there, too. Um, I think that a common feature that we get a lot of requests for is being able to really nicely export those things and play them back later. Kind of what commas compile 3 is doing. Um.. J. Suarez was asking for it. Like, just this idea that you can just export a JIT really nicely, not some weird pickle format. So, yeah. We can get there. It's on the priority list. But, uh, yeah. We can decide where it is on the priority list.

##### **Chenyu** [[00:30:56](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=1856)]
Oh, yeah. So another small thing to add is I was trying to simplify all the symbolic stuff, or I guess in general, a lot of the rewrites. Uh, it's.. There are hidden complexity about the older ones. There are a lot of things. And sometimes you need to add symbolic to a device renderer extra matter. Sometimes you really don't because sometimes you explicitly want something to not be rewrit. An example is, for example, for FP8 in AMD, uh, if you do an FP8 cast, we really want it to be cast to float first then to your whatever, BFloat 16 or something like that. So.. I think there are a lot of uh.. I tried, like, whopping the older or changed some rules here and there and something would just subtly break and that really is, like, impossible to maintain. Yeah, sometimes I hope I can.. Basically two things here. One is I root-caused the issue with the conf that's not compatible with the very last uh, VADDIHACK image thing. So hopefully I will have some solutions soon. Then another is I think we can better categorize these rules as, uh, some rules that strictly remove certain uops and return you something that's from its source. There are some rules that gives you uh, maybe gives you a const at the end and nothing else. And there are rules just reassemble stuff. I think instead of saying this is simple, this is symbolic, and this is sim, uh, having some understanding for, like, how to categorize this will help. And eventually we can decide, like, in what stages you use which one and, uh, it's like, some of these should always be safe to attach if you choose so. And some of these should be explicitly set, say for example your extra metric in the render. Uh, if you want to add some other symbolic rules you specify there and not in the main code gen loop. Something like that. For now people just, like, add another thing very, uh, freely and we can make like, your vector list pretty hard.

##### **Geohot** [[00:33:22](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2002)]
Yeah, I really like that idea. I think that our names are total nonsense. Symbolic, simple, symbolic. I know you could finally get rid of symbolic, flat, and then sim. Yeah, these names, yeah, these need to be named things like, like, there's probably, ChatsGPT will probably come up with great names for, like,

##### **Chenyu** [[00:33:39](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2019)]
I think, I think other from work. I don't know, I have an idea for the strictly return your source. So basically strictly remove, removing stuff. And they have one that's kind of give you a similar one and another one that's like, uh, rearranging stuff basically. I think that's

##### **Geohot** [[00:34:01](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2041)]
the idea. Yeah, we also, how much would eGraphs help? I don't know. I mean, there's some stuff,

##### **Geohot** [[00:34:13](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2053)]
if you're struggling with stuff that like, oh, like, different orders do different things.

##### **Chenyu** [[00:34:18](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2058)]
So for now, I don't really struggle with ordering, but it's just, for some device, extra metro renderers, it has, it kind of assumes you shouldn't do something to mess around with your rules. Because those assumptions are not explicitly set, and a lot of time not even tested. The reason I find it is I tried process replay, and I changed the order and see a diff in one of the kernel.

##### **Geohot** [[00:34:45](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2085)]
So I think that's the hard part. Yeah, I mean, I think that like,

##### **Geohot** [[00:34:55](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2095)]
the thing that you really want eGraphs for is things like factorization. Like try factoring and unfactoring things and seeing if you can get things to match and things to cancel out. But it's all a pretty simple addition on top of what we have. But you know, I mean, I really like this idea of like making a taxonomy of the symbolically right rules and just moving some to like the yeah, you're right, this is only going to either remove things or replace things with a const. Removes things, replaces things with a const, does other weird things.

##### **Geohot** [[00:35:28](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2128)]
Next.

##### **Chenyu** [[00:35:30](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2130)]
Some ideas for assembler?

##### **Geohot** [[00:35:33](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2133)]
Yeah, yeah, so you know, it's going to be a slow project. I posted that thing in announcements. I think it's like with this SQTT stuff, we're now working on the like the bottom and the top and then there's this LLVM in the middle, which kind of can ruin everything you did. Like it can make all these changes. So we do have to move to assembly. We have to remove LLVM. I think RDNA3 is the place to do it. We need to be able to tie each UI swap to what runs on the GPU. So yeah, you know, it's going to be a slow process. I'm going to work on it maybe a day a week, two days a week for the next three months and then we'll have some nice baseline assembler, disassembler and then I also want it to be a cycle accurate emulator. So for each instruction, I don't just want to have a like how to transform this into a string and back to something else. I want to say what this actually does. So how it updates the VGPRs and stuff, but also how many cycles it takes and what GPU resources it uses and we can validate all this with SQTT. So SQTT will show us when the instruction got dispatched and when the instruction actually ran and these things are mostly pretty simple. I think it should be pretty easy to make like a little model of a GPU. Modeling the memory system is probably more difficult, but modeling the ALU should be pretty easy. And then we can like, yeah, no for this chunk ALUs okay, are there going to be stalls here or not? None. And LLVM seems pretty unaware of a lot of this stuff. You can look at the code outputted by LLVM and there's ALU stalls and they're just nonsense. Like just simple reorderings would fix it. So I think the best thing to do though is to not try to fix it. It's just to never emit code that does this. Like the this gets into like what the de-vectorizer is, right? Like the de-vectorizer the order of the de-vectorizer and how the de-vectorized stuff is emitted to assembly matters a ton for avoiding ALU stalls.

##### **Geohot** [[00:38:08](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2288)]
So, yeah. The slow process of assembly,

##### **Geohot** [[00:38:12](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2292)]
adding assembly. I think RDNA3 is a good first target. It's documented. We know the most

##### **Geohot** [[00:38:17](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2297)]
about it. We have a lot of it. It's a GPU. It's mostly what you want. Sounds good.

##### **Chenyu** [[00:38:37](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2317)]
Oh, I see B1G is here. You want to share something? Standing on MI300X I saw you hit the device hand.

##### **B1tg** [[00:38:49](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2329)]
Yeah. I was still blocking by the GPU hands on MI350. And it also happened on the MI 300. I posted the reproduced script in the MLPath channel.

##### **Geohot** [[00:39:15](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2355)]
Nimogen, can you look at this? This is top priority. We need to get this stuff fixed.

##### **Nimlgen** [[00:39:21](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2361)]
Thank you.

##### **Geohot** [[00:39:23](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2363)]
Yeah, make sure. If you have any problems reproducing it, just let me know.

##### **Chenyu** [[00:39:28](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2368)]
I see the arrow screenshot, but I don't see the reproduced.

##### **B1tg** [[00:39:32](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2372)]
Just run the dev run message. In the master branch, if the GPU numbers bigger than

##### **Geohot** [[00:39:49](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2389)]
1, this can trigger the bug. Okay. Sounds good. And do you know if this is running AMD, right? Okay. It's running AMD backend.

##### **Qazalin** [[00:40:16](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2416)]
Okay.

##### **Geohot** [[00:40:17](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2417)]
MI350 the same

##### **Chenyu** [[00:40:19](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2419)]
MMU fault and on MI300 this Yeah, the

##### **B1tg** [[00:40:26](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2426)]
error message in the team message looks exactly the same.

##### **Geohot** [[00:40:31](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2431)]
I see. Okay.

##### **B1tg** [[00:40:37](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2437)]
And another thing I want to ask is, is there any way we can write no grade in tiny grade?

##### **Chenyu** [[00:40:49](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2449)]
What do you mean by that?

##### **B1tg** [[00:40:52](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2452)]
Because when I in the FP8 linear, I quantize the input and weight to FP8 and do the metmail. Okay. So in the backward function, I need to ignore the clamp and MX to make it not infect the

##### **Geohot** [[00:41:29](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2489)]
I think

##### **Chenyu** [[00:41:31](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2491)]
for now, if you want to ignore certain part of the auto gradus, probably better to use custom.

##### **B1tg** [[00:41:39](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2499)]
Yeah. Now I just write custom forward function and write custom backward function to set the gradient to none.

##### **Chenyu** [[00:41:57](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2517)]
I don't think we have currently anything look like that. Basically

##### **B1tg** [[00:42:05](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2525)]
So I need to write custom function.

##### **Chenyu** [[00:42:09](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2529)]
Yeah, I think to start with as a custom and we can think about what the API should look like because CAS is especially for small d-type. It's weird. FBA, they sometimes also use different FP8 for forward and backward because the scale is different. So for now, if the custom works, let's start with that. And if that doesn't work, just post the issue somewhere.

##### **Qazalin** [[00:42:40](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2560)]
Okay.

##### **B1tg** [[00:42:41](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2561)]
Also the client function client function's backward behavior not the same as touch. Client function Client function when a client function was become max of in tiny grad. So when it hits the edge value, the mean of the max value, it gives the gradient 0.5. 0.5.

##### **SPEAKER_02** [[00:43:23](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2603)]
0.5. 0.5.

##### **B1tg** [[00:43:25](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2605)]
0.5. But in touch, it's behavior difference. I think for the Do we want to match the touch behavior? I think generally yes.

##### **Chenyu** [[00:43:39](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2619)]
So for like for API returning different number or for its backward, it hits differently. You don't need to wait until the meeting. You can just open the issue and I think the idea is unless Torch does something very weird that we don't want to copy or the values or the backward behaviors we probably want to follow. So anytime we find a difference, it's either we explicitly say we behave differently or it's a bug and we want to match.

##### **Qazalin** [[00:44:21](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2661)]
Okay.

##### **Geohot** [[00:44:23](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2663)]
Cool. Yeah, these

##### **Chenyu** [[00:44:25](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2665)]
like have like the average of the two or the max of the two because I think Torch's principle is to use subgradient. We are kind of ad hoc. So it's very possible that we don't write some of these are things like matching the Torch and we probably

##### **Geohot** [[00:44:47](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2687)]
should. So it's good that we are finding these. What else?

##### **Chenyu** [[00:44:59](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2699)]
I see Flemeth. Flemeth, you want to say something about your past memo?

##### **Geohot** [[00:45:03](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2703)]
Yeah, I was just going to bring that up. I had to use a speaker. But you have to exit and re-

##### **Geohot** [[00:45:07](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2707)]
enter if you want to talk. Okay. Can you hear me? Yes.

##### **Geohot** [[00:45:19](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2719)]
So there's a draft version of UOP generated max GEMM kernels. They're a little slower than the hand-coded ones. And obviously the C style changes can't stay there. But surprisingly,

##### **Geohot** [[00:45:39](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2739)]
it's correct and it works. So it's a good thing. Yeah, I'm looking at your C style changes.

##### **Geohot** [[00:45:48](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2748)]
What are they doing that you can't do with or you're using LD matrix?

##### **Geohot** [[00:45:54](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2754)]
Yeah, it doesn't need to use that, obviously. But it doesn't need to use any code was. No, you can. I think you can issue for four loads. And it's equivalent. I mean, it should definitely be the same thing.

##### **Geohot** [[00:46:08](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2768)]
Cool. Yeah. I mean, the speeds on that look great. The testing the the testing the testing the the the the the the the the the

##### **Geohot** [[00:46:41](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2801)]
You basically move a lot of that complexity just into generating the right UOP structure, the swizzling, but it renders properly. So that's a start.

##### **Geohot** [[00:46:54](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2814)]
Great. How have you found the UOP programming language?

##### **Geohot** [[00:47:02](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2822)]
The agents have helped more. So I'm only starting to understand what's going on.

##### **Geohot** [[00:47:09](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2829)]
I mean, you're doing a lot of stuff. I see, I see. I mean, when you write something like that, you don't have to write that. That's equivalent to just saying, all of the beauty of TinyGrad should work in UOPs.

##### **Geohot** [[00:47:24](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2844)]
You can just do that.

##### **Geohot** [[00:47:30](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2850)]
Right. Yeah, I mean, this is, again, this is why this is a draft proof of concept. I was trying to get it to pass the test. Yeah, yeah, yeah. I mean, I'm glad it works. I'm glad it works properly.

##### **Geohot** [[00:47:44](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2864)]
Yeah. No, and it's great that we can show that the, like, the linearizer and all the output stuff works. But yeah, no, I think there's a ton of cleanup to this, and it could be really good, and we could maybe even almost ship it.

##### **Geohot** [[00:48:00](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2880)]
Yeah. I mean, it obviously doesn't use the linearizer, right? Wait.

##### **Geohot** [[00:48:07](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2887)]
Oh, it doesn't use the linearizer. Oh, you're just concatting. You're just.. Yeah. Yeah.

##### **Geohot** [[00:48:13](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2893)]
Any reason you can't use the linearizer?

##### **Geohot** [[00:48:20](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2900)]
Well, that's.. I'm not sure. Again, I don't know how the copy.. I don't know how the async stuff with the pipe commits and the weights would get pushed up that far on all the pipelining. I just don't know.

##### **Geohot** [[00:48:39](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2919)]
It should.. It should mostly work. I think you'd be surprised how good the linearizer is, especially when we fix after end. Yeah, there's just.. Basically, there's a function called after, and you have to use that. So after will.. Will, like.. Like, if you want a buffer after a store happened, you just do, like, buff.after the store. And that promises you that the store happened before that buffer.

##### **Geohot** [[00:49:10](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2950)]
Is returned to you.

##### **Geohot** [[00:49:13](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2953)]
But yeah, that after should let you do all the pipelining stuff and all the async stuff, too.

##### **Geohot** [[00:49:22](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2962)]
Yeah, sounds good. I mean, again, I just wanted to close it up there to see. It's like, it's doable.

##### **Geohot** [[00:49:28](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2968)]
It's just a matter of, you know, starting to lift it higher on the stack.

##### **Qazalin** [[00:49:32](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2972)]
Cool. Okay.

##### **Geohot** [[00:49:38](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2978)]
Sounds good.

##### **Chenyu** [[00:49:44](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2984)]
Do you have anything to summarize for your discussion between the buffer guy?

##### **Geohot** [[00:49:57](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=2997)]
Not particularly. I mean, he's complaining about the state of the documentation.

##### **SPEAKER_02** [[00:50:01](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=3001)]
Yes.

##### **Geohot** [[00:50:02](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=3002)]
Yeah, and the state of the error messages. I mean, those things aren't good. It's not 1.0 yet. He says a bunch of the current.. The kernels are faster, which is good. He wants aggregation in the profiler. Kwaslin, I don't know what, like, other profilers have for this. If there's some, like, obvious features that, like, every profiler has that we don't, we should add them.

##### **Chenyu** [[00:50:26](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=3026)]
One thing is for a profiler, I never understand, when does the profiling stop? It gives me a very long timeline that I can scroll.

##### **Geohot** [[00:50:36](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=3036)]
Our profiling never stops. What do you mean? Why do you want it to stop? It should.

##### **Chenyu** [[00:50:40](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=3040)]
No, no, I mean, the end of my program and the profiler starts, right? So how long does it take for my program to finish?

##### **Geohot** [[00:50:49](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=3049)]
Something like that? What do you mean? Just press space and you see the, like, whole graph. Yeah, if you press space, it'll zoom to that. Yeah. But you can zoom to everywhere you want. I don't want to limit you on that.

##### **Geohot** [[00:51:06](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=3066)]
Yeah, I think being able to zoom forever on both sides is totally fine. I mean, it's the same as the graph, right? Like, in theory, you can zoom out and make it super tiny.

##### **Qazalin** [[00:51:15](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=3075)]
Yeah.

##### **Geohot** [[00:51:16](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=3076)]
But I'm not understanding. Like, is that what you mean? If you just hit space, whatever the last thing, whatever the right side is there, that should be good.

##### **Chenyu** [[00:51:24](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=3084)]
Maybe we'll just, I'll try it later.

##### **Geohot** [[00:51:28](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=3088)]
Yeah, I don't know about these aggregate timer results over many calls to the same kernel after warmup. I'm curious, I've never, like, seen that in the Torch profiler. I've never used that in the Torch profiler either. I've just seen the Torch profiler show me all the steps. But yeah, I mean, if there's something obvious that we're missing. Yeah, and then the index set operations, like, he's using, like, a normal experience replay bot for an RL. I think that's mostly what I'm going to work on this week, which is also the same stuff that we need for, it's slice to sign, basically. It's like making slice to sign good in my user realize, which I think we can do.

##### **Geohot** [[00:52:07](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=3127)]
That's good. I think that's pretty much it for this meeting.

##### **Geohot** [[00:52:17](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=3137)]
I like this stuff. Error messages in general are not super helpful. You tend to hit internals a lot. Not a deal breaker since Torch sucks worse in compile mode. So.

##### **Qazalin** [[00:52:26](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=3146)]
Yep.

##### **Geohot** [[00:52:29](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=3149)]
Yeah. Yeah. I mean, that's been my experience with Torch compile too. Like, if it works, it's great. But if it doesn't work, good luck. I don't like the Enneagram. Oh. No. TinyGrad is fixable.

##### **Geohot** [[00:52:42](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=3162)]
It's just the error message isn't what you want. Like, Torch you actually can't fix. TinyGrad, yes. You can't fix it in five minutes like you could if the error message was good,

##### **Geohot** [[00:52:55](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=3175)]
but you can fix it in an hour. Yeah. I think we just have many stuff that currently is very hard for a user to fix.

##### **Chenyu** [[00:53:06](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=3186)]
It might be relatively easy for a dev team. Yes.

##### **Geohot** [[00:53:11](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=3191)]
Yes. When I say an hour, you're going to have to look at the TinyGrad code. But when you look at a TinyGrad code, you can look at the TinyGrad code, which is try to understand how Torch compile works. Good luck.

##### **Qazalin** [[00:53:24](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=3204)]
Yeah.

##### **Geohot** [[00:53:27](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=3207)]
Oh, I wouldn't have expected TF32 to have only been in mvars. I don't know if we can do something about that.

##### **Geohot** [[00:53:34](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=3214)]
I mean, I think it's only in mvars and Torch too. I don't know. I mean, yeah, the TF32 thing.

##### **Geohot** [[00:53:49](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=3229)]
Oh, I guess one more thing. I want to get that process replay thing merged. Do we ever get that merged? The subactions?

##### **Qazalin** [[00:54:00](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=3240)]
No. There's like three other refactors that you have to do.

##### **Geohot** [[00:54:06](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=3246)]
Well, one of those is the TF32. Yeah. And I'd like to. I'd like to fix that.

##### **Geohot** [[00:54:16](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=3256)]
Also, device count. Core ID still there? Which one? We still have core ID. Core ID?

##### **Geohot** [[00:54:26](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=3266)]
Oh, core ID in the C style. Yeah, yeah, that's got to go. That bothers me every time I see it, especially when I'm not using it.

##### **Geohot** [[00:54:38](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=3278)]
Yeah.

##### **Qazalin** [[00:54:38](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=3278)]
We just have three things that aren't. We're pretty usable. And those require refactors elsewhere. I tried doing TF32. I got bugs with things wanting tensor core but not getting tensor core. Oh, I see. Yeah. And for the compiler selection stuff, we do that on init. So if you set a context with CPU LLVM, it doesn't respect that. It just uses Clang.

##### **Geohot** [[00:55:09](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=3309)]
Yeah. We have to fix that. Yeah. No, but they're all good refactors that we should make anyway. And they're all surfacing real bugs. So yeah.

##### **Geohot** [[00:55:18](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=3318)]
Whoever wants to take one of them. I could take the TF32 one. I know what to do for that one. CPU count, I don't know. Oh, cool.

##### **Qazalin** [[00:55:38](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=3338)]
See? Yeah.

##### **Geohot** [[00:55:40](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=3340)]
Sounds good. I think that's it for this meeting. Great. December already. Yeah. Adventical. Let's train LLMA. Let's train LLMA. End of the year.

##### **Geohot** [[00:55:54](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=3354)]
We're going to have state of the art flash attention on LA350, as promised.

##### **Geohot** [[00:55:59](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=3359)]
Cool.

##### **Chenyu** [[00:56:01](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=3361)]
OK, thank you, everyone.

##### **Geohot** [[00:56:02](https://www.youtube.com/watch?v=S7w_cqqW8BM&t=3362)]
See you next week. Bye.
