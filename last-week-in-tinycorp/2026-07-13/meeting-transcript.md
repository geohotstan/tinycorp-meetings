# 2026-07-13 Meeting

### Meeting Agenda

**Time:** new meeting #28, 7/13 9am Monday San Diego time
- company update
- VIZ LLaMA training
- GPT-OSS training
- SLICE cleanups
- dtype cleanups
- CONST dtype, INDEX, STACK
- HCQ2
- bounties, issues, comma happiness, GLM


### Audio

[Youtube Link](https://www.youtube.com/watch?v=dfMxyGxd_WE)

### Highlights

* **[Company Update](#geohot-000008)**: AMD discussions continued around partially defective MI300X GPUs, which could enable inexpensive GLM-capable systems and potentially become a million-dollar opportunity.

* **[Product Launch](#geohot-000116)**: The USB dock remains on track for an end-of-month launch, with pricing still being finalized.

* **[LLaMA Training Performance](#qazalin-000229)**: Master achieves roughly 1.55 seconds per step, with incoming changes expected to reach 1.44 seconds; matching AMD requires approximately 1.3 seconds.

* **[Training Optimization](#geohot-000525)**: The immediate LLaMA priorities are eliminating elementwise and idle kernels, followed by GPT-assisted optimization of GEMM and FlashAttention kernels.

* **[GPT-OSS Training](#wozeparrot-000916)**: A promising GPT-OSS run reached 8,000 of 13,000 steps before the machine crashed; the projected full runtime is about 30 hours, with sliding-window attention still lacking a fast kernel.

* **[SLICE Removal](#chrism-001501)**: SLICE is close to removal after eliminating late `BUFFER_VIEW`; remaining work involves RANGEIFY aliasing rules and replacing SLICE-specific handling with CAST and SHRINK.

* **[Dtype Simplification](#geohot-002057)**: `dtype.vec`, `PtrDType`, and `ImageDType` have been completely removed, leaving SLICE, NOOP, INS, and CONST as the remaining blockers to removing dtype from the UOp constructor.

* **[MULTI Redesign](#geohot-002057)**: MULTI will be replaced with PAD-based semantics, eliminating MULTI, MSTACK, and MSELECT while enabling movement operations and `alloc_fragment`-style register distribution across threads.

* **[STACK Cleanup](#chenyu-003017)**: `_stack` and VECTORIZE have been removed; STACK is now the unified operation and works at every level.

* **[HCQ2 Progress](#nimlgen-004016)**: HCQ2 now supports cache linking, but still needs indirect buffers and lower CPU runtime latency; workers are being rewritten in UOps, with external C calls expected to use a renderable CALL operation.

* **[HCQ2 Migration](#geohot-005503)**: The company is fully committed to HCQ2 and will migrate AMD first, accepting temporary disruption while simplifying HCQ2-specific classes into the standard Buffer and Allocator abstractions.

* **[RDNA3 Backend](#reina-005828)**: The RDNA3 backend is down to roughly 19 failing tests; spill/fill support, slow integer-division expansion, and a few remaining correctness failures are the main blockers to reaching full test coverage.


### Transcript
##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=0)]
Okay, let's get started. Welcome. We'll start with company update.

##### **Geohot** [[00:00:08](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=8)]
Yeah, we got a few emails back from AMD. You know, this is the big deal that could make us a lot of money if it really comes through: the semi-broken MI300Xs. Um, yeah, a few more emails back and forth there, trying to find a way to actually plug one of these into a computer. There are some MI300 boxes on eBay right now that don't have MI300s in them. I asked the guy if it has the tray. We'll see about that. Yeah, I think this could potentially be a million dollars. I think we could sell boxes that can do GLM pretty cheaply with

##### **Geohot** [[00:01:05](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=65)]
semi-broken MI300Xs.

##### **Chenyu** [[00:01:11](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=71)]
It's not semi-broken. It's just 2% that's broken.

##### **Geohot** [[00:01:16](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=76)]
Well, I don't think, you see, I don't think they would work with the AMD driver. I don't think the AMD driver is designed to deal with that. You'd have to, like... Yeah, so it's not exactly 2%. It's 2% and only tinygrad. Um, and yeah, things are going pretty well for the product launch at the end of the month. Great. I think this one's pretty public. Yeah, the USB dock. You know, we're still working out pricing, but it's very, very pretty. Like, we have these little metal rails holding up the GPU. They're so nice. They're polished. I wanted to lick

##### **Geohot** [[00:01:54](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=114)]
them.

##### **Geohot** [[00:01:55](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=115)]
Oh, great. Okay. Nice. Nice. Okay. Anything else? Okay, let's move on. Next is LLaMA training.

##### **Qazalin** [[00:02:19](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=139)]
I started merging my stuff this week. So right now master... Can you hear me?

##### **Geohot** [[00:02:26](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=146)]
Yes.

##### **Qazalin** [[00:02:29](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=149)]
I started merging my changes. So right now master gets around 1.55 seconds per step, and we need 1.3 to match AMD. I have a few changes coming up that will get to 1.44. Can we fix the thermals?

##### **Geohot** [[00:02:54](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=174)]
We're working on it. So I mean, don't worry about it for now. It's not a fancy thing. What's going to be required to fix the thermals is that we have pretty high intake temperatures in our data center. Our intake temperatures are about 35 C, whereas usually 27 is the upper limit. This is fine for comma's stuff, because comma is using consumer cards. But yeah, it turns out the data center cards need a lot of cooling. The cooling solution is just not designed for full operation at 35. So we're working on lowering it. But I wouldn't worry about that. I think it's just, you know,

##### **Geohot** [[00:03:33](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=213)]
it shouldn't affect any of your work.

##### **Qazalin** [[00:03:39](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=219)]
So that should help with like total time.

##### **Geohot** [[00:03:42](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=222)]
What's the best total time we have now?

##### **Qazalin** [[00:03:45](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=225)]
Best total time we have is still the same two hours and 23 minutes.

##### **Geohot** [[00:03:54](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=234)]
Wait, but why? GPT made it faster.

##### **Qazalin** [[00:03:59](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=239)]
I can share what we're missing. GPT made it a little faster today. True. This is the step time breakdown.

##### **Geohot** [[00:04:09](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=249)]
All right, cool. And I mean, I like that. Yeah, I like that compute busy. So why are we why is compute ever not busy? Is that because of communication or?

##### **Qazalin** [[00:04:22](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=262)]
I'm not sure. I explicitly disabled overlap of SDMA with the backward pass because of the spikiness issue.

##### **Geohot** [[00:04:32](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=272)]
Oh, I see. Do we have a fix for the spikiness issue yet?

##### **Geohot** [[00:04:37](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=277)]
Um, today. Yeah. Oh, you got it today.

##### **Nimlgen** [[00:04:44](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=284)]
Yeah, I merged it already.

##### **Geohot** [[00:04:46](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=286)]
What was it?

##### **Nimlgen** [[00:04:49](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=289)]
Basically, it was spamming all the interrupts, like SDMA trap and EOP. So we just don't need them.

##### **Flata** [[00:05:02](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=302)]
Cool.

##### **Geohot** [[00:05:05](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=305)]
Yeah, that's a clean fix.

##### **Qazalin** [[00:05:07](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=307)]
Right. I'll check tomorrow morning. Yeah. Other than that, I have the elementwise kernels to go through. You'll see, 11% of the time is elementwise kernels.

##### **Geohot** [[00:05:25](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=325)]
Yeah, so I see basically two big areas. We just got to get rid of the elementwise kernels and the idle kernels.

##### **Geohot** [[00:05:35](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=335)]
Mm hmm.

##### **Geohot** [[00:05:37](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=337)]
Yeah, I think that's the stuff to focus on now. And then we can take it across the finish line with putting GPT on GEMM and FlashAttention.

##### **Qazalin** [[00:05:53](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=353)]
Yeah, it did some of it today. It was fun seeing it.

##### **Geohot** [[00:05:56](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=356)]
Yeah, great. Great. Great. Yeah, I think I think that if you have one kernel and you just want that kernel to get faster, GPTs are very, very good at that.

##### **Qazalin** [[00:06:07](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=367)]
Yeah, I merged the changes. I can't read them honestly, but it works.

##### **Geohot** [[00:06:14](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=374)]
Oh, I mean, be careful if you can't read them. I can't read it.

##### **Geohot** [[00:06:24](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=384)]
It's C++. You mean the one that you actually merged?

##### **Qazalin** [[00:06:30](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=390)]
Yeah.

##### **Geohot** [[00:06:32](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=392)]
Well, that looks okay.

##### **Qazalin** [[00:06:36](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=396)]
Yeah, I mean, it looks fine, but...

##### **Geohot** [[00:06:37](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=397)]
No, don't merge anything you actually can't read.

##### **Qazalin** [[00:06:41](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=401)]
Yeah.

##### **Geohot** [[00:06:42](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=402)]
I don't think anything there is unreadable. I see what it's doing.

##### **Qazalin** [[00:06:47](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=407)]
Yeah, I mean, it makes sense. Like it changed some stuff too.

##### **Geohot** [[00:06:52](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=412)]
It just messed with the sharding. It sharded across another axis, which is fine. Yeah. Cool. But it's really important that we have good tests if we're going to do this. I think those will get faster with GPT, but GPT is never going to do things like get rid of the elementwise kernels or get rid of the idle in satisfying ways.

##### **Geohot** [[00:07:15](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=435)]
We need to just fix that.

##### **Chenyu** [[00:07:20](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=440)]
I did the STACK thing. Does that help?

##### **Geohot** [[00:07:24](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=444)]
Sorry?

##### **Chenyu** [[00:07:26](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=446)]
I did the STACK thing. I'm not sure how much that helps.

##### **Qazalin** [[00:07:33](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=453)]
It helps a little bit because some of those elementwise kernels are because of STACK. Are you working on... because I saw some first-class STACK support things.

##### **Geohot** [[00:07:44](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=464)]
Yeah, I merged that.

##### **Qazalin** [[00:07:46](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=466)]
Yeah.

##### **Chenyu** [[00:07:47](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=467)]
So STACK doesn't create the ADD thing, the elementwise kernels. That's probably why you see fewer of those.

##### **Qazalin** [[00:08:00](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=480)]
Yeah, but `Tensor.cat` is still using the pad thing, right? I don't think that change updated that. `Tensor.cat`, sorry.

##### **Chenyu** [[00:08:12](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=492)]
Oh, yeah. So I don't know how to write cat with stack. Because cat can technically have different size. Yeah. So you might want to change the code if you know it's the same size and you can rewrite with stack. Cat cannot generically use stack. But if you know the inputs are with the same size, you can rewrite that part of the tensor code to use stack. Then that will be faster.

##### **Qazalin** [[00:08:40](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=520)]
Yeah, that should remove a bunch of elementwise kernels.

##### **Geohot** [[00:08:45](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=525)]
Great. Okay. Anything else? The plan is just to cleanly merge all the improvements. Yeah. Great. Anything else?

##### **Qazalin** [[00:09:05](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=545)]
That's all.

##### **Geohot** [[00:09:10](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=550)]
Okay. Next is GPT-OSS.

##### **Wozeparrot** [[00:09:16](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=556)]
We almost have a run. We were about 8,000 steps in before the machine crashed.

##### **Geohot** [[00:09:25](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=565)]
Does the curve look good?

##### **Wozeparrot** [[00:09:28](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=568)]
Curve looks good, yeah.

##### **Geohot** [[00:09:31](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=571)]
How many steps do you need?

##### **Wozeparrot** [[00:09:33](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=573)]
Oh, sorry. 13,000 steps. This is still pretty slow because we're still missing the sliding window attention as a fast kernel.

##### **Flata** [[00:09:48](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=588)]
Okay.

##### **Chenyu** [[00:09:48](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=588)]
So you say this is 8,000 and we need 13,000? Yeah. The projected time is?

##### **Geohot** [[00:10:00](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=600)]
1.2 days.

##### **Chenyu** [[00:10:02](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=602)]
30 hours for this for now?

##### **Geohot** [[00:10:04](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=604)]
Yep.

##### **Qazalin** [[00:10:05](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=605)]
Okay.

##### **Geohot** [[00:10:11](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=611)]
What is this crash? What? What?

##### **Flata** [[00:10:24](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=624)]
Oh.

##### **Geohot** [[00:10:26](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=626)]
Which, which, this is GPU, this is AMD 3 or AMD 4? AMD 4. Maybe we should just swap the tray. We haven't returned it yet.

##### **Geohot** [[00:10:39](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=639)]
Maybe we could swap the tray on AMD 4 to the other MI350 tray.

##### **Wozeparrot** [[00:10:44](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=644)]
I thought this was already the good tray.

##### **Geohot** [[00:10:47](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=647)]
No, we never opened the MI350 tray. They just reseated the GPUs. Oh, we probably want to do that then.

##### **Flata** [[00:10:55](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=655)]
Right.

##### **Geohot** [[00:10:56](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=656)]
Yeah, I'll just screenshot this and send it to them and say, hey, should I swap this? Will that fix it?

##### **Wozeparrot** [[00:11:04](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=664)]
Nimlgen thinks it's bad pages?

##### **Geohot** [[00:11:08](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=668)]
Oh, this is the bad pages issue. I'm not sure. I just inspected.

##### **Geohot** [[00:11:16](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=676)]
What is GPT? What is, what is this? But either way, yeah, use, use AMD 3 for this. If you want to switch computers, you could totally do the step speed up stuff. I want to get finished runs of this. So this should get to AMD 3. But actually, we'll swap the thing in AMD 4 today.

##### **Geohot** [[00:11:45](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=705)]
So hopefully that just fixes it. But . Was AMD 4 the faster one or was AMD 3 the faster one?

##### **Qazalin** [[00:11:58](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=718)]
AMD 4.

##### **Geohot** [[00:12:00](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=720)]
AMD 4. Great. The faster one is broken. Awesome.

##### **Qazalin** [[00:12:04](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=724)]
It's not totally broken. It's just sometimes broken.

##### **Geohot** [[00:12:08](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=728)]
Yeah, yeah.

##### **Qazalin** [[00:12:09](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=729)]
It's broken 60% of the time.

##### **Geohot** [[00:12:11](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=731)]
Oh, OK. Yeah. All right. So, and this is mostly slow because of the lack of sliding window attention.

##### **Nimlgen** [[00:12:19](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=739)]
Yes.

##### **Geohot** [[00:12:20](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=740)]
What time do you think we can have by the end of this sprint?

##### **Wozeparrot** [[00:12:30](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=750)]
Initial goal is just to get under a day.

##### **Geohot** [[00:12:35](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=755)]
Under a day.

##### **Wozeparrot** [[00:12:37](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=757)]
Yeah.

##### **Geohot** [[00:12:38](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=758)]
Like, how much of this is the... I don't think this is the memory. How much of this is just that one issue

##### **Geohot** [[00:12:57](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=777)]
versus many small issues?

##### **Wozeparrot** [[00:12:59](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=779)]
I haven't checked because I've just been trying to get a run done. There's been a lot of memory issues.

##### **Geohot** [[00:13:08](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=788)]
Well, good. At least I'm glad the loss curve matches what you think it should be. Yeah, and then AMD3 is yours.

##### **Geohot** [[00:13:20](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=800)]
So, yeah, I would just kick off a run right now.

##### **Chenyu** [[00:13:23](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=803)]
So, if we finish this run in like 30-something hours, does that comply with everything we need? Yes.

##### **Geohot** [[00:13:34](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=814)]
We still haven't gotten that contract from them. They keep telling me they're going to send it on Monday. That was the last Monday and this Monday.

##### **Chenyu** [[00:13:46](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=826)]
So... I don't mean for the contract. I mean for the... Is it a submittable or not? Other than logging, is everything... like, is there requirements for the context window and whatever?

##### **Wozeparrot** [[00:13:58](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=838)]
Yeah, it's just LLaMA 8B, but you swap the model.

##### **Geohot** [[00:14:07](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=847)]
Yeah, so this is MLPerf compliant.

##### **Wozeparrot** [[00:14:09](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=849)]
This is a good question. Yeah, yeah, yeah. It's the same as LLaMA 8B, except the model is swapped to GPT-OSS. That's fine.

##### **Geohot** [[00:14:24](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=864)]
Okay. Okay, so we will train this

##### **Geohot** [[00:14:34](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=874)]
on AMD3 and in up to two days, we should see the result.

##### **Flata** [[00:14:43](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=883)]
Yeah.

##### **Geohot** [[00:14:45](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=885)]
Sounds good. Anything else?

##### **Flata** [[00:14:52](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=892)]
Okay.

##### **Chenyu** [[00:14:57](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=897)]
Next is slice cleanups.

##### **Chrism** [[00:15:01](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=901)]
Yeah, so I'm hoping to be able to remove SLICE today. We only create SLICEs in two places now that I removed late BUFFER_VIEW. So all the slicing happens in RANGEIFY, or we also create SLICEs in the memory planner. The memory planner one is easy to get rid of, but unfortunately the RANGEIFY one is more complicated than I realized at first. I think we want to keep this invariant that PARAMs are not allowed to alias each other. That seems useful to keep around, and just due to the way the code is written right now it happens to respect this invariant, but there's no actual code that verifies that this is the case. And so I just need to write something that actually does that, because right now it just happens to be the case. It's not like a...

##### **Geohot** [[00:15:57](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=957)]
Well, you can, at least on read. You just kind of...

##### **Chrism** [[00:16:02](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=962)]
Yeah, yeah, that's true.

##### **Geohot** [[00:16:04](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=964)]
I mean, think about the version where you have one thing that's one texture and buffer that overlap in RAM, and read.

##### **Chrism** [[00:16:11](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=971)]
Yeah, yeah. Yeah, it is fine. I guess that's true. You don't have to do it like this. You could allow those alias. We're just gonna read from them.

##### **Geohot** [[00:16:21](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=981)]
Yeah, yeah, I mean, the only invariant we should actually enforce is one that says nothing that is written to can exist anywhere else. Like, if a buffer is marked write, then that buffer can't alias.

##### **Geohot** [[00:16:33](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=993)]
Mm hmm. Yeah.

##### **Chrism** [[00:16:37](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=997)]
Yeah, that makes sense. Anyway, I was really hoping to figure out a way to do this without having to add a field to the context thing that we use in RANGEIFY right now, but I feel like I might just need to do a pass over the graph, check what we write to, and then say, okay, don't use that.

##### **Geohot** [[00:16:56](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1016)]
I mean, it's simple. Yeah. I wouldn't worry about speed. Worry about simplicity.

##### **Chrism** [[00:17:05](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1025)]
But yeah, that's the deal. I have to go through, and we have code in JIT that says, here's what you do if you have a SLICE, and there's code in HCQ that says, here's what you do if you have a SLICE, and there's some special thing in Metal, like here's what you do if you see a SLICE. So I have to rewrite all that, but I think it should be doable. It should be relatively simple to swap that over to understand a CAST and SHRINK instead.

##### **Flata** [[00:17:36](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1056)]
Yeah.

##### **Geohot** [[00:17:43](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1063)]
All right. I think with this LLaMA training and GPT-OSS, we did a good job talking about what's happening next sprint. What's happening for you next sprint? SLICE should be done today or tomorrow.

##### **Chrism** [[00:17:52](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1072)]
Yeah. Yeah. Well, I can work on the like the up the type stuff. Also work on. It cast like matching jobs as well.

##### **Geohot** [[00:18:06](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1086)]
Um, I think the dtype stuff is good. I think that if you look at that GPT run I did where it gets CIFAR down to 20 seconds wall time, it has some interesting stuff about when it runs that dtype pattern matcher. It shouldn't, and that's not really the right thing, but the right thing to do is basically all of the decompositions should be one rewrite. It shouldn't be three staged rewrites.

##### **Geohot** [[00:18:34](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1114)]
Right.

##### **Geohot** [[00:18:35](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1115)]
And we have to be really careful during those to make sure that you keep the spec invariant. Really think about exactly what you want each of these dtype decomps to do.

##### **Flata** [[00:18:43](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1123)]
Yeah.

##### **Geohot** [[00:18:43](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1123)]
And there's a separate load/store thing, I guess. Yeah, it's the same thing that we always talk about: is op supported? We need that, and that's what to work on.

##### **Geohot** [[00:18:54](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1134)]
Yeah.

##### **Qazalin** [[00:18:54](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1134)]
Okay.

##### **Geohot** [[00:19:00](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1140)]
We're using work on disk. You want to work on disk? Uh, what? What? What? What about disk?

##### **Chenyu** [[00:19:11](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1151)]
Uh, DISK now has a special ASSIGN path.

##### **Chrism** [[00:19:16](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1156)]
Yeah. Uh, I can look at that too. I don't know exactly what all that does.

##### **Chenyu** [[00:19:22](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1162)]
Uh, pretty related to SLICE. Yeah. Yes, it was the old reason why those late rewrites, late BUFFER_VIEW or whatever, are there. Yeah, your code path for `Tensor.from_file` also showed that.

##### **Chrism** [[00:19:39](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1179)]
Yes. Yeah. Yeah. You're talking about the eager path and ASSIGN, right? Yeah, I can take a look at that.

##### **Chenyu** [[00:19:48](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1188)]
Maybe it's easier. It was a, it was a mass last time I check it. I hope it's easier.

##### **Chrism** [[00:19:54](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1194)]
I'll take a look because now that we do everything in RANGEIFY, maybe all of a sudden it's easier.

##### **Chenyu** [[00:20:00](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1200)]
Yeah. Or, or at least whatever you are replacing the current logic with should work towards that direction.

##### **Geohot** [[00:20:07](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1207)]
Yeah. Yeah. That makes sense.

##### **Flata** [[00:20:10](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1210)]
Cool. Yeah. Yeah. Yeah. Okay.

##### **Qazalin** [[00:20:14](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1214)]
Anything else?

##### **Geohot** [[00:20:15](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1215)]
I think that's it.

##### **Geohot** [[00:20:17](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1217)]
There's also still a few tests, like faults, that we have to get to the bottom of.

##### **Chrism** [[00:20:21](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1221)]
Okay. Yeah. I'll keep my eye out for that.

##### **Geohot** [[00:20:23](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1223)]
Um, I think, I mean, yeah, the big one was just the timeout thing showing up as a segfault. Yeah. I guess it's been pretty good lately.

##### **Chrism** [[00:20:31](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1231)]
Yeah. The other one was that stupid LLVM 18 bug, but we just moved off LLVM 18. I just swapped it to 20.

##### **Geohot** [[00:20:40](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1240)]
Oh, okay. Great. Then maybe the certificate.

##### **Qazalin** [[00:20:42](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1242)]
Yeah.

##### **Flata** [[00:20:46](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1246)]
Yeah. Okay.

##### **Geohot** [[00:20:50](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1250)]
Sounds good.

##### **Chenyu** [[00:20:51](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1251)]
Uh, next is the dtype stuff.

##### **Geohot** [[00:20:54](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1254)]
Yeah, it's finally done.

##### **Geohot** [[00:20:57](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1257)]
Um, yeah, yeah. Finally, `dtype.vec` is actually gone. Completely gone. Not in the codebase at all anymore. No more `dtype.vec`, no more `PtrDType`, and no more `ImageDType`. So dtype is now a boring, simple class that is actually just the dtype. Um, I also did all the stuff for removal of dtype from UOp itself. There are four blockers there right now. One of them is SLICE. One of them is NOOP. There's just one place where NOOP is abused and NOOP needs a dtype, so that one I will just refactor. Um, there is INS. x86 is the gift that keeps on giving and has more stupid crap, and that one I'll just fix. And then the trickiest one is CONST. Um, and I think, Chenyu, that's yours. But yeah, once those four, once SLICE is gone, CONST is fixed, and I'll do the refactors for the other two, we can move away entirely from even having dtype in the UOp constructor. Um, but yeah, `dtype.vec` is gone, `PtrDType` is gone, `ImageDType` is gone. I'm super happy about that. You know, it was very slow going at first. I had like two sprints where I thought I was going to do it, and I made the most grueling progress just because there were so many things to untangle. But then this sprint it kind of just all came apart, and yeah, it was just removed. So it's gone. We never have to think about that again. You know, it was my fault. I introduced two shape systems. There were basically two entire shape systems inside tinygrad. There was one that involved things like GEP and VECTORIZE, and then there was one that involved things like INDEX and STACK. So, you know, it was bad. It's gone. This sprint, I'm going to work on MULTI, PAD, and INVALID. I want to remove MULTI entirely and replace it with PAD. I'm excited about this for two reasons. One, it gets rid of a whole bunch of Ops. That'll get rid of MSTACK, MSELECT, and MULTI. So three Ops gone. And two, this will let us use the normal movement Ops for everything that used to do MULTI, in the same way that we now use the normal movement Ops for everything that used to do vectorization. If we use the normal movement Ops for everything that used to do MULTI, then MULTI can apply at every level. Currently MULTI only works across devices. But the big thing that I want is one of TileLang's greatest innovations, this thing called `alloc_fragment`. What `alloc_fragment` does is allocate registers across each warp, or each thread. It's really annoying when you're doing a WMMA. These WMMAs are warp-cooperative, so the WMMA can reach into the other threads, and you need things to be in certain places in the other threads. But normally, if you define a register or create a buffer with address space register, that will only appear on one thread. So it's kind of annoying how you do the WMMA. `alloc_fragment` creates a shaped fragment of registers across the entire warp, and that's effectively just MULTI. So we'll be able to reuse the new MULTI machinery for that. Then finally we can write kernels that are as beautiful as TileLang's, in a much more principled way. I read TileLang this weekend, and how they actually do `alloc_fragment` is a huge mess.

##### **Chrism** [[00:24:49](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1489)]
Yeah, contiguous movement Ops to VIEW also has a whole bunch of hacks for MULTI in it.

##### **Geohot** [[00:24:55](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1495)]
Yeah, yeah, yeah. There's a bunch of... MSTACK and MSELECT are also... These things should not exist. MSTACK should just be STACK, and MSELECT should just be SHRINK. You what?

##### **Geohot** [[00:25:12](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1512)]
MSELECT should be SHRINK.

##### **Qazalin** [[00:25:17](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1517)]
I see.

##### **Geohot** [[00:25:19](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1519)]
So the way that you represent a sharded Multi is when you create a buffer across devices, a buffer exists on all devices. Right? So if I create a buffer that has like four devices, that buffer just exists and it's full size on all devices. So if I'm creating like a 256 by 256 matrix that's sharded across four devices, the buffer that I create is 256 by 64. And then I pad that buffer by the device number. And just that pad alone gives me a 256 by 256 thing. I don't need to stack them. I don't need to do anything like that. It's just a 256 by 256 object.

##### **Geohot** [[00:25:57](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1557)]
A tensor that will be invalid on the devices that it doesn't exist on. The first thing I'll do is update the spec for this.

##### **Geohot** [[00:26:13](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1573)]
And then start implementing it. Oh, the other thing that I have to do quickly is, Chenyu, you deleted `Ops.WMMA`?

##### **Chenyu** [[00:26:21](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1581)]
Uh-huh.

##### **Geohot** [[00:26:23](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1583)]
That's used in AMD copy matmul. But yeah, my fault for not putting a test. I will put a test for `Ops.WMMA`. I'll put it back in, and what I'll do is have the WMMA path actually use the helper, because the helper is good.

##### **Chenyu** [[00:26:40](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1600)]
Yeah, I think that's more important. I deleted it because the signature was not matching the new WMMA.

##### **Geohot** [[00:26:49](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1609)]
It should be the new... Yeah, I can clean it all up a little bit. I'll do it. I'll just basically use that. But it was used in AMD copy matmul. What I'm really excited for is the new AMD copy matmul. That's going to use `alloc_fragment`, and then it's going to be as beautiful as TileLang. Great. Also, the GPTs are very good at using all our custom kernel stuff. They're very good at writing quick custom kernels to do stuff, which is great. How I finally see this working is, instead of BEAM search, it's going to be more like you write your thing, then you put it into GPT and just say, okay, write custom kernels where you need to, speed things up where you need to. It'll just work.

##### **Geohot** [[00:27:43](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1663)]
Yeah.

##### **Chenyu** [[00:27:45](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1665)]
Will that be the new codegen there?

##### **Geohot** [[00:27:48](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1668)]
No, I wouldn't go that far. Like, I do eventually want to. So if you see, I have a branch where HLB is. HLB CIFAR is running in 20 seconds wall time.

##### **Chenyu** [[00:28:02](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1682)]
By inserting CONTIGUOUS for every slow op?

##### **Geohot** [[00:28:06](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1686)]
Well, yes, it inserts those CONTIGUOUSes. Actually, it doesn't insert those CONTIGUOUSes because it makes the generated code faster. It inserts those CONTIGUOUSes so it doesn't do RANGEIFY. Yes, because RANGEIFY is slow. But we just need to make RANGEIFY fast. The RANGEIFY rewrite will happen after, I don't know. I think I'd rather prioritize MULTI than RANGEIFY. It's not long, it's just kind of crappy. Yeah, makes sense. But yeah, there's a much simpler RANGEIFY as well.

##### **Geohot** [[00:28:38](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1718)]
Yeah.

##### **Geohot** [[00:28:44](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1724)]
I mean, what we can really do with RANGEIFY is separate this idea of, I'm so happy it's not called BUFFERIZE anymore, it's called STAGE, because we can really separate this idea of saying, okay, where do we want our kernel breaks to be, from how do we compute the indexing? The indexing computation can be done locally. It doesn't even have to be done in the big graph. The reason we historically didn't do that is because it was annoying to deal with things like, what if you remove a kernel? Once you figure out a kernel is a NOOP and you want to remove it, it was kind of too late in the pass to go back and remove it. But now that's pretty easy. You can run all the local processing in the kernel, and if the local processing just says this is a trivial copy kernel, you're just like, all right, cool, remove it. I can do that right at the end.

##### **Geohot** [[00:29:46](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1786)]
If it's just a copy. Great. Yeah, MULTI this week. I'm excited about MULTI. MULTI success. Exciting.

##### **Chenyu** [[00:29:58](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1798)]
Yeah, multi. I think multi would be nice. Probably the fourth rewrite of multi.

##### **Geohot** [[00:30:06](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1806)]
The last rewrite of multi, yeah.

##### **Flata** [[00:30:10](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1810)]
Cool.

##### **Geohot** [[00:30:12](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1812)]
OK. Anything else?

##### **Flata** [[00:30:14](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1814)]
No.

##### **Chenyu** [[00:30:17](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1817)]
Next is my stuff. So CONST. We can talk about the things I have done first. So I did the STACK thing, because that looked fun. So now no more `_stack`, no more VECTORIZE. Everything is just STACK, and STACK works at every level.

##### **Flata** [[00:30:36](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1836)]
Great.

##### **Chenyu** [[00:30:39](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1839)]
So CONST is slightly annoying because we cannot really have implicit shape broadcasting and dtype broadcasting, because gradients need to be aware of that and do the reverse of it. And I think we also don't want a CAST to follow every weak dtype CONST, because then you will have CASTs everywhere, and your symbolic rewrite will match the CAST instead.

##### **Geohot** [[00:31:20](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1880)]
Yeah.

##### **Chenyu** [[00:31:21](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1881)]
I don't have a good solution there.

##### **Geohot** [[00:31:23](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1883)]
Wait, I don't understand why we can't have.

##### **Flata** [[00:31:26](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1886)]
Yeah.

##### **Geohot** [[00:31:26](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1886)]
My understanding always was that we'd have dtype broadcasting. Why do you think gradient means we can't have that?

##### **Chenyu** [[00:31:33](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1893)]
It cannot be fully implicit because you also need to cast it back in your backward.

##### **Geohot** [[00:31:44](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1904)]
But that's OK. What do you mean? I can just look and see if it's. Yeah, you have to handle it.

##### **Chenyu** [[00:31:50](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1910)]
So you want to say every time you see the dtype is different, insert a CAST? In the backward, at some point it needs to be aware that it needs to do a CAST there, right?

##### **Geohot** [[00:32:06](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1926)]
You can put the CASTs in the backward, sure. Yeah, if you need them.

##### **Chenyu** [[00:32:26](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1946)]
You can just inspect the dtype. But now, since dtype itself will be implicit, you cannot say check the dtype and, if it's different, insert a CAST.

##### **Geohot** [[00:32:37](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1957)]
Of course you can. But the UOp still has a dtype.

##### **Chenyu** [[00:32:45](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1965)]
Isn't that DTYPE coming from the cast?

##### **Geohot** [[00:32:50](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1970)]
Well, no.

##### **Chenyu** [[00:32:51](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1971)]
The cast creates the DTYPE.

##### **Geohot** [[00:32:53](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1973)]
So let's talk about the canonical example, which is like I have a tensor that's full of ints, right? And then I do plus 3. That 3 is a weak int. But you don't need a cast there. So it's just an add with a buffer and a constant. Now when I take the gradient of that, OK, I mean, what's the problem?

##### **Chenyu** [[00:33:18](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=1998)]
So int cannot have gradient.

##### **Geohot** [[00:33:21](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2001)]
Oh, whatever. It's float. It's fine. Make it float.

##### **Chenyu** [[00:33:24](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2004)]
OK. So say you have a float16 tensor, and in your forward you cast it to float32.

##### **Geohot** [[00:33:35](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2015)]
You mean I add it to something that's float32 and it's implicitly cast, or I explicitly cast it? Yes. Yes.

##### **Chenyu** [[00:33:40](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2020)]
You implicitly cast it, assuming we have an implicit concept. Sure. OK. Now when you do the backward, you need to cast it back to 16.

##### **Geohot** [[00:33:52](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2032)]
Yeah. Of course. But that's what it already is. That's what it already has to do. And that's no different from how it is now.

##### **Chenyu** [[00:33:59](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2039)]
So now this is done through an explicit cast in the forward. And that explicit cast has an explicit cast back in the backward.

##### **Geohot** [[00:34:11](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2051)]
Yeah, you'll have to insert a cast back in the backward. Just like we handled broadcasting in the backwards, you'll have to handle a. Don't we already handle this for broadcasting? Isn't it just the same thing?

##### **Chenyu** [[00:34:23](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2063)]
Yeah. When the broadcasting is explicit, then you explicitly do the backward of every kind of that. So same for EXPAND, same for CAST. And now if we want to make any of these implicit, we need a way of knowing that we need to do a CAST, or need to do a SUM over here.

##### **Geohot** [[00:34:47](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2087)]
Yeah, but whatever. I don't think this is hard. You just need to check the inputs. You can check the input dtype, right? So in that case, I have two tensors. One is float32 and one is float16. Then I have an ADD, and I don't have any CAST. That ADD outputs a float32, right? So in order to tell in the gradient if I need to add a CAST, I just check the sources of ADD and see what their dtypes are. If the source dtype doesn't match, you have to cast it back for that gradient.

##### **Chenyu** [[00:35:14](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2114)]
Yeah. So that's the solution. Yes.

##### **Geohot** [[00:35:17](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2117)]
Yeah. But this doesn't mean we can't have implicit cast. I think that works fine.

##### **Chenyu** [[00:35:22](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2122)]
Uh.

##### **Geohot** [[00:35:25](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2125)]
No, no, no. But the really important thing is that I don't want symbolic to match a CAST. I don't think CONST should almost ever need CASTs. I mean, they don't have gradients. We can also have a pass, like I have a pass in the devectorizer that makes broadcasts explicit, and we'll need that pass for RANGEIFY too. You could also imagine the opposite pass, which removes all CASTs that you don't need, all CASTs that can be implicit. So I could imagine symbolic kind of just having that in there.

##### **Chenyu** [[00:35:22](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2122)]
Yes. That's probably how I will be doing that.

##### **Geohot** [[00:36:10](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2170)]
Yeah.

##### **Geohot** [[00:36:12](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2172)]
Like remove all implicit casts, right?

##### **Chenyu** [[00:36:17](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2177)]
Yeah. I mean, I get how this can be done. And I understand we don't want `_cast` for CONST everywhere.

##### **Flata** [[00:36:27](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2187)]
Yeah.

##### **Chenyu** [[00:36:28](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2188)]
It's just slightly annoying. So I'm figuring out.

##### **Geohot** [[00:36:31](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2191)]
Yeah, yeah, yeah. But no, I mean, do you think this is a fundamental reason that we can't do this or shouldn't do this? Or?

##### **Chenyu** [[00:36:38](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2198)]
No, I don't think there is a fundamental reason this is wrong. It just needs to be done properly.

##### **Geohot** [[00:36:47](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2207)]
Oh, yeah.

##### **Chenyu** [[00:36:48](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2208)]
No, I don't think this is easy. Yeah, that's part of the reason why I split INDEX. We can discuss and add it back later, but I really don't want to mix these two when we design a proper weak dtype. INDEX is very self-contained and narrow now. We don't really have a case where INDEX touches any index dtype.

##### **Geohot** [[00:37:10](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2230)]
Yeah, yeah. Splitting INDEX is fine for this. This is really a different thing. I understand what you mean about index dtype being the top of the promotion lattice and weakint being the bottom.

##### **Chenyu** [[00:37:23](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2243)]
INDEX now is not even in the promotion lattice because it never touches the index dtype.

##### **Geohot** [[00:37:30](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2250)]
Right. Anyway, I want to unify it later, but I think it's more important to get this. This is the blocker on dtype removal, and I think it's just so much more beautiful to have CONSTs have implicit dtype of weakint or weakfloat. That makes sense.

##### **Chenyu** [[00:37:52](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2272)]
There are probably some other corner case, but it's fine.

##### **Geohot** [[00:37:56](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2276)]
It's so beautiful. If I have a float tensor and then I do plus three, that three doesn't even have to become a float. That three can just stay a weakint.

##### **Flata** [[00:38:06](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2286)]
Yeah.

##### **Wozeparrot** [[00:38:07](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2287)]
Beautiful.

##### **Chenyu** [[00:38:10](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2290)]
Yes. Well, another slightly annoying thing is, when you do MULTI, you probably need to find a way to deal with STACK, because STACK is the only movement op that can have multiple sources or zero sources.

##### **Geohot** [[00:38:31](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2311)]
Yeah. What about that?

##### **Chenyu** [[00:38:33](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2313)]
It's just annoying that every time you write something, you need to add a case for it.

##### **Geohot** [[00:38:41](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2321)]
Yeah. Yeah. I mean, it does look different from the other movement ops like that. But like you fundamentally need. I thought about this a lot. I thought about the movement ops back like a lot. I mean, you fundamentally need some combiner movement op.

##### **Flata** [[00:38:56](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2336)]
Yeah.

##### **Chenyu** [[00:38:58](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2338)]
Another thing quickly.

##### **Chenyu** [[00:39:00](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2340)]
So WHERE is still in INDEX, and it's kind of because we use it wrong when we do INDEX INVALID.

##### **Geohot** [[00:39:13](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2353)]
WHERE is still in INDEX because we use it wrong.

##### **Chenyu** [[00:39:16](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2356)]
Yeah. So we have a method called `get_valid` or `get_idx`, something like that.

##### **Geohot** [[00:39:25](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2365)]
I hate those methods. Yeah.

##### **Chenyu** [[00:39:27](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2367)]
Yeah. And those assume no broadcasting.

##### **Flata** [[00:39:32](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2372)]
Yeah.

##### **Geohot** [[00:39:33](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2373)]
They are. Yeah.

##### **Chenyu** [[00:39:37](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2377)]
There's that. I made some cleanup. It's more obvious why it's wrong, but it's still wrong.

##### **Geohot** [[00:39:47](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2387)]
Yeah. I don't know. I mean, I don't like those methods really at all. Yeah. So also.

##### **Geohot** [[00:39:56](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2396)]
Yeah.

##### **Chenyu** [[00:40:01](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2401)]
That's pretty much my thing. Yeah.

##### **Flata** [[00:40:03](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2403)]
Yeah.

##### **Chenyu** [[00:40:03](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2403)]
So I think we can move on to the next one. We can move on to HCQ2.

##### **Nimlgen** [[00:40:12](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2412)]
Yeah. So.

##### **Nimlgen** [[00:40:16](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2416)]
We now have cache linking, so basically it's a bit faster, but still not as fast as HCQ1. The main optimization that is missing is, in HCQ Graph we used to use indirect buffers, and that's not implemented in HCQ2 yet. Also, our CPU runtime has huge latency because of the threading. So I just started to rewrite the workers in UOps. It works. It's a bit annoying because in HCQ2 we need to do external calls to C functions. That works, but currently it's implemented as a CUSTOM UOp. So I don't know if we should do some proper UOp for this, because the annoying thing is that LLVM cannot render this.

##### **Geohot** [[00:41:39](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2499)]
To do what? I'm getting an error on HCQ2 now, by the way. So CUSTOM for what? Like a C call? Yeah. I mean, also, I'm not sure, we can disable threading for that. It makes it a lot easier. I don't know, the second link is better.

##### **Nimlgen** [[00:42:33](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2553)]
So, yeah, I mean, it's rendered as CUSTOM now, like calling C functions.

##### **Geohot** [[00:42:45](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2565)]
I see. Okay. Yeah. No, I like this basic idea. So you're building kind of like firmware for the CPU.

##### **Nimlgen** [[00:42:54](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2574)]
Yeah. So, yeah.

##### **Geohot** [[00:42:56](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2576)]
You're building firmware for the CPU. And then, yeah, okay, so the language is UOp. Then it executes a UOp graph. Yeah.

##### **Geohot** [[00:43:07](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2587)]
I like this basically.

##### **Nimlgen** [[00:43:12](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2592)]
Yeah. So, I mean, it works. It's just a lot faster than what they have. The main problem is that I can render these only with the Clang renderer and not LLVM. That's kind of the main blocker for this part.

##### **Geohot** [[00:43:28](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2608)]
Why can't you render this with LLVM?

##### **Nimlgen** [[00:43:33](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2613)]
Because of this CUSTOM thing, which is like...

##### **Geohot** [[00:43:39](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2619)]
Oh, this `make_c_call` thing.

##### **Nimlgen** [[00:43:41](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2621)]
Yeah. Yeah. Yeah.

##### **Geohot** [[00:43:46](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2626)]
I mean.

##### **Geohot** [[00:43:49](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2629)]
Yeah. Okay. I see what that's doing. You want to make that a UOp. That's fine. Or could you just use CALL?

##### **Geohot** [[00:44:05](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2645)]
Yeah. Yeah. Yeah.

##### **Nimlgen** [[00:44:07](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2647)]
I can use CALL.

##### **Geohot** [[00:44:08](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2648)]
I think CALL is right. You could basically just make CALL actually renderable.

##### **Geohot** [[00:44:17](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2657)]
Yeah.

##### **Geohot** [[00:44:19](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2659)]
I don't know what `dtype` is, but address is the function body or name, or an actual function body. `args` is the arguments.

##### **Geohot** [[00:44:30](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2670)]
Yeah, yeah, yeah. Why is that?

##### **Nimlgen** [[00:44:36](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2676)]
It will be. Yeah, cool. Yeah. Yeah. Cool.

##### **Geohot** [[00:44:43](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2683)]
I'm totally fine with you adding CALL to the renderer, basically.

##### **Qazalin** [[00:44:50](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2690)]
Yeah.

##### **Geohot** [[00:44:51](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2691)]
You know what? You know what the crash is? Okay.

##### **Flata** [[00:44:54](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2694)]
Yeah. Yeah. Yeah. Yeah.

##### **Nimlgen** [[00:44:57](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2697)]
I'll check that. I mean, I've been renaming a lot of stuff today, so it's HCQ2 CI.

##### **Chrism** [[00:45:04](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2704)]
Got it.

##### **Nimlgen** [[00:45:04](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2704)]
Yeah, I like it being the CI.

##### **Chrism** [[00:45:07](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2707)]
Yeah. Because that offset looks like it might be related to.

##### **Geohot** [[00:45:12](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2712)]
I just, I made.

##### **Flata** [[00:45:18](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2718)]
So, yeah.

##### **Geohot** [[00:45:24](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2724)]
So, yeah. So, yeah. So, I'm just gonna show you a little bit of a little bit of a bunch of stuff.

##### **Nimlgen** [[00:45:26](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2726)]
Actually, HCQ2 is kind of ready. For backends, the main blocker is that we need to rewrite a lot of stuff, because we need to use Buffer instead of HCQBuffer inside them. A lot of parts inside backends touch these buffer things. So I think I can start with NV. The main blocker for AMD is that it's a lot of code to keep two copies of the backends. And I cannot rewrite USB because, in CI, we still have the old firmware, and I just don't want to mess with it at all. Oh, we can fix that.

##### **Geohot** [[00:46:19](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2779)]
If there's still any old firmware in CI, we should fix that today.

##### **Nimlgen** [[00:46:26](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2786)]
Yeah. So if that's fixed, I'll remove the old USB and it will be easier.

##### **Geohot** [[00:46:32](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2792)]
I'll get people on fixing that. I'll get people on fixing that today. I didn't realize that was still like that. Do you want me to do a review of the new stuff before we start migrating everything?

##### **Nimlgen** [[00:46:53](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2813)]
Yeah, sure. But okay, let me do the final rewrite and cleanup stage.

##### **Geohot** [[00:46:59](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2819)]
Yeah, what I would do, how about this?

##### **Geohot** [[00:47:02](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2822)]
Get AMD switched over. And then before just doing the bulk of it, let's get AMD merged, and then let's iterate on AMD a bit. And get AMD to be exactly what we want before we migrate everything.

##### **Nimlgen** [[00:47:20](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2840)]
Yeah. I mean, it's kind of. I don't know. If AMD. Like, is the best back end. But because, I mean, we do training on AMD. Kind of scary to have some speed losses in the beginning.

##### **Nimlgen** [[00:47:36](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2856)]
I can do NV.

##### **Geohot** [[00:47:38](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2858)]
Wait, so when you say speed losses, you mean one-time speed losses?

##### **Nimlgen** [[00:47:47](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2867)]
Yeah.

##### **Qazalin** [[00:47:48](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2868)]
That's fine.

##### **Geohot** [[00:47:53](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2873)]
Not like. Not like. Speed loss is like per step.

##### **Nimlgen** [[00:48:01](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2881)]
That actually depends on the trainer itself, because some of them have unjitted things, and I'm still optimizing Python, scheduling, and linking to be fast, like the CPU runtime.

##### **Geohot** [[00:48:16](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2896)]
I think if a trainer has unjitted things, that's on them. OK. Yeah. Let's push. Let's get AMD switched over. If it slows down some people, it's the new stuff.

##### **Chenyu** [[00:48:32](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2912)]
I think it's much better to start with AMD because people are really using it. So you get more feedback and complaints early. I don't know if people use NV for anything real now, at least for this company. So I think don't be afraid to break other people's stuff. In the worst case, we just reverse it.

##### **Geohot** [[00:48:57](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2937)]
We are 100% committed as a company to HCQ2. So yeah, if it breaks for other people...

##### **Chenyu** [[00:49:06](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2946)]
Just apply what you think is the most correct and principled way to do this. Don't worry too much.

##### **Geohot** [[00:49:16](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2956)]
I mean, I'm reading it now.

##### **Geohot** [[00:49:19](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2959)]
It's a lot more readable than the old stuff.

##### **Geohot** [[00:49:27](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2967)]
We have AQL in here?

##### **Nimlgen** [[00:49:31](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2971)]
No, but that's on the backend.

##### **Flata** [[00:49:35](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2975)]
Yeah.

##### **Geohot** [[00:49:38](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2978)]
Wait, but what do you mean? We need AQL, right?

##### **Nimlgen** [[00:49:41](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2981)]
Yeah, I'll add it. I mean, it's not that big of a deal.

##### **Nimlgen** [[00:49:46](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2986)]
But.

##### **Nimlgen** [[00:49:52](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2992)]
I just wanted `hcq2.py` to have good abstractions and good passes. I mean, kind of...

##### **Geohot** [[00:49:59](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=2999)]
Let's do it with AMD. Everyone's got to deal with it. I made everyone deal with RANGEIFY, so...

##### **Geohot** [[00:50:13](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3013)]
What is HCQ2 buffer? So that's

##### **Nimlgen** [[00:50:27](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3027)]
Yeah, I think I should merge this with buffer. Yeah. And it's... Yeah, I've merged a lot of... Yeah, I think... Yeah, we shouldn't

##### **Geohot** [[00:50:41](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3041)]
have a class that looks like... Every class that has the word HCQ before it should basically just be the main class.

##### **Geohot** [[00:50:53](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3053)]
Yeah. Like, I think HCQAllocator should just be Allocator...

##### **Chenyu** [[00:51:08](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3068)]
Okay, let's move on.

##### **Geohot** [[00:51:10](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3070)]
Well, I think there's a little bit more here. I think... I mean, yeah. HCQ2 buffer definitely has to go. Like, look at this. Why does copy take buffers, but copy... copy in and copy out take HCQ2

##### **Geohot** [[00:51:25](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3085)]
buffers?

##### **Qazalin** [[00:51:31](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3091)]
Yeah.

##### **Nimlgen** [[00:51:35](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3095)]
Yeah, I'll remove that. I mean, I've... Actually, buffers support HCQ2 buffer needs. Like, mapping and all this. Yeah, I can... Yeah, I'll remove that.

##### **Geohot** [[00:51:48](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3108)]
Yeah, I mean, HCQ link looks good. Uh... I think we should also... This seems like more graph rewrites

##### **Geohot** [[00:52:00](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3120)]
than you need. Yeah. Like, how come these are all different graph rewrites

##### **Geohot** [[00:52:30](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3150)]
and not, like, kind of a couple of graph rewrites that have a bunch of rewrite rules?

##### **Nimlgen** [[00:52:41](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3161)]
Um... I didn't think about that, but...

##### **Nimlgen** [[00:52:56](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3176)]
I'm not really sure what I can merge here, but we'll take the bottom three.

##### **Geohot** [[00:53:06](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3186)]
Like the bottom three: `replace_rt_get_addrs`, `replace_rt_binaries`, `replace_args`, right? Why isn't that one replace?

##### **Geohot** [[00:53:20](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3200)]
Um,

##### **Flata** [[00:53:21](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3201)]
of course,

##### **Geohot** [[00:53:29](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3209)]
Yeah, uh... Okay, yeah, I think I can... Yeah, okay, got it.

##### **Geohot** [[00:53:37](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3217)]
Yeah, in general, like... So, okay, there are two schools of thought on this, right? There's the nanopass school, which is like, nanopass is a toy compiler, which is just: do the smallest amount of things in each pass. And in general I agree with that, but whenever I see stuff that looks like this, generally what it's masking is that the spec isn't... You described this well about the SLICE thing. It's when we use UOps to mean semantically more than the spec. So now the new stuff in codegen is very good at accepting any order. You can arbitrarily switch the order, combine pattern matchers, because if everything perfectly matches the spec, you should basically be able to do that. It's a question of how fragile things are. So I'm curious what would happen right now if I just concatenated all those pattern matchers together and saw what it does.

##### **Geohot** [[00:54:45](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3285)]
So, like, removing one is easy, but replacing parameters...

##### **Nimlgen** [[00:54:48](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3288)]
it's easy, but replace parameters... It's hard. That's harder. I mean, actually, what they do is that they just... I don't know if I should take time to describe that. But, yeah, okay, I got it.

##### **Geohot** [[00:55:03](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3303)]
Yeah, just a general idea. But, yeah, main takeaways here are: let's get AMD merged. Do the best you can, but if you slow other people down, don't worry too much about it. This whole company is committed to HCQ2, and everyone here has to deal with HCQ2. It's the future. It's clearly how things have to go. And then, yeah, deletion of every single one of these classes. So what I'm going to do is nitpick each one: do we really need this class, or can this just be the main class? No HCQ2Buffer, no HCQAllocator, just Buffer, Allocator. None of this class hierarchy stuff. There is one. It's all over tinygrad.

##### **Geohot** [[00:55:50](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3350)]
Yeah. Yeah, no, good work. Coming along nicely. It's a big refactor. Great. Okay. Comma happy?

##### **Chenyu** [[00:56:09](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3369)]
Is the GLM good?

##### **Geohot** [[00:56:13](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3373)]
I mean, probably. I'm happy with HCQ2.

##### **Chrism** [[00:56:17](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3377)]
They're really looking forward to that one. They're talking about switching to IR3,

##### **Chrism** [[00:56:32](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3392)]
which will be kind of neat. Although I saw it slowed down.

##### **Chrism** [[00:56:37](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3397)]
Yeah, I think it's one millisecond slower for some reason. I don't know, I can look into that. It depends on how interested they are in doing this, because I mentioned this last week and they were excited about doing it, and this was when it was not slower, and they didn't switch. So I don't know. But if they do switch, then I will make sure we switch all of our benchmarks to benchmark the thing that they're actually using.

##### **Chenyu** [[00:57:06](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3426)]
Do you want to share something about your FLUX run?

##### **Flata** [[00:57:13](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3433)]
Not a whole lot yet. I think the config from the reference implementation is configured with multiple GPUs for their system. So I think I'll have to readjust it, because the run was pretty much stable, but it just kind of maxed out on the max number of steps, which was 30k. I think the evaluation just didn't reach it yet, so I'll need to tweak that a little bit more.

##### **Geohot** [[00:57:39](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3459)]
Sounds good.

##### **Chenyu** [[00:57:45](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3465)]
We also have Reina. Do you want to talk about anything for your backend, the RDNA backend?

##### **Geohot** [[00:57:52](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3472)]
Reina, yeah, I added you as a speaker.

##### **Geohot** [[00:57:54](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3474)]
You have to exit the meeting and re-enter, and then you can talk. Can you hear me? Yes. OK, perfect.

##### **Geohot** [[00:58:23](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3503)]
Yeah, yeah, so just anything about the RDNA3 backend?

##### **Reina** [[00:58:28](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3508)]
Yeah, so most of the tests are passing now. If you see the latest CI run in the PR, I think I'm down to like 19 tests out of the backend run. Most of those are just spilling, which I'm working on right now, adding spill and fill to my regalloc.

##### **Flata** [[00:58:46](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3526)]
Cool.

##### **Reina** [[00:58:47](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3527)]
Yeah. One of the weird things is my integer division expansion algorithm seems to be super slow on the transcendental run. So tests SIN and COS are like 30 seconds, which is kind of annoying. That's something I need to look into too. And then there are two or three tests, I think a BITCAST shape change and a transformer test, that are also failing on the CI run. But I'm hoping in like a week, maybe this weekend, I should be able to have 100% of tests passing, and then I'll start working on speed.

##### **Flata** [[00:59:24](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3564)]
Yeah.

##### **Geohot** [[00:59:24](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3564)]
I mean, a few of these things. If you need a dtype decomposition for that division, you shouldn't have to handle that in your backend. We should have a generic one.

##### **Reina** [[00:59:33](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3573)]
Yeah, that's what I was thinking. Make it higher level, like in codegen or something.

##### **Geohot** [[00:59:38](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3578)]
We should already have that. This is what dtype decomp is.

##### **Reina** [[00:59:41](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3581)]
Well, it's not like IDIV needs integer division. I don't think there's a way to expand that at a high level. Even fast IDIV and stuff expands into `cdiv`, no?

##### **Chrism** [[00:59:56](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3596)]
Okay. So I don't know exactly what you're talking about here, but in theory there's already an implementation that does, for instance, long division. It gets lowered to int32s.

##### **Geohot** [[01:00:09](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3609)]
Yeah. I mean, GPUs don't actually have integer division. All this stuff should be dealt with at a higher level. You shouldn't have to deal with this in your backend.

##### **Reina** [[01:00:18](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3618)]
Okay. Because I thought LLVM does its own lowering for that, because I don't have `Ops.IDIV` in my code for op.

##### **Geohot** [[01:00:24](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3624)]
Yeah. You shouldn't have to.

##### **Geohot** [[01:00:27](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3627)]
Don't worry about that.

##### **Geohot** [[01:00:28](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3628)]
You do have to worry about spilling, though. You do need spilling to work.

##### **Reina** [[01:00:31](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3631)]
Yeah. No, I was planning on implementing that.

##### **Geohot** [[01:00:34](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3634)]
Yeah. If you get it down to just integer division stuff not working, then you can just skip those tests for your backend, and that's totally fine.

##### **Reina** [[01:00:45](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3645)]
Okay. Yeah. Hopefully I'll have spill/fill this weekend, and then I'll go and fix x86 because it's broken right now on my branch.

##### **Geohot** [[01:00:55](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3655)]
Right. Yeah. Enjoy your camping trip. Once you get these tests passing, I will get you access to it. Actually, just send me a public key and I'll get you access to a TinyBox. You can test this on real hardware.

##### **Reina** [[01:01:07](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3667)]
Perfect. Okay. Yeah, I've been using MockGPU, which has been great, though, because I don't even have an AMD GPU.

##### **Geohot** [[01:01:12](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3672)]
Oh, it's much better to test things with MockGPU anyway. I mean, the real GPU crashes and it's not that introspective. But yeah, send me, I'll get you that.

##### **Reina** [[01:01:22](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3682)]
It's also possible there are some bugs in my video.

##### **Reina** [[01:01:26](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3686)]
Yeah, I don't have a wait/sync pass yet. So I know it's going to fail right away, probably just because of the data dependencies. But I'm going to fix that too. I've been looking at LLVM to add that.

##### **Geohot** [[01:01:40](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3700)]
Oh, you mean a barrier?

##### **Reina** [[01:01:42](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3702)]
No, because when you do memory operations, it's asynchronous. So if you don't wait...

##### **Geohot** [[01:01:47](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3707)]
Oh, yeah. After you use the operands, yeah, it's going to fail.

##### **Geohot** [[01:01:51](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3711)]
No, those are required. Yep. Cool.

##### **Geohot** [[01:01:53](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3713)]
Yeah. Okay.

##### **Geohot** [[01:02:01](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3721)]
Oh, I think that's pretty much it. Anything else for this meeting?

##### **Flata** [[01:02:05](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3725)]
Nope. Cool.

##### **Chenyu** [[01:02:09](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3729)]
Oh, I will be in San Diego next week.

##### **Geohot** [[01:02:12](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3732)]
All right.

##### **Chenyu** [[01:02:13](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3733)]
Okay, see you soon. Bye-bye.

##### **Geohot** [[01:02:14](https://www.youtube.com/watch?v=dfMxyGxd_WE&t=3734)]
Bye.
