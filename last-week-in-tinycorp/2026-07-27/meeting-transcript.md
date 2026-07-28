# 2026-07-27 Meeting

### Meeting Agenda

**Time:** new meeting #30, 7/27  9am Monday San Diego time
- company update
- gpt-oss training
- tensor mixin done, expand, weak dtype
- SLICE, Program class, pytest timeout
- hcq2
- LOOP, COPY, multi
- viz llama training
- bounties, issues, comma happiness, kimi


### Audio

[Youtube Link](https://www.youtube.com/watch?v=J4bJVnAjntU)

### Highlights

- **[Company Update](#geohot-000002)**: AMD relations are progressing after the conference, a larger deal is moving forward, and MI350P cards are expected soon for faster CDNA4 kernel prototyping; fast cross-CU synchronization remains a key obstacle for mega kernels.
- **[GPT-OSS Training](#wozeparrot-000141)**: A GPT-OSS training run converged at roughly 2.5 seconds per step, but unnecessary MoE activation copying and routing dominate runtime; the target is 540 milliseconds, with a redesigned MoE GEMM kernel planned for master.
- **[Tensor Mixin and Weak Dtypes](#chenyu-000639)**: EXPAND was made implicit so WHERE works cleanly at both tensor-graph and late-UOp levels, while constants are being converted to weak integer, weak float, or boolean dtypes throughout the pipeline.
- **[Torch Backend and Chestnut Release](#chenyu-001046)**: The Torch backend is approaching `torch.compile` support despite several discovered bugs, and the next tinygrad release is planned alongside Chestnut with merged LLM speedups and benchmark results.
- **[SLICE and TinyELF](#chrism-001203)**: SLICE is nearly complete, with 64-bit UOp variables as the remaining issue; the new `TinyELF` program representation has already merged, and buffer offsets are being moved out of the Buffer abstraction.
- **[HCQ2 Compile-Time Blocker](#nimlgen-001814)**: The CPU backend has moved into UOps, while HCQ2 is primarily blocked by enormous generated C patching programs; the proposed direction is to factor repeated PM4 generation into parameterized CALLs or functions and use scatter-like runtime patching.
- **[LOOP Added with Strong Warnings](#geohot-004103)**: LOOP was introduced through an unbounded RANGE with an END termination condition, making it Turing complete; it is intended mainly for scoped polling of device state and should be avoided for ordinary finite computation.
- **[COPY Lowered to STORE](#geohot-004435)**: COPY now lowers to an anonymous STORE, allowing identical copies to deduplicate and removing COPY handling from rangeify; executable copies can later be assigned to SDMA, compute units, or even another device.
- **[MULTI as Top-Down Rangeify](#geohot-004633)**: MULTI will be generalized into top-down rangeify, propagating a device or execution-stage RANGE through the graph and automatically inserting an all-reduce whenever that RANGE reaches a REDUCE.
- **[AMD Machine Performance](#qazalin-004935)**: Running AMD’s own Docker image on the team’s machine was about 16 minutes, or 10%, slower than AMD’s submission; the current diagnosis centers on intake temperature and package-power limits reducing sustained clocks.
- **[FP4 Training Optimization](#qazalin-005446)**: MXFP4 training currently takes about three hours even though its GEMMs reach roughly five petaflops, indicating other inefficient kernels are responsible; the team plans to beat AMD’s FP8 result using FP4.
- **[AMD Assembly Backend](#raine-005900)**: The new backend is running on hardware with tensor cores working and roughly ten tests still failing; correctness, WMMA support, and simple grouped `waitcnt` handling are prioritized over dual-issue and intricate performance passes.
- **[Comma and IR3 Performance](#chrism-010711)**: Comma is considering IR3, but its RL model is slowed by a CONCAT kernel that fuses around ten differently shaped GEMMs; adding CONTIGUOUS to large groups of inputs is being considered as a generic OpenPilot rangeify workaround.

### Transcript
##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=J4bJVnAjntU&t=0)]
Let's start with the company update.

##### **Geohot** [[00:00:02](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2)]
It's new meeting 30. Yeah. We did the AMD conference

##### **Geohot** [[00:00:09](https://www.youtube.com/watch?v=J4bJVnAjntU&t=9)]
last week. We got a nice LEGO set.

##### **Geohot** [[00:00:12](https://www.youtube.com/watch?v=J4bJVnAjntU&t=12)]
AMD likes us. This is good. It's good. Progress on the big deal.

##### **Geohot** [[00:00:19](https://www.youtube.com/watch?v=J4bJVnAjntU&t=19)]
We're hopefully going to get MI350P cards soon as well. We'll be able to prototype the CDNA4 kernels on machines that boot fast.

##### **Geohot** [[00:00:31](https://www.youtube.com/watch?v=J4bJVnAjntU&t=31)]
And

##### **Geohot** [[00:00:33](https://www.youtube.com/watch?v=J4bJVnAjntU&t=33)]
nothing else. Too much happened.

##### **Geohot** [[00:00:36](https://www.youtube.com/watch?v=J4bJVnAjntU&t=36)]
A lot of people are interested in mega kernels and ways to

##### **Geohot** [[00:00:41](https://www.youtube.com/watch?v=J4bJVnAjntU&t=41)]
synchronize

##### **Geohot** [[00:00:42](https://www.youtube.com/watch?v=J4bJVnAjntU&t=42)]
between CUs fast. This seems to be the limiting factor of mega kernels because it uses atomics and they're really slow.

##### **Geohot** [[00:00:51](https://www.youtube.com/watch?v=J4bJVnAjntU&t=51)]
A lot of people are talking about lots of different kinds of parallelism: expert parallelism, data parallelism, tensor parallelism, pipeline parallelism. Hopefully we build a framework that just kind of incorporates all of that.

##### **Geohot** [[00:01:09](https://www.youtube.com/watch?v=J4bJVnAjntU&t=69)]
Yeah. That's kind of it.

##### **Geohot** [[00:01:11](https://www.youtube.com/watch?v=J4bJVnAjntU&t=71)]
Good.

##### **Chenyu** [[00:01:16](https://www.youtube.com/watch?v=J4bJVnAjntU&t=76)]
Great. Sounds good. I think we'll also know better once we have different kinds

##### **Chenyu** [[00:01:20](https://www.youtube.com/watch?v=J4bJVnAjntU&t=80)]
of things running using different parallelism.

##### **Chenyu** [[00:01:25](https://www.youtube.com/watch?v=J4bJVnAjntU&t=85)]
Was that it? Let's move on to GPT-OSS training.

##### **Wozeparrot** [[00:01:32](https://www.youtube.com/watch?v=J4bJVnAjntU&t=92)]
I mean, hopefully we don't need to use any other parallelism for GPT-OSS other than data parallel.

##### **Geohot** [[00:01:37](https://www.youtube.com/watch?v=J4bJVnAjntU&t=97)]
Oh yeah, for training it should be good. Yeah.

##### **Wozeparrot** [[00:01:41](https://www.youtube.com/watch?v=J4bJVnAjntU&t=101)]
So we have a trained run.

##### **Wozeparrot** [[00:01:45](https://www.youtube.com/watch?v=J4bJVnAjntU&t=105)]
Converged run.

##### **Wozeparrot** [[00:01:48](https://www.youtube.com/watch?v=J4bJVnAjntU&t=108)]
It is at 2.5 seconds a step. And then I posted the correct step breakdown. Most of it is just MoE routing.

##### **Geohot** [[00:01:58](https://www.youtube.com/watch?v=J4bJVnAjntU&t=118)]
What do you mean by routing?

##### **Geohot** [[00:02:00](https://www.youtube.com/watch?v=J4bJVnAjntU&t=120)]
What do you mean by most of it?

##### **Wozeparrot** [[00:02:03](https://www.youtube.com/watch?v=J4bJVnAjntU&t=123)]
There's a lot of time currently wasted in MoE routing. Per token, you have to get the top four, run the MoE router, and then run the gradient.

##### **Chenyu** [[00:02:12](https://www.youtube.com/watch?v=J4bJVnAjntU&t=132)]
Oh, maybe it's a good idea to rewrite gather using INDEX now.

##### **Chenyu** [[00:02:18](https://www.youtube.com/watch?v=J4bJVnAjntU&t=138)]
Would it be slow?

##### **Geohot** [[00:02:18](https://www.youtube.com/watch?v=J4bJVnAjntU&t=138)]
What does MoE routing even mean? It's on the same GPU, right? It's not like we have any expert parallelism.

##### **Wozeparrot** [[00:02:25](https://www.youtube.com/watch?v=J4bJVnAjntU&t=145)]
Yeah, no expert parallelism. It's just...

##### **Wozeparrot** [[00:02:30](https://www.youtube.com/watch?v=J4bJVnAjntU&t=150)]
The way that's currently written is a pretty slow pattern. Fairly slow.

##### **Wozeparrot** [[00:02:36](https://www.youtube.com/watch?v=J4bJVnAjntU&t=156)]
It's a huge copy basically because you're copying the...

##### **Wozeparrot** [[00:02:43](https://www.youtube.com/watch?v=J4bJVnAjntU&t=163)]
activation.

##### **Geohot** [[00:02:45](https://www.youtube.com/watch?v=J4bJVnAjntU&t=165)]
The activation or the weights?

##### **Wozeparrot** [[00:02:49](https://www.youtube.com/watch?v=J4bJVnAjntU&t=169)]
Because of the MoE kernel, you have to group by expert. You essentially have to do a sort.

##### **Wozeparrot** [[00:02:55](https://www.youtube.com/watch?v=J4bJVnAjntU&t=175)]
Then you copy the activations.

##### **Geohot** [[00:03:00](https://www.youtube.com/watch?v=J4bJVnAjntU&t=180)]
You copy the activations. I see why you have to do a sort.

##### **Wozeparrot** [[00:03:02](https://www.youtube.com/watch?v=J4bJVnAjntU&t=182)]
Yeah.

##### **Geohot** [[00:03:06](https://www.youtube.com/watch?v=J4bJVnAjntU&t=186)]
But why do you have to copy the activations?

##### **Wozeparrot** [[00:03:10](https://www.youtube.com/watch?v=J4bJVnAjntU&t=190)]
No, just right now tinygrad is generating a bunch of COPY kernels that are not needed.

##### **Geohot** [[00:03:14](https://www.youtube.com/watch?v=J4bJVnAjntU&t=194)]
Yeah, but are you sure it's the activations being copied? That doesn't make sense. I understand why the gem might... What?

##### **Wozeparrot** [[00:03:22](https://www.youtube.com/watch?v=J4bJVnAjntU&t=202)]
It is copying the activations. But what should happen is the MoE kernel should just read the list of indexes.

##### **Wozeparrot** [[00:03:32](https://www.youtube.com/watch?v=J4bJVnAjntU&t=212)]
It's because

##### **Wozeparrot** [[00:03:33](https://www.youtube.com/watch?v=J4bJVnAjntU&t=213)]
right now the way the MoE GEMM kernel is written is that it expects stuff to be bucketed already.

##### **Geohot** [[00:03:41](https://www.youtube.com/watch?v=J4bJVnAjntU&t=221)]
It expects stuff to be bucketed. But I still don't understand why it's copying the activations. I would understand why it was copying the weights because the weights it would change is based on what expert you select.

##### **Geohot** [[00:04:01](https://www.youtube.com/watch?v=J4bJVnAjntU&t=241)]
If it's really just gathering the... It's really just copying the activations. I think that's a bug.

##### **Geohot** [[00:04:07](https://www.youtube.com/watch?v=J4bJVnAjntU&t=247)]
Yeah, I have a question. I think you're doing a SLICE, right? You're slicing this and passing it to the GEMM.

##### **Wozeparrot** [[00:04:18](https://www.youtube.com/watch?v=J4bJVnAjntU&t=258)]
No, it is a gather over the activations. It is just a poorly written MoE GEMM kernel. I have a newer one that I'm testing that's a little bit more complex. It basically gets rid of all the MoE routing.

##### **Geohot** [[00:04:30](https://www.youtube.com/watch?v=J4bJVnAjntU&t=270)]
I see.

##### **Geohot** [[00:04:32](https://www.youtube.com/watch?v=J4bJVnAjntU&t=272)]
Okay, yeah. I guess I don't exactly understand why it's the activations.

##### **Geohot** [[00:04:36](https://www.youtube.com/watch?v=J4bJVnAjntU&t=276)]
Yeah, if you think you know how to fix that... I think before we start trying to make the GEMMs faster,

##### **Geohot** [[00:04:43](https://www.youtube.com/watch?v=J4bJVnAjntU&t=283)]
those first three categories just look like stupid.

##### **Wozeparrot** [[00:04:47](https://www.youtube.com/watch?v=J4bJVnAjntU&t=287)]
Yeah, a lot of it is kind of stupid.

##### **Wozeparrot** [[00:04:51](https://www.youtube.com/watch?v=J4bJVnAjntU&t=291)]
And then, yeah, those first three...

##### **Wozeparrot** [[00:04:56](https://www.youtube.com/watch?v=J4bJVnAjntU&t=296)]
A lot of that reduce bucket is sliding-window attention because our Flash Attention kernel doesn't support that yet.

##### **Geohot** [[00:05:05](https://www.youtube.com/watch?v=J4bJVnAjntU&t=305)]
Oh, I see. That should be faster, though.

##### **Wozeparrot** [[00:05:09](https://www.youtube.com/watch?v=J4bJVnAjntU&t=309)]
Cool.

##### **Geohot** [[00:05:10](https://www.youtube.com/watch?v=J4bJVnAjntU&t=310)]
Is this in master?

##### **Wozeparrot** [[00:05:14](https://www.youtube.com/watch?v=J4bJVnAjntU&t=314)]
I have one more thing left to merge into master, and it's the big MoE GEMM kernel. I still need to clean that up, and then I should merge it sometime early this week.

##### **Chenyu** [[00:05:25](https://www.youtube.com/watch?v=J4bJVnAjntU&t=325)]
And can I run this with the NULL backend

##### **Chenyu** [[00:05:27](https://www.youtube.com/watch?v=J4bJVnAjntU&t=327)]
to see how much RAM and how many kernels it uses?

##### **Wozeparrot** [[00:05:31](https://www.youtube.com/watch?v=J4bJVnAjntU&t=331)]
It should be possible.

##### **Chenyu** [[00:05:36](https://www.youtube.com/watch?v=J4bJVnAjntU&t=336)]
Once

##### **Chenyu** [[00:05:36](https://www.youtube.com/watch?v=J4bJVnAjntU&t=336)]
you

##### **Chenyu** [[00:05:37](https://www.youtube.com/watch?v=J4bJVnAjntU&t=337)]
have that, it's probably a good idea to put that on CI or something.

##### **Geohot** [[00:05:42](https://www.youtube.com/watch?v=J4bJVnAjntU&t=342)]
So what step time do we need?

##### **Wozeparrot** [[00:05:45](https://www.youtube.com/watch?v=J4bJVnAjntU&t=345)]
0.5? We need 540 milliseconds.

##### **Geohot** [[00:05:49](https://www.youtube.com/watch?v=J4bJVnAjntU&t=349)]
540 milliseconds. Okay, so if we just delete

##### **Geohot** [[00:05:51](https://www.youtube.com/watch?v=J4bJVnAjntU&t=351)]
the three stupid things, it seems kind of good.

##### **Wozeparrot** [[00:06:00](https://www.youtube.com/watch?v=J4bJVnAjntU&t=360)]
540. Does that get us there?

##### **Wozeparrot** [[00:06:03](https://www.youtube.com/watch?v=J4bJVnAjntU&t=363)]
Probably not, but

##### **Wozeparrot** [[00:06:04](https://www.youtube.com/watch?v=J4bJVnAjntU&t=364)]
that's a good start. 300 milliseconds of not accounted for time.

##### **Geohot** [[00:06:09](https://www.youtube.com/watch?v=J4bJVnAjntU&t=369)]
Oh, well, yeah, I don't know where that time's going to. That's more stupid time.

##### **Chenyu** [[00:06:12](https://www.youtube.com/watch?v=J4bJVnAjntU&t=372)]
We can also make the machine cooler.

##### **Geohot** [[00:06:16](https://www.youtube.com/watch?v=J4bJVnAjntU&t=376)]
Oh, that's questionable. Well, it may not be doable. And also, that may not even really be the problem. We'll get to that one. Yeah, we'll get to that.

##### **Chenyu** [[00:06:25](https://www.youtube.com/watch?v=J4bJVnAjntU&t=385)]
Sounds like good progress.

##### **Chenyu** [[00:06:28](https://www.youtube.com/watch?v=J4bJVnAjntU&t=388)]
Anything else?

##### **Wozeparrot** [[00:06:30](https://www.youtube.com/watch?v=J4bJVnAjntU&t=390)]
No.

##### **Chenyu** [[00:06:32](https://www.youtube.com/watch?v=J4bJVnAjntU&t=392)]
Here we go.

##### **Chenyu** [[00:06:34](https://www.youtube.com/watch?v=J4bJVnAjntU&t=394)]
Okay. Next is my stuff.

##### **Chenyu** [[00:06:39](https://www.youtube.com/watch?v=J4bJVnAjntU&t=399)]
So for the tensor mixin, I moved the last thing into WHERE. I really forget what the other one was, but WHERE was the last one.

##### **Chenyu** [[00:06:53](https://www.youtube.com/watch?v=J4bJVnAjntU&t=413)]
That was done by fixing EXPAND so it doesn't expand all the time, basically making it implicit. So WHERE works nicely at the tensor graph level and in the late UOp level.

##### **Chenyu** [[00:07:11](https://www.youtube.com/watch?v=J4bJVnAjntU&t=431)]
Most of the time was spent working on weak dtypes. The current progress is

##### **Chenyu** [[00:07:18](https://www.youtube.com/watch?v=J4bJVnAjntU&t=438)]
in the things that are merged already.

##### **Chenyu** [[00:07:22](https://www.youtube.com/watch?v=J4bJVnAjntU&t=442)]
If you look at `dtype_from_uop`,

##### **Chenyu** [[00:07:26](https://www.youtube.com/watch?v=J4bJVnAjntU&t=446)]
`dtype_from_uop` reads a CONST and infers its dtype as weak int, weak float, or bool directly from its argument. We have another function called `dtypes.from_py`, which is the interface between a Python constant and a Tensor constant, that I also flipped to use weak dtypes and bool. What's remaining in our pipeline that still generates a non-weak CONST is some rewrite rules, especially in the late dtype decomposition

##### **Chenyu** [[00:08:04](https://www.youtube.com/watch?v=J4bJVnAjntU&t=484)]
and

##### **Chenyu** [[00:08:07](https://www.youtube.com/watch?v=J4bJVnAjntU&t=487)]
transcendental stuff, that still regenerate concrete dtypes. Once I fix all that, we shouldn't have any concrete dtype for CONST, which should happen sometime this week. I also fixed a bunch of stuff. We have a lot of places with weird specs that I tried to fix. So this whole project so far is line-neutral, slightly down, which is a good sign that

##### **Chenyu** [[00:08:41](https://www.youtube.com/watch?v=J4bJVnAjntU&t=521)]
it's not crazy and I just need to make sure

##### **Chenyu** [[00:08:47](https://www.youtube.com/watch?v=J4bJVnAjntU&t=527)]
because we said we need to reinsert some of the dtype to make a backend work. Some backends still want you to specify the dtype when you render the literal of that CONST, so we need to know what that needs to be. Otherwise the backend will assume weird stuff and do a weird broadcast or upcast for you.

##### **Geohot** [[00:09:09](https://www.youtube.com/watch?v=J4bJVnAjntU&t=549)]
No, not much.

##### **Geohot** [[00:09:10](https://www.youtube.com/watch?v=J4bJVnAjntU&t=550)]
I mean, you can just match in the renderer on a CAST CONST.

##### **Chenyu** [[00:09:14](https://www.youtube.com/watch?v=J4bJVnAjntU&t=554)]
Yeah, we still need to do the last step right before dtype decomposition. Otherwise, you might later rewrite that into a dtype that you don't actually support in your renderer.

##### **Geohot** [[00:09:28](https://www.youtube.com/watch?v=J4bJVnAjntU&t=568)]
Okay,

##### **Geohot** [[00:09:29](https://www.youtube.com/watch?v=J4bJVnAjntU&t=569)]
yeah, so you want to make them all explicitly casted.

##### **Chenyu** [[00:09:30](https://www.youtube.com/watch?v=J4bJVnAjntU&t=570)]
Okay, yeah. So that needs to happen before dtype decomposition, and we need to make sure dtype decomposition itself won't regenerate a dtype that the renderer doesn't support.

##### **Geohot** [[00:09:41](https://www.youtube.com/watch?v=J4bJVnAjntU&t=581)]
Yeah, but this actually needs to get deleted from UOp.

##### **Chenyu** [[00:09:46](https://www.youtube.com/watch?v=J4bJVnAjntU&t=586)]
Yeah, so.

##### **Geohot** [[00:09:48](https://www.youtube.com/watch?v=J4bJVnAjntU&t=588)]
And then I'm also going to look into removing the metaclass once dtype's gone.

##### **Geohot** [[00:09:55](https://www.youtube.com/watch?v=J4bJVnAjntU&t=595)]
It's not really related to dtype's removal, but metaclasses are slow, and if we can do it in `__new__`, that's a lot better. And we have

##### **Chenyu** [[00:10:00](https://www.youtube.com/watch?v=J4bJVnAjntU&t=600)]
a crazy line there with the TODO that basically

##### **Chenyu** [[00:10:04](https://www.youtube.com/watch?v=J4bJVnAjntU&t=604)]
checks

##### **Chenyu** [[00:10:05](https://www.youtube.com/watch?v=J4bJVnAjntU&t=605)]
spec.

##### **Chenyu** [[00:10:06](https://www.youtube.com/watch?v=J4bJVnAjntU&t=606)]
Yeah.

##### **Chenyu** [[00:10:08](https://www.youtube.com/watch?v=J4bJVnAjntU&t=608)]
Okay, yeah, so that went nicely. I also

##### **Chenyu** [[00:10:13](https://www.youtube.com/watch?v=J4bJVnAjntU&t=613)]
started to

##### **Chenyu** [[00:10:15](https://www.youtube.com/watch?v=J4bJVnAjntU&t=615)]
I was interested in PCONTIG, or basically the high-level scheduling stuff that happens around rangeify.

##### **Chenyu** [[00:10:25](https://www.youtube.com/watch?v=J4bJVnAjntU&t=625)]
That is similar to how we auto-discover things like softmax backward and max. You can cancel that and some of the scheduler

##### **Chenyu** [[00:10:38](https://www.youtube.com/watch?v=J4bJVnAjntU&t=638)]
higher level scheduler stuff that's kind of interesting to look into. I have two drafts in the PR if you are interested.

##### **Chenyu** [[00:10:46](https://www.youtube.com/watch?v=J4bJVnAjntU&t=646)]
I also fixed a bunch of torch backend stuff.

##### **Chenyu** [[00:10:50](https://www.youtube.com/watch?v=J4bJVnAjntU&t=650)]
It's something that I don't really know if we want to support or not, but it's fun to improve. I almost got `torch.compile` working.

##### **Geohot** [[00:11:01](https://www.youtube.com/watch?v=J4bJVnAjntU&t=661)]
Sweet.

##### **Chenyu** [[00:11:01](https://www.youtube.com/watch?v=J4bJVnAjntU&t=661)]
Which is pretty easy.

##### **Geohot** [[00:11:02](https://www.youtube.com/watch?v=J4bJVnAjntU&t=662)]
I think we want our torch backend to work because it gives a really nice apples to apples comparison. Like we should just be able to run torch repos.

##### **Chenyu** [[00:11:09](https://www.youtube.com/watch?v=J4bJVnAjntU&t=669)]
Yeah, so that would be nice. But before that, I found like five different bugs in the old stuff. So if we want to support that, we also need to improve that.

##### **Geohot** [[00:11:19](https://www.youtube.com/watch?v=J4bJVnAjntU&t=679)]
I mean, that's a real way to get to get tinygrad users to like everyone should just have tinygrad installed in their system. Oh, we should do a release soon.

##### **Chenyu** [[00:11:27](https://www.youtube.com/watch?v=J4bJVnAjntU&t=687)]
Yeah, let's do a release maybe

##### **Chenyu** [[00:11:32](https://www.youtube.com/watch?v=J4bJVnAjntU&t=692)]
I don't know, maybe when

##### **Chenyu** [[00:11:35](https://www.youtube.com/watch?v=J4bJVnAjntU&t=695)]
after Chestnut launch, probably.

##### **Geohot** [[00:11:37](https://www.youtube.com/watch?v=J4bJVnAjntU&t=697)]
Yeah,

##### **Geohot** [[00:11:38](https://www.youtube.com/watch?v=J4bJVnAjntU&t=698)]
we'll do it with the Chestnut

##### **Geohot** [[00:11:39](https://www.youtube.com/watch?v=J4bJVnAjntU&t=699)]
launch.

##### **Chenyu** [[00:11:39](https://www.youtube.com/watch?v=J4bJVnAjntU&t=699)]
So we make sure it works with whatever tinygrad version we have.

##### **Geohot** [[00:11:43](https://www.youtube.com/watch?v=J4bJVnAjntU&t=703)]
Yeah. I'll try to get some of the LLM speedups merged. We'll have some out of the box Chestnut.

##### **Geohot** [[00:11:51](https://www.youtube.com/watch?v=J4bJVnAjntU&t=711)]
Yeah, I'll have some out of the box Chestnut bench numbers that look pretty good.

##### **Chenyu** [[00:11:56](https://www.youtube.com/watch?v=J4bJVnAjntU&t=716)]
Sounds good.

##### **Chenyu** [[00:11:58](https://www.youtube.com/watch?v=J4bJVnAjntU&t=718)]
Okay, that's my stuff. And we can move on to

##### **Chenyu** [[00:12:02](https://www.youtube.com/watch?v=J4bJVnAjntU&t=722)]
Chris' stuff.

##### **Chrism** [[00:12:03](https://www.youtube.com/watch?v=J4bJVnAjntU&t=723)]
Yeah. So SLICE is almost done. The last thing I need to do is

##### **Chrism** [[00:12:11](https://www.youtube.com/watch?v=J4bJVnAjntU&t=731)]
get 64-bit UOp variables working.

##### **Geohot** [[00:12:14](https://www.youtube.com/watch?v=J4bJVnAjntU&t=734)]
Does my stuff help?

##### **Chrism** [[00:12:17](https://www.youtube.com/watch?v=J4bJVnAjntU&t=737)]
That doesn't apply to UOp variables, but it should help with... No, it does help with SLICE. Yes, it should help with

##### **Chrism** [[00:12:24](https://www.youtube.com/watch?v=J4bJVnAjntU&t=744)]
other COPY stuff.

##### **Chenyu** [[00:12:24](https://www.youtube.com/watch?v=J4bJVnAjntU&t=744)]
Yeah, that's another blocker. Not a blocker, but one of the things I noticed while doing the weak dtype stuff, because we hard-coded several things as int32 and uint32

##### **Chenyu** [[00:12:39](https://www.youtube.com/watch?v=J4bJVnAjntU&t=759)]
so that it works better.

##### **Chrism** [[00:12:40](https://www.youtube.com/watch?v=J4bJVnAjntU&t=760)]
Yes.

##### **Chrism** [[00:12:42](https://www.youtube.com/watch?v=J4bJVnAjntU&t=762)]
And that kind of fits well with the other Program class changes.

##### **Geohot** [[00:12:48](https://www.youtube.com/watch?v=J4bJVnAjntU&t=768)]
What did you call the new Program class?

##### **Chrism** [[00:12:50](https://www.youtube.com/watch?v=J4bJVnAjntU&t=770)]
Well, the Program class is probably called `Program`, but the thing that you pass around is called `TinyELF`.

##### **Geohot** [[00:12:58](https://www.youtube.com/watch?v=J4bJVnAjntU&t=778)]
TinyELF!

##### **Chrism** [[00:13:00](https://www.youtube.com/watch?v=J4bJVnAjntU&t=780)]
Yeah.

##### **Chrism** [[00:13:02](https://www.youtube.com/watch?v=J4bJVnAjntU&t=782)]
Anyway, yeah.

##### **Geohot** [[00:13:04](https://www.youtube.com/watch?v=J4bJVnAjntU&t=784)]
Is TinyELF merged?

##### **Chrism** [[00:13:05](https://www.youtube.com/watch?v=J4bJVnAjntU&t=785)]
It is, yes.

##### **Geohot** [[00:13:06](https://www.youtube.com/watch?v=J4bJVnAjntU&t=786)]
Oh, sweet.

##### **Geohot** [[00:13:08](https://www.youtube.com/watch?v=J4bJVnAjntU&t=788)]
And is ELF all caps?

##### **Chrism** [[00:13:12](https://www.youtube.com/watch?v=J4bJVnAjntU&t=792)]
That implies that

##### **Chrism** [[00:13:13](https://www.youtube.com/watch?v=J4bJVnAjntU&t=793)]
the tiny part stands for something.

##### **Geohot** [[00:13:17](https://www.youtube.com/watch?v=J4bJVnAjntU&t=797)]
Oh, I love TinyELF! It's my favorite!

##### **Geohot** [[00:13:20](https://www.youtube.com/watch?v=J4bJVnAjntU&t=800)]
Wow, it has a signature. This is the most convenient. What's a `Target`?

##### **Chrism** [[00:13:26](https://www.youtube.com/watch?v=J4bJVnAjntU&t=806)]
It's like `dev=`.

##### **Geohot** [[00:13:28](https://www.youtube.com/watch?v=J4bJVnAjntU&t=808)]
Oh, alright, cool. Yeah. I haven't read this code.

##### **Chrism** [[00:13:33](https://www.youtube.com/watch?v=J4bJVnAjntU&t=813)]
Anyway, that should be useful. I don't know exactly what the implications are for HCQ2, because HCQ2 doesn't have a Program class.

##### **Chrism** [[00:13:45](https://www.youtube.com/watch?v=J4bJVnAjntU&t=825)]
But generally it should be nice to have that be a little more unified.

##### **Geohot** [[00:13:48](https://www.youtube.com/watch?v=J4bJVnAjntU&t=828)]
Why is there a device type separate from the TinyELF?

##### **Geohot** [[00:13:52](https://www.youtube.com/watch?v=J4bJVnAjntU&t=832)]
Why is there a dev here?

##### **Geohot** [[00:13:56](https://www.youtube.com/watch?v=J4bJVnAjntU&t=836)]
In `Program`, why is there a dev and a TinyELF?

##### **Chrism** [[00:14:00](https://www.youtube.com/watch?v=J4bJVnAjntU&t=840)]
Because a lot of the program classes depend on having access to the device to do validations or...

##### **Geohot** [[00:14:08](https://www.youtube.com/watch?v=J4bJVnAjntU&t=848)]
Having access to the real device. Yeah. Stop calling it `Compiled`. That's a pretty stupid name for the device. They're compiled devices; all devices are compiled. Why isn't that class just called `Device`? Oh no.

##### **Geohot** [[00:14:26](https://www.youtube.com/watch?v=J4bJVnAjntU&t=866)]
Oh, also, relevant to HCQ2, I guess we'll get to that next, but we're going to delete the... Can you explain what we're deleting?

##### **Chrism** [[00:14:35](https://www.youtube.com/watch?v=J4bJVnAjntU&t=875)]
What are we deleting?

##### **Geohot** [[00:14:37](https://www.youtube.com/watch?v=J4bJVnAjntU&t=877)]
The offsetable buffers.

##### **Chrism** [[00:14:39](https://www.youtube.com/watch?v=J4bJVnAjntU&t=879)]
Oh, yeah. So the idea is that I'm going to try to remove `_offset` from the allocator.

##### **Chrism** [[00:14:48](https://www.youtube.com/watch?v=J4bJVnAjntU&t=888)]
And this kind of fits in with the SLICE stuff. But I think this has something to

##### **Chrism** [[00:14:54](https://www.youtube.com/watch?v=J4bJVnAjntU&t=894)]
do with the implications

##### **Chrism** [[00:14:54](https://www.youtube.com/watch?v=J4bJVnAjntU&t=894)]
for COPY. So copy-in and copy-out will probably need to accept offsets.

##### **Chrism** [[00:14:59](https://www.youtube.com/watch?v=J4bJVnAjntU&t=899)]
Or you can just track this all in the Buffer object, but then not have it be an offset.

##### **Geohot** [[00:15:06](https://www.youtube.com/watch?v=J4bJVnAjntU&t=906)]
No, COPY just has to accept the offsets, right? You can see how I've moved toward that. There's a compiler now for copies. We could have a compiler for SDMA, and SDMA can support offsets. Basically like the HCQ2 compiler.

##### **Chrism** [[00:15:24](https://www.youtube.com/watch?v=J4bJVnAjntU&t=924)]
Yeah.

##### **Chrism** [[00:15:26](https://www.youtube.com/watch?v=J4bJVnAjntU&t=926)]
Anyway, `_offset` shouldn't exist anymore, which would be nice because WebGPU and CL don't support it.

##### **Geohot** [[00:15:32](https://www.youtube.com/watch?v=J4bJVnAjntU&t=932)]
In theory we could still implement offset, right? There's no reason we can't put the ADD outside the kernel, or the SHRINK outside the kernel and have the HCQ2 renderer do it. But it shouldn't be on the Buffer class.

##### **Geohot** [[00:15:47](https://www.youtube.com/watch?v=J4bJVnAjntU&t=947)]
The

##### **Geohot** [[00:15:48](https://www.youtube.com/watch?v=J4bJVnAjntU&t=948)]
offset has nothing to do with the buffer. That's just in the wrong place.

##### **Chrism** [[00:15:52](https://www.youtube.com/watch?v=J4bJVnAjntU&t=952)]
Anyway, in any case,

##### **Chrism** [[00:15:55](https://www.youtube.com/watch?v=J4bJVnAjntU&t=955)]
yeah, that also probably has implications for HCQ2.

##### **Geohot** [[00:15:58](https://www.youtube.com/watch?v=J4bJVnAjntU&t=958)]
You have like sub-buffers and alias buffers. Delete it all.

##### **Chrism** [[00:16:03](https://www.youtube.com/watch?v=J4bJVnAjntU&t=963)]
There's also all the stuff for tracking whether or not you're allowed to free a buffer because you might have sub-buffers.

##### **Chrism** [[00:16:10](https://www.youtube.com/watch?v=J4bJVnAjntU&t=970)]
Yeah,

##### **Geohot** [[00:16:11](https://www.youtube.com/watch?v=J4bJVnAjntU&t=971)]
I mean, you could still implement it two ways, right? It can either be implemented in the Program, where you take in a variable and add it using the GPU, or outside in the graph and compiled in HCQ2. But either way, offset is gone from Buffer.

##### **Chrism** [[00:16:28](https://www.youtube.com/watch?v=J4bJVnAjntU&t=988)]
Anyway, that is closely related to SLICE.

##### **Chrism** [[00:16:32](https://www.youtube.com/watch?v=J4bJVnAjntU&t=992)]
Yeah.

##### **Chrism** [[00:16:35](https://www.youtube.com/watch?v=J4bJVnAjntU&t=995)]
What else? Oh yeah, the pytest timeout. I deleted `pytest-timeout`, and if you look in `conftest.py`, I replaced it with a Python thing that handles and reports the timeouts, and actually successfully times out, because for whatever reason the signal timeout just doesn't work. So...

##### **Geohot** [[00:16:57](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1017)]
Where's `conftest.py`?

##### **Geohot** [[00:17:00](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1020)]
Is that a known thing?

##### **Chrism** [[00:17:03](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1023)]
It's a pytest configuration file.

##### **Geohot** [[00:17:07](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1027)]
Cool.

##### **Chrism** [[00:17:09](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1029)]
Anyway, if you see any issues with that, let me know. But

##### **Chrism** [[00:17:14](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1034)]
interestingly, I have not seen any timeouts since I made this change.

##### **Chenyu** [[00:17:21](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1041)]
Yeah, because I deleted a lot of slow paths. Okay, now the test is fast. It's like three

##### **Geohot** [[00:17:26](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1046)]
minutes. Lower the timeout then.

##### **Chenyu** [[00:17:30](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1050)]
Yeah, yeah.

##### **Geohot** [[00:17:31](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1051)]
Wow, that's great. Why did someone write a plugin for those lines?

##### **Chrism** [[00:17:37](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1057)]
Anyway, there was definitely stuff that was hanging forever before. I was pretty sure it was hanging forever. Maybe we fixed something. I guess it got fixed.

##### **Geohot** [[00:17:48](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1068)]
I believe that just works, man.

##### **Chrism** [[00:17:50](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1070)]
That's basically what `pytest-timeout` was doing.

##### **Geohot** [[00:17:52](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1072)]
Yeah, it probably had a thousand lines.

##### **Chrism** [[00:17:55](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1075)]
Yep.

##### **Chrism** [[00:17:57](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1077)]
Yeah. I think that's it.

##### **Geohot** [[00:18:01](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1081)]
Sounds good.

##### **Geohot** [[00:18:05](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1085)]
With that, we can move on to HCQ2.

##### **Nimlgen** [[00:18:12](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1092)]
So, yeah, um,

##### **Nimlgen** [[00:18:14](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1094)]
I merged the CPU backend, which is now in UOps. And, um,

##### **Nimlgen** [[00:18:24](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1104)]
yeah, so for HCQ2 itself, I just landed a lot of optimizations. The only reason HCQ2 is not merged is the compile time. The problem right now is that

##### **Nimlgen** [[00:18:36](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1116)]
for large schedules, like real training runs, we generate pretty big C kernels in non-JITted steps, like the first two. They take a lot of time to

##### **Nimlgen** [[00:18:54](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1134)]
to linearize and then compile.

##### **Nimlgen** [[00:18:59](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1139)]
So, um,

##### **Nimlgen** [[00:19:02](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1142)]
um,

##### **Nimlgen** [[00:19:03](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1143)]
so I've been thinking how

##### **Nimlgen** [[00:19:05](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1145)]
to solve this. Right now, lowering to PM4 and the other AMD instructions is done with rewrite rules: we rewrite HCQ2 instructions into real AMD instructions. I'm considering translating the encoders to UOps, compiling those PM4 encoders as C, and invoking them from

##### **Nimlgen** [[00:19:46](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1186)]
one program.

##### **Geohot** [[00:19:50](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1190)]
Um, I'm not totally

##### **Geohot** [[00:19:54](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1194)]
understanding this. I'm reading the HCQ2 code now. We want to get rid of `Compiled`.

##### **Geohot** [[00:20:02](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1202)]
HCQ2 should be the only way; all devices need to fit into the HCQ2 framework.

##### **Nimlgen** [[00:20:14](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1214)]
Yeah.

##### **Geohot** [[00:20:16](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1216)]
Including metal.

##### **Nimlgen** [[00:20:21](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1221)]
Yeah, but

##### **Nimlgen** [[00:20:24](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1224)]
but that should be possible,

##### **Nimlgen** [[00:20:24](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1224)]
but that's kind of a full backend rewrite.

##### **Geohot** [[00:20:29](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1229)]
Yeah, great. As long as the design decisions being made don't preclude that rewrite, right? I still see classes like `HCQ2Buffer` and `HCQ2Compiled`, and those should be replaced by just `Buffer` and `Compiled`.

##### **Geohot** [[00:20:46](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1246)]
It'd be nice to remove that too. Okay, so explain this to me: you're saying that compiling the C programs that do the submission is taking too long.

##### **Nimlgen** [[00:20:58](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1258)]
So, yeah, uh, so how this works right now is that

##### **Nimlgen** [[00:21:03](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1263)]
for non-JITted calls, we generate one template of the PM4 command buffer. After that, we need to patch it with the real input buffers, addresses, and so on. The C program does that.

##### **Nimlgen** [[00:21:20](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1280)]
For large schedules, there are a lot of things we end up patching because of that. It's about 20,000 lines of C code.

##### **Geohot** [[00:21:30](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1290)]
So that patching being generated, is that patching requiring a call to the C compiler? Or is that because, the way that I made the AMD emulator fast was that I just turned all these, uh, parameterizable things into variables.

##### **Geohot** [[00:21:45](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1305)]
Like, there's one basic C program for each instruction, and then things like which VGPR it is, is parameterized.

##### **Nimlgen** [[00:21:54](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1314)]
Um,

##### **Nimlgen** [[00:21:57](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1317)]
yeah, I mean, I

##### **Nimlgen** [[00:21:58](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1318)]
can turn them into loops, but I need two inputs, offset and value. This can be a loop then, and it should be fast.

##### **Geohot** [[00:22:09](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1329)]
Uh,

##### **Geohot** [[00:22:11](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1331)]
alright, let's not, we have to be very, very careful with loop.

##### **Geohot** [[00:22:16](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1336)]
If we have offset and value, that sounds a lot more like a scatter.

##### **Geohot** [[00:22:27](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1347)]
Eeeeee... I mean, it should just work as a scatter, right? Be very, very careful using loop. I'm gonna take loop away if loop causes problems.

##### **Geohot** [[00:22:36](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1356)]
You see what I mean?

##### **Nimlgen** [[00:22:37](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1357)]
No, that's not LOOP, but yeah, I see.

##### **Geohot** [[00:22:40](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1360)]
Okay, great.

##### **Geohot** [[00:22:41](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1361)]
But...

##### **Geohot** [[00:22:44](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1364)]
As

##### **Geohot** [[00:22:45](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1365)]
long as we're...

##### **Geohot** [[00:22:47](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1367)]
As long as we're not doing something like looping and looking for zero termination or something.

##### **Nimlgen** [[00:22:54](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1374)]
Yeah, no, it's not loop, like, it's finite.

##### **Nimlgen** [[00:22:59](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1379)]
Another idea, and I'm still thinking about this: if you open `ops_amd2`, `PM4Program` is just rewrite rules, and they

##### **Nimlgen** [[00:23:15](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1395)]
are still in Python. What if I rewrite all these lowerers in UOps, like `ops_cpu` is now, and invoke them the way Python already does?

##### **Nimlgen** [[00:23:33](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1413)]
Then I have one program, and I invoke all these lowerers from C to encode directly into the ring.

##### **Geohot** [[00:23:47](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1427)]
Okay.

##### **Geohot** [[00:23:49](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1429)]
So you're saying

##### **Geohot** [[00:23:49](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1429)]
that

##### **Geohot** [[00:23:50](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1430)]
instead of using rewrite rules, you want to write programs in UOps.

##### **Nimlgen** [[00:23:56](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1436)]
Yeah, and have HCQ2 call these small programs.

##### **Nimlgen** [[00:24:04](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1444)]
For JIT, I think this could be parallelizable, both for drivers and for speed. So we

##### **Geohot** [[00:24:13](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1453)]
need to ask which is easier to maintain and more likely to be correct. I never care about speed. We should never do things just to optimize for speed like that. If there's a reason it's better to write these things in UOps than rewrite rules, then that's justified. But if the only reason is speed, we should absolutely not do it.

##### **Nimlgen** [[00:24:39](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1479)]
Yeah, I see. I just, yeah, okay, I'll think. I just don't really want to generate, like, all these offset and values, because I just need to write this in Python and then just fit into this C program.

##### **Nimlgen** [[00:24:54](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1494)]
So if

##### **Nimlgen** [[00:24:54](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1494)]
I do

##### **Nimlgen** [[00:24:54](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1494)]
calls, I think it's

##### **Nimlgen** [[00:24:56](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1496)]
better.

##### **Geohot** [[00:24:58](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1498)]
Yeah. It can be fine if what you're doing is... You say write it in UOps, but can you write it in Tensor?

##### **Nimlgen** [[00:25:10](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1510)]
I can try, yeah.

##### **Geohot** [[00:25:20](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1520)]
It's like,

##### **Geohot** [[00:25:22](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1522)]
the more we can write these things in ways that look like Tensor manipulation, the better. If you're thinking about using UOps like a programming language,

##### **Geohot** [[00:25:32](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1532)]
like,

##### **Geohot** [[00:25:34](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1534)]
LOOP is really, really, really bad.

##### **Nimlgen** [[00:25:42](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1542)]
Yeah, but, okay,

##### **Nimlgen** [[00:25:44](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1544)]
for these programs that don't need LOOP, I can try them in a more Tensor-like way.

##### **Geohot** [[00:25:51](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1551)]
Yeah, I mean, also, like, the only thing to focus on, never worry about speed, the only thing to focus on is maintainability and what's going to be easier for more people to write new ones of these.

##### **Geohot** [[00:26:04](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1564)]
Yeah.

##### **Geohot** [[00:26:06](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1566)]
Um.

##### **Geohot** [[00:26:08](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1568)]
So, yeah, no, I mean, it doesn't have to be,

##### **Geohot** [[00:26:11](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1571)]
like, so what rewrite rules are you specifically talking about?

##### **Geohot** [[00:26:17](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1577)]
Like things such as this call to SDMA write?

##### **Geohot** [[00:26:21](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1581)]
Like,

##### **Nimlgen** [[00:26:23](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1583)]
Yeah, yeah. So,

##### **Geohot** [[00:26:24](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1584)]
these,

##### **Nimlgen** [[00:26:25](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1585)]
that actually just lower to the,

##### **Nimlgen** [[00:26:28](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1588)]
PM4 packets and SDMA packets.

##### **Geohot** [[00:26:35](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1595)]
Yeah.

##### **Geohot** [[00:26:39](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1599)]
And it's using `Ops.INS`.

##### **Geohot** [[00:26:41](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1601)]
That seems right, though.

##### **Geohot** [[00:27:02](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1622)]
Yeah.

##### **Geohot** [[00:27:05](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1625)]
Yeah, maybe I don't exactly understand what's slow. I mean, this doesn't look slow to me, right? This looks identical to lowering the, uh, the program itself, right? Like, this looks like an assembly backend for PM4 or SDMA, which I think is exactly what we want.

##### **Nimlgen** [[00:27:22](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1642)]
Yeah, but when I'm, uh, like,

##### **Nimlgen** [[00:27:27](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1647)]
the patching of these command buffers, because they have some unknown values, such as input addresses, that are only known at runtime and not when the command buffers are built.

##### **Geohot** [[00:27:40](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1660)]
But it wouldn't be these opsel pattern matches, because I think these opsel pattern matches are right. Which pattern matches would it specifically replace?

##### **Nimlgen** [[00:27:50](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1670)]
Um,

##### **Nimlgen** [[00:27:54](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1674)]
no, I wanted to replace this, um,

##### **Nimlgen** [[00:27:57](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1677)]
specifically, so,

##### **Nimlgen** [[00:28:00](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1680)]
So, I

##### **Nimlgen** [[00:28:01](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1681)]
mean, I wanted to rewrite `PM4Program`. It would be in UOps,

##### **Nimlgen** [[00:28:09](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1689)]
not the instructions. When I lower the program or the CALL operation, it will invoke this thing to encode into the buffer that was passed in.

##### **Geohot** [[00:28:25](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1705)]
Um,

##### **Geohot** [[00:28:28](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1708)]
No, I don't, I really don't think we want that. I, I, I think that this isn't why it's slow.

##### **Geohot** [[00:28:36](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1716)]
Like, I, I, I can't understand why lowering a program with,

##### **Geohot** [[00:28:41](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1721)]
Like, okay, So, here's what I would do instead.

##### **Geohot** [[00:28:45](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1725)]
You still want it to be UOps. But `PM4Program` is the perfect example, right? Some of those things in `PM4Program` are parameterized.

##### **Geohot** [[00:28:57](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1737)]
So you want to turn that into a CALL, but it still has the instructions.

##### **Nimlgen** [[00:29:06](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1746)]
Yeah.

##### **Geohot** [[00:29:07](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1747)]
This is the same problem as basically dealing with, like, when you have an instruction, and you want to assign that instruction, like, to a register, and you have to, like, bit shift the register and put the register actually in the machine code, this is the same problem as that. Um, So, what we don't want to do is, like, writing something that looks like, like, tensors that create the binaries, right? You could imagine that for assembly as well. You could imagine assembly like tensors concatenating machine code. Uh, We definitely don't want to do that.

##### **Geohot** [[00:29:38](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1778)]
We want it to go through a pipeline where we lower it as an `Ops.INS` instruction. However, what's slow here is the fact that you're calling `PM4Program` many, many times. This is the exact same problem I dealt with in the AMD emulator. You want to turn `PM4Program` into a function, or a CALL, that takes the relevant values as parameters.

##### **Geohot** [[00:30:04](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1804)]
Does that make sense? Do you think that

##### **Geohot** [[00:30:05](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1805)]
fixes it?

##### **Nimlgen** [[00:30:11](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1811)]
So,

##### **Nimlgen** [[00:30:12](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1812)]
they're already parameterized. I call the program once per kernel.

##### **Geohot** [[00:30:19](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1819)]
Like, You call program once per kernel, yeah.

##### **Geohot** [[00:30:24](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1824)]
I'm saying you can call it once per queue.

##### **Geohot** [[00:30:31](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1831)]
Uh, yeah. Maybe, yeah.

##### **Nimlgen** [[00:30:34](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1834)]
But, again, the problem is, like, the generated C looks like that. I

##### **Geohot** [[00:30:39](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1839)]
totally understand. That's what I'm saying. Like, it should be a call.

##### **Geohot** [[00:30:45](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1845)]
Yeah. The way to fix this in C is with hierarchy. Hierarchy is the square root. In the limit, imagine having a function in C called `PM4Program`

##### **Geohot** [[00:31:04](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1864)]
that has all that stuff in it and takes a bunch of parameters. Then, in the main function, you have ten calls to the program. CALLs should be lowerable.

##### **Nimlgen** [[00:31:18](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1878)]
Yeah. Uh, yeah.

##### **Nimlgen** [[00:31:23](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1883)]
Yeah, so, I think I, I wanted exactly that.

##### **Nimlgen** [[00:31:26](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1886)]
So,

##### **Nimlgen** [[00:31:28](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1888)]
I have `PM4Program` as a separate C program, call it with some parameters, and it returns instructions. Right?

##### **Geohot** [[00:31:40](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1900)]
Uh, no. No, no, no, no, no. Like, it's not a separate program. It's just a call. It's like a function.

##### **Chenyu** [[00:31:48](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1908)]
It's like how we write WMMA.

##### **Chenyu** [[00:31:51](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1911)]
We render the stuff we want to generate.

##### **Geohot** [[00:31:55](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1915)]
WMMA is dealt with terribly. It's not like WMMA.

##### **Geohot** [[00:32:01](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1921)]
you know, I'll write, like, so say, like, we want, like, you know, uh,

##### **Geohot** [[00:32:08](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1928)]
`PM4Program(params)`,

##### **Geohot** [[00:32:12](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1932)]
right, and then, like, you

##### **Geohot** [[00:32:13](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1933)]
know, void kernel, and then,

##### **Geohot** [[00:32:16](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1936)]
like,

##### **Geohot** [[00:32:24](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1944)]
I wish there was some way to type

##### **Geohot** [[00:32:26](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1946)]
live. Like that.

##### **Geohot** [[00:32:32](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1952)]
Not how we use WMMA. WMMA is hard-coded in the renderer. This should not be hard-coded in the renderer.

##### **Chenyu** [[00:32:37](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1957)]
Yeah. I mean,

##### **Chenyu** [[00:32:40](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1960)]
it should be like this.

##### **Geohot** [[00:32:41](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1961)]
Yeah. Uh, but, yeah, notably,

##### **Geohot** [[00:32:45](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1965)]
in UOps, what this should look like is a CALL with a repeated

##### **Geohot** [[00:32:55](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1975)]
PM4

##### **Geohot** [[00:32:55](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1975)]
program, and

##### **Geohot** [[00:32:57](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1977)]
then params.

##### **Geohot** [[00:33:03](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1983)]
Like that.

##### **Geohot** [[00:33:08](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1988)]
Um, do

##### **Geohot** [[00:33:09](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1989)]
you understand how the AMD emulator works?

##### **Nimlgen** [[00:33:13](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1993)]
Uh,

##### **Nimlgen** [[00:33:17](https://www.youtube.com/watch?v=J4bJVnAjntU&t=1997)]
I haven't read it in detail.

##### **Geohot** [[00:33:22](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2002)]
Run some stuff through the AMD emulator, because I dealt with a lot of these same problems. The main problem you run into there is that generating a program for each instruction is really slow because there are many different kinds of instructions. So I parameterized basically everything about the instruction. I didn't pass those parameters in; I read them from the instruction's machine code, but it's still the same basic idea.

##### **Geohot** [[00:33:50](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2030)]
Um, you, you parameterize your PM4 program entirely. Uh, like, I see things aren't...

##### **Nimlgen** [[00:34:00](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2040)]
Yeah, yeah, so,

##### **Nimlgen** [[00:34:02](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2042)]
so yeah, I, I just, okay, so just to be short, I just wanted exactly the same, but do you want to put this into the same like the C kernel? Or we can just compile PM4, because currently with, like, for the C backend, we have call which can use pointers and just do external calls using pointers. So we basically can do the same. We should modify

##### **Geohot** [[00:34:24](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2064)]
the C backend to be able to render normal functions.

##### **Geohot** [[00:34:30](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2070)]
Okay, yeah. I think that's not too hard to do. So then your return from `PM4Program` is an `Ops.LINEAR`.

##### **Geohot** [[00:34:40](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2080)]
What's happening when you return that `Ops.LINEAR` is that it gets flattened and turned into this massive C program. So that `Ops.LINEAR` should be an `Ops.CALL`.

##### **Geohot** [[00:34:56](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2096)]
Yeah. The PM4 creation program, right? So do you see how this is the square root of N UOps?

##### **Nimlgen** [[00:35:07](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2107)]
Um,

##### **Nimlgen** [[00:35:11](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2111)]
Yeah.

##### **Nimlgen** [[00:35:16](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2116)]
I think, yeah, yeah. So

##### **Geohot** [[00:35:18](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2118)]
I'm pretty sure this works. What we really need to avoid is manipulating machine code in Tensor land.

##### **Geohot** [[00:35:36](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2136)]
Like, I know it's doable.

##### **Geohot** [[00:35:47](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2147)]
Right.

##### **Geohot** [[00:35:48](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2148)]
So this turns N squared into 2N.

##### **Geohot** [[00:35:53](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2153)]
Factorizing like that.

##### **Nimlgen** [[00:35:56](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2156)]
Yeah.

##### **Nimlgen** [[00:36:06](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2166)]
Yeah.

##### **Geohot** [[00:36:09](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2169)]
And then you can, almost go even crazier with this and like.... You want like a scan operation.

##### **Geohot** [[00:36:18](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2178)]
I think just this will be enough. But you could imagine what it becomes as a scan operation. Which calls function one with uh ... You know, parameters that are in a list or something.

##### **Geohot** [[00:36:31](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2191)]
or in a tensor. You can imagine scanning function one across a list of programs. ...

##### **Geohot** [[00:36:41](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2201)]
You know.

##### **Geohot** [[00:36:46](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2206)]
Does this fix it?

##### **Nimlgen** [[00:36:53](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2213)]
Yeah. Yeah, so...

##### **Geohot** [[00:36:57](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2217)]
Yeah.

##### **Geohot** [[00:36:59](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2219)]
Cool. I mean, so is the slow one the PM4 program one?

##### **Nimlgen** [[00:37:07](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2227)]
I mean, this will solve the... Oh, I mean...

##### **Nimlgen** [[00:37:12](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2232)]
So we just... That's not the PM4 program. That's the amount of patches we do.

##### **Nimlgen** [[00:37:20](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2240)]
In the final C, it's not HCQ that's slow. The C linearizer and compilation are slow.

##### **Geohot** [[00:37:29](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2249)]
What file should I look in for this?

##### **Nimlgen** [[00:37:37](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2257)]
It's not actually the file. But basically, all these patches would...

##### **Geohot** [[00:37:43](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2263)]
Like,

##### **Nimlgen** [[00:37:46](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2266)]
you can see this C program.

##### **Nimlgen** [[00:37:49](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2269)]
So the current idea is that all these instructions there will be like in the binary blob. So they're binary. This is like one store to write them into the...

##### **Nimlgen** [[00:38:02](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2282)]
real buffer. So that's the minimal amount of work. But we have patches for addresses, like kernel and program addresses. At runtime, we replace them on top of the template we have.

##### **Nimlgen** [[00:38:23](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2303)]
Command buffer template. That was slow, not even in HCQ, but in C generation because there are so many patches.

##### **Nimlgen** [[00:38:32](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2312)]
So, but basically, it's like... Basically, calling like PM4 program in runtime should solve that.

##### **Nimlgen** [[00:38:40](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2320)]
I think.

##### **Geohot** [[00:38:42](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2322)]
I see. I mean, okay, so there's another thing that you can do.

##### **Geohot** [[00:38:47](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2327)]
Which is like...

##### **Geohot** [[00:38:54](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2334)]
Like, this should be pretty fast too.

##### **Geohot** [[00:38:59](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2339)]
And it should render.

##### **Geohot** [[00:39:04](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2344)]
Sorry, not

##### **Geohot** [[00:39:05](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2345)]
add,

##### **Geohot** [[00:39:05](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2345)]
I

##### **Geohot** [[00:39:05](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2345)]
mean offset.

##### **Nimlgen** [[00:39:11](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2351)]
Yeah, I see.

##### **Geohot** [[00:39:12](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2352)]
Yeah. That should work. If that doesn't work, we can all work on making it work. But that's basically like a scatter.

##### **Geohot** [[00:39:22](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2362)]
And then, if you want to encode all those CONSTs, STACK CONST is the way to do it.

##### **Nimlgen** [[00:39:31](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2371)]
Okay.

##### **Geohot** [[00:39:32](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2372)]
Okay, yeah. If you want to do patches.

##### **Geohot** [[00:39:36](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2376)]
Okay, cool. You

##### **Geohot** [[00:39:37](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2377)]
know, I mean overall, I think that most of the decisions in here have been very good.

##### **Geohot** [[00:39:43](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2383)]
But the way we should always think about it is as an assembly backend for the MEC and the SDMA engine.

##### **Nimlgen** [[00:39:59](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2399)]
Yeah.

##### **Geohot** [[00:40:02](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2402)]
Yeah, no, they look... I mean, they look pretty good. They

##### **Geohot** [[00:40:03](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2403)]
look beautiful. And

##### **Geohot** [[00:40:03](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2403)]
we could eventually factor `ops_amd2` into AMD PM4, AMD SDMA, and AMD RDNA3. It's all kind of the same thing.

##### **Geohot** [[00:40:14](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2414)]
Different, a little different about what you can actually run. But yeah, then for these scatters, it should just be this.

##### **Geohot** [[00:40:24](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2424)]
But you know, I mean, these get into like other problems that we haven't totally answered yet, which is like, how are we going to do things like machine code generation with the registers? Right? How do we know how to like put the register into the machine code of the instruction? Okay, R4 is the source input. Okay, we got to like bit shift for that kind of stuff. So, you know, that hasn't exactly been solved yet.

##### **Geohot** [[00:40:46](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2446)]
But yeah, I can see these being sort of similar problems.

##### **Nimlgen** [[00:40:50](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2450)]
Okay.

##### **Geohot** [[00:40:52](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2452)]
Anything else?

##### **Nimlgen** [[00:40:55](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2455)]
No.

##### **Chenyu** [[00:40:57](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2457)]
Okay, let's

##### **Chenyu** [[00:40:58](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2458)]
move on. Can you scroll a little bit?

##### **Chenyu** [[00:41:01](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2461)]
Next. It's your stuff.

##### **Geohot** [[00:41:03](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2463)]
Cool. So I very regrettably wrote LOOP. It's very regrettable. LOOP is so regrettable that I almost want to call it `LOOP_DO_NOT_USE`.

##### **Geohot** [[00:41:16](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2476)]
Because LOOP is Turing complete.

##### **Geohot** [[00:41:18](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2478)]
So yeah, there's that. As soon as you have something that has an unbounded number of iterations, it's Turing complete.

##### **Geohot** [[00:41:26](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2486)]
There's some more cleanup that can be done. The way we express LOOP right now is with a sourceless RANGE, a RANGE with a NOOP source. A RANGE with a NOOP source will not terminate, so you put a termination condition on the END, and that's where the loop exits. This is unfortunately Turing complete. There are some things for which you need this pattern and can't really get around it. We could always add a bound, right? We could always add a RANGE bound.

##### **Geohot** [[00:41:59](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2519)]
Oh, it's not time.

##### **Chenyu** [[00:42:01](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2521)]
It's LOOP.

##### **Geohot** [[00:42:03](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2523)]
Yeah, yeah. We could always add a bound. That kind of fixes it, but not really. There are some things for which you're fundamentally going to need this pattern. If you're waiting for another device to finish something, that's basically the only time. You might think, why not use something like `Ops.WAIT`? Presumably you have to poll on something, which is a LOAD. But if you do a LOAD and then an `Ops.WAIT`, that LOAD is not in any kind of scope, so it will fire once. This is the same problem as not using `volatile` in C. Because we have a dataflow compiler, our LOADs have to be scoped. We already have machinery for scoping LOADs inside a LOOP. You can have a RANGE and use AFTER: take the buffer, add AFTER, and then do the LOAD after the RANGE. Every time the RANGE loops, it will do that LOAD. That's why I settled on LOOP rather than WAIT.

##### **Geohot** [[00:43:15](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2595)]
Because we need some way to scope what you load and what you don't load. You need two UOps for that, and those two UOps look an awful lot like RANGE and END, so you reuse RANGE and END. But be very careful using this. If you're using it, it's very, very bad.

##### **Geohot** [[00:43:35](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2615)]
You shouldn't need it for anything.

##### **Geohot** [[00:43:38](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2618)]
But we can also use it for instruction selection. So a bunch of the backends. This just has to be cleaned up. If someone wants to do this, I wish those people would just do this. Because AI do it very untastefully. If it's just someone who would do this tastefully.

##### **Geohot** [[00:43:54](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2634)]
Like the LLVM backend, the PTX backend, and the NIR backend.

##### **Geohot** [[00:43:59](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2639)]
Their code to express loops is a lot simpler than their code to express ranges. So a range basically includes three things. A range includes an initializer. A range includes a comparison. And a range includes an increment.

##### **Geohot** [[00:44:12](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2652)]
But right now they're all stuffed into this one magic op called RANGE. That can obviously be broken out; I just described the three parts of a for loop. We could have some backends that don't support RANGE with a NOOP source and then simplify the renderers. We could do that with all of them, but it makes the C code uglier.

##### **Geohot** [[00:44:35](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2675)]
And that's LOOP. COPY is STORE. I now lower COPY to STORE, so COPY is kind of like an anonymous STORE. Think about a copy from the CPU device to the AMD device: that says to create a buffer on the AMD device and copy in from the CPU device.

##### **Geohot** [[00:44:56](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2696)]
Now, there's nice advantages to buffers being anonymous.

##### **Geohot** [[00:44:59](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2699)]
The

##### **Geohot** [[00:44:59](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2699)]
biggest advantage of an anonymous buffer is that if you do two copies of the same thing, those two COPY UOps dedupe to one. If you do two STOREs to different buffers, they won't dedupe.

##### **Geohot** [[00:45:14](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2714)]
With just one very contrived test disabled, I switched COPY to STORE. This simplifies things because rangeify never has to deal with COPY anymore.

##### **Geohot** [[00:45:29](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2729)]
So I re-add COPY at the end. But it's not really a COPY op. The thing I use to re-add COPY at the end should actually become the HCQ2 AMD compiler,

##### **Geohot** [[00:45:41](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2741)]
the HCQ2 SDMA compiler. What that COPY is basically saying is that I can run this program on the SDMA engine.

##### **Geohot** [[00:45:54](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2754)]
And then this also gets into the, well, so that program actually doesn't have to run on the SDMA engine.

##### **Geohot** [[00:45:59](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2759)]
This program can also run on CUs. There's no reason that CUs can't also implement a copy. So we have to get better about, like, saying, okay, right. You can even go crazy and say, like, this program is going to access buffers on AMD1, but it's going to run on AMD2. There's no reason that that shouldn't just work. So, yeah, moving in that direction.

##### **Chenyu** [[00:46:22](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2782)]
Does it work nicely with multi?

##### **Geohot** [[00:46:26](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2786)]
Well, yeah. I mean, multi. Okay, so it's not invalid.

##### **Geohot** [[00:46:33](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2793)]
MULTI is something else. And by something else, I mean it's actually rangeify.

##### **Geohot** [[00:46:39](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2799)]
MULTI is rangeify. That's written on the board.

##### **Geohot** [[00:46:44](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2804)]
However, MULTI is not like the existing rangeify. Existing rangeify operates from the bottom up: it takes an index and moves it up through the graph.

##### **Geohot** [[00:46:56](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2816)]
MULTI works the other way. MULTI lets us specify the axis at buffer creation time, which is at the top of the graph. At the top of the graph, you say you want this RANGE. A MULTI is a RANGE. If I say I want to shard across axis 0, that's a RANGE across axis 0. That factorizes out the top dimension of axis 0 and does a RANGE across it.

##### **Geohot** [[00:47:23](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2843)]
The way to rewrite MULTI is as a generic top dimension. I'll rewrite MULTI as top-down rangeify. I actually wrote top-down rangeify once before. The problem is that it creates very ugly things for convolutions.

##### **Geohot** [[00:47:38](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2858)]
And you can see why that is. Those things kind of go away, but they would fail on MULTI anyway. You can't MULTI across the weight axis of a convolution; that fails right now. I'll rewrite MULTI as top-down rangeify, and then it will be pretty generic. That RANGE is the UOp called `DEVICE_NUM`, but you could use any UOp you want, including the one I really care about, which is the warp. Then we can express alloc fragment by running top-down rangeify.

##### **Geohot** [[00:48:14](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2894)]
Yeah. So it's actually very similar. The code isn't going to be that different from multi. Like the code that we have in multi right now, which processes like the movement ops and stuff,

##### **Geohot** [[00:48:27](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2907)]
it doesn't really go away. It gets generalized and called top-down rangeify. Instead of moving an index up through the graph, we move a STAGE down through the graph.

##### **Chenyu** [[00:48:38](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2918)]
Great.

##### **Geohot** [[00:48:38](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2918)]
Yeah.

##### **Geohot** [[00:48:39](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2919)]
And this also beautifully answers how we introduce all-reduces. The problem with the PAD-invalid approach is that I can PAD invalid, but then when I REDUCE across the axis, that's not an all-reduce. Even if invalid is the identity in the REDUCE, you're still not communicating across devices, and it's not obvious how to add that communication. In rangeify, it's obvious: if I am moving my RANGE down through the graph and that RANGE reaches a REDUCE, great, insert an all-reduce.

##### **Geohot** [[00:49:23](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2963)]
That's it.

##### **Geohot** [[00:49:25](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2965)]
I'll work on MULTI

##### **Geohot** [[00:49:27](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2967)]
more this week.

##### **Chenyu** [[00:49:30](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2970)]
Anything

##### **Chenyu** [[00:49:30](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2970)]
else?

##### **Geohot** [[00:49:31](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2971)]
Nope.

##### **Chenyu** [[00:49:33](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2973)]
Next is LLaMA training.

##### **Qazalin** [[00:49:35](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2975)]
We

##### **Qazalin** [[00:49:35](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2975)]
can talk about the AMD machine slowness issue. We ran the AMD Docker, and it finished 16 minutes slower. So we're 10% slower than AMD with the same Docker.

##### **Qazalin** [[00:49:57](https://www.youtube.com/watch?v=J4bJVnAjntU&t=2997)]
And I really tracked it down.

##### **Qazalin** [[00:50:00](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3000)]
I even went as far as checking the voltages using the BMC. It really comes down to our intake temperatures being too high and the clocks slowing down. I have a repro: if you run a GEMM in a loop, you'll see it get about 2% fewer FLOPS.

##### **Geohot** [[00:50:26](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3026)]
So why

##### **Geohot** [[00:50:27](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3027)]
I'm reluctant to believe this entirely is when you throttle the power, it only gets to 70 C, but we still see a drop in the performance, right? That's not throttling.

##### **Qazalin** [[00:50:41](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3041)]
It's not. I checked the bits. AMD has these bits for violations.

##### **Geohot** [[00:50:49](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3049)]
Yeah.

##### **Qazalin** [[00:50:50](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3050)]
And the thermal is not set.

##### **Qazalin** [[00:50:54](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3054)]
The one that is set is called PPT, the package power limit. It seems that when it gets to the 1,000-watt maximum, it doesn't go any higher. Then it just...

##### **Qazalin** [[00:51:16](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3076)]
I guess the clocks slow down. That's what I see there.

##### **Qazalin** [[00:51:20](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3080)]
So

##### **Geohot** [[00:51:21](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3081)]
you see the clock slow down even when it's only set to 500 watts. You said even at 500 watts, the clock slow down.

##### **Qazalin** [[00:51:28](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3088)]
Yes, they slow down.

##### **Geohot** [[00:51:30](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3090)]
But why?

##### **Geohot** [[00:51:32](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3092)]
They're not hot.

##### **Qazalin** [[00:51:37](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3097)]
But it reaches the power limit.

##### **Geohot** [[00:51:43](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3103)]
Oh, the 500 watt power limit.

##### **Qazalin** [[00:51:46](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3106)]
Or the whatever I said. So it reaches that ceiling.

##### **Geohot** [[00:51:52](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3112)]
I mean, again, that still doesn't explain really why it slows down after minutes. It should reach that ceiling immediately. The 500 watts. If you set it to 500 watts.

##### **Geohot** [[00:52:07](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3127)]
I don't know. We're working on it. I think we can close this

##### **Geohot** [[00:52:15](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3135)]
investigation

##### **Geohot** [[00:52:15](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3135)]
for now.

##### **Chenyu** [[00:52:17](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3137)]
We're

##### **Chenyu** [[00:52:17](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3137)]
going to get a generator supposedly tomorrow. It will be loud here, probably, and we

##### **Chenyu** [[00:52:24](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3144)]
probably won't

##### **Chenyu** [[00:52:24](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3144)]
fix the temperature anyway.

##### **Geohot** [[00:52:28](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3148)]
Let's be optimistic here. OK, so we looked into buying an air conditioner and putting the air conditioner on the computer. We don't have enough power for the air conditioner. And everyone was opposed to my plan of a long extension cord.

##### **Geohot** [[00:52:41](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3161)]
So the rule at the office now is: if you want power, you have to make your own power. We have a generator coming tomorrow, and Harold and I have a hundred-dollar bet. He thinks the generator is an acceptable solution and will be quiet. I think it's going to be stupidly loud. So we'll see who's right.

##### **Chenyu** [[00:52:59](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3179)]
Yeah. We will fix the temperature issue later one way or another. But I think we can divert our energy back to making tinygrad schedule and render better kernels.

##### **Geohot** [[00:53:14](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3194)]
Yeah. We can, we can table this for now.

##### **Geohot** [[00:53:17](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3197)]
We will get you lower intake temperatures in a few weeks. They'll be on time for MLPerf. It seems like it's not anything else, so that's good. What other speedups can we get?

##### **Qazalin** [[00:53:33](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3213)]
All right. I have a list of tricks to merge into master.

##### **Qazalin** [[00:53:42](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3222)]
My deliverables for this week are merging the removal of CONTIGUOUS from custom kernels. I'm also going to work on the Flash Attention and GEMM improvements that I discovered from

##### **Qazalin** [[00:53:55](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3235)]
the profiler.

##### **Geohot** [[00:53:56](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3236)]
Are Flash Attention and GEMM written in HIP or the UOp language?

##### **Qazalin** [[00:54:02](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3242)]
HIP.

##### **Geohot** [[00:54:04](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3244)]
Do you

##### **Geohot** [[00:54:04](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3244)]
think we can write them in the UOp language without losing performance?

##### **Qazalin** [[00:54:08](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3248)]
Um,

##### **Qazalin** [[00:54:15](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3255)]
I can

##### **Qazalin** [[00:54:16](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3256)]
look. I think it's going to use a lot of `Ops.CUSTOM`, because a lot of the reason why

##### **Qazalin** [[00:54:21](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3261)]
it's written that way is because LLVM is bad.

##### **Geohot** [[00:54:26](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3266)]
Yeah.

##### **Qazalin** [[00:54:29](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3269)]
It would use a lot of `Ops.CUSTOM`. It's not going to look pretty.

##### **Geohot** [[00:54:35](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3275)]
Maybe we should think about doing this when we get to assembly languages, if there's no way to do it in LLVM. The other thing is MXFP4.

##### **Qazalin** [[00:54:46](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3286)]
Oh yes. So I have a run with MXFP4.

##### **Qazalin** [[00:54:53](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3293)]
The GEMM. There is no HIP GEMM for FP4. I tried; it's not fast. It's three hours. But it's three hours not because of the GEMMs. The GEMMs still get five petaflops.

##### **Geohot** [[00:55:07](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3307)]
Okay. Well,

##### **Geohot** [[00:55:08](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3308)]
it's, it

##### **Geohot** [[00:55:09](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3309)]
converges in the same steps or more steps.

##### **Qazalin** [[00:55:12](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3312)]
The same steps as AMD. Yeah.

##### **Geohot** [[00:55:15](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3315)]
I see. The other one you linked converges in 5,000, a thousand fewer steps.

##### **Qazalin** [[00:55:22](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3322)]
Same steps as AMD. So I ran AMD's FP4 Docker on our machine and compared that step time.

##### **Geohot** [[00:55:31](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3331)]
How fast was AMD's FP4 Docker on our machine?

##### **Qazalin** [[00:55:35](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3335)]
How fast was AMD's FP4? I don't quite remember, but it's still 10% slower than their submission.

##### **Geohot** [[00:55:41](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3341)]
Yeah. I'm sure it's 10% slower than their submission, but I mean, we're just trying

##### **Geohot** [[00:55:44](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3344)]
to get the,

##### **Geohot** [[00:55:44](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3344)]
we'll just operate in this, in this world where, you know, we're just competing with that AMD Docker rerun on our machines and assume that it'll just get faster.

##### **Chenyu** [[00:55:52](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3352)]
If at the end of this contract period, we really need AC, we'll just rent a machine or something.

##### **Geohot** [[00:55:59](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3359)]
If we get close to the end of the contract period and we need AC, I'm going to turn off half of Comma's data center or run a long extension cord.

##### **Qazalin** [[00:56:08](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3368)]
I was thinking of getting cloud machines with AMD GPUs.

##### **Geohot** [[00:56:13](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3373)]
Or we can use the cloud. Cloud machines with AMD GPUs, yeah. So why is MXFP4 slow?

##### **Qazalin** [[00:56:18](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3378)]
Dumb kernels. I'll fix that.

##### **Geohot** [[00:56:22](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3382)]
All right, great. Yeah. Yeah. Let's go. Let's go faster.

##### **Geohot** [[00:56:28](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3388)]
Are

##### **Geohot** [[00:56:28](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3388)]
we beating AMD's FP8?

##### **Qazalin** [[00:56:34](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3394)]
Are we matching AMD's FP8?

##### **Qazalin** [[00:56:35](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3395)]
We

##### **Qazalin** [[00:56:35](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3395)]
are matching

##### **Qazalin** [[00:56:36](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3396)]
AMD's FP8.

##### **Geohot** [[00:56:37](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3397)]
We have a faster one.

##### **Qazalin** [[00:56:41](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3401)]
You want a faster one for the FP8 or...?

##### **Geohot** [[00:56:43](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3403)]
Beat AMD's FP8 on master and I'm happy. It doesn't matter if it's FP8 or FP4. Just beat AMD's FP8.

##### **Qazalin** [[00:56:58](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3418)]
I'll beat it with FP4 because I have maxed out all the FP8 optimizations. It comes down to faster GEMM and Flash Attention, which I tried really hard to write, but they don't seem to be maxed out.

##### **Geohot** [[00:57:12](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3432)]
Wait.

##### **Geohot** [[00:57:14](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3434)]
There's no way there's... Flash Attention doesn't use FP4 though, right? Ever.

##### **Qazalin** [[00:57:19](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3439)]
Well, GEMMs do.

##### **Geohot** [[00:57:20](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3440)]
GEMMs do, yeah, but not Flash Attention.

##### **Qazalin** [[00:57:23](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3443)]
Yes.

##### **Geohot** [[00:57:25](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3445)]
Yes, it uses it or no, it doesn't use it?

##### **Qazalin** [[00:57:28](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3448)]
GEMMs use FP4.

##### **Geohot** [[00:57:31](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3451)]
And Flash Attention uses...

##### **Qazalin** [[00:57:34](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3454)]
BF16, I think.

##### **Geohot** [[00:57:37](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3457)]
I think it's BF16. Yeah, it's BF16. Oh, it's BF16. Okay, great. Even slower. So FP4 GEMM then. Good.

##### **Geohot** [[00:57:48](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3468)]
And yeah, let's get this stuff... Let's get this stuff merged into master.

##### **Qazalin** [[00:57:55](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3475)]
Sounds good.

##### **Geohot** [[00:57:57](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3477)]
Yeah. The investigation is closed on the speed. We're going to get an air conditioner

##### **Geohot** [[00:58:03](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3483)]
or cloud machines by the time it's submission time.

##### **Qazalin** [[00:58:08](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3488)]
Okay.

##### **Qazalin** [[00:58:10](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3490)]
Also, I'll just mention that a lot of the LLaMA tricks

##### **Qazalin** [[00:58:16](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3496)]
depend on MULTI.

##### **Qazalin** [[00:58:19](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3499)]
And I kind of don't want to touch MULTI while you're rewriting it, so maybe I'll wait until next week.

##### **Geohot** [[00:58:28](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3508)]
A lot of the LLaMA tricks depend on MULTI? Like what, the all-reduce?

##### **Geohot** [[00:58:34](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3514)]
Yeah,

##### **Chenyu** [[00:58:36](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3516)]
yeah, yeah. Okay. I mean, MULTI is not going to

##### **Geohot** [[00:58:38](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3518)]
change that much, but that's reasonable. We can focus on FP4 this week.

##### **Qazalin** [[00:58:46](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3526)]
All right. Okay.

##### **Geohot** [[00:58:52](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3532)]
Raine is here. Do you want to update?

##### **Raine** [[00:58:59](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3539)]
Can you hear me?

##### **Geohot** [[00:58:59](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3539)]
Yes.

##### **Chenyu** [[00:58:59](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3539)]
Yep.

##### **Raine** [[00:59:00](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3540)]
Yeah. So we're running on hardware now. With `test_ops` and `test_dtype`, I'm down to about ten failing tests, I think.

##### **Raine** [[00:59:09](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3549)]
I got tensor cores working. I got a little distracted because I found that WMMAs were failing in the emulator, so I'll need to finish that PR, hopefully in a few days. Basically, I'm trying to get to a mergeable state where everything works, even if it's pretty slow. I'm finishing getting the x86 tests passing with regalloc and stuff. I was prototyping a decent waitcnt pass and dual-issue ALU, a couple of smaller performance improvements. But I think I'm going to have to do some decent control-flow refactoring for the ISA layer to merge at branches. I'm looking at how LLVM does some of it, because I had dual-issue and waitcnt working for

##### **Raine** [[00:59:54](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3594)]
half

##### **Raine** [[00:59:55](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3595)]
the tests, but it's

##### **Raine** [[00:59:57](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3597)]
just not clean.

##### **Geohot** [[00:59:58](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3598)]
Don't worry about dual issue. Don't worry about dual-issue ALU. I don't care about that at all. I actually ripped out a whole lot of the performance improvements in x86. We are not at the level where we should care about performance yet.

##### **Geohot** [[01:00:10](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3610)]
We

##### **Geohot** [[01:00:11](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3611)]
should only care if performance is egregiously slow for some reason.

##### **Raine** [[01:00:14](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3614)]
Okay, so it is for waitcnt, because we're basically doing sequential I/O right now. It flushes all the outstanding instructions. I just do an `s_waitcnt 0` after my ops, so that definitely needs to be improved. I implemented a quick version, and it ran quite a bit faster on GEMM, but a lot of tests failed. There's a lot that goes into a proper waitcnt pass.

##### **Raine** [[01:00:41](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3641)]
So like I said,

##### **Raine** [[01:00:41](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3641)]
to merge at branches, you need a better representation of control-flow graph blocks and stuff.

##### **Geohot** [[01:00:47](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3647)]
Are you putting a waitcnt after each load or after each group of loads?

##### **Raine** [[01:00:53](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3653)]
Just each load right now. But I know I can do a group... Even with grouping,

##### **Raine** [[01:00:57](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3657)]
it's still going to be slow.

##### **Raine** [[01:00:58](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3658)]
Like we need

##### **Geohot** [[01:00:59](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3659)]
it to be... Listen, with grouping, it won't be that slow. I think that's where we leave that for now. If

##### **Geohot** [[01:01:04](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3664)]
you're

##### **Geohot** [[01:01:05](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3665)]
doing it

##### **Geohot** [[01:01:05](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3665)]
after...

##### **Raine** [[01:01:05](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3665)]
Just straight

##### **Raine** [[01:01:05](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3665)]
zero?

##### **Geohot** [[01:01:06](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3666)]
Okay. Yeah, you can do zero after the group, and that's fine. I want the GEMM kernel to basically be: do a bunch of loads, wait for the loads to finish, do a bunch of math, and then loop. That's going to be decently fast. I wouldn't worry about optimizing beyond that.

##### **Geohot** [[01:01:23](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3683)]
Again, always readability and low line count over speed. Most speed optimizations end up just falling out.

##### **Geohot** [[01:01:32](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3692)]
They don't...

##### **Geohot** [[01:01:34](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3694)]
Like they're not, oh, I need some very complicated pass to like make these...

##### **Geohot** [[01:01:41](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3701)]
You know, choices.

##### **Raine** [[01:01:41](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3701)]
Yeah. The control flow is already a little dirty, like loop resolution and stuff, even for x86. I still have two failing tests because of how I add source edges to loads. Sometimes the load gets placed outside the RANGE, which causes problems. Basically, I put the address in the source and try to hint to code

##### **Geohot** [[01:02:10](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3730)]
gen. Okay. Here's what you want to do for loads. You don't actually want to handle loads the way they're being handled. You want a rewrite pass beforehand that rewrites gated LOADs to STOREs.

##### **Raine** [[01:02:26](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3746)]
Okay. Oh, yeah. I saw how x86 does that because it does a local load-store, right? It creates a new

##### **Geohot** [[01:02:32](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3752)]
address. x86 is terrible code. We want to move the rewrite pass earlier. It's the same as the LOOP rewrite. Do you understand the RANGE-to-LOOP rewrite?

##### **Raine** [[01:02:43](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3763)]
Yeah.

##### **Geohot** [[01:02:45](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3765)]
You basically want to do that, but for gated LOADs to STOREs. In fact, you can rewrite all LOADs to STOREs. A LOAD is kind of like an anonymous STORE.

##### **Geohot** [[01:02:56](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3776)]
You can allocate a register and then do a STORE there. This works on assembly backends because registers and the ALU are in the same address space.

##### **Raine** [[01:03:06](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3786)]
Yeah.

##### **Geohot** [[01:03:09](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3789)]
But cool. Again, focus on those much more fundamental things. Don't worry about dual-issue ALUs or nonzero waitcnts. Those are not going to get you that much speed. A zero waitcnt after every load will be really slow, but a zero waitcnt at the end of a group of loads will be fast.

##### **Raine** [[01:03:29](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3809)]
Yeah. Even with some of the addressing, sometimes there's a bunch of loads that should be grouped, but there are actually instructions being emitted between them. So another thing is grouping them properly.

##### **Raine** [[01:03:40](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3820)]
I need to work on

##### **Raine** [[01:03:40](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3820)]
that too.

##### **Geohot** [[01:03:42](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3822)]
Yeah. I mean, instructions between them is fine as long as you don't have dependencies, right? Do you mean ALU instructions that are using them? Yeah. Then I would just fix that with a... Mostly just

##### **Raine** [[01:03:50](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3830)]
addressing instructions. So I can probably just emit the waitcnt after the group.

##### **Geohot** [[01:03:54](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3834)]
Well, addressing is fine, right? Because addressing doesn't have any

##### **Raine** [[01:03:57](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3837)]
dependencies. Yeah. It's not dependent on the loads. Yeah. That's fine. Yeah.

##### **Geohot** [[01:04:00](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3840)]
Okay.

##### **Raine** [[01:04:00](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3840)]
So hopefully this week we can be almost mergeable. I'm not saying you need to merge it. But like to the point where it's correct.

##### **Geohot** [[01:04:09](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3849)]
Sounds good. WMMA is important. Dual-issue ALU is not.

##### **Geohot** [[01:04:15](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3855)]
And you should be getting WMMA kernels with BEAM that are maybe 20% slower than LLVM. But it should only be 20%.

##### **Raine** [[01:04:27](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3867)]
In LLVM?

##### **Geohot** [[01:04:28](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3868)]
Yeah.

##### **Raine** [[01:04:29](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3869)]
Yeah. Okay.

##### **Geohot** [[01:04:30](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3870)]
Yeah. I see no reason why a WMMA kernel should be slow, unless it's all in the

##### **Raine** [[01:04:35](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3875)]
instruction.

##### **Geohot** [[01:04:37](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3877)]
Yeah. A lot of the reason you only need to wait at the end of the load group is that you have warps, and warps will hide tons of latency. But if you put it after every single load, the warps can't hide latency anymore because there are more waitcnts than warps. But as

##### **Geohot** [[01:04:55](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3895)]
long as

##### **Geohot** [[01:04:55](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3895)]
you

##### **Geohot** [[01:04:55](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3895)]
have the same...

##### **Raine** [[01:04:57](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3897)]
The other thing is that I do it after a STORE right now, but it should probably be before the instruction that uses the address, because that's the only dependency for the STORE.

##### **Geohot** [[01:05:07](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3907)]
I don't even know if STOREs need waitcnts at all. Do they?

##### **Raine** [[01:05:10](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3910)]
If you reuse the VGPR that has the address in it, I'm pretty sure you have to do a vscnt.

##### **Geohot** [[01:05:16](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3916)]
Double check that. I'm not sure. It could be either way. I'm not sure.

##### **Raine** [[01:05:20](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3920)]
Dependency. Yeah. Okay.

##### **Geohot** [[01:05:23](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3923)]
Yeah. I think that it does register scoreboarding and I'm not sure you need that, but maybe do. Anyway,

##### **Chenyu** [[01:05:29](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3929)]
the idea is to write the correct thing, make it simple, make it look nice, and then worry about the actual speed.

##### **Geohot** [[01:05:39](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3939)]
Yeah. And if you find yourself writing something that's like finicky and tricky, there's another way to write it. I don't care if it's 10% slower.

##### **Raine** [[01:05:45](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3945)]
Yeah. Do you want me to do that WMMA emulation PR? Do you want me to fix that soon, or does it matter? I started it and then thought maybe I should work on the backend instead.

##### **Geohot** [[01:05:56](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3956)]
Do

##### **Geohot** [[01:05:56](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3956)]
things in whatever order you want.

##### **Geohot** [[01:06:00](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3960)]
We don't have testing for integer WMMAs. I don't think the emulator supports them.

##### **Raine** [[01:06:07](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3967)]
Oh, yeah. I fixed GFX12 and RDNA3, but now I need to add scaled...

##### **Raine** [[01:06:17](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3977)]
I think scaled MFMA for CDNA is not in the emulator, and that's kind of annoying. I was getting Codex to help with that. But yeah.

##### **Geohot** [[01:06:23](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3983)]
Yeah. The emulator is slop code anyway. You can put more slop in the slop. The emulator is slop; I wrote the emulator.

##### **Geohot** [[01:06:32](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3992)]
Yeah, well, it's for tests. Tests can be slow. I deeply regret ever writing slop.

##### **Chenyu** [[01:06:39](https://www.youtube.com/watch?v=J4bJVnAjntU&t=3999)]
Maybe we'll clean it up. I think you get the idea. If you think something is totally broken on master, prioritize fixing that. Otherwise, we trust you to prioritize.

##### **Geohot** [[01:06:52](https://www.youtube.com/watch?v=J4bJVnAjntU&t=4012)]
Yeah, yeah, yeah. Whenever you want to get stuff merged. Yeah.

##### **Chenyu** [[01:06:55](https://www.youtube.com/watch?v=J4bJVnAjntU&t=4015)]
Yeah.

##### **Geohot** [[01:06:55](https://www.youtube.com/watch?v=J4bJVnAjntU&t=4015)]
Okay.

##### **Chenyu** [[01:06:56](https://www.youtube.com/watch?v=J4bJVnAjntU&t=4016)]
Sounds good. If you have any questions, just post your PR somewhere and say you have questions.

##### **Chenyu** [[01:07:06](https://www.youtube.com/watch?v=J4bJVnAjntU&t=4026)]
Cool.

##### **Chenyu** [[01:07:07](https://www.youtube.com/watch?v=J4bJVnAjntU&t=4027)]
Is Comma happy?

##### **Chrism** [[01:07:09](https://www.youtube.com/watch?v=J4bJVnAjntU&t=4029)]
Yeah.

##### **Chrism** [[01:07:11](https://www.youtube.com/watch?v=J4bJVnAjntU&t=4031)]
So they're interested in switching to IR3, although apparently their new RL model got reverted, but it's probably going to get unreverted.

##### **Geohot** [[01:07:19](https://www.youtube.com/watch?v=J4bJVnAjntU&t=4039)]
No, it's unreverted. They found the link bug. Oh,

##### **Chrism** [[01:07:21](https://www.youtube.com/watch?v=J4bJVnAjntU&t=4041)]
okay. Anyway, that is apparently slower with IR3. So we're going to start testing that one.

##### **Chenyu** [[01:07:26](https://www.youtube.com/watch?v=J4bJVnAjntU&t=4046)]
If you add it somewhere, I'll have my Codex look at it.

##### **Chrism** [[01:07:30](https://www.youtube.com/watch?v=J4bJVnAjntU&t=4050)]
All the slowness is in that CONCAT kernel. In fact, if you go into `onyx.py`, replace CONCAT with `Tensor.cat`, and put CONTIGUOUS on all the inputs to CONCAT, it becomes much faster.

##### **Chenyu** [[01:07:46](https://www.youtube.com/watch?v=J4bJVnAjntU&t=4066)]
Great. Let's just add that to the OpenPilot hack and call it a day.

##### **Geohot** [[01:07:49](https://www.youtube.com/watch?v=J4bJVnAjntU&t=4069)]
Want to add CONTIGUOUS on those? Yeah, just add CONTIGUOUS.

##### **Chenyu** [[01:07:54](https://www.youtube.com/watch?v=J4bJVnAjntU&t=4074)]
We already have an OpenPilot hack flag. Use that.

##### **Chrism** [[01:07:59](https://www.youtube.com/watch?v=J4bJVnAjntU&t=4079)]
Sure. Yeah.

##### **Chenyu** [[01:08:00](https://www.youtube.com/watch?v=J4bJVnAjntU&t=4080)]
Or are you saying you're going to fix that? I don't know.

##### **Geohot** [[01:08:03](https://www.youtube.com/watch?v=J4bJVnAjntU&t=4083)]
No, no. Codex can take a stab at it; don't worry.

##### **Chenyu** [[01:08:07](https://www.youtube.com/watch?v=J4bJVnAjntU&t=4087)]
Okay. If it's only that, just add a flag and we'll worry about it later.

##### **Geohot** [[01:08:12](https://www.youtube.com/watch?v=J4bJVnAjntU&t=4092)]
I wouldn't make it totally non-generic. I wouldn't make it detect that kernel specifically. I would say that if a kernel has tons of inputs, put CONTIGUOUS on all of them. That can be an OpenPilot hack, and it's a rangeify rule. It's two lines in rangeify.

##### **Chrism** [[01:08:26](https://www.youtube.com/watch?v=J4bJVnAjntU&t=4106)]
Okay. That's

##### **Geohot** [[01:08:26](https://www.youtube.com/watch?v=J4bJVnAjntU&t=4106)]
fine.

##### **Chrism** [[01:08:26](https://www.youtube.com/watch?v=J4bJVnAjntU&t=4106)]
All right.

##### **Chrism** [[01:08:28](https://www.youtube.com/watch?v=J4bJVnAjntU&t=4108)]
Yeah. Anyway, that kernel is always the kernel that causes problems.

##### **Chrism** [[01:08:32](https://www.youtube.com/watch?v=J4bJVnAjntU&t=4112)]
That's always the one that's slow.

##### **Geohot** [[01:08:33](https://www.youtube.com/watch?v=J4bJVnAjntU&t=4113)]
Yeah. Because why? It's not because it's trying to fuse with the things above it.

##### **Chrism** [[01:08:36](https://www.youtube.com/watch?v=J4bJVnAjntU&t=4116)]
It's fusing about ten GEMMs into a CONCAT kernel with different shapes.

##### **Chenyu** [[01:08:41](https://www.youtube.com/watch?v=J4bJVnAjntU&t=4121)]
Also, that's also an IR3 issue. IR3 cannot lower that properly.

##### **Geohot** [[01:08:46](https://www.youtube.com/watch?v=J4bJVnAjntU&t=4126)]
It's not an IR3 issue.

##### **Chrism** [[01:08:49](https://www.youtube.com/watch?v=J4bJVnAjntU&t=4129)]
Qualcomm.

##### **Chenyu** [[01:08:50](https://www.youtube.com/watch?v=J4bJVnAjntU&t=4130)]
The ranges are all just totally messed up.

##### **Geohot** [[01:08:51](https://www.youtube.com/watch?v=J4bJVnAjntU&t=4131)]
I see what it's doing. It can't take a global dimension across the things.

##### **Chenyu** [[01:08:56](https://www.youtube.com/watch?v=J4bJVnAjntU&t=4136)]
No problem.

##### **Chrism** [[01:08:59](https://www.youtube.com/watch?v=J4bJVnAjntU&t=4139)]
I mean, I think it's faster. I'll double check. I'm pretty sure it's faster for CL as well.

##### **Geohot** [[01:09:04](https://www.youtube.com/watch?v=J4bJVnAjntU&t=4144)]
Wait, wait. If it doesn't improve both of them, I don't want to add the OpenPilot hack. But if it clearly improves both of them.

##### **Chrism** [[01:09:08](https://www.youtube.com/watch?v=J4bJVnAjntU&t=4148)]
I'm pretty sure.

##### **Chenyu** [[01:09:09](https://www.youtube.com/watch?v=J4bJVnAjntU&t=4149)]
Yeah.

##### **Chenyu** [[01:09:11](https://www.youtube.com/watch?v=J4bJVnAjntU&t=4151)]
I can believe that. Okay. Great. I think that's it for this meeting. Anything else?

##### **Geohot** [[01:09:16](https://www.youtube.com/watch?v=J4bJVnAjntU&t=4156)]
Is Kimi downloaded?

##### **Chenyu** [[01:09:20](https://www.youtube.com/watch?v=J4bJVnAjntU&t=4160)]
Oh, it's slow.

##### **Geohot** [[01:09:25](https://www.youtube.com/watch?v=J4bJVnAjntU&t=4165)]
Yay. Kimi by tonight.

##### **Chenyu** [[01:09:28](https://www.youtube.com/watch?v=J4bJVnAjntU&t=4168)]
Just post somewhere when you're done downloading, and we'll see what we do with that. Cool. All right. That's it for this meeting. Thank you, everyone. See you next week. Bye-bye.

##### **Geohot** [[01:09:40](https://www.youtube.com/watch?v=J4bJVnAjntU&t=4180)]
Bye. Bye.

##### **Chrism** [[01:09:42](https://www.youtube.com/watch?v=J4bJVnAjntU&t=4182)]
Bye. Bye. Bye.
