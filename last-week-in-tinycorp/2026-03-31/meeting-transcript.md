# 2026-03-31 Meeting

### Meeting Agenda

**Time:** new meeting #12, 3/30 9pm Monday San Diego time
- company update
- viz SQTT
- new jit
- llama training, flat llama
- custom driver
- mixin, more Tensor cleanups
- IMAGE, device target
- other issues, bounties, any karma complaints


### Audio

[Youtube Link](https://www.youtube.com/watch?v=yyXjuQHvx6E)

### Highlights

- **[Company update: sales and Huawei compiler discussion](#geohot-000008)**: The team resumed box sales with three green boxes and one red box sold recently, memory prices are falling again, and Geohot met with Huawei’s compiler team about Ascend support while reiterating that any hardware support must come through normal open-source pull requests.
- **[Huawei support must stay open-source-only](#geohot-000218)**: Geohot said sanctions mean they cannot directly help Huawei as a U.S. business, but they can still merge open-source support for Huawei accelerators as long as the work is public and equally available to everyone.
- **[SQTT visualization got much more usable](#qazalin-000421)**: Qazalin reported major progress on the SQTT tooling, including a better CLI, improved UI, colored VAMIs, and cycle visualizations that make memory issues like bank-conflict-induced gaps much easier to spot.
- **[SQTT “other” instructions should be assigned to waves](#geohot-000812)**: Geohot pushed back on the new “other” bucket in the visualization and argued those dispatches should instead be broken down onto waves, while also confirming LDS can overlap with LDS-Alt but not with itself.
- **[Goal: let Claude design kernels beyond the state of the art](#geohot-001238)**: Geohot said they want Claude to use the profiling and kernel tooling to produce better-than-state-of-the-art kernels, and if the DSL gets in the way, the model should be allowed to work directly in assembly.
- **[New JIT captures linear ops and may add a beam UOp](#nimlgen-001445)**: Nimlgen said the updated JIT now captures linear execution, enabling movement of the memory planner and graph construction into ops; Geohot suggested representing beam search as a dedicated beam UOp near the sink in the graph rewrite engine.
- **[Apple approved the needed DriverKit entitlement](#geohot-001651)**: Geohot said Apple approved the “DriverKit user client access” entitlement, which should unblock easier installation and testing of the custom driver on Apple hardware.
- **[Two-machine training should look like one 12-GPU system](#geohot-001838)**: Geohot outlined a plan for multi-node training where two remotes would simply enumerate as GPUs `amd0` through `amd11`, with tensor graphs staying unaware of machine boundaries and transport decisions handled only in late copy lowering.
- **[FlatLlama with FP32 master weights is converging better](#wozeparrot-002619)**: Wozeparrot reported that FlatLlama runs with FP32 master weights and stochastic rounding both converge correctly, with FP32 master weights converging faster and currently landing at about 6 hours 19 minutes.
- **[Custom ASM firmware is close and should massively improve transfer speed](#geohot-003342)**: Geohot said the new firmware already has USB 2, USB 3, and PCIe working, makes TLP access about 10× faster, and should eventually provide a slow direct PCIe path in the 1–5 MB/s range plus a DMA path potentially reaching 100–500 MB/s.
- **[Tensor cleanup: move more methods out of `tensor.py`](#chenyu-004019)**: Chenyu described ongoing mixin refactors that moved more broadcast, reduce, and dtype-promotion logic out of `tensor.py`; Geohot agreed the core `Tensor` class should shrink dramatically and mostly just hold state.
- **[Device targeting is shifting to `DEV=` syntax](#chrism-004829)**: Chrism said the new device-target environment syntax is moving from per-device env vars like `CPU=1` or `CL=1` to a unified `DEV=...` form, with image creation now delayed until late codegen and further syntax details to be timeboxed and finalized after some real usage.

### Transcript
##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=0)]
Okay, welcome everyone. Let's get started with company update.

##### **Geohot** [[00:00:08](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=8)]
So we've been selling boxes again. Three green boxes in the last like week, week and a half. And one red box. That's pretty good. We had a bit of a lull for that. The memory prices are coming back down. That's pretty good too. We didn't overbuy, we didn't panic. Everything was good on that front. At a meeting with the Hong Kong Huawei compiler team yesterday, working on the compiler for the Ascend chips. So apparently there's a dev kit that you can buy that has an Ascend chip.

##### **Geohot** [[00:00:48](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=48)]
Huawei, but overall it seemed pretty behind.

##### **Geohot** [[00:00:57](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=57)]
The Orange Pi, it's like a collaboration. This one.

##### **Geohot** [[00:01:07](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=67)]
You know, overall, it seems pretty behind GPUs, and it's not very open source. The assembly language is in open source, but they say they're going to open source everything. So, you know, I know that they think they have to interact with like a company and like get something official. But I was just like the same rules that apply to you apply to everybody else. You want to, you know, they were like, oh, we can offer you engineers. I'm like, well, I got to manage engineers. That's ridiculous. I said basically the same thing that applies to anyone here, which is if you submit a pull request and your pull request meets our standards and it supports hardware that is available on the open market, we're happy to upstream it.

##### **Geohot** [[00:01:53](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=113)]
We're talking about this chip. I mean, this board is like, where is the Huawei chip? Is the middle thing the Huawei chip?

##### **Geohot** [[00:02:05](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=125)]
What else? But yeah, that happened.

##### **Geohot** [[00:02:08](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=128)]
That's pretty much it. Do they want MLPerf?

##### **Geohot** [[00:02:18](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=138)]
No, they didn't. Well, OK, so there's also a potential issue with. Sanctions. And working with Huawei. So I looked into it. There's two basic things. As long as everything is open source and available equally to everybody, the sanctions don't really apply. But we're not allowed to like, yeah, directly as a U.S. business, even as a U.S. citizen. We're not allowed to directly help Huawei. But if they fund open source efforts, that's totally. Fine. And obviously we can merge support for their accelerators. There's also some weird stuff around model training. So, yeah, I don't know about that.

##### **Geohot** [[00:03:05](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=185)]
But, you know, so we'll see. Great. Sounds good.

##### **Geohot** [[00:03:15](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=195)]
They also have this AI station.

##### **Geohot** [[00:03:19](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=199)]
Oh, this one looks more reasonable, actually.

##### **Qazalin** [[00:03:23](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=203)]
Yeah. So.

##### **Geohot** [[00:03:34](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=214)]
What are these things?

##### **Geohot** [[00:03:40](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=220)]
They don't have the buy link. It doesn't work. No, I don't think this is out yet. They've been teasing this on their Twitter for a bit. Interesting. But they're probably real, and they can send us some. I think this is actually the one they're talking about. I don't think it's the other one. I don't really know what the other one is.

##### **Geohot** [[00:04:13](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=253)]
Sounds good.

##### **Chenyu** [[00:04:15](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=255)]
Let's move on. The first item is this.

##### **Qazalin** [[00:04:21](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=261)]
Yeah, this got some progress. The CLI is much better now and much more usable. The UI is much nicer. Right now, you can see if you run with `VIZ=2`, especially with VMEM, you can see the VMEMs colored differently and the execs showing the cycle numbers. So it's actually not the number of cycles. I think it's a fixed thing, because it exists for memory too. It's the number of cycles that it would take at issue. So if you have bank conflicts, you would have huge gaps between your LDS execs. That was an interesting pattern that I saw.

##### **Geohot** [[00:05:10](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=310)]
Oh, you mean that the number in the thing isn't the actual number

##### **Geohot** [[00:05:22](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=322)]
of cycles?

##### **Qazalin** [[00:05:24](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=324)]
Oh, it is the number of cycles. Like, it says that a store takes two cycles. Well, yeah, but if you have bank conflicts,

##### **Geohot** [[00:05:32](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=332)]
it's going to take more.

##### **Geohot** [[00:05:34](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=334)]
That doesn't have to do with the instruction. There's the submission and the completion.

##### **Geohot** [[00:05:42](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=342)]
Correct.

##### **Qazalin** [[00:05:44](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=344)]
So if you would have bank conflicts, you would be having gaps.

##### **Geohot** [[00:05:48](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=348)]
Yeah, you'd have gaps, and that's totally expected. Nothing's wrong with that. If I have WMMAs, I'm supposed to see them show up. Where is it?

##### **Geohot** [[00:06:11](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=371)]
Yeah, if you have a WMMA, it says.

##### **Geohot** [[00:06:14](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=374)]
Is the thing at the end of the, so you have the 32 cycles. Is that, is the timestamp at the end? Or at the beginning?

##### **Geohot** [[00:06:25](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=385)]
Timestamp is at the end.

##### **Geohot** [[00:06:29](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=389)]
Timestamp's at the end. OK, so you extend backwards. And you extend backwards for everything.

##### **Geohot** [[00:06:34](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=394)]
Extend backwards for everything. Cool.

##### **Geohot** [[00:06:45](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=405)]
And we don't have any more.

##### **Geohot** [[00:06:47](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=407)]
Timestamp is fixed.

##### **Geohot** [[00:06:48](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=408)]
The overlaps are fixed?

##### **Qazalin** [[00:06:51](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=411)]
The overlaps exist. And they're normal for LDS and VMEM?

##### **Geohot** [[00:06:57](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=417)]
Are you sure about that? They exist. So I think there's some bug on RDNA. I don't think so. No, I'm sure there is.

##### **Geohot** [[00:07:14](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=434)]
I don't think so. So on RDNA,

##### **Geohot** [[00:07:19](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=439)]
everything was right. OK. Sorry, go ahead?

##### **Geohot** [[00:07:23](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=443)]
From what I saw, everything was correct. How are you getting this thing called other? It's just the other instructions.

##### **Geohot** [[00:07:46](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=466)]
And they're not on a wave?

##### **Geohot** [[00:07:50](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=470)]
They are on a wave. But they're only on a wave. They're only issued once.

##### **Geohot** [[00:07:54](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=474)]
What do you mean, only issued once?

##### **Qazalin** [[00:07:57](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=477)]
It doesn't. So there's only one issue of those other instructions

##### **Geohot** [[00:08:04](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=484)]
per cycle.

##### **Geohot** [[00:08:09](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=489)]
I don't follow. So I see a thing now called other.

##### **Geohot** [[00:08:12](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=492)]
I see a tab now called other. And I don't think that's right. I think those should be on a wave.

##### **Qazalin** [[00:08:19](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=499)]
But the wave exists. But we don't know which name they bring. So it's like all the other instruction types, right? So from what I saw, it's that.

##### **Geohot** [[00:08:33](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=513)]
I'm visualizing everything.

##### **Geohot** [[00:08:34](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=514)]
So if it's.

##### **Qazalin** [[00:08:36](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=516)]
Yeah.

##### **Geohot** [[00:08:37](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=517)]
But they should not be. There should not be something called other. There should be a wave.

##### **Qazalin** [[00:08:46](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=526)]
But it's not the same wave as the wave that you're visualizing there. Right? It's the other instruction types.

##### **Geohot** [[00:08:56](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=536)]
Do they call it other? Is that their name for it?

##### **Qazalin** [[00:08:59](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=539)]
Yeah. It's the other SIMD.

##### **Geohot** [[00:09:02](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=542)]
It's the other . But I think like right now you have this thing called other. And I really think that those dispatches belong on waves.

##### **Qazalin** [[00:09:11](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=551)]
So you want to break it down by wave? Yeah, I can do that. I mean. Yeah. I can do that.

##### **Geohot** [[00:09:17](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=557)]
But it's just that it's not issued simultaneously.

##### **Geohot** [[00:09:24](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=564)]
I don't follow that.

##### **Geohot** [[00:09:26](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=566)]
And I definitely see overlap. I see overlap in LDS. But the only overlap I see is between LDS and LDS-Alt, which is fine.

##### **Geohot** [[00:09:37](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=577)]
Yes. LDS does overlap a lot.

##### **Geohot** [[00:09:40](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=580)]
LDS can overlap with LDS-Alt. But it can't overlap with itself. LDS and LDS-Alt should almost be two different devices.

##### **Geohot** [[00:10:07](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=607)]
See what I mean? Yeah.

##### **Geohot** [[00:10:11](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=611)]
Those other things have to go on a wave.

##### **Qazalin** [[00:10:15](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=615)]
Yeah. So it's not just a wave. Yeah.

##### **Geohot** [[00:10:23](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=623)]
So I think it's the same thing.

##### **Geohot** [[00:10:23](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=623)]
Yeah. I really like these. Super nice. I wonder why there's gaps between them. I wonder if you could do stuff with the registers, like register cache miss or something.

##### **Qazalin** [[00:10:42](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=642)]
Oh God, there's so many white spaces. So I got a 100 teraflop RDNA3 GEMM, and I profiled it with the same thing. It's in the best channel, before and after. Left is that GEMM and right is our 67 teraflop.

##### **Geohot** [[00:11:06](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=666)]
You have it to the point where, is the CLI good enough that Claude can improve it?

##### **Qazalin** [[00:11:15](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=675)]
Claude can tell you exactly what's wrong. It can give you a very good plan. When it tries to implement it, it is miserable.

##### **Geohot** [[00:11:25](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=685)]
Trying to implement it in assembly or in Hint?

##### **Geohot** [[00:11:30](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=690)]
In DSL. In UOPs.

##### **Geohot** [[00:11:36](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=696)]
Why is it bad at implementing this?

##### **Qazalin** [[00:11:41](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=701)]
On the tricky side. When you try to do specialization and it can't be done because you also don't have `if`-`then`, stuff like that, it would give up saying that the DSL is not good and not supportive of what it wants to

##### **Geohot** [[00:11:58](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=718)]
do. Sick. I'll have to try that.

##### **Qazalin** [[00:12:08](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=728)]
I'm going to try that.

##### **Geohot** [[00:12:17](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=737)]
Our path is still doing it with the UOp DSL and going through LLVM.

##### **Qazalin** [[00:12:26](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=746)]
Got it.

##### **Geohot** [[00:12:37](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=757)]
Yeah.

##### **Geohot** [[00:12:38](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=758)]
I think pick up the other thing, and then just like, if it's complaining about the DSL, try it on the assembly one. You can write one with WMMAs in assembly. I mean, I want to get to the point where Claude can use the CLI and make kernels that are beyond the state of the art.

##### **Geohot** [[00:13:03](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=783)]
I think it should be able to.

##### **Geohot** [[00:13:13](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=793)]
And if it can't use the DSL, it can't use the DSL.

##### **Geohot** [[00:13:16](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=796)]
Let it just use assembly.

##### **Chenyu** [[00:13:19](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=799)]
What's the best one we have now? I would try this later.

##### **Geohot** [[00:13:24](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=804)]
The best one we have. Well, so the one that I've really put effort into for assembly is the FP32 one. And we can get like, it's like

##### **Geohot** [[00:13:33](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=813)]
58 teraflops or something. Theoretically, I think you can get like 70. Yeah.

##### **Geohot** [[00:13:44](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=824)]
But we also don't have a good assembly.

##### **Geohot** [[00:13:48](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=828)]
One that's using the WMMA instructions and stuff.

##### **Geohot** [[00:13:51](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=831)]
And that one, I think Torch can get like 110,

##### **Geohot** [[00:13:55](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=835)]
theoretical is like 130, 140.

##### **Chenyu** [[00:13:56](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=836)]
Oh, that's pretty good. Okay.

##### **Chenyu** [[00:14:01](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=841)]
How about that's for the fixed size? Like, max if you sweep over some sizes, the best one.

##### **Geohot** [[00:14:07](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=847)]
No, no, no, no, no. This is just one 496 by 496.

##### **Qazalin** [[00:14:11](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=851)]
Yeah.

##### **Geohot** [[00:14:11](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=851)]
You can probably do it doesn't really matter.

##### **Geohot** [[00:14:15](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=855)]
Like, that shouldn't really be a problem.

##### **Geohot** [[00:14:22](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=862)]
Sounds good. Anything else for this?

##### **Geohot** [[00:14:27](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=867)]
I think that's it.

##### **Geohot** [[00:14:33](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=873)]
Well, next is the new JIT.

##### **Nimlgen** [[00:14:45](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=885)]
So it's actually the old JIT. But now it captures linears. So, yeah. And because of that, I can move the memory planner and JIT graph into the UOps. So, yeah, that's done. So the next thing I think I'm going to do is actually I would like to switch `capture_graph` to linears as well, and to not capture exec items. But the current blocker is beam kernels. I need to take a look at that and do something around beam kernels, because currently they won't capture. And also, I'm looking towards removing `Runner`. So I think I'm going to come up with some spec and put that on our GitHub. So, yeah.

##### **Geohot** [[00:15:56](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=956)]
So what I always imagined for beam was imagine we can make a beam UOp. And then the graph rewrite of the beam UOp is what triggers the beam. Right. So if you have beam set, what you want to do is you just want to put a beam UOp, probably right under the sink. So normally when it goes to, like, sink-call, it'll just be sink-beam-call. And then whenever you have that beam thing, you run beam on that sink.

##### **Geohot** [[00:16:26](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=986)]
Uh-huh.

##### **Geohot** [[00:16:28](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=988)]
And that's all in the graph rewrite engine.

##### **Geohot** [[00:16:31](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=991)]
It's pretty simple.

##### **Geohot** [[00:16:39](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=999)]
Okay. Yeah. Thanks. Also, did you see the Apple e-mail this morning? Is it the right thing?

##### **Nimlgen** [[00:16:48](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1008)]
I haven't seen it yet.

##### **Geohot** [[00:16:51](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1011)]
It should be there.

##### **Geohot** [[00:16:52](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1012)]
Yeah. Yeah. I got an e-mail from Apple saying that they approved us for something.

##### **Geohot** [[00:16:56](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1016)]
Hopefully it's the right thing. The DriverKit user client access entitlement.

##### **Nimlgen** [[00:17:06](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1026)]
Yeah. That sounds right.

##### **Geohot** [[00:17:08](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1028)]
Sweet. Yeah. That was great. be great if we have that you know there's that guy asking for it if we have some instructions i think we could probably get like there's probably like at least 10 people out there

##### **Geohot** [[00:17:19](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1039)]
who will quickly install it on a Mac and use it

##### **Nimlgen** [[00:17:30](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1050)]
yeah we'll do it um also i merged the like the melanox driver so it's clean up and i just put

##### **Geohot** [[00:17:38](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1058)]
it in extra for now um so yeah uh so with that yeah how easy would it be to just uh be training across two computers

##### **Geohot** [[00:17:58](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1078)]
um

##### **Nimlgen** [[00:17:58](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1078)]
i think it's like from the hardware and all of these things it should be not that hard but yeah we need to we need some way to describe topology like in the upper layers so i think we discussed that that we want like basically to have like the custom europe of copies and that already on the like maybe late europe level should describe like if it's transfer if it's melanox so if it's like the regular

##### **Geohot** [[00:18:38](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1118)]
right yeah so i think there's kind of like there's two things that should be separate here um so so okay let's let's talk concretely about what the goal is um for any one of our trainers like our resident trainer that supports multiple gpus uh the api to train across two computers just be like basically i think the prerequisite to training across the computers is being able to specify two remotes um so i think the core of that is to have two remotes like you could specify two remotes and then if each computer has six gpus you're just going to get amd 0 to 11. this is how i imagine it um if you have this amd 0 to 11 uh enumeration in a single thing you know that one process right i imagine that process not having any gpus in it itself like i think that we don't support uh a process having both locals and remote it would be remote across the internet being able to run or go to different environments or using that kind of two computers back to two ips all that stuff um so then the topology description like how we do the all reduce is a separate question from what the like physical thing doing the copy is um so i'm fine with any kind of like hard-coded thing in the all reduce ring thing like specify whatever you want the topology to be for now um and then when you actually go to like lower the copy when you lower the copy in the same way we currently like lower the copy and the copy is implicitly sdma it shouldn't implicitly be sdma it should be like oh you want to copy from gpu amd6 to amd11 okay those are on separate remotes we have to copy across the uh the melano for that yeah the end goal here would be to be able to launch like a resnet trainer on let's even say for simplicity a third computer

##### **Geohot** [[00:20:34](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1234)]
and then have that resnet trainer uh use the gpus in computer one and computer two as well

##### **Chenyu** [[00:20:44](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1244)]
so if you want the shard to be on amd 0 through 11 or 15 and who hold like what holds this information that is actually two machines

##### **Geohot** [[00:20:59](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1259)]
so that's all at a much lower level so there's there's two reasons you have to know that it's two machines um one is to figure out what your all reduced topology is going to be and it actually might not change it i think your all reduced apology might not be changed at all i think it's the same ring across two machines yeah i think i think i think for two

##### **Chenyu** [[00:21:18](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1278)]
is fine it's more of a okay so you don't want this to be in your tensor graph because you still want to abstract it as like just 12 gpus well yeah it's definitely not your tensor graph

##### **Geohot** [[00:21:28](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1288)]
Your tensor graph doesn't include anything about even how to do an all-reduce. So we do this multipass, which creates this UOp all-reduce. There's a UOp called all-reduce, and then the lowering of that UOp all-reduce to a bunch of ring copies is what does that. But yeah, I think it's just the same ring. It'd be the same ring if you're going across two computers. It would only be in the late UOps that you actually have to say, oh, you're trying to do a copy from GPU6 to GPU7? Okay, those are on separate machines. You have to go across the Mellanox.

##### **Geohot** [[00:22:04](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1324)]
Oh, yeah.

##### **Chenyu** [[00:22:05](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1325)]
It's more of a practically, where do you want to store or specify this information?

##### **Geohot** [[00:22:12](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1332)]
I think it's like the…

##### **Chenyu** [[00:22:14](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1334)]
Previously, everything's kind of describing the tensor graph itself, right? You can just take a graph and know what compute would be done where, kind of.

##### **Geohot** [[00:22:22](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1342)]
Yeah, I don't think that the tensor graph… I don't think that you need to know that anything is special in the tensor graph. Yeah. …without two machines. I think it's just GPU0 to GPU1.

##### **Chenyu** [[00:22:33](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1353)]
Oh, yeah. Okay, so you're saying tensor graph doesn't need to be aware there's even two machines.

##### **Qazalin** [[00:22:40](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1360)]
Yeah.

##### **Chenyu** [[00:22:41](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1361)]
Okay.

##### **Geohot** [[00:22:43](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1363)]
Does that match what you think?

##### **Geohot** [[00:22:47](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1367)]
Yeah. Yeah.

##### **Geohot** [[00:22:51](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1371)]
Yeah, I think you're right. I think we're overthinking it with the topology thing. We don't even have to worry about that. We just need to worry.

##### **Geohot** [[00:22:58](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1378)]
We don't need to worry about what the physical transport layer is doing to copy. That didn't lay you off.

##### **Geohot** [[00:23:05](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1385)]
How does this work?

##### **Wozeparrot** [[00:23:08](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1388)]
How does this work with, like, the MI machines? One card per…

##### **Geohot** [[00:23:22](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1402)]
I don't get it. Can you repeat?

##### **Geohot** [[00:23:24](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1404)]
Can you repeat? They have one…

##### **Geohot** [[00:23:27](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1407)]
…card per… …card per GPU.

##### **Geohot** [[00:23:30](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1410)]
The MI machines have eight cards, and one is, like, connected on a PCI switch to each GPU.

##### **Geohot** [[00:23:44](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1424)]
Yeah. Yeah.

##### **Qazalin** [[00:23:56](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1436)]
Oh.

##### **Geohot** [[00:23:56](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1436)]
So, I think that the way that you deal with that is you just kind of have, like… So, right now, we actually make an opinionated decision here. When you're copying from GPU 0 to GPU 1, there's actually two ways to do this. You could use the SDMA controller on GPU 0 to push the GPU 1, or you can use the SDMA controller on GPU 1 to pull from SDMA 0… from GPU 0.

##### **Geohot** [[00:24:24](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1464)]
Yeah.

##### **Geohot** [[00:24:25](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1465)]
Yeah. Yeah. Yeah. Yeah. Yeah. I would expect a kind of consolidated stance on that. But I think that specifying that is the same problem as specifying kind of, like, when you have a pair of GPUs, what's your transport like? Right? If I copy from GPU 0 to GPU 1, I can use three potential transport lengths. I can use SDMA on GPU 0, SDMA on GPU 1, or I can use a kernel… I guess, actually, four. I can use a kernel on GPU 0 or a kernel on GPU 1. Yep. The way that we specify the eight network cards is just saying, when you're doing a copy from GPU A to GPU…

##### **Geohot** [[00:24:56](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1496)]
and you use this network card.

##### **Geohot** [[00:25:08](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1508)]
I'm okay with also, like, I don't think we necessarily have to deal with how to generically specify topologies right now. We can just kind of put in some really dumb heuristic, like saying, pick the network card that has the closest PCI ID or something.

##### **Geohot** [[00:25:35](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1535)]
Are we going to have this soon?

##### **Chenyu** [[00:25:38](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1538)]
I think it would be cool if we submit AB with also training on two machines.

##### **Geohot** [[00:25:47](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1547)]
I think I can do that probably in a week.

##### **Chenyu** [[00:25:53](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1553)]
Yeah, I think as long as we have this stable in the next two or three weeks, we can also submit that as part of the ML perf.

##### **Geohot** [[00:26:03](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1563)]
That'd be amazing. Yeah, I like this.

##### **Geohot** [[00:26:07](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1567)]
Cool. That's good. Anything else? No.

##### **Chenyu** [[00:26:15](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1575)]
Next is Lama.

##### **Wozeparrot** [[00:26:19](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1579)]
Flatch merged a bunch of runs last week with a bunch of different things to do. We're going to have to see if we can and try to make it converge faster and, like, correct. So FP32 master weights and stochastic rounding both converge correctly with the ML perf in it. Master weights converge faster than rounding does. That's the latest run that I have.

##### **Geohot** [[00:26:47](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1607)]
How much faster?

##### **Wozeparrot** [[00:26:49](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1609)]
Six hours, 19 minutes. That's master weights.

##### **Geohot** [[00:26:53](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1613)]
That's master weights.

##### **Wozeparrot** [[00:26:55](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1615)]
That's FP32 master weights.

##### **Geohot** [[00:26:56](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1616)]
Would you post these 1-2-B links? Would you include the description?

##### **Geohot** [[00:27:03](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1623)]
Legit description. I can include something that says this is not . This is not . I think most of my . Oh.

##### **Geohot** [[00:27:25](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1645)]
Enter. That's better. OK. OK.

##### **Geohot** [[00:27:34](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1654)]
Yeah. I will post something that says it. Usually I do.

##### **Wozeparrot** [[00:27:37](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1657)]
I don't know why I didn't put the latest one.

##### **Chenyu** [[00:27:44](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1664)]
So when you say faster, like, in terms of number of examples compared to the RCP or from other people's submission,

##### **Wozeparrot** [[00:27:52](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1672)]
is it close? From other people's submission.

##### **Chenyu** [[00:27:55](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1675)]
Yeah.

##### **Wozeparrot** [[00:27:55](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1675)]
So with FP32, I think the FP32 master weights were very close.

##### **Geohot** [[00:27:59](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1679)]
Yeah. So I see 184,000 for the FP32 master weights one and 221,000 for the other. What's their submission?

##### **Wozeparrot** [[00:28:10](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1690)]
NVIDIA submission is 175, I think.

##### **Qazalin** [[00:28:15](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1695)]
OK.

##### **Geohot** [[00:28:21](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1701)]
And then, yeah, what are we going to need to make this go faster?

##### **Geohot** [[00:28:24](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1704)]
Did you do the call? Did you do the fix up yet? Not like, re-compute things?

##### **Wozeparrot** [[00:28:29](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1709)]
Well, I guess remove. So these runs have function removed.

##### **Geohot** [[00:28:32](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1712)]
OK.

##### **Wozeparrot** [[00:28:33](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1713)]
How much slower is it with function? Function is 7 hours 41. OK. Yeah.

##### **Geohot** [[00:28:41](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1721)]
We got to fix function and get that to work and be the same speed. Just figure out what you want to save.

##### **Geohot** [[00:28:48](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1728)]
Even if you save everything, that's fine. But I want it to work with function.

##### **Wozeparrot** [[00:28:53](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1733)]
And AMD did get back to me on. The machines. I don't know if you've been following the email thread.

##### **Geohot** [[00:29:02](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1742)]
Oh, I might have been taken off of it. I saw they got back. I saw you sent a bunch of stuff and then I didn't see another follow up.

##### **Wozeparrot** [[00:29:08](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1748)]
Oh, interesting. Because you are CC'ed in the thread. Maybe he CC'ed the wrong email. I'm not sure. Yeah. There's some. Apparently, most of our machines are bad. There's.

##### **Geohot** [[00:29:20](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1760)]
Oh, I see. Yeah, yeah, yeah. He wants to RMA a bunch of GPUs.

##### **Wozeparrot** [[00:29:23](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1763)]
A bunch of GPUs.

##### **Geohot** [[00:29:26](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1766)]
Wait, he thinks one of them is bad in Tiny 3?

##### **Geohot** [[00:29:30](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1770)]
Yeah, I'm confused about that. Yeah. OK, I'll get back to us on hardware update next week. Yeah.

##### **Geohot** [[00:29:41](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1781)]
I also think we should ask nicely and keep the broken GPUs. I'd like to play with them this summer and see

##### **Geohot** [[00:29:47](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1787)]
if we could bring them up with our PCIe adapter cards.

##### **Geohot** [[00:29:51](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1791)]
OK.

##### **Geohot** [[00:29:58](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1798)]
Yeah, OK. Yeah, they said they'd get back to us next week.

##### **Qazalin** [[00:30:01](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1801)]
Yeah.

##### **Wozeparrot** [[00:30:02](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1802)]
So I'm just waiting for that. I need to send him the software stuff too. I'm not entirely sure what BKC is.

##### **Geohot** [[00:30:12](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1812)]
Yeah, I don't know. Catchy-kitchy-smicky. So hoping that we can submit for two machines,

##### **Wozeparrot** [[00:30:24](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1824)]
but we kind of need two machines. Two machines that work.

##### **Geohot** [[00:30:28](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1828)]
This should be fast. Yeah, no, I mean, I don't understand. Why are we getting such a bad time? I mean, why are they getting two hours, and we're only getting, oh, how about FBA? Have you tried that?

##### **Wozeparrot** [[00:30:40](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1840)]
I have not tried FBA. Is FBA gem merged? I don't think I saw.

##### **Geohot** [[00:30:48](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1848)]
It's a version.

##### **Wozeparrot** [[00:30:49](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1849)]
OK, I will try FBA.

##### **Geohot** [[00:30:52](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1852)]
Wait, Kazal, it's merged or it's not?

##### **Qazalin** [[00:30:54](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1854)]
It's not merged.

##### **Wozeparrot** [[00:30:56](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1856)]
Yeah.

##### **Geohot** [[00:30:56](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1856)]
Oh, yeah, let's get that.

##### **Wozeparrot** [[00:30:59](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1859)]
And then the other thing is AMD runs with batch size 16. Last time I tried batch size 16, it was the same speed.

##### **Geohot** [[00:31:14](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1874)]
Yeah, I think we should match their batch size, but it's probably a big deal.

##### **Wozeparrot** [[00:31:18](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1878)]
It was actually slightly slower because the gem hit worse shapes.

##### **Geohot** [[00:31:30](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1890)]
So I'm going to try this one.

##### **Geohot** [[00:31:31](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1891)]
Let's see. ChatGPT says BKC stands for best known configuration.

##### **Wozeparrot** [[00:31:36](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1896)]
Best known configuration. Oh, I see.

##### **Geohot** [[00:31:41](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1901)]
This is a software update? No, it's just like an acronym because AMD loves acronyms.

##### **Geohot** [[00:31:49](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1909)]
OK, great.

##### **Qazalin** [[00:32:02](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1922)]
OK, so, well, I just need to do this first. I can make calls on my id. Oh, I need to do that too.

##### **Wozeparrot** [[00:32:12](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1932)]
OK, .

##### **Qazalin** [[00:32:13](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1933)]
Yeah, I'm going to test this. I'm going to do it. So, again, I used native PHP to run a format in localdom. But we're going to do Flat ζ, because I want FBA for operationien. OK.

##### **Wozeparrot** [[00:32:24](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1944)]
Just a note. I'll change that.

##### **Qazalin** [[00:32:26](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1946)]
It doesn't just compile at all. If you can compile on the null device, I can work on.

##### **Geohot** [[00:32:32](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1952)]
Okay, I will get FPA working with FlatLama then.

##### **Geohot** [[00:32:38](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1958)]
Oh, it works with FlatLama, I'm not sure if it works with the other one.

##### **Geohot** [[00:32:42](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1962)]
We only have FlatLama now.

##### **Geohot** [[00:32:45](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1965)]
I see.

##### **Geohot** [[00:32:47](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1967)]
Oh, that's great. The other one's deleted?

##### **Geohot** [[00:32:50](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1970)]
It's still in repo, but we don't use it anymore. We should delete it.

##### **Chenyu** [[00:33:05](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1985)]
When you say cache size 16 compared to 8, did you change the accumulation?

##### **Geohot** [[00:33:14](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1994)]
Yes.

##### **Geohot** [[00:33:18](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=1998)]
I mean, I can't believe that that's the same speed. If you do less accumulation, I'm sure it's faster.

##### **Geohot** [[00:33:31](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2011)]
Okay, anyway, let's investigate this separately and we can move on.

##### **Chenyu** [[00:33:38](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2018)]
Next, there's your stuff. I just put custom driver.

##### **Geohot** [[00:33:42](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2022)]
Yeah, sorry, I'm a little slow today. I'm a little out of it on tinygrad because I haven't worked on tinygrad for the last week. I just worked on the ASM firmware. It's kind of like reverse engineering psychosis. Something about reverse engineering can just pull me in and I can stay up really late and focus on it. So I've just been focused on that. We're very close. I have USB 2, USB 3, and PCIe all working. So there's two ways that the device can communicate. There's a TLP mode, which is initiated by the ASM chip, and then there's the DMA mode. The TLPs are way faster on the custom firmware because I wrote a custom USB control message that triggers the TLP engine. What is currently in tinygrad is something that pokes the PCIe registers to manually trigger this TLP. I just wrote code that does that on the device, and it runs about 10x faster than the one in tinygrad. I can even probably get another 4x by having the device automatically do it. These TLPs, which are again the transfers that are put on the PCIe bus by the chip, only support 4 bytes. But I can still make it even faster by putting a loop on the device that does multiple of these 4-byte transfers and not requiring USB in the loop. This is also going to make things a lot faster for the comma device, because the reason the comma device is slower than the PC is because it has to do all of these USB transfers and there's kernel overhead in each USB transfer. You can basically do any PCIe operation with a single USB transfer. I could even get fancier with it and support multiple addresses and stuff. I'll look into what the tinygrad API is and see if that's reasonable. So that's thing one. Then that's probably going to get us, if I really push it, something like 5 megabytes per second. And again, that's up from like 50 kilobytes per second. The other way to do it, which is going to get us like 500 megabytes per second, is the DMA. So there's a big chunk of SRAM available on the chip, and the GPU can DMA to and from this SRAM. This SRAM is just available on the PCIe bus. Then there's a fast path in order to get from the USB into this SRAM. It's very hard to trigger. There's not a simple DMA controller. It's all pretty tied in with the mass storage device stuff. But this morning, I finally got the emulator to be able to do these things. So I can now play these DMA transactions through the emulator. What the emulator does is it runs the stock firmware on the host and then proxies every MMIO read and write on the UART. So it pokes and peeks each peripheral through the UART interface, which means you can just see everything that it's doing. So I should get that today. And then that's DMA out, being able to copy quickly to the device. But I think it'll be pretty simple also to get DMA in, which is pretty impossible on the stock firmware. So we'll have these two paths: one that can read and write anywhere on the PCIe bus at somewhere between 1 and 5 megabytes a second, and then the DMA path at something between 100 and 500 megabytes a second. My firmware is also really short and 100% not written by AI. AI is good for exploring things. It's not good for writing code. So the firmware is 383 lines, including blank lines and comments. I don't think it's going to get too much longer. It'll probably get to 500 with DMA support. But this whole thing is going to be 500 lines of firmware, and then I think we could probably delete about 100 lines from tinygrad and get this new thing merged. Then I don't want to support the old firmware anymore. I don't want to support the old hacky way of using the ASM.

##### **Geohot** [[00:38:19](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2299)]
Just clean firmware.

##### **Geohot** [[00:38:20](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2300)]
The exact transfers you want to the PCIe bus.

##### **Geohot** [[00:38:25](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2305)]
I think the rest of the week. And it's going to be done. And I never have to work on it again.

##### **Geohot** [[00:38:34](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2314)]
Great.

##### **Geohot** [[00:38:39](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2319)]
Will USB 4 work on the firmware?

##### **Geohot** [[00:38:43](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2323)]
I haven't looked at USB 4 yet, but I think USB 4 is very simple. So I have the PCIe bring up. And there's these registers on the PCIe. So, okay, PCIe bring up. It starts out with this thing that's doing like a thousand reads and writes. And I just had Claude binary search through everything. And now I've got it down to like 10. You have to poke like 10 registers to bring up the PCIe. So I think USB 4 is even simpler. There's this bit called the PCIe tunnel bit. And I think that you just have to set that to three instead of one. And then it will automatically tunnel all transactions over USB 4. I might have to also do something for the USB 4 in it. This will be easy for me to do. The hardest thing to get to work is this DMA controller. I think USB 4 is going to be very easy because I shouldn't even be able to get it working with the emulator. If I can. Yeah, I flash with the, I think it'll work with the emulator. And then if it works with the emulator, it's super trivial to just replay. Okay. So I'm going to do this because I can use our board, flash the emulator to it, connect it to the UART. And then you can poke the MMOs while I plug it into the band.

##### **Geohot** [[00:39:57](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2397)]
I think that was going to be really kind of long.

##### **Geohot** [[00:40:01](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2401)]
It'll definitely support both. Sounds good. Anything else?

##### **Qazalin** [[00:40:15](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2415)]
Nope.

##### **Geohot** [[00:40:18](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2418)]
Okay.

##### **Chenyu** [[00:40:19](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2419)]
Next. Next is my stuff. So there's some cleanup for mixin. Most notably, all the broadcast stuff and reduce are now part of the mixin. And to do that, I also added `weakint` in the dtype promo lattice. I think there are a lot more things that can be cleaned up. It's just `tensor.py` has a lot of old debt. It's still very big.

##### **Qazalin** [[00:40:58](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2458)]
Yeah.

##### **Chenyu** [[00:40:58](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2458)]
And so for now I structure it as: we used to have `elementwise.py`, and in mixin there's an ops mixin. So I added reduce. At some point it's very hard to distinguish what is a reduce and what is an ops mixin. So you can see for now we have the matmul in the ops mixin because it requires both elementwise and reduce, and only the three most fundamental reduce ops are in the reduce mixin. That's currently how I structure it. And if we want to move other tensor methods to mixin, I think most likely they will all be in the ops mixin.

##### **Geohot** [[00:41:46](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2506)]
Yeah, I think ops mixin makes a lot of sense. How I always imagined it was like the elementwise, those are just the things that have the calls to the lower level. Ops mixin can inherit from all the mixins, but it shouldn't have any calls to the lower level. It should only have calls to methods that are on the mixins. So it's hierarchical.

##### **Chenyu** [[00:42:16](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2536)]
I see.

##### **Geohot** [[00:42:18](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2538)]
We also need. The other thing that I was never sure how to move was all the creation methods. I think we should have another mix in for creation.

##### **Chenyu** [[00:42:25](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2545)]
Yeah. I think that makes sense. So a few things that I'm still debating. One is those creation methods. The full and to some extent the ufix and const like. They are kind of a creation method and probably should be treated very similarly. Yeah.

##### **Geohot** [[00:42:46](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2566)]
We can remove and make that API simpler. Yeah. Yes.

##### **Chenyu** [[00:42:54](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2574)]
Another slightly annoying thing is `div` and `mod`, because `div` and `mod` at the tensor level are the floor version, the Python version. But in `UOp` it's the C `div` and C `mod`. And in `UPat`, it directly matches the `div` and `mod`. So I was trying to clean those up, then I started this rabbit hole of direct `div`/`mod` folding, because some of the image folding was not correct. It's only correct for loading images, because images guarantee your valid context is always negative or something like that. Yeah. I was hoping I could maybe get a common function where you can specify you want the floor or the C version, kind of like how we do it in tensor now. Then `UOp` and tensor can call their corresponding default arguments.

##### **Qazalin** [[00:43:59](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2639)]
Yeah.

##### **Chenyu** [[00:44:00](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2640)]
And then we are left with a bunch of bigger functions. We have a very big QR decomposition, so we can't just do it. And then we have a very big... I don't have a huge opinion. Do we really write those in `UOp`?

##### **Geohot** [[00:44:15](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2655)]
I mean, I want to work in `UOp`. I'm okay with putting that in different mixins. I'm okay with putting that in a big `ops` mixin. Great. Yeah. Something like that.

##### **Chenyu** [[00:44:29](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2669)]
Another one is the random functions. So I don't know if I thought of anything there. Currently we represent this state in a tensor, and every function derives from this `rand` function.

##### **Geohot** [[00:44:47](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2687)]
Yeah. Those are probably one of the last to go because of that.

##### **Geohot** [[00:44:54](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2694)]
Okay. It's using state in `tensor.py`, right? And it's like, how do you deal with this kind of state? I'm mostly okay with leaving the random functions. Not much needs them. It's a `tensor.py` thing.

##### **Qazalin** [[00:45:06](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2706)]
Okay.

##### **Chenyu** [[00:45:08](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2708)]
Cool. Then I'll probably just move as many of these tensor methods as possible to the `ops` mixin, if that structure sounds good. Then I'll see what's left. I think this shouldn't be that many, because another thing is the image thing. But I think it's probably fine to keep in `tensor.py`: the image conv2d and `image.py`.

##### **Geohot** [[00:45:37](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2737)]
Yeah.

##### **Geohot** [[00:45:38](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2738)]
I mean, I see no reason why they can't move.

##### **Chenyu** [[00:45:45](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2745)]
They probably can. It's just, for example, there is still a `matmul` somewhere in tensor, and it takes either the image or the `asm_gemm` flag. Sure, I can just move it. There's also no test for that. Things like that. Yeah.

##### **Geohot** [[00:46:06](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2766)]
Yeah. I mean, this is a good chance to clean up all these tensor methods. Mixin also lets us factorize things into different files. I'd be fine with, like, an `image.py` under mixins. I see no fundamental reason. I guess the distinction between mixin and tensor is that if something requires state, it can't quite go on mixins. If it requires state, it stays on tensor. If it doesn't require state, I don't know why it can't just go to mixins.

##### **Chenyu** [[00:46:35](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2795)]
OK. Cool. Yeah. Tensor now is still like 3,500 lines. It probably should be less than 1,000 lines. We'll see. That'd be great. We'll get a 3,000-line `ops` mixin though.

##### **Geohot** [[00:46:53](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2813)]
Well, yeah. But you could also like factor that however you want, right? Like mixin is kind of like...

##### **Chenyu** [[00:46:59](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2819)]
So previously, the things like save lines, if it already has a function in the uop, right? It's like, sure. There are functions that already re-implemented layer.

##### **Geohot** [[00:47:11](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2831)]
Oh, I don't really care if it reduces lines overall. The thing that I care about here is just that it's factorized nicely, right? It's not one stupid big file. It's just like, oh cool, we can have different types of operations in different places. I don't know what the `ops` mixin file should be called. You can factorize this however you want.

##### **Chenyu** [[00:47:31](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2851)]
OK. I'll see. I just want to make this files generally smaller. So...

##### **Geohot** [[00:47:39](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2859)]
Yeah, no. I mean, this stuff should not be in the root directory of the whole thing. Tensor.py should be like a nothing class. It just has a little bit of state on it.

##### **Chenyu** [[00:47:49](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2869)]
Well, sounds good. Yeah.

##### **Geohot** [[00:47:51](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2871)]
I mean, it's like, why does our most core class have things on it like a QR decomposition?

##### **Chenyu** [[00:47:57](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2877)]
Because everyone loves QR decomposition, maybe. I don't know.

##### **Geohot** [[00:48:01](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2881)]
And that's a great feature to have, shoved in a file two directories deep.

##### **Chenyu** [[00:48:07](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2887)]
OK. Yeah. Sounds good.

##### **Geohot** [[00:48:12](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2892)]
Yeah, that's pretty much it.

##### **Geohot** [[00:48:16](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2896)]
I'm excited for it. Yeah.

##### **Qazalin** [[00:48:20](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2900)]
Cool.

##### **Geohot** [[00:48:22](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2902)]
OK.

##### **Chenyu** [[00:48:23](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2903)]
Speaking of image, next we have image and device target.

##### **Chrism** [[00:48:29](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=2909)]
Yeah. I guess, I mean, `IMAGE=2` has been gone. But image creation is now late in codegen. That's cool. In `heuristics.py`, we still check if image is set to make sure we do the early upcast to `float4`, but you don't have to worry about images existing before late codegen anymore, so that's nice. Other than that, there's not really much to say about image, I don't think.

So the big thing is this new syntax for the `DEV` environment variable. I put a photo of what we talked about in tiny-dev, although I realize that's a little unintelligible if you weren't there for the conversation we had. Obviously it's really important that we write up some docs for this once it all gets merged, just so people can understand the syntax behind this stuff. But yeah, I'm just kind of plugging along implementing that stuff.

So a big change from last week was the syntax of `CPU=1` or `CL=1` or whatever. You can no longer do that. You have to do `DEV=CPU` or `DEV=CL`. I also deprecated this thing where we used to support monkey-patching `device.defaults`. Now it asserts if you try to do this, because it's unclear what exactly you want to do in that context. Instead, you should be setting the `DEV` context var if you want to be modifying that. Yeah, I don't know. Especially if there are any issues people see with the syntax around `DEV`, I feel like there's some controversial stuff there.

##### **Geohot** [[00:50:48](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3048)]
But... Yeah. Yeah. Is Comma on the latest tinygrad yet?

##### **Chrism** [[00:50:57](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3057)]
They... Apparently, they have a PR that's ready to go. And it just needs to be merged.

##### **Qazalin** [[00:51:03](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3063)]
Yeah.

##### **Geohot** [[00:51:05](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3065)]
Yeah, just make sure that gets merged. Advocate for our latest stuff.

##### **Chrism** [[00:51:10](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3070)]
Yeah, yeah. Of course. Yeah, no. From what I can tell, they're... All they have to do is click merge. So... If it doesn't get... If it's not done by tomorrow, then I'll bug them.

##### **Chenyu** [[00:51:22](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3082)]
Yeah, just go there. Find the one pull request. Say, please click.

##### **Geohot** [[00:51:27](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3087)]
I have it. I have it.

##### **Chenyu** [[00:51:29](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3089)]
Great. Sounds good.

##### **Wozeparrot** [[00:51:31](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3091)]
Is there any reason the dev target specification uses colons and not dashes?

##### **Geohot** [[00:51:39](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3099)]
Like, we...

##### **Chrism** [[00:51:41](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3101)]
We did discuss this as an option.

##### **Geohot** [[00:51:45](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3105)]
Do you have a strong preference for dashes? And if so, why?

##### **Wozeparrot** [[00:51:49](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3109)]
I feel like most other target triples are dashes. And then colons also collide if... Because I heard what the remote syntax is, and it collides with that.

##### **Geohot** [[00:52:02](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3122)]
So it doesn't collide with the remote syntax, right? The remote's on the other side of the plus.

##### **Wozeparrot** [[00:52:08](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3128)]
Sure, but it still, like, visually collides if I'm quickly scanning the triple, right?

##### **Geohot** [[00:52:15](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3135)]
Yeah... Okay, you two can figure this out.

##### **Geohot** [[00:52:23](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3143)]
Yeah, I mean, look, if you have a strong... If it's just like, I want it to visually match LLVM's triple, I don't really care about that. But if there's a reason why colons are bad, definitely a good time to...

##### **Chenyu** [[00:52:41](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3161)]
Advocate for your favorite representation.

##### **Geohot** [[00:52:43](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3163)]
Speak now?

##### **Chenyu** [[00:52:44](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3164)]
Yeah.

##### **Wozeparrot** [[00:52:45](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3165)]
I don't know. I just feel like there's a lot of... Symbols in this syntax overall.

##### **Geohot** [[00:52:52](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3172)]
Well, I mean, yeah, but your proposal of switching to dashes is just replacing the colon with a dash.

##### **Wozeparrot** [[00:52:58](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3178)]
I have a couple...

##### **Geohot** [[00:53:02](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3182)]
Issues with the syntax. Okay. You guys are both there. Hash it out. What are your proposals? I mean, we went through this, and yeah, like, I agree it's complicated, but, like, what... There's nothing to really... Cut.

##### **Wozeparrot** [[00:53:18](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3198)]
And not all these things are used that often. Yeah, it's not really stuff to cut. It's just that it feels very semantically random. Like, there's not exactly one symbol that's assigned for one semantic purpose.

##### **Chenyu** [[00:53:33](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3213)]
If you have a design language that you think is kind of future-proof, it's very welcome to... Now is the best time to propose that.

##### **Geohot** [[00:53:44](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3224)]
Yeah, definitely. Uh, I mean, I don't know. Like, we discussed... We definitely discussed dashes in the target triple. Yeah, we did.

##### **Chrism** [[00:53:52](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3232)]
Yeah.

##### **Wozeparrot** [[00:53:53](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3233)]
I mean, dashes are a very small part. Like, that is kind of not really...

##### **Geohot** [[00:53:58](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3238)]
All right. All right, so it's not about dashes. What else?

##### **Wozeparrot** [[00:54:02](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3242)]
The semicolon feels very weird to me to split the thing. It's again just symbol choice. I think the worst thing semantically for me is that the arch flag specification isn't split with something to separate specifying the arch and the flags that modify the arch. That's split with commas, but then the flags themselves are additionally split with commas.

##### **Geohot** [[00:54:34](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3274)]
Yeah, I don't know. The first one is the arch, and then you split things with commas.

##### **Wozeparrot** [[00:54:40](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3280)]
Yeah, but then this makes it, like, semantically messy, because it is unclear... Well, but... It's unclear. What's the...

##### **Geohot** [[00:54:46](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3286)]
No, there's no difference between the arch and the modifier flags, right?

##### **Geohot** [[00:54:49](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3289)]
Like, what's the difference?

##### **Wozeparrot** [[00:54:54](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3294)]
I mean... I... See, this is what I mean. Like, I assume that there is a difference, because the first one is separated with a colon from the render.

##### **Geohot** [[00:55:02](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3302)]
Yeah, but, like... I don't know. Like, it's not, like... Something like specifying which FMA instruction to use, which would be, like, a modifier, and what the arch is, it's, like, almost the same thing. Yeah.

##### **Geohot** [[00:55:15](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3315)]
If the arch isn't really special... The arch has no meaning to tinygrad as a whole. The arch only has meaning inside your renderer, which is the same as those flags.

##### **Geohot** [[00:55:33](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3333)]
And as far as the semicolon, yeah, the semicolon is, like... The semicolon is very rare. The only time you need a semicolon is if you're using two devices and you want to specify a different renderer for your second renderer. So, like, if you're using a second device, the semicolon...

##### **Chrism** [[00:55:48](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3348)]
Yeah, the semicolon is nasty enough that you could almost, like, put this in a separate variable, because it's just, like... It's not... It's semantically different to be specifying the renderer for when you're not using the default device.

##### **Geohot** [[00:56:02](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3362)]
I care nothing about... The semicolon syntax can be literally whatever. I don't care about that.

##### **Chrism** [[00:56:09](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3369)]
Okay.

##### **Geohot** [[00:56:09](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3369)]
But the... Yeah, the commas and the colons, I mean, they were discussed.

##### **Chrism** [[00:56:15](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3375)]
Yeah.

##### **Geohot** [[00:56:15](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3375)]
I'm certainly open to other proposals, but the commas, the colons, and the plus were definitely discussed and thought through.

##### **Geohot** [[00:56:22](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3382)]
Yeah. No, I...

##### **Wozeparrot** [[00:56:24](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3384)]
I assume that... Colons were... Yeah, yeah. I heard that this was discussed a lot. To me, this is not a very semantically clear syntax. It makes more sense now that you say the arch isn't exactly that special for the renderer, but clearly we do treat the arch as different than the other modifiers. Well, it doesn't have to be different, though, right? I haven't written this code yet.

##### **Geohot** [[00:56:49](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3409)]
Yeah, I almost think that, like, it's unclear if the Arch string even includes the modifiers. Like, it might. I think it kind of does, actually. I think that is the Arch string.

##### **Chrism** [[00:57:00](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3420)]
Yeah, that's true. That could just... Could just be the whole thing.

##### **Geohot** [[00:57:04](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3424)]
The commas are just, like, per renderer, right? Like, some renderers support flags, some renderers don't support flags. I actually think that that is the Arch string.

##### **Chrism** [[00:57:11](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3431)]
Yeah, yeah, I think that makes more sense.

##### **Geohot** [[00:57:13](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3433)]
With the commas.

##### **Qazalin** [[00:57:14](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3434)]
Yeah.

##### **Geohot** [[00:57:15](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3435)]
Okay.

##### **Geohot** [[00:57:18](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3438)]
Hopefully that addresses that. Colons versus dashes? I don't know. I spent some time typing out both. I like the colon better.

##### **Geohot** [[00:57:28](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3448)]
Yeah. Colons are well-accepted environment variables. They're the separator and path. Yeah.

##### **Chrism** [[00:57:37](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3457)]
Anyway, this is definitely a little bit bike-shedding, I think.

##### **Geohot** [[00:57:41](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3461)]
Yeah.

##### **Chrism** [[00:57:42](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3462)]
I need to look at it more.

##### **Geohot** [[00:57:43](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3463)]
Yeah. If you have another proposal,

##### **Geohot** [[00:57:45](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3465)]
we're definitely open to it. But, sure.

##### **Chenyu** [[00:57:48](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3468)]
I think part of this is also, like, some use case, we really would feel the need to justify one way or another after we really start to use it. So, for the initial one, maybe just timebox it for the, let's say, end of this week. Then we decide, okay, this is the first version. Then later, if we feel strongly, we can always update that. It's just like how we get all the device equals to, you know, one usage.

##### **Chrism** [[00:58:17](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3497)]
Yeah, for sure. I think I can get something working and then we can see how we feel about it.

##### **Wozeparrot** [[00:58:21](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3501)]
I definitely do feel like I need to use it before I can make.

##### **Chenyu** [[00:58:25](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3505)]
Yeah, because now it's very hard to advocate for one way or another. So, we'll see.

##### **Geohot** [[00:58:32](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3512)]
Yeah, for sure. For sure. The thing that I'm most...

##### **Chenyu** [[00:58:36](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3516)]
Go ahead.

##### **Geohot** [[00:58:37](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3517)]
Okay.

##### **Chenyu** [[00:58:39](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3519)]
I was trying to conclude this, so you go first.

##### **Geohot** [[00:58:42](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3522)]
Oh, the thing that I'm most excited about with this is being able to start using it. Being able to type `mock+AMD` and `USB+AMD` and not having to remember `MOCKGPU=1`, `AMD_IFACE=USB`, or `AMD_IFACE=PCI`.

##### **Qazalin** [[00:59:01](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3541)]
Yeah.

##### **Wozeparrot** [[00:59:01](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3541)]
Yeah, because what you said was already wrong. Now you should be saying `AMD_IFACE=USB` or `AMD_IFACE=PCI`.

##### **Geohot** [[00:59:10](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3550)]
Yeah. See, I already did it wrong. Great. That's why I use the plus.

##### **Chenyu** [[00:59:16](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3556)]
Sounds good. Let's quickly conclude this meeting. Are we good? Do we have, like, the Qwen thingy? I see something was just merged.

##### **Geohot** [[00:59:30](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3570)]
Yeah, I just merged that. I think also, I don't know if the size output one broke it, but it looks like something kind of broke in my CI tests. But yeah, I want to merge Qwen 3.5 soon.

##### **Chrism** [[00:59:44](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3584)]
I think the thing that's broken in my CI tests is a flaky viz test. I've seen that fail. It's something to do with the setup and teardown when we do `-n=auto`. That test seems to not be playing nicely with parallelism.

##### **Qazalin** [[01:00:05](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3605)]
I'll look into that if you give me a link.

##### **Chenyu** [[01:00:09](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3609)]
Everyone, please close your PR. Why is the same number as last week? Please close.

##### **Geohot** [[01:00:15](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3615)]
I closed some. See, who's the biggest offender here?

##### **Chenyu** [[01:00:20](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3620)]
Make a guess.

##### **Geohot** [[01:00:22](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3622)]
Is it me? I don't know. I see tons of Nimlgen. I see a lot of Qazalin.

##### **Chenyu** [[01:00:33](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3633)]
Okay, that's not pointing fingers. Please go there. And I think that's it for this meeting. Thank you, everyone. We'll discuss if we want to change time later when people are not in Asia anymore. We'll discuss later.

##### **Chenyu** [[01:00:54](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3654)]
Cool.

##### **Geohot** [[01:00:54](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3654)]
Thank you. Bye bye. Bye. Bye.

##### **Chrism** [[01:00:57](https://www.youtube.com/watch?v=yyXjuQHvx6E&t=3657)]
Bye. Bye.
