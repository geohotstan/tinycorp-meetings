# 2026-06-29 Meeting

### Meeting Agenda

**Time:** new meeting #26, 6/29 9am Monday San Diego time
- company update
- MLPerf
- VIZ LLaMA schedule
- new codegen
- tensor.py, Tensor.training, UNIQUE
- HCQ2
- CI updates
- bounties, issues, comma happiness, GLM


### Audio

[Youtube Link](https://www.youtube.com/watch?v=bm61_vsrGEI)

### Highlights

- **[Company Update](#geohot-000005)**: MLPerf 6.1 removed the 405B model, shifting focus to GPT-OSS; the upside is shorter training runs, but mixture-of-experts support now matters.
- **[Exa Box Progress](#geohot-000005)**: The first shipping container for the Exa Box is expected Thursday, the office buildout is underway, SDG&E transformer work is being pursued, and the team is on track to build two Exa Boxes this year.
- **[TinyAMD GLM Access](#geohot-000152)**: A GLM is running on TinyAMD 1, and anyone with Tiny Box access is invited to use it.
- **[GPT-OSS MLPerf Target](#wozeparrot-000450)**: Wozeparrot is targeting GPT-OSS 20B training by the end of the week; the group prefers data parallelism over the reference implementation’s expert-parallel setup.
- **[Small LLaMA Performance](#qazalin-000709)**: The best small LLaMA run is now 2h36m, improved from 2h50m the prior week, with remaining bottlenecks centered around multi/all-reduce kernel counts.
- **[Stack / Copy-Cat Optimization](#geohot-001348)**: Geohot suggests unifying `stack` and `_stack`, switching cat/stack behavior to movement ops, and building a copy-stack path similar to shrink-copy to reduce all-reduce kernel counts.
- **[New Codegen Refactor](#geohot-001742)**: Geohot moved memory coalescing logic out of the devectorizer into `coalesce`, making images behave more like instruction selection and simplifying the new devectorizer/expander.
- **[PtrDType and dtype.vec Cleanup](#geohot-002230)**: `POINTERCAT` and `VCAT` were deleted, `EXPAND`/`CONTRACT` or `UNROLL`/`CONTRACT` are next, and `PtrDType` plus `dtype.vec` are close to removal.
- **[Tensor Cleanup](#chenyu-003120)**: Chenyu removed `Tensor.training`, moved training state through `ContextVar`, cleaned up unique buffers so `UNIQUE` and `LUNIQUE` are gone, and made `ParamArg` the dedup key.
- **[Ops.DEVICE Removal Plan](#chenyu-003120)**: The last `Ops.DEVICE` use in program construction should be removed by deriving device information from params/SINK instead of storing it separately on programs.
- **[HCQ2 Refactor](#nimlgen-003808)**: HCQ2 is being split into explicit `schedule` and `link` phases so device interaction is delayed as long as possible; AMD support is expected this week, with USB/Metal possibly later.
- **[CI Updates](#chrism-004435)**: macOS tests besides Metal now behave more like Windows tests by running `test_tiny`; benchmark cleanup continues, with AMD BEAM flakiness and slow benchmark grouping still under investigation.
- **[Runner Alerting](#wozeparrot-005445)**: Runner service state is now exposed in stats, making alerting straightforward; the team wants alerts before GitHub drops stale runner tokens.
- **[GLM Bounty](#geohot-005743)**: A new $3,000 bounty is available for getting GLM running in tinygrad at 100+ tokens/sec and merged into master.

### Transcript
##### **Geohot** [[00:00:05](https://www.youtube.com/watch?v=bm61_vsrGEI&t=5)]
Cool. So yeah, I mean, I think the big news this week is that 405B is removed from MLPerf. So we got to go with OSS. I think the big pro is that it trains quickly. So we won't have to deal with day training runs. But yeah, we got to get mixture of experts working. Because there's no 405B in MLPerf 6.1. We're getting the first shipping container for the Exa Box is coming on Thursday. So that's exciting. We're building out the office so we'll have like two spots. Trying to contact SDG&E to get a transformer up at the back of the building. Yeah. No, like with the government, I will believe it when I see it. And I'll have the call this week to determine what our what our customer wants in his Exa Box. But uh, yeah, we're on

##### **Geohot** [[00:01:13](https://www.youtube.com/watch?v=bm61_vsrGEI&t=73)]
track to build two Exa Boxes this year. And we've been doing really well on Twitter lately. Not that it matters, but we've been

##### **Geohot** [[00:01:27](https://www.youtube.com/watch?v=bm61_vsrGEI&t=87)]
getting a lot of views on Twitter. Sayi is very popular these days.

##### **Wozeparrot** [[00:01:36](https://www.youtube.com/watch?v=bm61_vsrGEI&t=96)]
And it's just roasting Anthropic is popular.

##### **Geohot** [[00:01:37](https://www.youtube.com/watch?v=bm61_vsrGEI&t=97)]
Roasting Anthropic is popular. It's true. Okay. Anything else?

##### **Geohot** [[00:01:52](https://www.youtube.com/watch?v=bm61_vsrGEI&t=112)]
Also, everyone who has access to Tiny Boxes, on TinyAMD 1, there is a GLM running,

##### **Geohot** [[00:02:03](https://www.youtube.com/watch?v=bm61_vsrGEI&t=123)]
and you're welcome to use it for whatever you want. Let's move on to MLPerf.

##### **Chenyu** [[00:02:19](https://www.youtube.com/watch?v=bm61_vsrGEI&t=139)]
AMD pushed to remove the big LLaMA.

##### **Geohot** [[00:02:24](https://www.youtube.com/watch?v=bm61_vsrGEI&t=144)]
It's on the internet.

##### **Wozeparrot** [[00:02:35](https://www.youtube.com/watch?v=bm61_vsrGEI&t=155)]
I can only see half of what you're saying.

##### **Geohot** [[00:02:47](https://www.youtube.com/watch?v=bm61_vsrGEI&t=167)]
I'll be better. Hello? Is it better? Hello?

##### **Qazalin** [[00:03:31](https://www.youtube.com/watch?v=bm61_vsrGEI&t=211)]
Is it better? Is this better?

##### **Chenyu** [[00:03:34](https://www.youtube.com/watch?v=bm61_vsrGEI&t=214)]
I think so, yeah. I don't know what's wrong with my Wi-Fi. Yeah, I'm on cellular. How does this stuff work?

##### **Chrism** [[00:03:44](https://www.youtube.com/watch?v=bm61_vsrGEI&t=224)]
It's not just you. I think Discord must be having issues, because I'm also having issues, like you guys.

##### **Geohot** [[00:03:52](https://www.youtube.com/watch?v=bm61_vsrGEI&t=232)]
Great. OK.

##### **Chenyu** [[00:03:54](https://www.youtube.com/watch?v=bm61_vsrGEI&t=234)]
No, I was saying AMD pushed MLPerf to remove the big LLaMA.

##### **Geohot** [[00:04:00](https://www.youtube.com/watch?v=bm61_vsrGEI&t=240)]
Really?

##### **Chenyu** [[00:04:02](https://www.youtube.com/watch?v=bm61_vsrGEI&t=242)]
They proposed and really pushed through it. That's my understanding. So I'm like, I need to do this.

##### **Geohot** [[00:04:10](https://www.youtube.com/watch?v=bm61_vsrGEI&t=250)]
I mean, yeah. I think it's because it's hard to do.

##### **Chenyu** [[00:04:17](https://www.youtube.com/watch?v=bm61_vsrGEI&t=257)]
OK, anyway, I mean, it's what it is. And we can.

##### **Geohot** [[00:04:20](https://www.youtube.com/watch?v=bm61_vsrGEI&t=260)]
Yeah, yeah. Well, I don't have approval yet from Anush that we can get a contract on GPT-OSS. He proposed it.

##### **Chenyu** [[00:04:29](https://www.youtube.com/watch?v=bm61_vsrGEI&t=269)]
Yeah, he also proposed DeepSeek.

##### **Geohot** [[00:04:32](https://www.youtube.com/watch?v=bm61_vsrGEI&t=272)]
Well, I'm definitely not doing that. But yeah, yeah, so that's what he said.

##### **Chenyu** [[00:04:37](https://www.youtube.com/watch?v=bm61_vsrGEI&t=277)]
OK. Yeah, we'll wait and see. But yeah. You saw my reply.

##### **Geohot** [[00:04:43](https://www.youtube.com/watch?v=bm61_vsrGEI&t=283)]
Yeah. Yeah.

##### **Chenyu** [[00:04:47](https://www.youtube.com/watch?v=bm61_vsrGEI&t=287)]
OK, off to Wozeparrot.

##### **Wozeparrot** [[00:04:50](https://www.youtube.com/watch?v=bm61_vsrGEI&t=290)]
I guess I'm still targeting the GPT-OSS 20B training by the end of the week.

##### **Geohot** [[00:04:56](https://www.youtube.com/watch?v=bm61_vsrGEI&t=296)]
Yeah, that would be great. Let's just do it. Let's just, we want to train this anyway. This is actually useful. 405B was kind of stupid. Like, who wants to sit there for 11 days?

##### **Wozeparrot** [[00:05:06](https://www.youtube.com/watch?v=bm61_vsrGEI&t=306)]
Yes, interesting. Offscreen MLPerf reference has an MI355 config. But no one submitted GPT-OSS 20B on MI355 for 6.0.

##### **Geohot** [[00:05:25](https://www.youtube.com/watch?v=bm61_vsrGEI&t=325)]
Do you know if it's no one submit,

##### **Chenyu** [[00:05:27](https://www.youtube.com/watch?v=bm61_vsrGEI&t=327)]
or they like remove after submission? I also just read that some company recalculated submission with MI machines because of bad performance.

##### **Wozeparrot** [[00:05:41](https://www.youtube.com/watch?v=bm61_vsrGEI&t=341)]
Maybe that was it.

##### **Geohot** [[00:05:44](https://www.youtube.com/watch?v=bm61_vsrGEI&t=344)]
OK. It's interesting that the reference implementation is EP, expert parallel and not data parallel. Yeah, I mean, like, What did Nvidia do? They're all data parallel. Yeah, let's just do data parallel.

##### **Qazalin** [[00:06:17](https://www.youtube.com/watch?v=bm61_vsrGEI&t=377)]
OK.

##### **Geohot** [[00:06:17](https://www.youtube.com/watch?v=bm61_vsrGEI&t=377)]
So we will have something training end of this week?

##### **Nimlgen** [[00:06:22](https://www.youtube.com/watch?v=bm61_vsrGEI&t=382)]
Yep. OK.

##### **Geohot** [[00:06:27](https://www.youtube.com/watch?v=bm61_vsrGEI&t=387)]
OK.

##### **Chenyu** [[00:06:27](https://www.youtube.com/watch?v=bm61_vsrGEI&t=387)]
Do we need to do anything special, or this just works with, like, tinygrad? Tinygrad?

##### **Geohot** [[00:06:37](https://www.youtube.com/watch?v=bm61_vsrGEI&t=397)]
I'm hoping it just works.

##### **Wozeparrot** [[00:06:41](https://www.youtube.com/watch?v=bm61_vsrGEI&t=401)]
I haven't looked too much at the architecture yet. OK.

##### **Geohot** [[00:06:48](https://www.youtube.com/watch?v=bm61_vsrGEI&t=408)]
Sounds good. OK.

##### **Chenyu** [[00:06:53](https://www.youtube.com/watch?v=bm61_vsrGEI&t=413)]
We still need to do small LLaMA next round. So let's move on to this LLaMA schedule.

##### **Geohot** [[00:07:00](https://www.youtube.com/watch?v=bm61_vsrGEI&t=420)]
Small LLaMA staying, right? I believe so.

##### **Nimlgen** [[00:07:05](https://www.youtube.com/watch?v=bm61_vsrGEI&t=425)]
OK.

##### **Qazalin** [[00:07:09](https://www.youtube.com/watch?v=bm61_vsrGEI&t=429)]
Oh, sure. My best run is 2 hours and 36 minutes.

##### **Geohot** [[00:07:18](https://www.youtube.com/watch?v=bm61_vsrGEI&t=438)]
And what's our progress week over week?

##### **Geohot** [[00:07:22](https://www.youtube.com/watch?v=bm61_vsrGEI&t=442)]
How fast was it last week?

##### **Qazalin** [[00:07:24](https://www.youtube.com/watch?v=bm61_vsrGEI&t=444)]
Two hours and 50 minutes.

##### **Geohot** [[00:07:26](https://www.youtube.com/watch?v=bm61_vsrGEI&t=446)]
All right. All right. 14 minutes a week. That's pretty good.

##### **Qazalin** [[00:07:32](https://www.youtube.com/watch?v=bm61_vsrGEI&t=452)]
I want to trend it like that, because stuff's getting hard. I thought the rest of, because, like, I've basically kind of plateaued over the past four days, because it looks like it's all multi. And, like, I removed all the little hanging fruit. Like, there's no dumb kernels doing dumb things in my branch. But there is problems with multi in that our all-reduce lowers to a giant amount of kernels, both E kernels and SDMA copies. So basically our all-reduce, rangeify, or multi lowers it to shrinks and copies. And then adds, which are add-like E kernels that just add things and store. And then the final cat kernel.

##### **Geohot** [[00:08:41](https://www.youtube.com/watch?v=bm61_vsrGEI&t=521)]
So what you can work on for this is stack. So, like, what I want to do is I want to do a little bit of a stack. And then I want to get the, I mean, those E kernels, what they're doing is effectively they're cat kernels, right?

##### **Qazalin** [[00:09:06](https://www.youtube.com/watch?v=bm61_vsrGEI&t=546)]
Well, there's a bunch of, like, there's SDMA copies. And then there is E kernels that add things. And then there's a final cat.

##### **Geohot** [[00:09:17](https://www.youtube.com/watch?v=bm61_vsrGEI&t=557)]
Oh, there's a cat after they add things.

##### **Qazalin** [[00:09:21](https://www.youtube.com/watch?v=bm61_vsrGEI&t=561)]
Yeah, yeah. So, like, you reduce and then you collect and sum them.

##### **Geohot** [[00:09:25](https://www.youtube.com/watch?v=bm61_vsrGEI&t=565)]
Yeah, I mean, so what you basically want to do is like, it's kind of the opposite of the shrink copy thing. Right? So you have the shrink copy thing, which is copying out of a piece. But the copy cat is you want to copy into a piece.

##### **Qazalin** [[00:09:41](https://www.youtube.com/watch?v=bm61_vsrGEI&t=581)]
Yeah.

##### **Geohot** [[00:09:44](https://www.youtube.com/watch?v=bm61_vsrGEI&t=584)]
Yeah, can you make that work? I mean, so one of the ideas here might be to switch to the stack operator. Like to switch to the stack movement op and then have some lowering path.

##### **Qazalin** [[00:09:58](https://www.youtube.com/watch?v=bm61_vsrGEI&t=598)]
Yeah, even if we do that, it's still going to be the same kernel counts.

##### **Geohot** [[00:10:04](https://www.youtube.com/watch?v=bm61_vsrGEI&t=604)]
Well, it doesn't have to be like right because you could put the cat kernels before the add kernels, right?

##### **Qazalin** [[00:10:14](https://www.youtube.com/watch?v=bm61_vsrGEI&t=614)]
Like, so AMD launches five all-reduces, right. So per step, we launched like thousands.

##### **Geohot** [[00:10:26](https://www.youtube.com/watch?v=bm61_vsrGEI&t=626)]
Well, that's a different question. Why do we launch 1000s? Isn't there just like one big weight tensor? Or like 10?

##### **Qazalin** [[00:10:37](https://www.youtube.com/watch?v=bm61_vsrGEI&t=637)]
I mean, like we, so one all reduce becomes like many kernels for every device.

##### **Geohot** [[00:10:44](https://www.youtube.com/watch?v=bm61_vsrGEI&t=644)]
We launch thousands of kernels, or we launch thousands of all-reduces? Like how many buffers are we all-reducing?

##### **Qazalin** [[00:10:53](https://www.youtube.com/watch?v=bm61_vsrGEI&t=653)]
How many buffers are we all-reducing? I don't know that number, but we are like every time I look at this, there's a bunch of all-reduces there.

##### **Geohot** [[00:11:06](https://www.youtube.com/watch?v=bm61_vsrGEI&t=666)]
Uh, yeah, I mean, at first, at first, I would figure out how many buffers we're all-reducing, right? We really should just be all-reducing like once per once per tensor, and there should only be like 10 or 11 tensors or something.

##### **Geohot** [[00:11:18](https://www.youtube.com/watch?v=bm61_vsrGEI&t=678)]
Yeah.

##### **Geohot** [[00:11:19](https://www.youtube.com/watch?v=bm61_vsrGEI&t=679)]
But then, yeah. But then, so you see what I'm saying about how, you see what I'm saying how you can flip the cat in the ad, right?

##### **Qazalin** [[00:11:26](https://www.youtube.com/watch?v=bm61_vsrGEI&t=686)]
Yeah, you can do the cats before.

##### **Geohot** [[00:11:28](https://www.youtube.com/watch?v=bm61_vsrGEI&t=688)]
You can do the cat before, right? Now, once you do the cat before, what you want to do is it's the, like you have like shrink copy, which is, which is fused to copy. You want to have copy cat fused also just to copy.

##### **Qazalin** [[00:11:48](https://www.youtube.com/watch?v=bm61_vsrGEI&t=708)]
Copy.

##### **Geohot** [[00:11:50](https://www.youtube.com/watch?v=bm61_vsrGEI&t=710)]
Sure. Yeah. Right. Like imagine. Yeah.

##### **Geohot** [[00:11:55](https://www.youtube.com/watch?v=bm61_vsrGEI&t=715)]
Yeah. So imagine you have like, you're like, you know, you're copying from like the eight GPUs, right? Like right now you're doing copies into another buffer and then you have some cat kernel, which concatenates the eight together. Right. What you instead want to do is just allocate a big buffer and then copy all eight of them into that.

##### **Qazalin** [[00:12:11](https://www.youtube.com/watch?v=bm61_vsrGEI&t=731)]
Yeah. All those slices.

##### **Nimlgen** [[00:12:14](https://www.youtube.com/watch?v=bm61_vsrGEI&t=734)]
Yeah.

##### **Qazalin** [[00:12:15](https://www.youtube.com/watch?v=bm61_vsrGEI&t=735)]
You should be able to write that. Yeah.

##### **Geohot** [[00:12:19](https://www.youtube.com/watch?v=bm61_vsrGEI&t=739)]
Yeah. You should be able to write that generically too.

##### **Geohot** [[00:12:22](https://www.youtube.com/watch?v=bm61_vsrGEI&t=742)]
Yeah.

##### **Geohot** [[00:12:24](https://www.youtube.com/watch?v=bm61_vsrGEI&t=744)]
But what you may want to do is you may want to change all of the cat and stack stuff right now to just use movement ops and not use add.

##### **Qazalin** [[00:12:44](https://www.youtube.com/watch?v=bm61_vsrGEI&t=764)]
It would have to reduce at some point, or am I missing something?

##### **Geohot** [[00:12:48](https://www.youtube.com/watch?v=bm61_vsrGEI&t=768)]
Well, okay. So there's two things. There's two things we're talking about here, right? There is the reduce add, and then there is the add that is a cat. The way that we currently write cat is that we have two buffers.

##### **Geohot** [[00:13:01](https://www.youtube.com/watch?v=bm61_vsrGEI&t=781)]
We pad them both and then we add them together. But you can also write that using stack. It's very easy if they're the same size. It's just stack. Yeah.

##### **Nimlgen** [[00:13:18](https://www.youtube.com/watch?v=bm61_vsrGEI&t=798)]
Yeah. Yeah.

##### **Qazalin** [[00:13:21](https://www.youtube.com/watch?v=bm61_vsrGEI&t=801)]
Stack of slices. Yeah.

##### **Geohot** [[00:13:24](https://www.youtube.com/watch?v=bm61_vsrGEI&t=804)]
Yeah. But you have to, I mean, you got to add stack support basically to everything.

##### **Geohot** [[00:13:36](https://www.youtube.com/watch?v=bm61_vsrGEI&t=816)]
Like there's currently stack support in codegen, like in the lowest level stuff, there's stack support, but there's no stack support yet from the top. Like that would need to be added.

##### **Nimlgen** [[00:13:47](https://www.youtube.com/watch?v=bm61_vsrGEI&t=827)]
Yeah. Yeah. Yeah.

##### **Geohot** [[00:13:48](https://www.youtube.com/watch?v=bm61_vsrGEI&t=828)]
And ideally what you want to do is you want to unify the stack methods. So there's a method that we call stack right now that does this pad add construction. And then there's another method called `_stack`, which is just a stack op. So first switch it to a stack op, then figure out how to do something similar to what you did for shrink copy, but on copy stack.

##### **Geohot** [[00:14:24](https://www.youtube.com/watch?v=bm61_vsrGEI&t=864)]
Yeah, so this will probably make things a little faster, I think.

##### **Qazalin** [[00:14:31](https://www.youtube.com/watch?v=bm61_vsrGEI&t=871)]
14 minutes faster this week? No, no. I think that would require kernel counts to go down.

##### **Geohot** [[00:14:43](https://www.youtube.com/watch?v=bm61_vsrGEI&t=883)]
This would lower kernel count. You'd lose 64 kernels per buffer if you do this.

##### **Qazalin** [[00:14:57](https://www.youtube.com/watch?v=bm61_vsrGEI&t=897)]
64 kernels per buffer if I do this?

##### **Geohot** [[00:15:01](https://www.youtube.com/watch?v=bm61_vsrGEI&t=901)]
So if there's 10 buffers, you'll lose 640 kernels. Or... Sorry, one last. 56. 560 kernels.

##### **Qazalin** [[00:15:10](https://www.youtube.com/watch?v=bm61_vsrGEI&t=910)]
How many kernels do we have in all-reduces? In one all-reduce for one tensor?

##### **Geohot** [[00:15:17](https://www.youtube.com/watch?v=bm61_vsrGEI&t=917)]
Probably... Probably...

##### **Geohot** [[00:15:21](https://www.youtube.com/watch?v=bm61_vsrGEI&t=921)]
Well, this exact thing, this exact copycat construction is one kernel per GPU square.

##### **Qazalin** [[00:15:32](https://www.youtube.com/watch?v=bm61_vsrGEI&t=932)]
Yeah.

##### **Geohot** [[00:15:35](https://www.youtube.com/watch?v=bm61_vsrGEI&t=935)]
So, yeah, that's a pretty good place to start. I think you could lose a lot of kernels there. And I think it could be nicely generic, too. Yeah.

##### **Qazalin** [[00:15:46](https://www.youtube.com/watch?v=bm61_vsrGEI&t=946)]
And it's a good start. And then we can... We can think about how we're going to even batch the different tensors. That's what they do.

##### **Geohot** [[00:15:57](https://www.youtube.com/watch?v=bm61_vsrGEI&t=957)]
I don't think we have to worry about that. Because there should only be, like, 10 or 11 tensors. If there's not, that's a different bug.

##### **Geohot** [[00:16:07](https://www.youtube.com/watch?v=bm61_vsrGEI&t=967)]
Yeah.

##### **Geohot** [[00:16:09](https://www.youtube.com/watch?v=bm61_vsrGEI&t=969)]
Understand the number of tensors, number of kernels per all-reduce.

##### **Geohot** [[00:16:13](https://www.youtube.com/watch?v=bm61_vsrGEI&t=973)]
You know, kind of figure out where we're going.

##### **Qazalin** [[00:16:15](https://www.youtube.com/watch?v=bm61_vsrGEI&t=975)]
Yeah. So, I will work on stack. Hopefully that will be both generic and also solve the remaining 36 minutes left to go. We're at, like, around 1.48, 1.5. Where's that? They're at, like, 1.3, 1.4. So...

##### **Geohot** [[00:16:42](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1002)]
14 minutes off this week.

##### **Qazalin** [[00:16:44](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1004)]
Yeah.

##### **Nimlgen** [[00:16:45](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1005)]
Okay.

##### **Qazalin** [[00:16:46](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1006)]
Cool. It's not going to be more handwriting. It's just that I did handwrite some used tiles.

##### **Geohot** [[00:16:56](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1016)]
Yeah. It's kind of okay, too.

##### **Qazalin** [[00:16:58](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1018)]
Yeah. But... Yeah. That's all for me.

##### **Nimlgen** [[00:17:05](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1025)]
Cool. Cool.

##### **Geohot** [[00:17:08](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1028)]
Yeah.

##### **Chenyu** [[00:17:08](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1028)]
Read the stack and the `_stack` thing. And complain if it looks weird. Because they certainly look weird.

##### **Geohot** [[00:17:17](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1037)]
Well, we have `_stack`, and then we have vectorize. Vectorize is just `_stack` with the stupid dtype.vec. But that can go away soon.

##### **Chenyu** [[00:17:26](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1046)]
Yeah. That would be nice. And then there's like MSTACK when you have, like, multi and those. Well, that's a different problem. But... Yeah.

##### **Geohot** [[00:17:36](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1056)]
Okay.

##### **Chenyu** [[00:17:37](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1057)]
Next is the new codegen stuff.

##### **Geohot** [[00:17:42](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1062)]
Yeah. I made good progress last week. Um... I have something almost passing all the tests. Uh... The... I mean, the main... The main whole thing was just rewriting the... So the devectorizer was doing two things. The devectorizer was... And they're really completely separate concerns. So the devectorizer was handling devectorization. Which was saying, like, okay, if you have, like, two float4 adds, convert it into four adds. But it was also handling memory. And memory coalescing. And... Memory coalescing is saying that if I have loads from four contiguous addresses. From four, like, plus zero, plus one, plus two, plus three. Turn that into one load. And this is a completely separate concern from the devectorizer. But they were mushed together. And then image was interacting with this whole thing in a weird way, too. So what I did last week was I moved all of that logic out of devectorizer into coalesce. And now images are finally where they should be. So images are now, like, treated almost perfectly like instruction selection. Because when you look at memory coalescing, it actually looks more like instruction selection. Than it does any kind of, like, vector operation. Right? You're just basically saying, instead of doing four load instructions, you can just do one load instruction. In the same way you might, like, you know, have a...

##### **Geohot** [[00:19:12](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1152)]
Have a multiply... I cannot hear you.

##### **Geohot** [[00:19:29](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1169)]
Pretty simple. Like, I'm passing most of the tests. I should have that done in, like, two days. With the new devectorizer and the new expander. Because there's nothing really there anymore. I mean, the expander is just... The expander is just broadcast. And the new devectorizer is just... It's, like, one basic rewrite rule. That says, oh, okay, you have a float4... Okay, cool. Turn that into index, add, stack. Yeah, you know, it was also, like... The last one I was, like, too concerned with premature optimization. I was too concerned with making sure that, like, nothing ever happened. That was, like, the size of the... The size of the... The, like, 128. It was when I was doing the DSP contract. But, like, on GPUs, these things aren't 128. On GPUs, these things are, like, 4 or 8. Like, who cares? So it's a lot simpler to read. Yeah. So they'll get done this week. Then there's a multi-project. And there's a rangeify cleanup project. A bunch of things are also just way simpler. So one of the big problems with dtype.vec... Is dtype.vec only supported a single dimension. And there were many things where a single dimension was just, like... Really, really hard to deal with. For example... If you had something that was, like... Like locals. And the locals was upcasted four... So I have something that's doing, like, a two-stage reduce. And the middle of the stage is, like, size 16. But then I also upcast the output four... So you'd have this thing that was... Really 16,4. But dtype.vec didn't support 16,4. dtype.vec only supported 64. And a huge amount of complexity came from that. So now we can just support something that's actually 16,4. And it's simple.

##### **Nimlgen** [[00:21:35](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1295)]
Yeah.

##### **Geohot** [[00:21:37](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1297)]
Hopefully everyone understands the new codegen. I'm going to put... It might take more than two days to get it merged. Because I do want to put a lot of time into... Into... Polishing this. Because I think these are the final implementations. Like, I don't think there's any way to... I think these are, like, gradient. Like, the new expander and the new devectorizer are, like, gradient. Where they're going to each be basically 20 or 30 line things. That... It's fundamental.

##### **Geohot** [[00:22:05](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1325)]
There's no way to simplify it. Just done. Great.

##### **Chenyu** [[00:22:12](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1332)]
Do we still use... Do we still use... PtrDType now?

##### **Geohot** [[00:22:17](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1337)]
No. No. So, well... Where? And what do you mean by now? So, PtrDType and...

##### **Chenyu** [[00:22:25](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1345)]
And just delete PtrDType?

##### **Geohot** [[00:22:30](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1350)]
Once the devectorizer... I don't want to spend too much time, like, fixing up the old devectorizer and expander. But I'm pretty sure that one can be deleted now. Yeah. It's close. I deleted... I deleted two... Two ops. Last week, POINTERCAT and VCAT. And this week, we will delete EXPAND and CONTRACT.

##### **Geohot** [[00:22:52](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1372)]
Okay.

##### **Geohot** [[00:22:53](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1373)]
Or UNROLL and CONTRACT. Yeah, I don't... I don't know.

##### **Chenyu** [[00:22:58](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1378)]
But it's nice that it's going to be removed.

##### **Geohot** [[00:23:01](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1381)]
Yeah. But that's PtrDType. And dtype.vec is close, too. I mean, the new stuff just doesn't use it. There's a bunch of tests that, like, directly reference it that have to be deleted. And then, like, actually removing it from dtype requires... Cleaning up x86 more. Because x86 re-injects it in a few places. But otherwise... Well, okay. And then the real thing...

##### **Geohot** [[00:23:26](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1406)]
Hopefully, I can get it done.

##### **Geohot** [[00:23:29](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1409)]
Probably not this week, but next week. Is the deletion of dtype from UOp. Because once dtype.vec and PtrDType are gone... I would... Yeah.

##### **Chenyu** [[00:23:45](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1425)]
I don't know. It would be nice if you just...

##### **Geohot** [[00:23:48](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1428)]
Yeah. I mean, there's a few places. So, it's most annoying... x86 is really annoying. Because x86 uses dtype pretty explicitly. Because INS doesn't have dtype. Yeah. We'll have to change, like...

##### **Geohot** [[00:24:02](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1442)]
Const is going to have to change the argument to... It has to include the dtype, right? Oh, sure. Yeah. That's fine.

##### **Geohot** [[00:24:20](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1460)]
Yeah. So, const has to include the dtype in the argument. That has to happen.

##### **Geohot** [[00:24:26](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1466)]
Do you really need that? We can always have a cast after const. It's an interesting idea.

##### **Chenyu** [[00:24:39](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1479)]
Because with that, all your constants are the same thing. And you just specify what... What dtype you want. But anyway, that's a... Yeah.

##### **Geohot** [[00:24:49](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1489)]
Yeah. Yeah. I mean, it's kind of... Actually, we kind of do that. That's kind of the best way that we express... Like, that's how we express a BF16 const. Because there's no C suffix for it. Yeah. Yeah. Well, OK. New codegen first. Then when I start looking at the dtype, we'll solve something there. But yeah. Maybe we don't. It'd be interesting if the type of the const was determined by... Yeah. The type of the Python object, the arg.

##### **Geohot** [[00:25:17](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1517)]
And then const could either be weakint, weakfloat, or bool. Yeah. Or weakint, double, or bool.

##### **Chenyu** [[00:25:33](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1533)]
It's probably slightly more than that. There's like minus zero and some weird.

##### **Geohot** [[00:25:42](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1542)]
Oh, the stupid float crap. Yeah. That fake... That class I have for minus zero. Oh, yeah.

##### **Chenyu** [[00:25:47](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1547)]
Anyway, we can work on that later.

##### **Geohot** [[00:25:52](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1552)]
Yeah. I mean, maybe the only thing like, is there a weakfloat type in JAX?

##### **Geohot** [[00:25:59](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1559)]
Yes.

##### **Geohot** [[00:26:01](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1561)]
Really? Probably.

##### **Chenyu** [[00:26:02](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1562)]
Yeah. We should add that. But the thing is, these things, when they first introduced and designed, it has a good principle around it and good logic. Yeah. So it's like, now we have small dtypes and all the weird stuff. It's not very clean, but fine situation for JAX. I see.

##### **Geohot** [[00:26:30](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1590)]
I mean, it's unclear what a weakint means.

##### **Geohot** [[00:26:34](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1594)]
Say that again?

##### **Geohot** [[00:26:36](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1596)]
It's clear what a weakint means. It's not clear what a weakfloat means.

##### **Chenyu** [[00:26:41](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1601)]
It does mean, say, I have a Python 1.5 and I ALU it with something, that dtype of that 1.5 should change based on the other operand that I'm doing operation with. So if you add that to a float8, then it's automatically inferred as a float8. Oh, I see.

##### **Geohot** [[00:27:04](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1624)]
I see. So it's at the bottom of the dtype hierarchy, unlike double, which is at the top of the dtype hierarchy.

##### **Nimlgen** [[00:27:10](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1630)]
Yes.

##### **Chenyu** [[00:27:11](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1631)]
That's also where we use weakint slightly weirdly, because you really want the weakint to be the bottom. But since we also use it for the index, which is kind of infinite-width integer, that sits on the top of every integer. Yeah.

##### **Geohot** [[00:27:30](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1650)]
I mean, I think once we get rid of dtypes, if we want basically dtype broadcasting, I don't know what it's called, do we want to be able to just promote? Yeah, dtype promotion, right? But like implicit promotion, right? Like should I be able to add an int to a char?

##### **Chenyu** [[00:27:53](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1673)]
I think that's fine. The issue we didn't do this because we want to enforce in the spec to make sure we don't accidentally cast it to something else. It's like no one would expect uint64, int64 plus together. What's a dtype for that?

##### **Geohot** [[00:28:13](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1693)]
That's the worst one.

##### **Nimlgen** [[00:28:15](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1695)]
OK.

##### **Chenyu** [[00:28:16](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1696)]
No, this sounds good. Anything else?

##### **Geohot** [[00:28:22](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1702)]
Nope.

##### **Nimlgen** [[00:28:24](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1704)]
OK.

##### **Geohot** [[00:28:25](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1705)]
Moving on. That is my stuff.

##### **Chenyu** [[00:28:28](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1708)]
Also, I asked PtrDType, because if you look at tensor.py, there are a where that's there, and there is a bitcast that's there. So here, bitcast is blocked by dtype.vec, and where is blocked by PtrDType, because we use lets in a weird way.

##### **Geohot** [[00:28:52](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1732)]
Where? Yeah, there's a, so we, in our very lower part,

##### **Chenyu** [[00:29:02](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1742)]
we manually construct wheres on a PtrDType.

##### **Geohot** [[00:29:09](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1749)]
So it behaves slightly differently. So for now, it's different. But it can be the same.

##### **Geohot** [[00:29:21](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1761)]
I don't see this logic. What do you mean? I see like UOp where. I don't see anything about PtrDType.

##### **Chenyu** [[00:29:26](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1766)]
So there is a `tensor.where`, because you cannot directly use the ones in `uop.where`. And `uop.where` is written that way, because it needs to work with PtrDType. That's what I mean by different logic. There's override now.

##### **Qazalin** [[00:29:47](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1787)]
Oh, I see.

##### **Geohot** [[00:29:50](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1790)]
Wait, in UOp, there's an override?

##### **Chenyu** [[00:29:53](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1793)]
In tensor, there's an override.

##### **Geohot** [[00:29:55](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1795)]
In tensor, there's an override. But the only thing I see the override doing is broadcasting.

##### **Chenyu** [[00:29:59](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1799)]
Yeah, and you don't want to do that for PtrDType. If you go into broadcasting, it will work on the PtrDType. So now if you want to where... I see. You say, don't do that for PtrDType, which is bad.

##### **Geohot** [[00:30:13](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1813)]
Yeah, yeah, yeah. I mean, also, how close are we to just enabling broadcasting and taking it out of tensor?

##### **Geohot** [[00:30:24](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1824)]
I don't know.

##### **Chenyu** [[00:30:25](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1825)]
I don't really check. I haven't checked. If we want to do that, we can do that. So you already have this in one of your branch. So I didn't really check.

##### **Geohot** [[00:30:35](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1835)]
No, I haven't done this. I think this is on your side. I think this is on the tensor side. I have a branch which enables, which turns off disallow broadcast because I need it for the new expander. But I don't change how broadcasting is done at all at the tensor level.

##### **Chenyu** [[00:30:52](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1852)]
So what do you mean by disable or change that?

##### **Geohot** [[00:30:55](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1855)]
Oh, so like right now, we do explicit broadcasting, like in the where function in tensor.

##### **Chenyu** [[00:31:00](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1860)]
If we remove that, then we need to enable that flag, right?

##### **Geohot** [[00:31:04](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1864)]
Yeah. I think that flag's fine to enable. I think whatever you want to enable it. Oh, OK. Sure. Yeah.

##### **Geohot** [[00:31:10](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1870)]
Yeah, yeah. Yeah, I'm sure.

##### **Geohot** [[00:31:13](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1873)]
The only reason I put that flag was just to prevent bugs for as long as we can. But we have to just enable broadcasting eventually.

##### **Chenyu** [[00:31:20](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1880)]
OK. Yeah, so I think that's really the last bit of tensor. Probably pretty ready if we, or before I talk on this. I also removed Tensor.training. So everything training related now goes through that ContextVar training. And I also did some cleanup on the unique buffer. So UNIQUE and LUNIQUE are gone. Now the dedup key is the ParamArg. Then there's one last use for Ops.DEVICE that's in program. So I think the correct way to do that, I think, is to remove. And then you can use the ProgramSpec and specify a device, like put the correct device there. Is that right? Because I saw a lot of manually constructed programs that use Ops.DEVICE.

##### **Geohot** [[00:32:24](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1944)]
Yeah, I mean, I think we could put it in ParamInfo. What do you mean?

##### **Qazalin** [[00:32:35](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1955)]
So we could. So when we construct the.

##### **Geohot** [[00:32:38](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1958)]
Yeah, for a program. Yeah, but it could just inherit, right?

##### **Geohot** [[00:32:49](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1969)]
Like we can create, when we create the program right now, we create the params without a device.

##### **Geohot** [[00:32:57](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1977)]
But is there any downside to just putting a device in them?

##### **Geohot** [[00:33:03](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1983)]
Where?

##### **Geohot** [[00:33:06](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1986)]
So like in.

##### **Geohot** [[00:33:08](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1988)]
In not ProgramInfo, no, no, no, in a ParamInfo. What's it called? The arg on param. Param.

##### **Chenyu** [[00:33:16](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1996)]
ParamInfo.

##### **Geohot** [[00:33:18](https://www.youtube.com/watch?v=bm61_vsrGEI&t=1998)]
ParamArg. Yes. So we have these ParamArgs on as an arg of all the params in the program. Why not just put devices on?

##### **Chenyu** [[00:33:33](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2013)]
When you construct the program.

##### **Geohot** [[00:33:37](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2017)]
You don't necessarily know the device of your inputs, right? Of course I do. Isn't it just some like. Well, OK. So this brings me to another problem.

##### **Geohot** [[00:34:02](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2042)]
Currently, device is overloaded to mean two things. Like we should remove the colon from device basically. But you absolutely know when you're constructing the program that this is AMD or this is Clang or this is.

##### **Geohot** [[00:34:23](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2063)]
Right?

##### **Qazalin** [[00:34:25](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2065)]
Right.

##### **Geohot** [[00:34:33](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2073)]
I mean, so my program has a linear, has a source, has a binary, and a device.

##### **Chenyu** [[00:34:38](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2078)]
I mean, it should be in the linear basically.

##### **Geohot** [[00:34:46](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2086)]
There's only one device in the program.

##### **Geohot** [[00:34:49](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2089)]
Yes. Like the SINK should have it. OK. Yeah. It should come from the. It should come from the.

##### **Geohot** [[00:34:56](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2096)]
I mean, it should be like a production rule. It will come through the SINK. But it should just be on the params. I guess.

##### **Nimlgen** [[00:35:06](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2106)]
Yeah.

##### **Chenyu** [[00:35:06](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2106)]
Then why was PROGRAM done this way? If SINK is its first source and SINK has it, why does it need a device before?

##### **Geohot** [[00:35:17](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2117)]
It doesn't. So the reason that it was done this way is just because the old, back when it was still called DEFINE_GLOBAL, didn't have a device.

##### **Geohot** [[00:35:28](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2128)]
But now that it's a param, you can just put the device in there.

##### **Nimlgen** [[00:35:36](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2136)]
OK.

##### **Geohot** [[00:35:37](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2137)]
Okay, we have.

##### **Chenyu** [[00:35:39](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2139)]
OK.

##### **Chenyu** [[00:35:40](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2140)]
OK. I'll think about this. That kind of makes sense. It's just slightly confusing when all the examples that use this are manually constructed.

##### **Geohot** [[00:35:51](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2151)]
I mean, I don't know about that.

##### **Geohot** [[00:35:54](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2154)]
So the. You can add it to the rewrite of params. You can add it here. If you want to just have it inject the device into those params. Or you could even do it. You could do it in rangeify.

##### **Chenyu** [[00:36:31](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2191)]
OK. I just need a way to update at least tests and functions that work with custom kernel and the custom program.

##### **Geohot** [[00:36:44](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2204)]
That would be the last use of Ops.DEVICE. Can I delete, please?

##### **Geohot** [[00:36:52](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2212)]
Yeah, it should definitely come from a param. And there's no such thing as a program that doesn't have a param. Like a program without a param is nonsense.

##### **Geohot** [[00:37:04](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2224)]
Because what does it do?

##### **Chenyu** [[00:37:06](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2226)]
I thought you can put placeholder or something. But I don't know too much about this.

##### **Geohot** [[00:37:13](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2233)]
Well, placeholder is param. Placeholder is a terribly named function that creates params.

##### **Geohot** [[00:37:19](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2239)]
OK.

##### **Geohot** [[00:37:21](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2241)]
Remember, param is buffer from the outside. And buffer is buffer only in the scope.

##### **Geohot** [[00:37:30](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2250)]
Yeah. Yeah. So all. All programs must have at least one param. OK. OK. I mean, that sounds good.

##### **Chenyu** [[00:37:52](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2272)]
Then we will get rid of device in the program.

##### **Nimlgen** [[00:37:56](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2276)]
Great.

##### **Geohot** [[00:38:00](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2280)]
I think that's pretty much it for my part.

##### **Chenyu** [[00:38:04](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2284)]
We can move on to HCQ2.

##### **Geohot** [[00:38:06](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2286)]
We can move on to HCQ2.

##### **Nimlgen** [[00:38:08](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2288)]
Yeah. So I'm still working on refactoring HCQ2. So basically have two explicit parts now, schedule and link. So link is basically when we just start to touch devices, and it's just kind of postponed. So we can do, I mean, with devices and like for Metal and for USB, we just also pass C pointers to the C functions inside the buffer, so like the program can use this.

##### **Geohot** [[00:38:52](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2332)]
Yeah, so I still need to...

##### **Geohot** [[00:38:59](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2339)]
I'm hitting the assertion on memory coalescing when I try HCQ2.

##### **Nimlgen** [[00:39:05](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2345)]
Yeah, I just reverted this thing and I'm just going to fix this in my branch in the rewrite. Basically yeah, I think I know I've seen you pull request on bitcasts. So what's the... What shapes do we want? Do we want like empty shape or just one?

##### **Geohot** [[00:39:32](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2372)]
Yeah, so okay. The bitcast that's hard, the thing that I'm not exactly sure how to do, and maybe you have an opinion on which way it should go, is like... So it's easy what you have when you want to do a bitcast. If you have like a float with size one and you want to cast it to like uint16, right? So that's going to go from one to two. But now... What happens when you have an empty shape, a zero-dimensional tensor, and you bitcast that?

##### **Geohot** [[00:40:05](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2405)]
Should that be allowed? That's a good question. I think probably.

##### **Geohot** [[00:40:31](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2431)]
So it's easy to see what to do for the zero-dimensional shape being bitcasted. But now, what if you have something that's like shape two of a uint16 and you want to bitcast that to float?

##### **Geohot** [[00:40:43](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2443)]
What's the output shape? uint16 to float.

##### **Nimlgen** [[00:40:56](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2456)]
Should this be legal? You have something? Yeah, yeah, two. Two. I see. I would say one.

##### **Geohot** [[00:41:07](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2467)]
You'd say one.

##### **Geohot** [[00:41:09](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2469)]
So that's the annoying one. Because if you have something that goes from like one to two and two to one, that's clear. But if you have something that goes from zero dimensional to two, and then you bitcast it back, and it goes from two to one, that's annoying.

##### **Geohot** [[00:41:28](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2488)]
Yeah.

##### **Geohot** [[00:41:30](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2490)]
I mean, I think that's the way to do it. I think that that's the right way to do it. I haven't come up with a better way. The only other thing would just be to... Maybe the clear solution here is just to not allow bitcast on zero dimensional shape.

##### **Geohot** [[00:41:52](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2512)]
Mm-hmm. I think that's what Torch does. Try it. I think that's what Torch does. Tensor has no attribute bitcast. Yeah. I don't see... I don't see HCQ2 working. Is that expected?

##### **Qazalin** [[00:42:43](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2563)]
Yeah, I think after a while, yeah.

##### **Geohot** [[00:42:53](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2573)]
But why? So Torch allows this? Oh, no, it doesn't.

##### **Nimlgen** [[00:43:04](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2584)]
Yeah. I guess I'll just have to wait until I get in some runtime functions, like USB runtime functions or like Metal runtime functions.

##### **Geohot** [[00:43:13](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2593)]
Cool. Yeah, no, the separation makes a lot of sense. I mean, the schedule is basically it's like codegen, it's like buffer gen.

##### **Nimlgen** [[00:43:21](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2601)]
Yeah.

##### **Geohot** [[00:43:23](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2603)]
Yeah, okay. So you want to do buffer gen, and you have a separate phase where you... Yeah, we want to wait as long as possible to touch the device.

##### **Geohot** [[00:43:32](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2612)]
Yeah.

##### **Nimlgen** [[00:43:36](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2616)]
Cool.

##### **Geohot** [[00:43:38](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2618)]
What do you think the approximate ETA is of getting switched over to HCQ2?

##### **Nimlgen** [[00:43:46](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2626)]
So I think I'll definitely complete this rewrite this week, and it will work on AMD. Not sure about USB. Yeah. Yeah, Metal is a bit annoying, all these Objective-C functions. Maybe next week.

##### **Geohot** [[00:44:07](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2647)]
Cool. Yeah. OK, anything else?

##### **Qazalin** [[00:44:23](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2663)]
No.

##### **Chenyu** [[00:44:26](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2666)]
OK, next is CI.

##### **Geohot** [[00:44:28](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2668)]
Yeah. So everything's a bit faster.

##### **Chrism** [[00:44:35](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2675)]
I just sort of cleaned up. The biggest thing that changed was the macOS tests are now, besides Metal, are now sort of in the same state as Windows tests, in that they just run `test_tiny`. macOS unit is still slow. It takes four minutes. I need to figure out exactly what I'm going to do to make that faster. In particular, like test/unit is pretty slow. So I just have to figure out exactly what to do there. I also cleaned up the benchmarks a little bit, although I need to look into why that one BEAM on AMD is flaky. So I'll look into that and try and figure out what's going on with that this week. Yeah, that's the big changes. I also, so I looked into that, the reason that I fixed IR3. And it's interesting because like this, obviously, we should set this flag. But it's interesting that this only appeared after the changes to image, that we only discovered this after. And I think this is because the codegen is emitting a whole bunch of casts for whatever reason.

##### **Chrism** [[00:45:59](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2759)]
For whatever reason. And so for instance, let me have a screenshot of this.

##### **Geohot** [[00:46:06](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2766)]
Yeah, I mean, I know where those casts are being emitted. It's just because it should be, yes. Yeah, the where somehow didn't get casted and used to get casted. I saw that change. It made no difference on the Qualcomm backend. The code is the same. So yeah.

##### **Geohot** [[00:46:31](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2791)]
If the assembly was the same. So wait, the assembly is the same? Yeah, I mean, on the Qualcomm backend, yeah.

##### **Chrism** [[00:46:43](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2803)]
I see a whole bunch of convert instructions. I'll have to double check. I didn't look at it super closely. But I remember looking at that and seeing a whole bunch of convert instructions that

##### **Geohot** [[00:46:51](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2811)]
looked like they shouldn't be there. Oh, maybe I did it wrong. Oh. OK.

##### **Nimlgen** [[00:46:57](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2817)]
OK.

##### **Geohot** [[00:46:58](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2818)]
OK. What should be, nothing should be converted, though. It's just a data op. It's not a. Here's the, right, that's COV F16 to F32.

##### **Qazalin** [[00:47:19](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2839)]
Huh. Oh, maybe I checked it badly.

##### **Chrism** [[00:47:27](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2847)]
Anyway, it's interesting they didn't slow it down all that much because when I was working on this previously, I noticed that this was one of the slowest things with all these conversion instructions.

##### **Geohot** [[00:47:35](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2855)]
I mean, this is nonsensical.

##### **Geohot** [[00:47:37](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2857)]
What?

##### **Chrism** [[00:47:38](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2858)]
Look at that. Why do that?

##### **Geohot** [[00:47:43](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2863)]
Yeah. Well, I mean, you can't remove that, right?

##### **Chrism** [[00:47:46](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2866)]
That cast has an effect.

##### **Geohot** [[00:47:51](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2871)]
That cast, oh, it's not this kernel. OK, no, no, no, no, no. It's not this kernel. Yeah. This kernel is actually, OK, no, no, no, no, no. It's not this kernel. That didn't make a change. There's one where the only thing that's changed is the where. No, but I guess, no, yeah, yeah, yeah. If you're cast down to.

##### **Chrism** [[00:48:18](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2898)]
Yeah, that's not an optimization. You can't optimize that out. I mean, obviously, whatever code is doing that is kind of silly. But it's observable.

##### **Geohot** [[00:48:29](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2909)]
Yeah.

##### **Geohot** [[00:48:30](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2910)]
Also, that assembly syntax is so confusing. It's convert F32, F16. And then the first argument is F16, and the second argument is F32.

##### **Chrism** [[00:48:43](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2923)]
The first argument's the destination, right?

##### **Geohot** [[00:48:45](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2925)]
Yeah, the first argument's the destination. But wouldn't you write that the other way? I guess it's like convert F32 to F16.

##### **Chrism** [[00:48:52](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2932)]
Yeah.

##### **Geohot** [[00:48:56](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2936)]
Yeah, I don't know. I mean, the whole thing was faster. I didn't do that wrong, did I?

##### **Chrism** [[00:49:01](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2941)]
No, it is. Yeah, it is faster, although the IR3 is slower. IR3 is slower. Yeah, yeah, yeah. Yeah. I looked at that. That's almost all of the time difference in that is in the big concat kernel at the end. I haven't looked exactly why that is, but that's almost where all of it is.

##### **Geohot** [[00:49:19](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2959)]
There were a bunch of things that just got reordered.

##### **Geohot** [[00:49:23](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2963)]
Yeah.

##### **Chrism** [[00:49:27](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2967)]
Anyway, in any case. Yeah. I think that was one of the, at least when I was working on this, that was one of the most frustrating things, was trying to get those casts to go away. But I guess if it doesn't, I don't know. I mean, it seems surprising to me. This doesn't impact the speed of the kernel, but I guess maybe it's just so negligible.

##### **Geohot** [[00:49:43](https://www.youtube.com/watch?v=bm61_vsrGEI&t=2983)]
Yeah. Yeah, I mean, this is kind of, you see why this is happening. What I moved is where the image load. Yeah. Yeah. The image load becomes a float later. Yeah. So yeah, the image load, I mean, the image load used to be a hard float that it would output. But I don't even know exactly how it changed because the tensor graph says that it's a half.

##### **Geohot** [[00:50:20](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3020)]
So when that where is inserted in the tensor graph, that where is being inserted on a half. So I think that's the reason why it's so frustrating.

##### **Chrism** [[00:50:34](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3034)]
Yeah. I think if I remember correctly, the reason this becomes so frustrating is because the casts move through the where. And then it gets promoted past the where. And then that's the reason that this becomes so hard to optimize or so hard to remove later, is because you'd have to look through the where's to be able to tell that they need to collapse. And you can't just be like, oh, this is where the load is.

##### **Nimlgen** [[00:50:59](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3059)]
And then you have to look through the where's to be able to tell that it's a half.

##### **Geohot** [[00:51:01](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3061)]
So I think that's the reason why it's so frustrating.

##### **Geohot** [[00:51:02](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3062)]
I think it's just so frustrating to be able to do that. I mean, you'd want to like, let's see what this is doing. I mean, wait, this is just straight up. This is just straight up float half casting. I thought we were able to remove that. Yeah. You can't generically remove this.

##### **Geohot** [[00:51:30](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3090)]
Well, I have a rule. There's a clear rule in PM simplify add image to remove this.

##### **Geohot** [[00:51:37](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3097)]
I don't know why it's not. Like the bottom rule there should remove that, right? ALU 10 is being casted to half and then being casted to float.

##### **Geohot** [[00:51:51](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3111)]
I don't know. I can't read all those parentheses, but.

##### **Nimlgen** [[00:51:54](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3114)]
I don't know. I don't know.

##### **Geohot** [[00:51:55](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3115)]
I can also get rid of a lot of those parentheses. Oh, yeah. Yeah. Yeah. You don't really need them all. I just kept them in. When I rewrote the codegen for this, I just kept them in so that process replay would match, but you can take them out. That's interesting, but it doesn't get removed. I don't know what's up with that. Yeah, that's what I mean. I'm pretty sure. I don't know what happened because I'm pretty sure I checked this and that this went away. I don't know. I don't know. I don't know what happened. Well, this is R4, R4, R4.

##### **Chenyu** [[00:52:34](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3154)]
It's possible that at that point it becomes a half4 or float4 instead of float?

##### **Geohot** [[00:52:43](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3163)]
No, there's no such thing as half4 and float4 anymore.

##### **Geohot** [[00:52:48](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3168)]
I mean the dtype. Oh, there's.

##### **Geohot** [[00:52:52](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3172)]
Oh, it's gone.

##### **Chrism** [[00:52:53](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3173)]
No. It's gone. The PM simplify add image is happening. Like this should get removed by that rule.

##### **Chenyu** [[00:53:00](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3180)]
OK. Something to check.

##### **Geohot** [[00:53:04](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3184)]
I think it was getting removed by that rule and then something happened because I did check this.

##### **Chrism** [[00:53:09](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3189)]
Yeah, I don't know what's up with that. Anyway, this is one kernel. This is the kernel that triggered the IR3 bug.

##### **Nimlgen** [[00:53:15](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3195)]
Yeah.

##### **Geohot** [[00:53:17](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3197)]
The IR3 bug was a real bug. I'm glad we fixed it. Yeah. I think. Yeah. The thing to focus on this week is we can't. We got to get benchmark times. More manageable.

##### **Chrism** [[00:53:29](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3209)]
Yeah. This is the reason I didn't add OLMo again. It's just because it was so slow. Like it takes a full 10 minutes to run on NV and AMD. Yeah. Yeah.

##### **Geohot** [[00:53:42](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3222)]
I mean, even just like breaking these up better, right? Like we still have things called like benchmark. I mean, like we should just call it like LLMs and CIFAR. I mean, like, we should just call it like LLMs and CIFAR.

##### **Nimlgen** [[00:53:53](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3233)]
Right. We should just call it like LLMs and CIFAR. Yeah. Yeah.

##### **Geohot** [[00:53:54](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3234)]
Yeah. Yeah. All right. I mean, there's no, there's no downside. There's no, the launch cost of this process is so negligible compared to the runtime. Yeah.

##### **Geohot** [[00:54:08](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3248)]
Yeah. Okay.

##### **Geohot** [[00:54:09](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3249)]
I'm saying if you, if you take a 10 minute job and you split it into two, five minute jobs, that's only a win.

##### **Chrism** [[00:54:14](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3254)]
Yeah. Yeah. Okay. Yeah. Yeah. This is definitely going to go under, under, under 10 minutes. We might need more runners though. Right. Like that was the only thing that I was like, okay, well now we have to sit around waiting for these things to queue because they're, you know, they're backed up.

##### **Chenyu** [[00:54:30](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3270)]
We don't need more runners. We just, we need to make sure the current runners are all running.

##### **Geohot** [[00:54:35](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3275)]
That is true. We need alerting. Wozeparrot, alerting?

##### **Geohot** [[00:54:40](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3280)]
GPT-OSS is more important than alerting, but we need alerting.

##### **Wozeparrot** [[00:54:45](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3285)]
We need alerting. Somewhat alerting. If you go to stats right now, go to the bottom. I explicitly pull the state of the actions runner services now. Oh, nice. So it's really quick to set up alerting off of that. So I can just do that today.

##### **Chrism** [[00:55:04](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3304)]
Cool. It also just helps to have that because you can see immediately when something goes wrong. All right. Because in the past what we've seen is like, oh, like one of these goes offline and then, you know, no one notices that it's gone offline until like, you know, a week later and then all the logs have rotated and it's like impossible to tell what's going on. What happened?

##### **Geohot** [[00:55:22](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3322)]
Yeah. I'm hoping this is reliable too. Like this reliably determines whether it's taking jobs. There's not like some way it can report good state while not taking jobs.

##### **Chenyu** [[00:55:32](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3332)]
I think it's reliable if every machine now has the timestamp of when was the last time it did a job and if that becomes too long, it means it does nothing.

##### **Geohot** [[00:55:47](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3347)]
Then we can base off of that. In any case, like even if we have all the jobs are.

##### **Wozeparrot** [[00:56:00](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3360)]
I don't know if we can pull exactly when the last ran job was, but the runner service does automatically die if the token is not correct. Which seems to be the main is like the only reason our runners have been going offline is that they go offline. For some other reason, no one notices and then the token is rotated. So rebooting the machine doesn't bring the runner back online.

##### **Geohot** [[00:56:30](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3390)]
Why is the token getting rotated?

##### **Wozeparrot** [[00:56:33](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3393)]
GitHub automatically drops the token if the runner doesn't connect.

##### **Geohot** [[00:56:38](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3398)]
I see, okay, good. Well then we fix this with alerting and then fix everything. How long does GitHub take to drop the token?

##### **Wozeparrot** [[00:56:47](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3407)]
They say two weeks. There's cases where it's been less than that and the token still drops.

##### **Geohot** [[00:56:57](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3417)]
Okay.

##### **Chenyu** [[00:57:00](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3420)]
Let's follow this up in the channel offline. And anything else for this meeting? Is comma happy?

##### **Chrism** [[00:57:11](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3431)]
I think comma is happy. I saw their update like automatic updates. It's failing. But it's not. It's failing for some other reason. It's like that's not related to us. So I think that's still good.

##### **Geohot** [[00:57:26](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3446)]
I think the runtime is also slightly faster.

##### **Chrism** [[00:57:30](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3450)]
Yeah. Yeah. So hopefully they're happy about that.

##### **Chenyu** [[00:57:34](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3454)]
Okay. And we have a newly added GLM bounty. Yes.

##### **Geohot** [[00:57:43](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3463)]
$3,000 if someone gets GLM running in tinygrad, 100 tokens plus, merged into master.

##### **Geohot** [[00:57:49](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3469)]
100 tokens per second plus.

##### **Nimlgen** [[00:57:56](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3476)]
Okay.

##### **Geohot** [[00:58:00](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3480)]
Anything else for the meeting?

##### **Chenyu** [[00:58:04](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3484)]
Oh, I found having Claude summarize past meetings and cross-compare with the actual code and code changes very useful. Now I have a list of things people promised to do and have not done. How many things did I promise to do and didn't? Probably a lot.

##### **Nimlgen** [[00:58:21](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3501)]
Yeah.

##### **Chenyu** [[00:58:22](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3502)]
I mean, this is a good list for like projects or things to do.

##### **Geohot** [[00:58:30](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3510)]
What channel did you put that in?

##### **Chenyu** [[00:58:32](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3512)]
I saw that. I didn't read it. Oh no. I mean, I don't have a continuous update, but I can have Claude update this every day for me. Great. Nah, it's some small stuff. And I think one important lesson here is the spec was very useful. Because everything can compare with spec. Great. You need some ground truth to know where the end goal is and go from there. So having spec. This is the year of spec and we have an end goal. Yeah. Cool. Okay. I think that's it for this meeting. Thank you everyone. See you next week. Bye bye.

##### **Geohot** [[00:59:12](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3552)]
Bye.

##### **Nimlgen** [[00:59:14](https://www.youtube.com/watch?v=bm61_vsrGEI&t=3554)]
Bye.
