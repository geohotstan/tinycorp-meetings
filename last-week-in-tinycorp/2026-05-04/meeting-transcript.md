# 2026-05-04 Meeting

### Meeting Agenda

**Time:** new meeting #18, 5/4 9am Monday San Diego time
- company update
- MLPerf LLaMA
- new DEV
- vecless
- tensor UOp mixin, divmod
- runner refactor
- viz
- bounties, issues, Comma happiness


### Audio

[Youtube Link](https://www.youtube.com/watch?v=zYkkGZtEw_A)

### Highlights

- **[Company Update](#geohot-000016)**: Tinygrad should focus less on converting PyTorch users for now and more on two audiences: people who want LLMs running fast on eGPUs, and kernel/performance hackers working on off-the-beaten-path hardware.
- **[Hardware Update](#geohot-000300)**: Around 20 Chestnuts have been built, and the team thinks they work after cable swaps, though more validation is implied.
- **[TileLang / DeepSeek Direction](#geohot-000332)**: DeepSeek V4 reportedly wrote its kernels in TileLang; the team wants to study TileLang’s primitives and performance path, especially because tinygrad may be able to compete through a smaller IR and search-based optimization.
- **[AMD LLaMA Performance Target](#geohot-000409)**: The LLaMA speedup effort remains centered on building a high-performance AMD LLaMA trainer that can outperform the HIP-stack implementation.
- **[MLPerf LLaMA Submission](#wozeparrot-001340)**: The best LLaMA run is still about 2:54, the MLPerf logging checker passes, and the team plans to validate with 10 back-to-back runs before submission.
- **[405B Follow-up](#geohot-001948)**: After submitting the current MLPerf result, the team wants to test whether 405B can run at least a few steps to estimate timing, though the second AMD machine issue may block this.
- **[DEV / Offline USB GPU](#chrism-002029)**: Work is underway to make USB GPU support not depend on the internet; AMD register autogen files were reduced to roughly 1.4 MB, which the team accepts for the next tinygrad release.
- **[Firmware Fetch Policy](#chrism-002316)**: The team discussed using `/lib/firmware` for NVIDIA firmware when available, pinning firmware by hash, validating downloads, and making internet fetches explicit.
- **[Vecless / UOp Refactor](#geohot-002640)**: Removing `dtype.vec` is turning into a broader cleanup: make shapes correct first, move gates off indexes, reconsider load/store semantics, remove the expander, and tighten the schedule / early CodeGen / late CodeGen pipeline.
- **[Divmod Semantics](#chenyu-003320)**: Chenyu proposed making divmod semantics consistently use Python-style floor division, since most kernel divmod use is indexing math and floor semantics simplify symbolic transformations better.
- **[Runner Refactor / HCQ Graph](#geohot-004009)**: Runners are now gone; Nimlgen is cleaning up `realize.py` and exploring HCQ graph execution through generated C plus a Python backend path for USB/MMIO-style interfaces.
- **[Viz / LLaMA Debuggability](#qazalin-004808)**: Viz work can now replay LLaMA kernels on the null device via pickles; rather than chasing every custom-kernel contiguous copy, the team wants better tools to explain why kernels are generated and help agents improve them.
- **[45B Profiling and Custom Kernels](#geohot-005140)**: The team wants to reduce the 45B profiling/startup loop, identify low-MFU custom kernels, and eventually replace more HIP or assembly custom kernels with tinygrad-language kernels.
- **[Comma / QCOM Regression](#chrism-005725)**: Comma is blocked on a tinygrad bump because `run_linear` and enqueue-copy timing regressed; the likely fix is to avoid Python overhead for JIT copies, possibly via compiled graph execution or a software-SDMA-style path.

### Transcript
##### **Geohot** [[00:00:00](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=0)]
Start the meeting with company updates. So I've been... We've got to think about where

##### **Geohot** [[00:00:16](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=16)]
this stuff's going to start to get adoption. We have to think about what the boundary between users and developers is. So the key to making projects I think successful is to be able to build something that normal people can understand the value of, but only a sort of self-selected chosen group can understand what it is and why it's valuable. I've been talking a lot about philosophy with GPT 5.5. So... We have to think about what type of audience we want to target. And there's the EGPU audience, and that's one audience. And there's the same audience, the TileLang targets.

##### **Geohot** [[00:01:17](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=77)]
Then there's the PyTorch audience.

##### **Geohot** [[00:01:26](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=86)]
And, yeah. We've just got to think about kind of who our audience is. And I think our audience, I think we try with the EGPU people and LLM, and we try with like the TileLang kind of people. And I think it's less going to be the PyTorch kind of people, at least for now.

##### **Geohot** [[00:01:45](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=105)]
Because we haven't really succeeded at getting conversion from that. So, yeah, I mean, we've got to think about how to...

##### **Geohot** [[00:01:57](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=117)]
We win because... If we win, it's because our IR is like tiny. It's not because... From a user... It's just way too ambitious to try to target the kind of PyTorch people. And I think this was a mistake. But I think the right people to target are the people who are writing either this... I just want the LLM to run type people, or the... Okay, I want to write a kernel and explore high performance on my slightly off the beaten path hardware type people. And I think that's how we target both the kind of like the pipeline to developers and then this sort of user hype people who are like, wait, you actually won't believe the tokens per second I'm getting on my EGPU.

##### **Chenyu** [[00:02:57](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=177)]
Blah, blah, blah, blah, blah.

##### **Geohot** [[00:03:00](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=180)]
Yeah, I think that's kind of where where things have been going. And then yeah, the more boring company update thing we got, we got a bunch of Chestnuts. Like 20 built. I think they work.

##### **Geohot** [[00:03:14](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=194)]
Yeah, yeah. I was gonna say I work. Well, hopefully swapping some cables around fixed it.

##### **Qazalin** [[00:03:21](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=201)]
Okay. Yeah. Who's using TileLang?

##### **Geohot** [[00:03:32](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=212)]
Who's what? Who used... Oh, DeepSeek. DeepSeek V4 wrote all their kernels in TileLang. And like, in many ways, we're better TileLang. We just didn't integrate with the high-speed NVIDIA stuff.

##### **Nimlgen** [[00:04:03](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=243)]
Okay.

##### **Geohot** [[00:04:06](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=246)]
Our goal is to integrate...

##### **Geohot** [[00:04:09](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=249)]
No, I don't care about NVIDIA. Let's do it for AMD, right? Yeah, but our goal is basically to be able to... It's the same project, right? Not much has actually changed. The LLaMA speedup project is basically the same project, right? We want to write a really high-performance LLaMA trainer that outperforms the HIP stack one.

##### **Qazalin** [[00:04:32](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=272)]
Yeah, but if the issue is

##### **Chenyu** [[00:04:35](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=275)]
not using the whatever, the fast stuff, are we using the fast AMD hardware features? We should be able to,

##### **Geohot** [[00:04:45](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=285)]
yeah. I mean, we are right now. We're using custom kernels. The custom kernels are pretty bad. The custom kernels, and these are the same ones AMD use. They're only getting like 50%

##### **Geohot** [[00:04:58](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=298)]
MFU on GEMMs. Yeah, I mean, there's no reason

##### **Geohot** [[00:05:07](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=307)]
we don't support that, right? Like, it's the same way we write this, like, the WMMA kernel, but how do we get the WMMA kernel to work on MI350X and how do we get it to be faster than the AMD one?

##### **Geohot** [[00:05:18](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=318)]
I see. Okay.

##### **Geohot** [[00:05:21](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=321)]
Yeah, I mean, I think the way to do it is search. I think that the thing that we can get that TileLang doesn't get is search. TileLang's IR is kind of... I mean, it's... they layered it over TVM. I think they also now have a cute DSL backend. But you inherit all the problems when you layer on top of those things, which are you're left with this extremely complicated hand-tuned code gen pipeline that happens to work for really one piece of hardware. And I don't know if it's like... I didn't experience the fragility of it, but I didn't stress it that hard. With Triton, I would run into all these places where it was just extremely fragile. Like, if you do stuff slightly different, you'd lose 10x performance and you'd have no idea really how to debug it. But with TileLang, I didn't find that. With TileLang, I found that it was a lot more robust. So... But then when you look at the TileLang syntax, it's interesting. Like, TileLang's an example... It's not a programming language. Triton tries to be a programming language in the sense of, like, you can express arbitrary things in it. But when you look at the TileLang example, like, on the front page, you can look at that t.copy. Right? And this is... this is is nonsensical Python. Because

##### **Geohot** [[00:07:00](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=420)]
block M is just defined as an integer. It's not like those things are ranges.

##### **Chenyu** [[00:07:11](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=431)]
Where should I be looking at?

##### **Geohot** [[00:07:13](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=433)]
Well, the thing I just... The thing I just did, tcopy I just posted? What does that really

##### **Geohot** [[00:07:23](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=443)]
mean? tcopy...

##### **Nimlgen** [[00:07:32](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=452)]
Oh...

##### **Geohot** [[00:07:33](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=453)]
Maybe by is a range. Maybe by is a range. Okay.

##### **Geohot** [[00:07:39](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=459)]
A little confusing. It's not like selecting a...

##### **Chrism** [[00:07:44](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=464)]
What's a range? Okay, that makes sense.

##### **Geohot** [[00:07:46](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=466)]
But it's not like selecting a... You'd expect the copy to be like a slice. Right? That's taking like a slice out of the global memory. And putting it into the shared buffer. And you'd expect it to be a slice.

##### **Geohot** [[00:08:04](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=484)]
Okay.

##### **Chenyu** [[00:08:04](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=484)]
I don't know if this is good enough. This looks like it copies the first slice into the shared memory.

##### **Geohot** [[00:08:10](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=490)]
Yeah, it actually looks like `by` is a range. Okay, that's actually more sensible than I thought. But yeah, we should look into TileLang and make sure we can basically express all these same primitives that they can. Which we can. GPT says we can, but we just gotta actually do it and

##### **Geohot** [[00:08:30](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=510)]
figure out how they're getting performance when we aren't.

##### **Qazalin** [[00:08:36](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=516)]
Interesting. Do you know why they picked TileLang?

##### **Chenyu** [[00:08:39](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=519)]
I think they previously write their kernels. Is it just the new hardware is very hard to use? Or I don't even know what hardware they have access to.

##### **Qazalin** [[00:08:51](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=531)]
Um... Okay.

##### **Geohot** [[00:08:56](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=536)]
Let's see if they say why. Yeah, so this is the library that we should... Let's see. And they have a note there.

##### **Geohot** [[00:09:21](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=561)]
However, they don't represent best practices, and we are actively working on improving the code quality and documentation.

##### **Geohot** [[00:09:29](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=569)]
Makes sense. But, uh, yeah, it's

##### **Qazalin** [[00:09:35](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=575)]
it's it's interesting.

##### **Geohot** [[00:09:43](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=583)]
Yeah, that they moved off of.

##### **Chenyu** [[00:09:45](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=585)]
Because this looks very specialized.

##### **Geohot** [[00:09:49](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=589)]
What do you mean?

##### **Chenyu** [[00:09:51](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=591)]
They said in their tile kernels, uh, the kernels here approaches the limit of hardware performance. So I would imagine that's less robust if you want to copy this to other machine.

##### **Geohot** [[00:10:06](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=606)]
Oh, I'm sure it only works for the one GPU. Yeah, yeah. But I don't know. I mean, I've read that like the code looks nice.

##### **Geohot** [[00:10:15](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=615)]
Code looks quite like readable.

##### **Geohot** [[00:10:18](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=618)]
Uh, they're also doing these things called fragments. This is, this is another cool feature of TileLang that I haven't really seen before. So Triton doesn't let you talk about the registers. Triton just operates at the local scale and then has the compiler do all of it. TileLang lets you define the registers, and they have this thing called fragments, which is basically multi across the registers. And we have to make sure that our new multi stuff supports what fragments are. A fragment just means, like, it's a register on each of the warps. You can imagine, like, when you do a copy from locals to fragments, it's like going to the registers in each warp. It's nice. And you don't have to hand specify how to index the fragment.

##### **Qazalin** [[00:11:15](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=675)]
It's basically multi.

##### **Chenyu** [[00:11:19](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=679)]
It's also interesting. They have a full transposed kernel.

##### **Geohot** [[00:11:25](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=685)]
They have a which?

##### **Chenyu** [[00:11:26](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=686)]
They have a kernel for just transpose.

##### **Geohot** [[00:11:29](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=689)]
Oh, yeah.

##### **Chenyu** [[00:11:30](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=690)]
Okay, anyway, I'll read this.

##### **Geohot** [[00:11:35](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=695)]
Yeah.

##### **Geohot** [[00:11:36](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=696)]
No, but it's very... It looks like syntactic sugar on top of tinygrad. Like, we can write a lot of the stuff that they have as syntactic sugar. And, I mean, I'm not exactly... I am curious what backend DeepSeek used because this is... I mean, is it really based on TVM?

##### **Qazalin** [[00:12:01](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=721)]
I thought TVM was kind of dead.

##### **Chenyu** [[00:12:05](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=725)]
So everyone under the hood

##### **Geohot** [[00:12:07](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=727)]
in some version used TVM? Like, have you seen the commits on TVM?

##### **Qazalin** [[00:12:14](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=734)]
It's a dying project.

##### **Geohot** [[00:12:19](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=739)]
Oh. Oh. Maybe there's a little bit...

##### **Chenyu** [[00:12:21](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=741)]
Or maybe it's a complete project. Who knows?

##### **Geohot** [[00:12:24](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=744)]
No, no, it's definitely not complete. Actually, there's been a slight uptick.

##### **Qazalin** [[00:12:31](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=751)]
Yeah.

##### **Geohot** [[00:12:35](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=755)]
Okay, anyway. Let's see.

##### **Chenyu** [[00:12:40](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=760)]
Let's see what speed we got for... I think that's just because a person was fired by NVIDIA or something. They are not supposed to do any work for the six months or something.

##### **Qazalin** [[00:12:55](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=775)]
Wait, who was hired by NVIDIA?

##### **Geohot** [[00:12:59](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=779)]
The TVM person?

##### **Qazalin** [[00:13:02](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=782)]
Or the whole TVM team or something like that?

##### **Geohot** [[00:13:05](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=785)]
Yeah. Oh, I didn't know about that. Yeah. I think they are required. That's why it went down a bit. Okay, anyway.

##### **Qazalin** [[00:13:19](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=799)]
Yeah. Cool.

##### **Geohot** [[00:13:22](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=802)]
Okay.

##### **Chenyu** [[00:13:25](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=805)]
Like a good segue into LLaMA?

##### **Geohot** [[00:13:30](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=810)]
Yeah.

##### **Wozeparrot** [[00:13:31](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=811)]
We have a transpose kernel now.

##### **Qazalin** [[00:13:34](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=814)]
Great. What's our best time we got now?

##### **Wozeparrot** [[00:13:40](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=820)]
Still 2:54.

##### **Geohot** [[00:13:41](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=821)]
2:54.

##### **Wozeparrot** [[00:13:42](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=822)]
And it's very dependent on seed. Because some seeds will just converge in more steps. So if you get a good seed, you're slightly faster.

##### **Chenyu** [[00:13:52](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=832)]
I think now we should try to be stabilized and really try to run things like back-to-back for five times and see if all flows converge.

##### **Wozeparrot** [[00:14:02](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=842)]
Yes. That's basically what I've been doing. I've been prepping a bunch of stuff for submission. So I went through the MLPerf logging package checker and it passes. So we're good for submission.

##### **Geohot** [[00:14:21](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=861)]
So we're good for submission. Chen Yu, I think you're the only one who's actually submitted one of these. Could there be anything we're missing? Could there be anything that's wrong and it'll get rejected?

##### **Chenyu** [[00:14:34](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=874)]
I mean, as long as you run it back-to-back for five runs and at least four of those converges, I think in principle we are good. So it's ten runs. I thought you said five last time.

##### **Wozeparrot** [[00:14:49](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=889)]
Yeah, I was wrong. I was wrong last time. I checked again and it's ten runs.

##### **Chenyu** [[00:14:52](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=892)]
Okay. So I think ten runs still needs to be good, I think, eight or nine of it should converge.

##### **Geohot** [[00:15:03](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=903)]
Yeah.

##### **Chenyu** [[00:15:04](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=904)]
I mean, yeah, let's start doing it. We don't have that many more days.

##### **Nimlgen** [[00:15:08](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=908)]
Yep.

##### **Chenyu** [[00:15:10](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=910)]
Yeah, because if it's like three hours, then...

##### **Geohot** [[00:15:12](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=912)]
Oh, also,

##### **Chenyu** [[00:15:15](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=915)]
how does the setup look like? You also need to... You only have, like, 30 minutes for setup, right? From scratch.

##### **Geohot** [[00:15:23](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=923)]
Yeah.

##### **Chenyu** [[00:15:24](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=924)]
So it's all the, like, prepping, searching, whatever data movement processing thing.

##### **Wozeparrot** [[00:15:31](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=931)]
You can't do data prepare and setup, though, right? Because that's technically touching data?

##### **Geohot** [[00:15:39](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=939)]
Yes. Yeah.

##### **Chenyu** [[00:15:43](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=943)]
So basically just the search of kernels? If you still have any kernel search?

##### **Wozeparrot** [[00:15:48](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=948)]
Yes, yes, there is. Yeah. So Beam happens, like the runtime still does Beam.

##### **Chenyu** [[00:15:54](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=954)]
Yeah, just make sure the first part is below 30 minutes and the logging should reflect that. I won't worry too much after the review. The worst case is they find some minor issue and we probably need to rerun. You don't see any big issue, especially if it's not very fast and challenges everyone's time. They only pay super attention if they are faster than your fastest. And if you are Google doing very fast time, then NVIDIA would be very unhappy about your result. Other than that, I think it's quite peaceful.

##### **Geohot** [[00:16:35](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=995)]
Well, yeah, I mean, we might, we have to make sure that we do everything right this time, because next time we might actually get times that upset people.

##### **Chenyu** [[00:16:44](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1004)]
Yes.

##### **Geohot** [[00:16:45](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1005)]
Yeah.

##### **Chenyu** [[00:16:47](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1007)]
So I think now we know it's 10 times, we need to start doing these back-to-back runs. This is just to make sure the parameters are good for actually for convergence. Because when we test, if it doesn't look good, we will terminate it. We run a new one and we cannot do that for a submission. Yes.

##### **Wozeparrot** [[00:17:08](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1028)]
So far, I haven't really stopped runs early. They've all converged.

##### **Chenyu** [[00:17:13](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1033)]
That's great. Let's just make sure, say, to start with like three to five back-to-back ones for the final one. And yeah, if you merge like everything in the master and just config for a small one, or you still have many things left not merged.

##### **Wozeparrot** [[00:17:36](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1056)]
For the 2:54, everything should be merged.

##### **Nimlgen** [[00:17:41](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1061)]
Okay, sounds good.

##### **Geohot** [[00:17:43](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1063)]
Yeah, let's just let's just unless we see a magic way to get some time speed up. Let's stick with like what's in master and what we trust. We get a 2:54, we get a 2:54.

##### **Geohot** [[00:17:54](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1074)]
Yeah. Is the logging merged?

##### **Wozeparrot** [[00:17:59](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1079)]
Yeah, logging is merged.

##### **Chenyu** [[00:18:02](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1082)]
Okay, well, let's just do some runs. Once you feel comfortable that there's nothing magically, you can make it faster or start to do like 10 runs back to back.

##### **Geohot** [[00:18:14](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1094)]
Yeah. Be able to submit sometime this week.

##### **Chenyu** [[00:18:21](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1101)]
So previously, I always wait until the last two days because that's when we have the results. But if we are ready and we want to be extra careful. Once you have the thing ready, we can have the submission we can have submitted.

##### **Wozeparrot** [[00:18:38](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1118)]
Yeah, it's also possible I'm looking more into speed this week. So if I find something, I will push the submission till next week.

##### **Geohot** [[00:18:48](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1128)]
Well, I mean, let's get it ready. So we have something to submit at this speed. And then if we get a speed up, we get a speed up.

##### **Chenyu** [[00:18:53](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1133)]
Yeah. Yeah, like just spend a day or two and have 10 runs ready for submission. Then we can submit. And if between our first submission to the deadline, you find something, we can resubmit.

##### **Geohot** [[00:19:09](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1149)]
What's the latest with AMD fixing the other computer?

##### **Wozeparrot** [[00:19:15](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1155)]
So far, I send them pictures that they asked for. And then they haven't responded. I'm assuming they also haven't contacted you either.

##### **Geohot** [[00:19:25](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1165)]
No.

##### **Geohot** [[00:19:28](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1168)]
All right, I'll send an email following up.

##### **Nimlgen** [[00:19:31](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1171)]
Okay.

##### **Geohot** [[00:19:32](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1172)]
I mean, this actually makes it impossible for the 405B.

##### **Chenyu** [[00:19:40](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1180)]
Okay, sounds good. Let's get the submission candidate and just submit it. And get it done.

##### **Geohot** [[00:19:48](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1188)]
Yeah, and then just to think a little bit beyond once we get this submitted, I want to start, can we do a 405B? Is there any reason we can't?

##### **Wozeparrot** [[00:19:58](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1198)]
We should be able to. I need to see if. There might be some memory issues.

##### **Geohot** [[00:20:06](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1206)]
Yeah, I mean, it doesn't matter if it actually converges. I just want to like, have it do 10 steps and like, figure out what our time would be.

##### **Wozeparrot** [[00:20:14](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1214)]
Okay, yeah.

##### **Nimlgen** [[00:20:15](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1215)]
Yeah.

##### **Geohot** [[00:20:17](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1217)]
After it gets submitted.

##### **Nimlgen** [[00:20:19](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1219)]
Yep.

##### **Chenyu** [[00:20:22](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1222)]
Okay, sounds good. Next is the dev stuff.

##### **Chrism** [[00:20:29](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1229)]
Yeah. Well, so I mean, DEV hasn't really changed all that much. I mean, obviously, if there's anything that you find unergonomic, let me know. The thing I've been working on is getting USB GPU to work without, or I guess this is not just USB GPU, but get USB GPU to work without depending on the internet. So the big one is like the big thing that we need to do for that is the basic regs, and like on all the different GPUs. This is totally different. Anyway, I have that down to like, a little less than one and a half megs of autogen files. I can make it smaller. So one thing you could do is you could say, Okay, well, like, a lot of these are shared between different versions.

##### **Geohot** [[00:21:16](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1276)]
So how do you get it down to 1.5?

##### **Chrism** [[00:21:21](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1281)]
Like you just filter to the ones that we need using regexes, like a list of regexes. How long is the regex list? There's like, that's like 10 lines or something. I have it. I have a PR open.

##### **Geohot** [[00:21:33](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1293)]
Yeah, I don't know. 1.5 meg is probably fine. Okay, let's not let's not go crazy with some complex thing that could have bugs.

##### **Chrism** [[00:21:40](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1300)]
Okay, yeah, I think that works. I just need to run.

##### **Geohot** [[00:21:44](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1304)]
Yeah, I mean, what's our current like, what's our current PyPI package size? 1.8 megs. How much are we increasing it?

##### **Chrism** [[00:21:56](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1316)]
1.4.

##### **Geohot** [[00:21:58](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1318)]
I think we keep it under five megs. Like, it'd be nice if it fit on a floppy disk. But like, wait, really, that's how much space these things use.

##### **Chrism** [[00:22:06](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1326)]
Well, the problem is that like, there's a lot there's nowhere where it's documented, like which versions of like MMHUB that you need, where it says like, okay, like, this GPU has this MMHUB and this GPU has this version of this thing. So I'm kind of being sort of conservative and saying that we need all of them, or at least all of them within a certain range. But I don't have a 7900 XTX to see like, what does that GPU use? Or, or like this mobile, you know, processor that we definitely should support, but it has a different, it may have a different, you know, version of this IP version.

##### **Nimlgen** [[00:22:40](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1360)]
Nimlgen, do you have any thoughts on this? No, I think this approach, yeah, filtering registers is the correct one. Because yeah, I mean, yeah.

##### **Chrism** [[00:22:55](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1375)]
Yeah, the other thing that I had thought about doing was saying like, Okay, like, let's just include the ones that we know we need for now. And then if someone complains that we can add the other ones, but it's kind of annoying.

##### **Geohot** [[00:23:04](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1384)]
That's annoying. Yeah, okay, fine. 1.4 megs. We'll accept it.

##### **Chrism** [[00:23:07](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1387)]
Okay.

##### **Geohot** [[00:23:07](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1387)]
We'll accept that in tinygrad next and then I think we'll do a release after that.

##### **Chrism** [[00:23:16](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1396)]
The other thing that I was I was thinking about doing was, so we move where we look in /lib/firmware now for AMD GPU firmware, but like, in theory, we could do the same thing for NVIDIA firmware. Some people already have in /lib/firmware, NVIDIA, the GSP binaries. So I was considering looking at that. But right now we do this weird thing where we parse it from a C file rather than downloading the binary. So we download like some C file and then inside the C file has like an array literal that contains the bytes. And then we parse that.

##### **Geohot** [[00:23:51](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1431)]
Well, that's of the... Yeah, yeah, that's the bootloader.

##### **Chrism** [[00:23:55](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1435)]
Yeah, but when I looked, if you look in /lib/firmware, they have like separate binaries. And one of them says like bootloader.

##### **Geohot** [[00:24:00](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1440)]
Yeah, I mean, I think NVIDIA's one is more weird because it's not included in the... maybe they upstreamed it to Linux firmware. I think they did.

##### **Nimlgen** [[00:24:08](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1448)]
And also, yeah, the problem for different binaries is that they can change like we should like the GSP structures and the binary and the bootloader. They should have all the same version.

##### **Chrism** [[00:24:21](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1461)]
Yeah, exactly the same version. I see. Yeah.

##### **Geohot** [[00:24:25](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1465)]
We should pin everything with a hash anyway, if we're gonna go.

##### **Chrism** [[00:24:28](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1468)]
Yes. Yeah. Yeah. If you if you if the hash is wrong, then you have to you have to download and we should

##### **Geohot** [[00:24:35](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1475)]
check that we should check the hash anyway. Is there like some arg to fetch to like, validate the hash?

##### **Chrism** [[00:24:40](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1480)]
Oh, yeah, we should do that.

##### **Geohot** [[00:24:41](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1481)]
Oh, yeah.

##### **Nimlgen** [[00:24:42](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1482)]
Yeah.

##### **Chrism** [[00:24:46](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1486)]
Anyway, that seems like since Nouveau has to boot the GPU, and so they use the thing in /lib/firmware as far as I can tell to boot the GPU.

##### **Geohot** [[00:24:55](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1495)]
Yeah, you need that booter. You don't actually need it for the 590, but the 390 or 490 have it. Yeah.

##### **Chrism** [[00:25:03](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1503)]
I thought I might look at that. I mean, right now, considering we're downloading a C file, like, obviously, that's not the most efficient encoding for the most positive bootloader is small.

##### **Geohot** [[00:25:11](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1511)]
Anyway, it's just the GSP is big. That's true. Yeah, I mean, the other question is that if we wanted to start including firmware, but I don't think we do.

##### **Chrism** [[00:25:22](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1522)]
Yeah, I think /lib/firmware is probably pretty good for most people.

##### **Geohot** [[00:25:25](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1525)]
I mean, it's also there's a difference between like, yeah, having to do the driver and then having to do the like the AMD ASIC regs are needed even if you have AMD GPU inserted, right? Yeah, I want if you have the driver inserted, it never has to go to the internet. Is that true for NVIDIA too?

##### **Chrism** [[00:25:44](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1544)]
I'm not sure I have to check. I haven't been using an NVIDIA GPU with my dock.

##### **Geohot** [[00:25:48](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1548)]
We should Yeah, we should we should we should check that we should just be careful whenever we have to go to the internet. Yeah, you know, definitely. What good is being a self contained project? It's like, yeah, my installer is one meg. Download seven gigs from the internet.

##### **Chrism** [[00:26:03](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1563)]
Yeah, no, I thought maybe it would be a good idea. We have like some context var that says like, you know, disallow opening devices or something. It could also have a disallow fetch or something.

##### **Geohot** [[00:26:15](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1575)]
Yeah, make the error message more explicit. Like you try to download something.

##### **Geohot** [[00:26:20](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1580)]
Yeah, well, I mean, system fetch, but yeah.

##### **Geohot** [[00:26:28](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1588)]
I think that's it. Next, George's stuff.

##### **Geohot** [[00:26:40](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1600)]
Yeah, so I mean, you just try to remove dtype.vec and of course, this doesn't work. There's like seven things you have to untangle before you can remove dtype.vec and I've done like two of them. So the first is, you can separate removing dtype.vec from making the shapes correct. Like you can first make the shapes correct and just have it be in the shape and in dtype.vec. Um, so I'm almost there with that. I did get... So now pretty much everything has shapes. There's a few things that don't have shapes, but we might be able to like remove it. I don't know. I'll have to like, like, we probably still want None for some things.

##### **Chenyu** [[00:27:23](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1643)]
But like, we certainly want None for something. And I think some of some of UOp currently has like the empty tuple. That's probably wrong. If you think about the broadcast rules for those.

##### **Geohot** [[00:27:40](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1660)]
Yeah, yeah.

##### **Chenyu** [[00:27:41](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1661)]
Well, we want to also... Yeah, because empty tuple means you expect it to broadcast, but when broadcasted it works where it can be broadcasted.

##### **Geohot** [[00:27:54](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1674)]
But that's a good way to think about it. So I guess like, yeah, you think about like device, and that's fine to broadcast. But yeah, it's, that's, that's a good thing to think about. I mean, I want to move broadcasting production rules. Anyway.

##### **Geohot** [[00:28:10](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1690)]
Yeah. Um, we'll get there.

##### **Geohot** [[00:28:14](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1694)]
Hopefully this stuff. I tried to do like some refactors to move some stuff out of Ops.py, because like, that's kind of the thing that's going to be left on UOps, these production rules. These production rules for dtypes, these production rules for shapes, these production rules for devices. These recursive production rules, but yeah, they're much much better because they don't involve any, like, you know, my saying about buttons, right? Like, you should never give the user a button, right? Because if you give the user a button, they're going to press it when you don't want them to press it, and they're not going to press it when you want them to press it. So why give them the button? And that's like what dtype is on UOp, right? Like, we're giving them this option, but why? Right? Like, there's the right answer. There's an obvious right answer. You shouldn't be allowed to put anything in besides the obvious right answer. So yeah, like dtype needs to be removed from UOp, and part of that is removing vec. I think I have a plan to do that slowly. But so I can get the shapes, most of the shapes are kind of correct now, but I haven't gotten the actual vector shapes to be correct because the big blocker on that is the image indexing. The image indexing is done with a vec2, and it shouldn't be, because it's actually just normal 2D indexing. It's normal 2D indexing like we use everywhere else. It gets a little bit annoying because late indexes can have a gate. But then you realize that late indexes just shouldn't have a gate. That gate doesn't belong on the index. That gate belongs on the store. So moving the gates to the store. And then you realize that well do you want to move the gates to the load? And then you start realizing, well I don't even want load. Load is ridiculous. It's like what is load, right? Load doesn't really mean anything. What load really is, is a store from a global to a register, or from a local to a register. So you can make the definition of that register explicit and that cleans up a whole bunch of things. But okay, now we're getting into this really big refactor. So I'm just going to explore rewriting CodeGen and seeing kind of where that goes. Because there's so much crap. Like, if you look at that store, it doesn't have ranges anymore. I feel like there's a lot more things like that. I feel like there's a lot of things in CodeGen that only exist to reference something that used to be in CodeGen. And it's just a lot more complex than it needs to be. I have a prototype of just removing the expander entirely. The expander is not really anything. The expander is just a bunch of reshapes and broadcasting, basically. So we can just use reshapes and broadcasting. Yeah, so we can rewrite that with reshapes and broadcasting. You still have to have the devectorizer. This doesn't remove the devectorizer. And the devectorizer conflates basically two concerns. One of the concerns is how to destructure loads. So if you have a load of like a VEC9, you can't actually do that. You can't actually do that on a GPU. You have to refactor that to loads of like, if it's all contiguous, loads of like 4, 4, and 1. Or if it's not contiguous, maybe it all has to be 1 or whatever. So there's that. And then there's the devectorizer, which says, well, you can't actually add a VEC9 to a VEC9. You have to turn that into individual adds, because that's how GPUs work. So that stuff kind of basically has to stay. But the expander can go. Yeah, I mean, it's not like that messy. It is kind of clean. And then we also can do more to just drive the separation between, right now there's two steps before this step called add loads. But that kind of begins the CodeGen section. And the earlier part is all like part of scheduling. So there's kind of like three steps right now in our lowering pipeline, right? There's schedule, which breaks things into kernels and does rangeify. There's like early CodeGen, which is what does optimizations and beam search and reduce folding and local buffers and all those things. And then there's like late CodeGen, which does decompositions, removing of weakint, those kind of things. So it's a pretty clear three-stage pipeline. We can just tighten it up a bit. I'll play with it. Hopefully, the dtype vec will finally be gone. I don't know whether it's a full refactor or not. Usually, I like do these full refactors. I get halfway through them. And then I'm like, I could just clean the whole thing up.

##### **Geohot** [[00:33:00](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1980)]
I think it makes sense.

##### **Qazalin** [[00:33:04](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1984)]
Great.

##### **Geohot** [[00:33:06](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1986)]
Anything else?

##### **Nimlgen** [[00:33:07](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1987)]
No.

##### **Chenyu** [[00:33:11](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1991)]
Next is mixin.

##### **Geohot** [[00:33:15](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=1995)]
So I think I cleaned up like rand.

##### **Chenyu** [[00:33:20](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2000)]
I did some of the rand. Rand now should be easier to read. Then you will understand that in rand function, we use bitcast. And then in bitcast function, we use divmod. And we cannot move divmod because divmod is different. So a very similar story of like rabbit hole. I came to a conclusion that we probably just want all the divmod to be floor divmod because actually most of the divmod we use in actual kernel source is indexing math and those can really be simplified better if you have the floor version, not the C div version.

##### **Geohot** [[00:34:10](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2050)]
So the floor version is the Python version, not the C version. Yeah. And we're using the C version now. I'm not even really sure which one. Yeah. I'm not sure what we're doing.

##### **Chenyu** [[00:34:21](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2061)]
So for now, tensor.py uses the floor Python version, but Ops.IDIV and Ops.MOD is the C div version. I see. That's why we have flags like correct divmod folding rules because sometimes you can fold, sometimes you cannot. This is creating troubles. Not just because the one in tensor and one in UOps are different, but also just mathematically always having the floor version is better because you can simplify more. Halide specifically picked this for the same reason. And on GPU, there's no single instruction for these anyway. It's always the same correction, just off by one or not if it's negative and something like that. So I think I would just do something similar.

##### **Geohot** [[00:35:19](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2119)]
Yeah. I have no problem with adding some more complexity to GPU kernel that's doing integer division or something.

##### **Chenyu** [[00:35:25](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2125)]
Especially if you know the, the vmin of that is always positive. You don't even need to code a more complicated version. So it might be a slightly, a few dtype-dependent render paths, but that's just very similar to how we codegen LLVM. Well, that's my justification.

##### **Geohot** [[00:35:47](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2147)]
Then I started to look into how to really do that. I'm not sure if I can do this migration because this thing is everywhere. So you want to add another UOp for a,

##### **Chenyu** [[00:35:56](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2156)]
no, I don't want to add another UOp. I probably will just rename the current ones to floor first, like actually change the meaning to be the floor ones.

##### **Geohot** [[00:36:08](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2168)]
Well, but if you don't add another UOp, like how does that lowering stage work? Which one?

##### **Geohot** [[00:36:14](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2174)]
The stage that like, what if it is negative, right?

##### **Geohot** [[00:36:26](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2186)]
You know what I mean?

##### **Geohot** [[00:36:28](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2188)]
Like floor div is not renderable in C, right? Yeah. So in render you just render the correct version. Oh, you want to put that in renderer? You don't want to do that earlier? Are you sure? So I think that's the correct place.

##### **Chenyu** [[00:36:53](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2213)]
I really don't know. At least every part that we touch symbolic and do the simplified transformation, I want it to be floor.

##### **Geohot** [[00:37:02](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2222)]
Oh, completely. Yeah, yeah, yeah. No, but I'm saying that I think the right place might be in something like decompositions.

##### **Chenyu** [[00:37:08](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2228)]
Oh, yeah, maybe. Maybe. That's what I thought through. So it's the same thing. Like, do you do this thing in decomposition so that it writes into the C div and C mod at the end? Or you just put it as a render rule? I haven't thought about that.

##### **Geohot** [[00:37:25](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2245)]
I would definitely do it in decompositions and not as render rules. Don't worry about having multiple UOps, right? Because what we're getting to after, like, don't worry about this stuff once you're after add loads. Once you're after add loads in the pipeline, we've kind of entered. Like, I kind of want to merge the x86 stuff because it makes it really clear what these things are. So there is, like, after add loads, all of that stuff is basically forms of instruction selection. And we shouldn't put any instruction selection in the renderer. We should keep it all outside. So things like this. Like, don't be afraid to add more ops. They're totally fine. We just need to make sure that we really restrict those ops

##### **Geohot** [[00:38:18](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2298)]
to only the instruction selection stuff.

##### **Qazalin** [[00:38:24](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2304)]
Yeah.

##### **Geohot** [[00:38:28](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2308)]
There's two things that are missing currently from the CodeGen pipeline. One is instruction selection, and one is register allocation. But we kind of already do register allocation. We just call it memory planning. And then all of the stuff, the second half of CodeGen, is all, all basically instruction selection. And that's the full pipeline.

##### **Chenyu** [[00:38:46](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2326)]
OK, sounds good. Anyway, that was my next plan. And hopefully, after this, everything will be cleaner. I will also look into the stack vectorizing, other than I immediately open that function and see a dtype.vec somewhere.

##### **Geohot** [[00:39:10](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2350)]
Oh, sorry. OK. OK. You can wait till after I get rid of that vec. Yeah, I forgot that's still there. It's not there on my branch. OK. OK. Yeah, no, you can wait till I get rid of that.

##### **Chrism** [[00:39:23](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2363)]
That makes sense.

##### **Geohot** [[00:39:25](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2365)]
But yeah, no, I mean, I think that's a lot of the, like the mixin stuff should be removing these methods off of UOp.

##### **Geohot** [[00:39:35](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2375)]
Yep, yep.

##### **Nimlgen** [[00:39:37](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2377)]
OK.

##### **Geohot** [[00:39:39](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2379)]
Hey, things are finally getting simpler. Notice how we haven't really added anything in a long time. We just kind of removed it. We just kind of removed things now.

##### **Chenyu** [[00:39:47](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2387)]
I'm not too sure. But if so, that's good.

##### **Qazalin** [[00:39:51](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2391)]
Seems like things get removed now.

##### **Nimlgen** [[00:39:53](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2393)]
Yeah.

##### **Chenyu** [[00:39:55](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2395)]
OK. Let's keep that going, if that's the case. And we can move on to, oh, the one where we removed stuff, the runner refactor.

##### **Geohot** [[00:40:09](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2409)]
Yeah, so runners are gone now.

##### **Nimlgen** [[00:40:13](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2413)]
Yeah. OK. So I need to also clean up like the realize.py bit. So, and it's, I think it's 99% complete. So also fixed some CI issues with RDNA4 recovery. So, yeah, and I started to look into the HCQ refactor, I think, and I started with HCQ graph. So currently I have in my branch I can render, like I can render a C program to execute and use this C program to execute the graph and just to push it to the GPU, ring the doorbell and all these things. So I'm thinking about the USB. So actually it currently works with Python as a backend as well. And I think with a bit refactoring,

##### **Geohot** [[00:41:23](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2483)]
so yeah, I mean, it's kind of hard.

##### **Nimlgen** [[00:41:31](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2491)]
I mean, for USB, like for USB backend, I think the only solution is to use Python backend, not the CPU.

##### **Qazalin** [[00:41:42](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2502)]
Why? What is, what is actually doing right?

##### **Geohot** [[00:41:48](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2508)]
Like we use libusb, but how does libusb actually talk to the kernel?

##### **Geohot** [[00:41:53](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2513)]
Yeah, I think.

##### **Geohot** [[00:41:57](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2517)]
I mean, I'd be okay with adding ops that get rendered in C for like read and write with the syscalls.

##### **Geohot** [[00:42:07](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2527)]
Really annoying on macOS though. Okay. So I think that's,

##### **Geohot** [[00:42:11](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2531)]
I guess it doesn't work on macOS.

##### **Qazalin** [[00:42:13](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2533)]
I don't know.

##### **Geohot** [[00:42:16](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2536)]
Yeah.

##### **Geohot** [[00:42:17](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2537)]
Yeah. I mean, okay. If we use Python, like, yeah, we can have this like backdoor where you just like put like some Python code in the arg and just execs it.

##### **Geohot** [[00:42:23](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2543)]
Is that like what you're thinking or?

##### **Qazalin** [[00:42:29](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2549)]
I can do that.

##### **Geohot** [[00:42:31](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2551)]
Oh, but is that what you're thinking?

##### **Geohot** [[00:42:32](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2552)]
What do you mean by use the Python backend?

##### **Nimlgen** [[00:42:36](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2556)]
No, I basically like just execute these calls as the Python backend. I mean,

##### **Geohot** [[00:42:44](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2564)]
well, then how does that access the USB where C can't?

##### **Nimlgen** [[00:42:50](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2570)]
Yeah. With the, so that's why I just, for the final solution, I think we can refactor buffer to expose the, not the memory views, but the memory interface. So the Python backend can also use this.

##### **Geohot** [[00:43:06](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2586)]
Oh, I see what you're saying. Oh yeah. That makes a lot of sense. Yeah. Okay. That's definitely the way to do it.

##### **Nimlgen** [[00:43:13](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2593)]
Yeah. So yeah, going to work on this, this week.

##### **Geohot** [[00:43:23](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2603)]
I mean, I can also see the memory interface kind of being exposed as like the remote protocol.

##### **Nimlgen** [[00:43:29](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2609)]
Yeah. Yeah.

##### **Geohot** [[00:43:32](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2612)]
But you know, I mean, I think that that's a totally reasonable approach to the USB thing. That that's a, that's clean. Just, just, just have it do a Python backend and have the MMIO interface.

##### **Nimlgen** [[00:43:44](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2624)]
Yeah. So because basically they, uh, like for QCOM, there is no doorbell. You just need to ioctl. And I think it's fine for C,

##### **Wozeparrot** [[00:43:54](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2634)]
but yeah,

##### **Nimlgen** [[00:43:55](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2635)]
for USB, I think Python is the easiest solution.

##### **Geohot** [[00:44:01](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2641)]
So for the ioctl, you want to create a like Ops.IOCTL and do that, or no?

##### **Nimlgen** [[00:44:09](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2649)]
I don't know. I actually, I thought that I can refactor like the whole backends. I don't know. Actually, my idea was that I have like the shared function and we'll just have the

##### **Geohot** [[00:44:29](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2669)]
function. I didn't know. I thought that I can just, I know I need to think about this. Yeah.

##### **Nimlgen** [[00:44:41](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2681)]
Basically I can do like a syscall with like custom thing, but I don't know if I,

##### **Geohot** [[00:44:50](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2690)]
I think that's fine.

##### **Nimlgen** [[00:44:53](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2693)]
But in this case, I mean, we don't have libs. I mean, I can do like, like the interrupt on x86 and something similar on ARM, but do we really want this?

##### **Geohot** [[00:45:05](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2705)]
Um, no, I think we can link, right? Like the ELF thing can kind of link. I think there's some PR that does that.

##### **Geohot** [[00:45:13](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2713)]
If the ELF thing currently...

##### **Nimlgen** [[00:45:16](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2716)]
I can, I mean, I can put like the, I know, I don't know. At least I can like pass the pointer to the function and just call it.

##### **Geohot** [[00:45:26](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2726)]
Yeah. I would use like, I would use like Ops.CUSTOM and just call a function. I don't want to do anything that's like arch-specific, like int 80 or whatever the SVC ARM one is or something. I do want to keep the C code architecturally independent,

##### **Nimlgen** [[00:45:46](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2746)]
but only see actually I have something for barriers.

##### **Geohot** [[00:45:53](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2753)]
Oh no.

##### **Nimlgen** [[00:45:55](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2755)]
Like I have custom implementation for x86 and ARM.

##### **Geohot** [[00:46:00](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2760)]
That's probably fine. I mean they're actually different in that. I don't know. Like if there's some like simple libc thing that abstracts things like ioctl, that's good. If it requires thinking about memory orderings or whatever, then yeah, I don't know. Maybe there's only x86 and ARM. Whatever you think is good. You know what I mean? I really, I really like this direction. I'm okay with assuming that we have a C compiler in every environment. So I wouldn't worry about that. Right. It's kind of like the system backend. And to think that tinygrad eventually, like because I think as these neural network runtimes get more complex, like think about something like speculative decoding, like imagine speculative decoding being generated kind of as like a C program, right? Like the C program is the scheduler. So, yeah, it's the eventual direction that all of this stuff goes, right? Like it's just like, you know, these things get so tricky to think about, okay, this is the Python, this is the C, this is the GPU. But I think we have a clearer understanding of what these things actually are than everybody else, right? Because they've built these abstractions, but these abstractions are somewhat nonsensical. Well, like HIP and stuff is somewhat nonsensical, right? This is all based off an abstraction. It's like 20 years old now. Yeah. But then when you think about like where the actual trigger is, what actually has to run on the CPU, what can the GPU do to schedule itself and all of these kinds of things. So yeah, I really like this direction. Go work with the refactors.

##### **Geohot** [[00:47:52](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2872)]
I think realize is quite clean. Yeah. So that's it. Okay. Now, next we have viz.

##### **Qazalin** [[00:48:08](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2888)]
Last week I worked on tracking down the LLaMA kernels. And it's very good because currently with the, with pickles, we can basically replicate everything on the null device. So merge some stuff to make the null device more like AMD.

##### **Qazalin** [[00:48:30](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2910)]
With tracing the graphs and stuff. So currently,

##### **Qazalin** [[00:48:34](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2914)]
I can work this week on tracking down the kernels one by one and fixing them. We're spending about 4% of step time on just copying stuff because of the custom kernel contiguouses.

##### **Geohot** [[00:48:54](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2934)]
Yeah. So I looked into this for like 20 minutes and do you have a clean way to

##### **Geohot** [[00:49:00](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2940)]
do it?

##### **Nimlgen** [[00:49:01](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2941)]
Yeah.

##### **Qazalin** [[00:49:05](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2945)]
I don't think removing the contiguouses from custom kernels is easy,

##### **Qazalin** [[00:49:13](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2953)]
but we can probably change some stuff. I tried,

##### **Geohot** [[00:49:17](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2957)]
I tried removing it and then like, like new contiguouses get inserted and they're all like a little bit different.

##### **Nimlgen** [[00:49:26](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2966)]
Yeah.

##### **Geohot** [[00:49:27](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2967)]
So I worry that this project is just a rabbit hole and like, you know, it looks like it's going to like add complexity, like add a lot of complexity to gain that 4% and then it's probably not worth it. Like if you see like some obvious wins that are simple, I think it's good. But I think trying to get rid of every last one of these is it's not one

##### **Geohot** [[00:49:51](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2991)]
bug.

##### **Qazalin** [[00:49:57](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2997)]
Yeah.

##### **Chenyu** [[00:49:57](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=2997)]
And I think to add to that, we are wrapping up the 7B MLPerf submission. And we are going to focus on the big ones right after we have a submission. So I don't know how much viz can work on the big one now.

##### **Geohot** [[00:50:14](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3014)]
Does it work? Something like that.

##### **Qazalin** [[00:50:22](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3022)]
I mean, like the other direction that they wanted to go is the LLM stuff and

##### **Qazalin** [[00:50:28](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3028)]
replicating that on AMD. I think like all of these are kind of similar, because they're kind of about debuggability of the scheduler and how agents can make progress on this stuff.

##### **Geohot** [[00:50:43](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3043)]
Yeah. Like this, I like a lot better, right? If there's some way we can like expose more to the user or the agent about why those contiguouses appear. Like you kind of need them, but if you could like, like, I think the general thing here is instead of trying to make, instead of trying to fix the automatic thing, just figure out how to expose more control to the user or not.

##### **Qazalin** [[00:51:19](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3079)]
Yeah. Fundamentally, the control is more like you have to track down why a kernel got generated.

##### **Geohot** [[00:51:34](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3094)]
How can we help? Yeah. How can we, how can we like better expose that kind of stuff?

##### **Qazalin** [[00:51:39](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3099)]
Yeah. Yeah, that's what I'm working on.

##### **Geohot** [[00:51:40](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3100)]
and then also to Chenyu's point, how does 45B work? I mean, can we profile 45B?

##### **Qazalin** [[00:51:49](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3109)]
I don't have a command to run it,

##### **Geohot** [[00:51:51](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3111)]
so I don't know how to verify it. It should.

##### **Wozeparrot** [[00:51:54](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3114)]
I will have a command to run it this week. Oh, it'd be the same command. You just try 45B.

##### **Geohot** [[00:52:01](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3121)]
Oh, okay. I'll try it. I think it should work.

##### **Wozeparrot** [[00:52:05](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3125)]
Wait, because I need to fix some, just the sharding stuff that has to change.

##### **Nimlgen** [[00:52:10](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3130)]
Yeah.

##### **Geohot** [[00:52:12](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3132)]
I mean, I think, I think basically the same project you did to get the 8B profiler down to two minutes. I mean, it's not just the profiler, it's down to two minutes now. It's also the startup time, which is down to two minutes, which is great. Yeah. I think we basically got to do the same thing. Yeah. Maybe we just need to fix it for 45B.

##### **Geohot** [[00:52:36](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3156)]
And I think that's more valuable than tracking down every last,

##### **Geohot** [[00:52:42](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3162)]
every last copy is just okay. That's 4%. I mean, we have, we have, I think, I think like 4% is not the, I think the complexity required to address that versus like the low hanging fruit is not worth it.

##### **Geohot** [[00:52:59](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3179)]
I think we have other, I think there's cheaper ways to get speed gains, if that's even what we want to do.

##### **Geohot** [[00:53:13](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3193)]
Yeah, I think in general, continuing with the overall LLM usability project, when can we just set an LLM loose on some command and have it automatically find improvements?

##### **Qazalin** [[00:53:37](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3217)]
Yep.

##### **Geohot** [[00:53:39](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3219)]
And an LLM remove the bank conflicts. So if you run AMD copy matmul with WMMA=1, there's bank conflicts.

##### **Qazalin** [[00:53:51](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3231)]
Yeah.

##### **Geohot** [[00:53:54](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3234)]
How can we get an LLM to fix that?

##### **Qazalin** [[00:53:58](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3238)]
That's the assembly one is a little hard. There's more problems with assembly than just this.

##### **Geohot** [[00:54:08](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3248)]
But not just the assembly. I mean, copy matmul is not assembly.

##### **Qazalin** [[00:54:12](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3252)]
Oh, copy matmul. I thought you were talking about the assembly one.

##### **Geohot** [[00:54:17](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3257)]
Oh, that assembly one's crappy.

##### **Nimlgen** [[00:54:20](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3260)]
Yeah.

##### **Geohot** [[00:54:21](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3261)]
You know, copy matmul has the bank conflicts too. And I wonder, can an LLM track down the bank conflicts? Is our tooling good enough for an LLM to fix that?

##### **Geohot** [[00:54:30](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3270)]
Yeah. Like GPT-5.5 to fix that. Hm.

##### **Qazalin** [[00:54:41](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3281)]
I'm thinking how the ThunderKittens people did it, which is basically write a solver. So you need to read docs and solve it on your own.

##### **Qazalin** [[00:54:53](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3293)]
It's fun. I tried a little bit with it. But like.

##### **Nimlgen** [[00:54:59](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3299)]
Yeah.

##### **Geohot** [[00:55:00](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3300)]
I think that's the project.

##### **Geohot** [[00:55:02](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3302)]
And then the 45B. Just decreasing the REPL loop on 45B. We can hopefully like. I don't know. Maybe by the end of.

##### **Geohot** [[00:55:13](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3313)]
By the end of the month. At least sometime in June. Have a complete 45B run. I mean. I also. Want to like.

##### **Geohot** [[00:55:27](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3327)]
For each one of our custom kernels in LLaMA. And we'll really see this with 45B. Like with 45B. We have to figure out which custom kernels are now not getting high MFU. Like with 45B. We should be able to get more MFU. Assuming that our kernels are good. But I mean, those custom kernels like seem kind of bad. They're also in like assembly or HIP. How do we get them in our language? Yeah. Like how many of the custom kernels can be rewritten?

##### **Geohot** [[00:55:55](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3355)]
In tinygrad language? Like if you replace it with AMD copy matmul. Or the flash attention one I have.

##### **Chenyu** [[00:56:19](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3379)]
That's an open question, right? We'll figure that out.

##### **Geohot** [[00:56:23](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3383)]
Yeah. Yeah. But that's kind of like. Yeah. That's kind of the project. That I want you to work on. I think it's all kind of the same project.

##### **Qazalin** [[00:56:32](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3392)]
Yeah. It'll be interesting to see like how.

##### **Qazalin** [[00:56:36](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3396)]
We can express the warp specialization stuff. And like every time I ask an LLM. It's like. Oh, I can't do this. So no. But.

##### **Qazalin** [[00:56:46](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3406)]
Are the kernels warp specialized? The AMD ones?

##### **Qazalin** [[00:56:52](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3412)]
No. But like in general.

##### **Geohot** [[00:56:54](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3414)]
Yeah. Yeah. If the AMD.

##### **Qazalin** [[00:56:55](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3415)]
Ones aren't warp specialized.

##### **Geohot** [[00:56:56](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3416)]
I wouldn't worry about it. Right? Like we first want to match the AMD ones with our language. We want to replace the custom HIP kernels with tinygrad kernels. Even if they're hand-coded tiny kernels.

##### **Geohot** [[00:57:07](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3427)]
Even if they're like UOp tinygrad kernels. Okay. Uh, move on. Uh, any open issues, especially from Comma.

##### **Chenyu** [[00:57:24](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3444)]
Yeah.

##### **Chrism** [[00:57:25](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3445)]
So I'm trying to get them to bump tinygrad. Um, but they're complaining about, uh, run_linear and enqueue, uh, the timings for enqueueing a copy had regressed. And I haven't looked at this too much, but my understanding is that, uh, like, I mean, clearly we're aware of this because when, when we merged run_linear, uh, we, you know, changed the assert min step time. Um, so, uh, yeah, I mean, now they're complaining about that.

##### **Qazalin** [[00:57:59](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3479)]
Who changed the assert min step time? I was on the edge.

##### **Geohot** [[00:58:08](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3488)]
You're on the edge.

##### **Geohot** [[00:58:09](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3489)]
Okay. Okay. Yeah.

##### **Geohot** [[00:58:09](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3489)]
Okay.

##### **Chrism** [[00:58:10](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3490)]
And anyway, they, they are now complaining about that. Like we, we know that, that, that, that, that was something they were upset about. And I said that, uh, you know, now they're upset about it. Um, so, uh, I need to try again with the, I saw you merge like the faster run_linear. Um, but that didn't make any major changes to the copy path. Right. So I think that's the majority of what's being slow is there's a whole bunch of stuff that needs to be recomputed every time that used to be cached, uh, in like the BufferXfer object. Um, or I guess it wouldn't be BufferXfer, it'd be BufferCopy, but, uh, I have to imagine

##### **Chenyu** [[00:58:47](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3527)]
that where the slowdown is coming from. Is there something you can put on benchmark?

##### **Chrism** [[00:58:53](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3533)]
Well, it is. It's there. It's assert min step time.

##### **Geohot** [[00:58:56](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3536)]
No, but assert min step time includes a lot of other stuff.

##### **Geohot** [[00:58:59](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3539)]
Esther. Yeah.

##### **Chenyu** [[00:59:01](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3541)]
Uh, yeah. Can we make it. Uh, assert min step time didn't regress.

##### **Chrism** [[00:59:07](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3547)]
It did. Uh, and.

##### **Nimlgen** [[00:59:10](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3550)]
I, yes, actually in this example, they have like, they have several copies and then they have one graph and I think run_linear in the recent and in master, it's like four milliseconds slower for each call or for each ExecItem.

##### **Geohot** [[00:59:39](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3579)]
Yeah, I mean, the other thing is that they could just,

##### **Chrism** [[00:59:44](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3584)]
like, probably the right thing for them to do is do this from_blob on the tensors beforehand so that they're already on QCOM.

##### **Geohot** [[00:59:55](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3595)]
But it is a regression.

##### **Qazalin** [[01:00:00](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3600)]
Sorry, which assert min step time regressed?

##### **Geohot** [[01:00:03](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3603)]
In the thing I just sent at the top of the file.

##### **Geohot** [[01:00:10](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3610)]
The driving policy ones went from three to four. But yeah, it doesn't seem like major. I mean, it was only that one.

##### **Chrism** [[01:00:14](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3614)]
Yeah.

##### **Geohot** [[01:00:15](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3615)]
That's the one that has three copies at the beginning of it.

##### **Geohot** [[01:00:17](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3617)]
I see. I mean, yeah, if they can use from_blob instead.

##### **Chrism** [[01:00:23](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3623)]
That's what I told them to do. And they're like, well, I don't know. Well, but now I have to write different code for AMD USB and for, you know. Fair. Which, yeah.

##### **Qazalin** [[01:00:33](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3633)]
OK.

##### **Geohot** [[01:00:38](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3638)]
I don't know.

##### **Qazalin** [[01:00:39](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3639)]
Do something.

##### **Chrism** [[01:00:42](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3642)]
Yeah, I think they should use from_blob. I think that's.

##### **Geohot** [[01:00:45](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3645)]
No, no, no, no, no, no. But then you're right about that. It should be, no, that violates the tinygrad promise. Write code once, run anywhere.

##### **Nimlgen** [[01:00:54](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3654)]
Yeah.

##### **Geohot** [[01:00:55](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3655)]
But I think it's better.

##### **Nimlgen** [[01:00:56](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3656)]
But I mean, with some Python optimizations I know and tricks, I can probably get it down three milliseconds. But what's the current time?

##### **Geohot** [[01:01:09](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3669)]
Will the C stuff fix this? I mean, that's the real solution to this, right?

##### **Nimlgen** [[01:01:14](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3674)]
Actually, no. I mean, graph is still fast and maybe even faster than they were before. But yeah, the problem is that they have non-graphed copies. Yeah. Oh. That's like several calls. Yeah, and because of that, like.

##### **Geohot** [[01:01:30](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3690)]
They have to graph the copies. They are too.

##### **Chrism** [[01:01:35](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3695)]
I don't think they have to put the SDMA on QCOM.

##### **Geohot** [[01:01:36](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3696)]
No, no, no, no, no, no, no, no, no, no. They have to graph the copies. Oh, if they're using ungraphed copies, then that's on them.

##### **Chrism** [[01:01:43](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3703)]
But how do you, what do you mean?

##### **Geohot** [[01:01:44](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3704)]
Is it in a JIT?

##### **Chrism** [[01:01:46](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3706)]
No, no, no, it is.

##### **Nimlgen** [[01:01:47](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3707)]
No, they probably cannot be graphed because it's...

##### **Geohot** [[01:01:50](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3710)]
Yeah, it's copying from CPU.

##### **Qazalin** [[01:01:54](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3714)]
Oh. I think probably.

##### **Geohot** [[01:01:58](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3718)]
If it's in a JIT, it's on us. If it's not in a JIT, it's on them. If it's in a JIT, then yeah, we need to like compile this to C, basically. We need to compile the graph runner to C, basically.

##### **Chrism** [[01:02:09](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3729)]
Yeah, it is in a JIT.

##### **Geohot** [[01:02:10](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3730)]
It's doing a copy from NPY to QCOM in a JIT.

##### **Nimlgen** [[01:02:14](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3734)]
Yeah. OK.

##### **Chenyu** [[01:02:19](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3739)]
Another minor thing. We probably want to increase the granularity of assert min step time here. Like 3 to 4 is too big. I don't know if we just put it back 3.5, does it work or something.

##### **Chrism** [[01:02:33](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3753)]
I mean, maybe we should have a different benchmark because there is a lot of noise. I don't know if increasing it or not.

##### **Chenyu** [[01:02:40](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3760)]
Or that. We basically want to make sure that it's effectively capturing something that we don't want to regress.

##### **Nimlgen** [[01:02:48](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3768)]
Yeah.

##### **Geohot** [[01:02:49](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3769)]
I mean, but yeah. I think the fix here is just not to go to Python for the copies, right? Sure, we don't have an SDMA on QCOM, but we can make an SDMA out of a C thread that listens and runs mem copies, right? If we're using mem copies, we're using mem copies. But we could have a C thread that just like.

##### **Chrism** [[01:03:07](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3787)]
It's frustrating, but it doesn't have to be at all.

##### **Geohot** [[01:03:09](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3789)]
It's the SDMA, the software SDMA. Soft SDMA. But it's the same memory, right? Yeah, but this is probably copying six bytes. Who cares?

##### **Chrism** [[01:03:18](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3798)]
That's true. That's true.

##### **Geohot** [[01:03:19](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3799)]
It's not about the six bytes. It's about the three milliseconds of Python overhead. Oh, we're going to process a UOp. Got to construct and deconstruct 252 Python objects.

##### **Chenyu** [[01:03:33](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3813)]
Anyway, we should prioritize this and make sure it's there before our next release.

##### **Qazalin** [[01:03:44](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3824)]
Sounds good.

##### **Geohot** [[01:03:46](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3826)]
Yeah. I mean, I think the answer is some kind of like software SDMA. I think. Does that make sense?

##### **Qazalin** [[01:03:57](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3837)]
Yeah.

##### **Geohot** [[01:03:59](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3839)]
Or whatever. I mean, whatever it is. We've got to like compile it, right? Because right now, even though it's in the JIT, it's still running it through the realize path.

##### **Geohot** [[01:04:12](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3852)]
Yeah.

##### **Nimlgen** [[01:04:15](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3855)]
OK.

##### **Chenyu** [[01:04:20](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3860)]
Anyway, I think that's it for this meeting. Thank you, everyone. I will be in San Diego next week. So I'll see you.

##### **Geohot** [[01:04:27](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3867)]
See you soon.

##### **Qazalin** [[01:04:28](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3868)]
Bye. Bye. Bye.

##### **Geohot** [[01:04:30](https://www.youtube.com/watch?v=zYkkGZtEw_A&t=3870)]
Bye.
