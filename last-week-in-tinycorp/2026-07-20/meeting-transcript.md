# 2026-07-20 Meeting

### Meeting Agenda

**Time:** new meeting #27, 7/20 9am Monday San Diego time
- company update
- hcq2
- dtype cleanups, multi, llm app
- weak dtype, shifts
- SLICE cleanups
- viz llama training
- gpt-oss training
- bounties, issues, comma happiness, kimi


### Audio

[Youtube Link](https://www.youtube.com/watch?v=Rsl-Gtifyuc)

### Highlights

* **[AMD Payment](#geohot-000003)**: Tinygrad received a $400,000 wire payment from AMD on the morning of the meeting.
* **[Tinygrad’s Scope](#geohot-000039)**: Geohot described Tinygrad as replacing ROCm and much of its surrounding GPU software stack, reducing millions of lines of code to roughly 25,000.
* **[Chestnut Launch](#geohot-000247)**: Final Chestnut units are ready, with a tentative August 7 launch; Geohot said it will be the cheapest hardware product the company has made.
* **[Multi Rewrite](#geohot-001112)**: The proposed Multi redesign would replace the current dedicated operation and pass with a cleaner algebra supporting `alloc_fragment` and warp-cooperative register layouts.
* **[LLM-Written Kernels](#geohot-001327)**: Beam search cannot naturally express optimizations such as Flash Attention, so the team wants a cleaner kernel language that LLMs can use to generate fast, correct kernels.
* **[Weak Dtypes](#chenyu-001434)**: Chenyu has largely completed the weak-constant design, with weak types preserved through symbolic operations and materialized or explicitly cast only when required.
* **[Removing Buffer Views](#chrism-001853)**: Chrism proposed eliminating buffer views by representing accesses as a base buffer plus variable offsets, simplifying scheduling and backends such as OpenCL and WebGPU.
* **[Llama Training Speed](#qazalin-002343)**: The latest Llama training run reached a best total time of 2 hours 26 minutes, with step time beginning around 1.28 seconds before power or thermal effects raised it to roughly 1.44 seconds.
* **[Scheduler Stalls](#qazalin-002529)**: Current Llama performance loses about 100 milliseconds per device to synchronization stalls, but the immediate priority is upstreaming and simplifying the accumulated optimizations.
* **[GPT-OSS Training](#wozeparrot-003134)**: GPT-OSS training improved to about 2.4 seconds per step and an estimated 10-hour full run, down from roughly 30 hours, although convergence remains incorrect.
* **[Benchmark Mismatch](#wozeparrot-003427)**: The team found that accepted GPT-OSS benchmark submissions do not match the published reference architecture, so they plan to match accepted submissions while documenting the discrepancy with organizers.
* **[MXFP4 Roadmap](#geohot-003919)**: Recent AMD benchmark times use MXFP4 while Tinygrad’s comparable run uses FP8; because HipKittens lacks MXFP4 infrastructure, the team will first upstream its work and target AMD’s FP8 performance.
* **[Kimi Inference Bounty](#geohot-004747)**: The Kimi inference bounty remains open with a target of more than 100 decoded tokens per second using tensor parallelism.
* **[Agent-Generated PR Quality](#chenyu-005225)**: The maintainers welcome agent-discovered optimizations but emphasized that contributors must understand, simplify, and polish generated changes into focused, mergeable pull requests.


### Transcript
##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=0)]
Let's start the meeting with company update.

##### **Geohot** [[00:00:03](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3)]
We got paid $400,000 by AMD, so that wire came in this morning. That's pretty good.

##### **Geohot** [[00:00:10](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=10)]
I'll do my presentation for you guys. Let's see if it's any good.

##### **Chenyu** [[00:00:14](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=14)]
When is it?

##### **Geohot** [[00:00:17](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=17)]
Wednesday.

##### **Chenyu** [[00:00:18](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=18)]
Is it online?

##### **Geohot** [[00:00:20](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=20)]
Yeah, I just want to run through the slides with you guys and see if they make sense.

##### **Geohot** [[00:00:25](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=25)]
Presenting a bunch of Tinygrad features. Features.

##### **Geohot** [[00:00:28](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=28)]
Really just talking about what it does.

##### **Geohot** [[00:00:33](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=33)]
How it pretty much replaces the whole... Not just RockM.

##### **Geohot** [[00:00:39](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=39)]
RockM is one small piece of what Tinygrad replaces. Tinygrad replaces RockM. All of the stuff on top of RockM, like Composable Kernel, RockWame, RockNickel, Rockle. And AMD GPU.

##### **Geohot** [[00:00:59](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=59)]
And it replaces what's really millions and millions and millions of lines of code with 25,000 lines of code. And it's not cheating.

##### **Geohot** [[00:01:09](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=69)]
I kind of... I always wonder what this means.

##### **Geohot** [[00:01:13](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=73)]
I wonder if there is some limitation to why most software is not written this way. But I have a theory that... I don't know. I haven't tried the alternative. But I've been playing with just putting Codex Goal on Tinygrad and saying, like, achieve whatever benchmarks. And it's doing a great job. I wonder if that same job can be done with other stuff.

##### **Geohot** [[00:01:41](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=101)]
Because it can't... the LLM can't read.

##### **Geohot** [[00:01:44](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=104)]
For the LLM to recompile, you know, RockWame, this

##### **Flata** [[00:01:52](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=112)]
is going to take 20 minutes.

##### **Geohot** [[00:01:55](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=115)]
It can't do this. I think that we'll have so much tighter agentic loops than everybody else. You know, people on Twitter are saying, like, but is Tinygrad really designed for the agentic future? And my take on this stuff is always, like, what's good for humans is good for agents. Humans want this stuff to the time requirement. The other thing that I talk about is uncrashable drivers.

##### **Geohot** [[00:02:20](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=140)]
That's so important. I can't believe anyone has a workflow... ...where they have to wait

##### **Unknown** [[00:02:25](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=145)]
for a few hours to complete a problem, you know. wait

##### **Geohot** [[00:02:25](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=145)]
12 minutes for a machine to reboot.

##### **Geohot** [[00:02:28](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=148)]
And AMD still has bugs and whatever the BKC is, hopefully that got fixed. But yeah, you just want to delete absolutely all of this. You know, at least I'm confident with the USB 3 GPU that that thing could never, ever crash your computer. USB 4 can still crash your computer somehow, mysteriously. But yeah.

##### **Geohot** [[00:02:47](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=167)]
So yeah, that's the main thing. And we're launching the chestnut. We have final chestnuts. It'll launch, I think, August 7th.

##### **Chrism** [[00:02:58](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=178)]
So

##### **Geohot** [[00:02:58](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=178)]
everyone get your wallets ready.

##### **Geohot** [[00:03:01](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=181)]
That's money. It's cheap. Don't worry, it's cheap. It's the cheapest thing TinyGun ever made.

##### **Geohot** [[00:03:09](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=189)]
Okay, anything else?

##### **Geohot** [[00:03:12](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=192)]
Moving on. Or with HTTQ 2?

##### **Nimlgen** [[00:03:19](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=199)]
So yeah, this week I've been preparing for

##### **Unknown** [[00:03:22](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=202)]
the next few weeks.

##### **Nimlgen** [[00:03:35](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=215)]
So yeah,

##### **Nimlgen** [[00:03:41](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=221)]
this week I'm going to refactor AMD and merge it finally. Also, I think do some training runs. With AMD,

##### **Unknown** [[00:03:52](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=232)]
I'm going to do some training runs.

##### **Nimlgen** [[00:03:52](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=232)]
With HTTQ 2. But yeah.

##### **Qazalin** [[00:04:00](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=240)]
Yeah.

##### **Geohot** [[00:04:06](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=246)]
I'm happy to see a whole bunch of those those graph rewrites deleted.

##### **Geohot** [[00:04:13](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=253)]
Like those.

##### **Geohot** [[00:04:16](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=256)]
Yeah.

##### **Geohot** [[00:04:19](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=259)]
That's cool. Cool.

##### **Geohot** [[00:04:22](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=262)]
I did you see I had some issues where it's unreliable for some reason on my Yeah.

##### **Nimlgen** [[00:04:29](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=269)]
Yeah.

##### **Geohot** [[00:04:33](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=273)]
And then I'm seeing PTE already mapped, but I don't know what that is. Could be many things.

##### **Geohot** [[00:04:42](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=282)]
Maybe not HTTQ related.

##### **Qazalin** [[00:04:51](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=291)]
Have

##### **Geohot** [[00:04:52](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=292)]
other things, x translates.

##### **Nimlgen** [[00:05:01](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=301)]
You just can seeashing something for you. You kept split them,

##### **Geohot** [[00:05:02](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=302)]
it's been perfect. The last

##### **Unknown** [[00:05:05](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=305)]
league. I

##### **Geohot** [[00:05:05](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=305)]
didn't

##### **Unknown** [[00:05:07](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=307)]
actually want to.ト want to

##### **Geohot** [[00:05:07](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=307)]
remove things for theisses with the mixture. So

##### **Unknown** [[00:05:09](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=309)]
like

##### **Geohot** [[00:05:09](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=309)]
most,

##### **Unknown** [[00:05:09](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=309)]
what I like. I just wanted to remove that just about to say like.

##### **Geohot** [[00:05:09](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=309)]
Some的時候, I have gathered like a, some. ZX machines that I could never watch live can make.

##### **Nimlgen** [[00:05:11](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=311)]
I know that music agnostic is just lessons for having them on a new video program. I work on that as well. So I just replaced all the custom. Yeah, I just replaced all the customs. So it's nice.

##### **Nimlgen** [[00:05:26](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=326)]
The opcp looks nice. I just need to more thoughtfully merge all the changes in the rangeify and other things before.

##### **Geohot** [[00:05:38](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=338)]
What changes did rangeify need?

##### **Nimlgen** [[00:05:42](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=342)]
I had some issues with loops, because I have the outer loop.

##### **Unknown** [[00:05:50](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=350)]
And

##### **Nimlgen** [[00:05:50](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=350)]
when I have, and actually, because I have different comments, instead of gating, I just use for loops, because if it's not allowed in the graph. So do we want to allow this?

##### **Geohot** [[00:06:07](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=367)]
I see your changes to rangeify. And I'm

##### **Unknown** [[00:06:10](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=370)]
sorry. I

##### **Geohot** [[00:06:10](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=370)]
can't say I understand them.

##### **Wozeparrot** [[00:06:13](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=373)]
Yeah.

##### **Geohot** [[00:06:15](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=375)]
Do we want to allow ifs in the big graph?

##### **Geohot** [[00:06:22](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=382)]
What do you need an if for?

##### **Nimlgen** [[00:06:26](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=386)]
Like parsing different ones from the so -called CPU Mac.

##### **Geohot** [[00:06:34](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=394)]
Can you use a where?

##### **Geohot** [[00:06:55](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=415)]
No.

##### **Geohot** [[00:06:57](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=417)]
Now you mentioned storages and Didn't we do this in the voorwaarde module And so.

##### **Qazalin** [[00:07:04](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=424)]
Yeah.

##### **Geohot** [[00:07:06](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=426)]
If that's what you're worried about. So no, I don't really want to allow if in the big graph because the problem with allowing if in the big graph is then you have to start thinking about allowing and if in the big graph.

##### **Geohot** [[00:07:17](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=437)]
And that creates kind of weird, like all things that you want to do with if should basically just be like gated. If you want to have a gated call, that's something I'm much more open to.

##### **Geohot** [[00:07:35](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=455)]
Yeah.

##### **Qazalin** [[00:07:37](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=457)]
Because GPUs

##### **Geohot** [[00:07:38](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=458)]
don't really have... Go ahead.

##### **Nimlgen** [[00:07:42](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=462)]
Yeah.

##### **Nimlgen** [[00:07:44](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=464)]
Yeah, actually, I need just gated load, store, wait, and call. Like for them.

##### **Geohot** [[00:07:50](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=470)]
Oh, that's totally fine. I mean, wait's already kind of gated.

##### **Geohot** [[00:07:55](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=475)]
Yeah. Yeah, if you want to gate call, if adding a gate to call would fix it, then that's probably fine. Though again, I'm going to argue, why do you even need a gate to call? What you want to gate instead is the stores inside the call and then pass in that gate.

##### **Geohot** [[00:08:16](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=496)]
Oh.

##### **Geohot** [[00:08:25](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=505)]
If stores the only thing that has side effects, again, don't worry about execution time. Execution

##### **Unknown** [[00:08:28](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=508)]
time.

##### **Geohot** [[00:08:28](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=508)]
Execution time is free. And if stores the only thing that has side effects, right, we can already express basically a gated call by gating all the stores inside of a call and then putting in a gate as a parameter. This is just normal parameter.

##### **Geohot** [[00:08:45](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=525)]
Yeah.

##### **Nimlgen** [[00:08:53](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=533)]
I don't know if we actually have any stores because...

##### **Nimlgen** [[00:08:58](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=538)]
Wait, what? We

##### **Qazalin** [[00:08:58](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=538)]
just

##### **Nimlgen** [[00:08:58](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=538)]
need to execute function.

##### **Geohot** [[00:09:01](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=541)]
If you don't have stores, then your function does nothing.

##### **Nimlgen** [[00:09:07](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=547)]
No, it just calls another function. Like... Oh, okay.

##### **Geohot** [[00:09:12](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=552)]
Which is...

##### **Geohot** [[00:09:13](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=553)]
Maybe you got to show me the example.

##### **Geohot** [[00:09:17](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=557)]
But, you know, I don't want to allow if in the big graph. But if you want to have some gated call thing, that's more... Okay.

##### **Geohot** [[00:09:33](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=573)]
Yeah. I'm not even 100% sure we need that.

##### **Geohot** [[00:09:40](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=580)]
We should treat if just like an assembly instruction.

##### **Geohot** [[00:09:47](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=587)]
Yeah, okay. It's like... So, no... Uh... Yeah. We could even remove if. There's an argument to just say we should remove if and make all the renderers just support gated stores.

##### **Geohot** [[00:09:57](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=597)]
Because all the renderers are just gated stores. Well, the only place if is used right now is for gated store.

##### **B1tg** [[00:10:06](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=606)]
Yeah.

##### **Geohot** [[00:10:06](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=606)]
I

##### **B1tg** [[00:10:06](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=606)]
remember

##### **Geohot** [[00:10:06](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=606)]
trying

##### **B1tg** [[00:10:06](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=606)]
that months ago. Somehow, though...

##### **Chenyu** [[00:10:11](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=611)]
Maybe we just need a better assembly backend. But it's slower. It's slower.

##### **Chenyu** [[00:10:18](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=618)]
It's

##### **Geohot** [[00:10:19](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=619)]
slower. It's slower. We'll have to delete those ops.

##### **Chenyu** [[00:10:22](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=622)]
All right. We're cool.

##### **Geohot** [[00:10:23](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=623)]
Okay. Sounds good. Yeah, sounds good. Excited to have AMD merged.

##### **Geohot** [[00:10:27](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=627)]
Okay. Thanks. Anything else?

##### **Geohot** [[00:10:31](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=631)]
No.

##### **Geohot** [[00:10:33](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=633)]
Okay.

##### **Qazalin** [[00:10:35](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=635)]
Let's move on.

##### **Chenyu** [[00:10:36](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=636)]
Just this bunch of weird stuff.

##### **Geohot** [[00:10:40](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=640)]
Yeah, so... I mean... Dtype cleanups is waiting for slice and waiting for const.

##### **Unknown** [[00:10:49](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=649)]
Uh... Yeah.

##### **Geohot** [[00:10:51](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=651)]
So, when const... When slice is deleted and const is weak. week, we can delete DTYPE from UOP entirely. I don't want to start putting it in. The const is the really annoying one, where you don't just want to start putting that on all the args. And slice is just something that's easier to just clean up first.

##### **Geohot** [[00:11:12](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=672)]
Yeah, that'll be the end of the DTYPE cleanups. For multi, it's been a lot of theoretical work to try to figure out how we want to represent this. There's still debates about whether it's a pad, whether it's invalid, whether it's just a stack. But we should figure out a new algebra for multi that doesn't have a stupid op called multi and a pass called multi. Because the real goal of the new multi is to support alloc fragment. I think that the alloc fragment is the greatest innovation of Tylang. I think that's why people like Tylang. Overall, our syntax is pretty much like our kernels.

##### **Geohot** [[00:11:58](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=718)]
I have three PRs up that are codex slot PRs. But codex has gotten very, very good at writing kernels using our language.

##### **Geohot** [[00:12:07](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=727)]
But you see that it could probably write kernels that are more likely to be correct and shorter with alloc fragment. And that's why people like Tylang. So what alloc fragment is is basically multi for registers. It's multi, but instead of going across multiple GPUs, it goes across multiple threads in the warp. And this lets you. Very cleanly express warp cooperative things. So we have warp cooperative things like reduce across the warp or whammy.

##### **Geohot** [[00:12:35](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=755)]
They're much nicer to express when you have instead of a single register being a single register and having to deal with weird indexing for it, you can just express what shape the registers form across the whole things. And then you can just see that the loading from the locals into the registers becomes a normal store. Ah. And the indexing is all dealt with like implicitly, not explicitly. It's a much cleaner syntax. So yeah, that's my goal with the multi rewrite.

##### **Geohot** [[00:13:08](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=788)]
And then I want to spend some time making the kernel syntax beautiful, figuring out why. Because then we have like a thing about the kernel syntax is that's all working with everything below the kernel. That's working with the linearizer, it's working with the LVM stuff, it's working with the C, assembly stuff, it's working with everything.

##### **Geohot** [[00:13:27](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=807)]
This whole bottleneck, for tinygrad being fast, seems to be the search. Beam does not express flash attention. And the fact that Beam doesn't express flash attention is probably not addressable by a smarter Beam.

##### **Geohot** [[00:13:45](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=825)]
The better thing to do is probably to figure out how to make this syntactically beautiful, and then just tell the LLM, hey, speed up this model.

##### **Geohot** [[00:13:55](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=835)]
And let it express kernels in the kernel language.

##### **Geohot** [[00:14:00](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=840)]
And it doesn't seem to mess up too much on correctness. Versus if you tell GPT still today to optimize assembly code, it messes up constantly on correctness.

##### **Geohot** [[00:14:13](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=853)]
So yeah, multi is kind of what I'm working on in the AMD presentation.

##### **Geohot** [[00:14:24](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=864)]
The reviewer said, I'm not sure if you guys are going to review my slides. They do not. We had a conversation about that, and they agreed with me that they

##### **Chenyu** [[00:14:31](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=871)]
don't want to review my slides.

##### **Chenyu** [[00:14:34](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=874)]
OK, let's move on. That is my stuff. So work mostly on the weak const design. I think I got most of the design good. And I have been putting small search or test or the text. Just need to define some of the behavior. You cannot materialize a thing with a weak D type, because weak D materialized needs to know how big your D type is.

##### **Chenyu** [[00:15:06](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=906)]
And basically, have all those boundaries defined.

##### **Chenyu** [[00:15:12](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=912)]
And I list Shift, because I realize Shift has a very weird spec.

##### **Chenyu** [[00:15:19](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=919)]
Currently, our spec is the second source of the ship,

##### **Unknown** [[00:15:23](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=923)]
and

##### **Chenyu** [[00:15:23](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=923)]
your shift distance needs to be an integer.

##### **Chenyu** [[00:15:27](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=927)]
But in some backends, they only support you in 32. So we need to cast in those backends. Then you have the issue for, OK, should we broadcast D type on this or not? This is the first source of where. The first source of where is always a Boolean. You don't upcast your D type with other source.

##### **Geohot** [[00:15:48](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=948)]
That's interesting. You can implicitly

##### **Chenyu** [[00:15:50](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=950)]
cast it.

##### **Geohot** [[00:15:53](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=953)]
Like C supports that, right? In C, I can say, if I is an integer, I can say, I question mark 40, 30, colon 30. And then that I will be implicitly cast into a Boole.

##### **Chenyu** [[00:16:05](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=965)]
Yeah, but how does that work for, say, assembly?

##### **Geohot** [[00:16:11](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=971)]
Well, there should be no implicit cast by the time you get to assembly.

##### **Chenyu** [[00:16:13](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=973)]
Yeah, so there's a cast somewhere that casts the first one into a Boole.

##### **Geohot** [[00:16:19](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=979)]
Yeah, yeah. My point is, so we have that. There's a. My

##### **Chenyu** [[00:16:23](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=983)]
point is,

##### **Geohot** [[00:16:23](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=983)]
there's a. My

##### **Chenyu** [[00:16:23](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=983)]
issue was basically, I need to define what happened. If currently the second shift is allowed to be an integer, then can it be weak? And if yes or no, then where do we normalize this? It's not very clear. And while doing that, I find some bugs in our existing shift.

##### **Geohot** [[00:16:41](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1001)]
Yeah, no, but my point is, I think the generic answer to this is kind of like, I have a thing before rangeify that will, like broadcasting now is enabled. But I have a thing that will insert all the explicit reshapes and expands that are required for the broadcast.

##### **Chenyu** [[00:16:58](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1018)]
That makes sense.

##### **Geohot** [[00:16:59](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1019)]
So I think it's the same thing with the D types, right? The D types are implicitly casted, and then before we actually load an assembly, it inserts all the explicit casts. Yeah,

##### **Chenyu** [[00:17:06](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1026)]
that's how I'm doing it now. And that's kind of where the first source of where it should be treated a similar way to the second source of shifts.

##### **Geohot** [[00:17:15](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1035)]
And there's a good argument to be made for that pipeline going both ways. You could imagine something that removes any casts, removes any explicit casts. That would be implicit, because then you don't need to overcast it everywhere in the rules. Yeah,

##### **Chenyu** [[00:17:28](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1048)]
so we certainly don't want to overcast it to a symbolic or in big graph. So the idea here is we should defer the week as late as possible. So keep mostly the as a week. So every symbolic rule will just work. Then there will be a path that really needs to. So if you still render this as a week,

##### **Chenyu** [[00:17:54](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1074)]
then you can do this as late as a renderer. Some backends need their language to specify the type of your const, then so be it. It's just in the renderer saying we need this. But in some case, we don't even really need that. And we can have the week through.

##### **Geohot** [[00:18:10](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1090)]
You could just put a rule in the renderer that looks like a const. Yeah, yes.

##### **Chenyu** [[00:18:13](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1093)]
And another place is when we materialize, say, we call the item on a const. It should just return that, because that's how people use it.

##### **Unknown** [[00:18:23](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1103)]
So

##### **Chenyu** [[00:18:23](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1103)]
there we also have another pass to an actual. For now, you just go to default int or default float when you materialize a weekly type.

##### **Geohot** [[00:18:33](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1113)]
Seems right. Yeah. So

##### **Chenyu** [[00:18:35](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1115)]
basically, I got all the rules figured out. Hopefully, we can get this this week.

##### **Geohot** [[00:18:42](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1122)]
That would be really nice.

##### **Geohot** [[00:18:46](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1126)]
Let's avoid.

##### **Geohot** [[00:18:49](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1129)]
Next

##### **Chenyu** [[00:18:49](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1129)]
is slice.

##### **Chrism** [[00:18:51](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1131)]
Yes. So.

##### **Chrism** [[00:18:53](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1133)]
The thing I was looking at was replacing slice instead with you submit your rather than having any buffer views at all, you would have just your base buffer and then all bunch of offsets into that base buffer. And that would define. So rather than say, we're going to have slice or we're going to have shrink, and then that's going to be corresponding to a buffer view. Instead, you pass a variable.

##### **Chrism** [[00:19:23](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1163)]
And then you pass a variable that becomes this.

##### **Unknown** [[00:19:25](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1165)]
And

##### **Chrism** [[00:19:25](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1165)]
then this allows you to have not required recompiling when you have different offsets, but at the same time, also, actually not necessarily to have the same effect as the shrink or as a slice.

##### **Chrism** [[00:19:43](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1183)]
The only issue with this is, for instance, we have a schedule linear, which expects that there's no variables in your. Like generated linear. But then this thing can arbitrarily add variables if there's any sort of review.

##### **Chrism** [[00:20:04](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1204)]
So I don't know. I mean, maybe there's no point in having scheduled linear, but.

##### **Geohot** [[00:20:10](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1210)]
I don't really know what having scheduled linear does, but I mean, yeah, the basic idea is that it turns out we never really needed a review in the first place. Most of the time, the reason buffer view exists is just to. Express the fact that this kernel can operate on multiple indexes into this buffer. It's the only reason it exists. So why not just pass that index in as a variable?

##### **Chrism** [[00:20:33](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1233)]
Yeah, anyway, it mostly works.

##### **Chrism** [[00:20:37](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1237)]
Yeah, there's also some stuff about like.

##### **Geohot** [[00:20:40](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1240)]
This

##### **Chrism** [[00:20:40](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1240)]
should

##### **Geohot** [[00:20:40](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1240)]
simplify a lot of stuff. Yes, yeah, this is great.

##### **Chrism** [[00:20:44](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1244)]
Yeah, I need to go in and I think there's some changes that I need to make to some code and stuff.

##### **Chrism** [[00:20:51](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1251)]
Because like. Yeah. Right now it's regressing open pilot.

##### **Chrism** [[00:20:57](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1257)]
And just because like this offset doesn't work with the item exactly why it's why the requested, but it doesn't work exactly with the. With the image.

##### **Chrism** [[00:21:07](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1267)]
But stuff, so I don't know exactly what the issue is there, but. Well,

##### **Geohot** [[00:21:10](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1270)]
that sounds like a bug to fix. Yeah, NimbleGen, I wonder if you have any thoughts on this like this would just get rid of buffer view entirely and you wouldn't have to deal with this in ATQ either. Like there's no more offset and buffers. Yeah.

##### **Geohot** [[00:21:25](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1285)]
Yeah. I mean,

##### **Nimlgen** [[00:21:28](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1288)]
sounds fine. If you need any help with scheduling, you can.

##### **Nimlgen** [[00:21:36](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1296)]
Yeah, I can help continue to do.

##### **Chrism** [[00:21:39](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1299)]
Yeah, yeah. Yeah, I'll let you know, especially if I ran into anything with ATQ2.

##### **Geohot** [[00:21:46](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1306)]
I can't wait to delete this crap from the jet like.

##### **Chrism** [[00:21:50](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1310)]
Well, that's all the other things that adds a little bit to the jet. Because now you have these extra variables that are not passed into the function and you need to track those variables.

##### **Geohot** [[00:21:59](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1319)]
Why are they not passed into the function?

##### **Chrism** [[00:22:01](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1321)]
Well, they're not passed by the user into the jitted Python function.

##### **Geohot** [[00:22:06](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1326)]
Well, yeah, but. Okay, fine. Yeah, I got it. That's fine.

##### **Chrism** [[00:22:10](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1330)]
Yeah,

##### **Chenyu** [[00:22:10](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1330)]
got

##### **Geohot** [[00:22:11](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1331)]
it. Still. Anyway. They're normal variables. They remove something from the from the back end. That's the best place to remove stuff from.

##### **Chrism** [[00:22:20](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1340)]
Yeah. Yeah. Yeah. Anyway. Yeah. I got to figure out what's going on with the image stuff. And I heard like a couple other things, but it does look like it should all work out nicely.

##### **Geohot** [[00:22:29](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1349)]
No more dealing with CL not supporting offsets.

##### **Chrism** [[00:22:32](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1352)]
Yes. Yeah. That'll be nice. And WebGPU. And

##### **Geohot** [[00:22:36](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1356)]
WebGPU.

##### **Chrism** [[00:22:38](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1358)]
Yeah. And then the other thing I was looking at is trying to get USB4 to work with the Chestnut.

##### **Chrism** [[00:22:45](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1365)]
So right now it obviously works for the stock firmware and that's what we run in CI. But we wanted to work with our custom firmware as well. Yeah.

##### **Chrism** [[00:22:53](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1373)]
So we're running this on the Mac. So there is stuff merged that supposedly does this and we've gotten it to work on one computer

##### **Chrism** [[00:22:59](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1379)]
and haven't gotten to work on any other computer.

##### **Chrism** [[00:23:01](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1381)]
So I just need to have some time looking at that and figure out what's going on.

##### **Geohot** [[00:23:07](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1387)]
I've never gotten it to work on my Mac.

##### **Geohot** [[00:23:12](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1392)]
Yeah. Do you have the emulator running? Yeah.

##### **Chrism** [[00:23:15](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1395)]
Yeah, the emulator.

##### **Geohot** [[00:23:16](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1396)]
And you're coming up on four or only three?

##### **Chrism** [[00:23:18](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1398)]
I haven't tried yet. I do have the board with the. Do

##### **Geohot** [[00:23:21](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1401)]
you have the board with the power on it? Yeah.

##### **Geohot** [[00:23:27](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1407)]
Yeah.

##### **Qazalin** [[00:23:28](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1408)]
Yeah, yeah.

##### **Geohot** [[00:23:31](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1411)]
Sounds

##### **Chenyu** [[00:23:31](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1411)]
good. We can talk more about that when we discuss about Comma happiness. For now, let's move on to Lama's meet.

##### **Qazalin** [[00:23:43](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1423)]
I can't share this is the pink line is this week. Green line is last week. week so oh

##### **Geohot** [[00:23:54](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1434)]
in general uh yeah

##### **Qazalin** [[00:23:57](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1437)]
in general cool

##### **Geohot** [[00:23:59](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1439)]
that looks faster so our best time is the two hours 26 minute two

##### **Qazalin** [[00:24:04](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1444)]
hours 26 and i think it matches rcp but yeah great

##### **Geohot** [[00:24:11](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1451)]
um um what are still the things making it slower than amd um

##### **Qazalin** [[00:24:19](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1459)]
it's actually 1.28 so it's the same as amd because of the power issue it jumps up to 1.44 seconds have you

##### **Geohot** [[00:24:34](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1474)]
looked at amds does amds manage to stay like the same as the first step the whole time i

##### **Qazalin** [[00:24:41](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1481)]
can try their run i think this is a hardware issue though so i don't think but i'll try it if

##### **Chenyu** [[00:24:48](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1488)]
it's easy if you run their stuff and they show a similar pattern then we can say yes it's hardware it's likely a hardware and air issue but if yeah that'll be good it's fast like this is something else yeah

##### **Geohot** [[00:25:01](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1501)]
that's we should try their run on our hardware if that's easy then that just says that just answers this question completely

##### **Qazalin** [[00:25:07](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1507)]
yeah i'll do that tomorrow great

##### **Geohot** [[00:25:10](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1510)]
i mean is it possible to run on a hardware and then run on a hardware and then run on is there anything else regardless of even like as fast as amd is there anything else still making uh our run slow oh

##### **Qazalin** [[00:25:19](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1519)]
yes so um i'm sure another chart because this is so interesting to see that

##### **Qazalin** [[00:25:29](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1529)]
this is our run versus what we submitted with so this is this has been like all the bug fixes to especially the spikiness getting that done right so right now our problem is uh Our problem is stalls. We stall 100 milliseconds per device. So that would get us to, if I can fix the stalls, that would get us to

##### **Geohot** [[00:25:54](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1554)]
B2MD. I'll

##### **Qazalin** [[00:25:57](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1557)]
share the white space. These are the white spaces in our backward pass.

##### **Geohot** [[00:26:03](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1563)]
How much of this is upstreamed into master?

##### **Qazalin** [[00:26:08](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1568)]
How much of this is upstreamed? I'm steadily upstreaming. I'm going to be honest. I love the stuff with CodexLog. I need to really go through it one by one and test it and properly figure out, understand it.

##### **Geohot** [[00:26:22](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1582)]
I think we're good on speed for now. I think what we have to do is get this stuff upstreamed.

##### **Qazalin** [[00:26:29](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1589)]
Yeah, I'll do that.

##### **Geohot** [[00:26:31](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1591)]
Yeah, so I wouldn't even worry about that. I see what you mean by the stalls, but I wouldn't worry about that for now. I think we just have to figure out how to tastefully get these things upstreamed. It's really easy to overextend yourself with Codex on things that can't, possibly work. Yes, they're fast, but,

##### **Geohot** [[00:26:45](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1605)]
you know, they're a slop.

##### **Qazalin** [[00:26:47](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1607)]
Yeah. Yeah, I think I got it like a proper workflow with Codex. It's still not really properly able to

##### **Qazalin** [[00:26:57](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1617)]
independently figure out what the fixes should be, but if I give it an idea for a fix, it can implement it very easily and verify that it did the right thing.

##### **Qazalin** [[00:27:08](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1628)]
So, that has been my experience with it.

##### **Qazalin** [[00:27:12](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1632)]
But yeah, this stuff is,

##### **Qazalin** [[00:27:14](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1634)]
once the stalls are fixed.

##### **Geohot** [[00:27:17](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1637)]
Yeah, I mean, we still have a big cluster. Oh, I guess that's,

##### **Geohot** [[00:27:24](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1644)]
that's pretty zoomed in now. And that's on the backwards pass. Okay, so you're on the backwards pass. You are sending things separately. They're just as like those weird little stalls in the compute for some reason.

##### **Qazalin** [[00:27:37](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1657)]
It's because some compute, so the overduce and line, my branch doesn't require the CAD kernel anymore. The CAD is expressed as a bunch of slices. The problem is that in the end, you have to like add

##### **Qazalin** [[00:27:54](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1674)]
the things that come from multiple GPUs. I

##### **Geohot** [[00:27:57](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1677)]
understand. So

##### **Qazalin** [[00:27:58](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1678)]
it waits on the STMA.

##### **Geohot** [[00:28:01](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1681)]
Yeah, I mean, we may just be able, I wonder, when do you actually need them added by? Not to like way later, right? I mean, maybe we can just change the order.

##### **Qazalin** [[00:28:10](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1690)]
Yeah, yeah. That's kind of.

##### **Geohot** [[00:28:13](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1693)]
In theory, you could do all these ads like way later.

##### **Geohot** [[00:28:17](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1697)]
I guess you got to deal a little bit with RAM, but.

##### **Qazalin** [[00:28:21](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1701)]
Yeah. I think that's. I think it's right there. It doesn't work, but I can look at it. Yeah. It's almost short.

##### **Geohot** [[00:28:30](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1710)]
Let's just focus on simplification first. But yeah, no, I mean, I see why this is happening, right? Like if you think about it, it's doing the STMA and then you have a kernel on the same. I understand why you asked for a second compute, but in general, the solution is never a second compute queue. The solution is just better ordering on the compute queue you have. If you imagine deferring all those ad kernels to the next layer, it would fix this.

##### **Qazalin** [[00:28:59](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1739)]
At the cost of more memory. Yeah.

##### **Geohot** [[00:29:02](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1742)]
At the cost of one layer more memory, which is super negligible. Yeah.

##### **Geohot** [[00:29:08](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1748)]
That's right. But for now, yeah. Yeah. Yeah. Focus on merging. This is a, this is a generic scheduler problem that we should fix in some beautiful generic way.

##### **Geohot** [[00:29:19](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1759)]
Uh, but great. No, I'm glad it's that. I mean, that's very understandable what that is, why that's happening. Um, and the solution is not even the deletion of the ad kernels. The solution is the deferring of the ad kernels after,

##### **Geohot** [[00:29:32](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1772)]
uh,

##### **Geohot** [[00:29:36](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1776)]
after the layer.

##### **Geohot** [[00:29:42](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1782)]
Yeah. I bet there's like a one line rule to fix this, but

##### **Geohot** [[00:29:50](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1790)]
I look at it. I would doubt the LLMs could find it, but, uh, I, I think that there, like there is in theory, some idea of like,

##### **Geohot** [[00:29:59](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1799)]
the, the SDMA thing is a separate compute queue already.

##### **Geohot** [[00:30:06](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1806)]
Uh,

##### **Geohot** [[00:30:07](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1807)]
understanding that you have to whip, whatever. Um, but cool. Yeah. Yeah. Let's get this done. I'm upstreamed, uh, looking pretty good. Uh, and if you get a chance, if it's easy, just have an LLM replicate the AMD,

##### **Geohot** [[00:30:20](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1820)]
uh, run and see if we can get like just kernel times out of it.

##### **Chenyu** [[00:30:26](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1826)]
A

##### **Geohot** [[00:30:26](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1826)]
step times. I mean, sorry, or even just plot their step times from the run, because I don't know if this thermal throttling is entirely fixable.

##### **Geohot** [[00:30:36](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1836)]
Like, I don't know if putting cold air in would entirely fix this, or some of it is limited by, uh, if you're limited by the package transfer, then nothing fixes this,

##### **Geohot** [[00:30:51](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1851)]
right? Like, like there can be different limitations in thermal systems. If your limitation is below what you can do, right? Like your limitation is imagine it's the limitation of the Silicon die to the aluminum package. Even if you had perfect cooling on that aluminum package, I wonder if you could, uh, pull the heat off. I mean, there's a chance you can't, but

##### **Geohot** [[00:31:21](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1881)]
what's good.

##### **Geohot** [[00:31:26](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1886)]
Okay. Uh, so next. Maybe here, SA is we

##### **Wozeparrot** [[00:31:34](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1894)]
still have convergence issues.

##### **Wozeparrot** [[00:31:37](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1897)]
My whole call this week was making it faster were, a lot faster than the beginning of the week.

##### **Wozeparrot** [[00:31:44](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1904)]
Or at mass adalah, 2.4 seconds of step now.

##### **Geohot** [[00:31:50](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1910)]
What's the current step time and how long would it take?

##### **Wozeparrot** [[00:31:58](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1918)]
A full run now should take about 10 hours.

##### **Geohot** [[00:32:02](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1922)]
A

##### **Wozeparrot** [[00:32:02](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1922)]
lot better than 30 hours.

##### **Geohot** [[00:32:10](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1930)]
10 hours. It says that we're getting 19% MFU. Is that true?

##### **Wozeparrot** [[00:32:17](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1937)]
MFU is just copied from Lama, so it's not correct because not all the experts are active per token.

##### **Geohot** [[00:32:24](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1944)]
I understand.

##### **Geohot** [[00:32:26](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1946)]
Alright, so it should be 10 hours, but we have convergence issues.

##### **Nimlgen** [[00:32:34](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1954)]
Yes.

##### **Nimlgen** [[00:32:36](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1956)]
It's

##### **Wozeparrot** [[00:32:37](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1957)]
also very hard to pull the implementation from this because the reference implementation is

##### **Wozeparrot** [[00:32:45](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1965)]
very hard. And you do have access to the working group notes.

##### **Geohot** [[00:32:51](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1971)]
I

##### **Wozeparrot** [[00:32:52](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1972)]
have no idea

##### **Geohot** [[00:32:52](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1972)]
what that is, but

##### **Chenyu** [[00:32:53](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1973)]
do you think you can train, say, 20% longer without converge?

##### **Geohot** [[00:33:02](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1982)]
It's like I know it's off, but is it off by a lot or just a little bit?

##### **Wozeparrot** [[00:33:08](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1988)]
It's off by a decent amount.

##### **Wozeparrot** [[00:33:11](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1991)]
It's just consistently to reference off by

##### **Unknown** [[00:33:14](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1994)]
a lot. off by

##### **Wozeparrot** [[00:33:14](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=1994)]
0.3 on the loss.

##### **Geohot** [[00:33:21](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2001)]
0.3 seems like a lot.

##### **Geohot** [[00:33:25](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2005)]
0.3

##### **Wozeparrot** [[00:33:26](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2006)]
level of complexity? Yeah.

##### **Chenyu** [[00:33:30](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2010)]
Because we previously also have had this issue even while we were training ResNet or BERT. We initially had converging issue and we were like, and we're going to be and say, okay, 20% longer. It converges. And we later realize what the

##### **Wozeparrot** [[00:33:47](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2027)]
issue is. I don't really want to do that. It should match what other people are submitting for.

##### **Geohot** [[00:33:54](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2034)]
Are you confident that we don't have some like usually this is some like D type issue, like some like Max is in the wrong D type or something?

##### **Wozeparrot** [[00:34:02](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2042)]
Yeah, I've been looking into that. And from this, I actually found out for Lama, our rope is in the wrong D type.

##### **Geohot** [[00:34:10](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2050)]
In what way?

##### **Wozeparrot** [[00:34:13](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2053)]
It's not flow 32.

##### **Wozeparrot** [[00:34:15](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2055)]
The rope frequencies are done in D plus 16.

##### **Qazalin** [[00:34:23](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2063)]
I see. Coco?

##### **Wozeparrot** [[00:34:27](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2067)]
It doesn't seem to affect that much. But what I have noticed is that none of the submitted runs match the reference implementation.

##### **Chenyu** [[00:34:38](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2078)]
Yeah, because you can use whatever D types. And I thought people really dive into this. It's not clearly, I have a very good method in, especially for this model, because they squeeze it in. Need to change your rule.

##### **Wozeparrot** [[00:34:51](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2091)]
They don't just match in not D type. The model architectures just don't match

##### **Wozeparrot** [[00:34:56](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2096)]
between the reference and what people are submitting.

##### **Geohot** [[00:35:01](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2101)]
Why? What doesn't match?

##### **Wozeparrot** [[00:35:04](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2104)]
The reference is like this weird GPD OSS hybrid that uses the deep seek V2 config. And it has a lot of different,

##### **Wozeparrot** [[00:35:14](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2114)]
it has yarn thrown in. It has no attention sinks.

##### **Geohot** [[00:35:22](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2122)]
So are we matching the reference or are we matching other people's submission?

##### **Wozeparrot** [[00:35:26](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2126)]
We match other people's submissions.

##### **Geohot** [[00:35:29](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2129)]
And I think we have to.

##### **Wozeparrot** [[00:35:30](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2130)]
Yeah.

##### **Geohot** [[00:35:31](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2131)]
Yeah.

##### **Chenyu** [[00:35:33](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2133)]
I think let's just say for, I know this particular model, when they were developing the benchmark, it was a mess. So, we certainly want to match other people's implementation. If you feel unclear, you can ask like, why is it different? I thought it would give you a useful answer, but it's nice to have a record saying that we, we are aware that's different and our submission match other people's submission. Have

##### **Geohot** [[00:36:00](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2160)]
we evaluated it with the real GPD OSS 20B?

##### **Wozeparrot** [[00:36:05](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2165)]
Have not just because the model doesn't exactly match GPD OSS 20B.

##### **Geohot** [[00:36:13](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2173)]
So does the reference, does anything match the real GPD OSS 20B?

##### **Wozeparrot** [[00:36:18](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2178)]
Not fully.

##### **Qazalin** [[00:36:22](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2182)]
Yeah.

##### **Geohot** [[00:36:27](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2187)]
I

##### **Chenyu** [[00:36:27](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2187)]
mean, either way. I mean, it sounds like the best next thing is run some of the benchmark on our machine to get the model and use that. But that's also sounds, sounds, it's a waste of time.

##### **Geohot** [[00:36:42](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2202)]
No, I don't think it's a waste of time. I think we should just match what's submitted. Like that's the best we can do.

##### **Chenyu** [[00:36:47](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2207)]
Yeah, but what does it even mean to match what's submitted?

##### **Geohot** [[00:36:50](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2210)]
There's things submitted that were accepted onto the MLPerf leaderboard and they converge and ours doesn't. So we should fix them.

##### **Chenyu** [[00:36:58](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2218)]
Yeah, that's fair.

##### **Geohot** [[00:36:59](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2219)]
Right. Like if we just match what's submitted, it's like, okay, you want to go back and invalidate the old ones or you want to, you know, let ours in. That's your choices.

##### **Chenyu** [[00:37:09](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2229)]
Yeah. I mean, let's just annoying, you know, sounds like now you really need

##### **Chrism** [[00:37:14](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2234)]
to make sure it matches other people's reference,

##### **Chenyu** [[00:37:17](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2237)]
which is supposed to be the thing that everybody at chat too.

##### **Geohot** [[00:37:21](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2241)]
Okay. I think writing this up and I'm how responsive are you? How the organizers about stuff like this? You think they won't give you a

##### **Wozeparrot** [[00:37:28](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2248)]
slide? I'm probably going to open an issue upstream. I think, I

##### **Chenyu** [[00:37:32](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2252)]
think it's just nice to ask, especially we are still early in this cycle. To say, we found the discrepancy between the two. And we just want to make sure everyone is on board with this and not saying later saying, okay, let's invalidate everyone's wrong.

##### **Geohot** [[00:37:50](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2270)]
Cool.

##### **Wozeparrot** [[00:37:50](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2270)]
I was asking for the training working. If you have access to the training working group, like meeting notes, if this was brought up at all during those.

##### **Geohot** [[00:38:02](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2282)]
Oh, you don't have access. I can, I can look it up. Okay.

##### **Unknown** [[00:38:06](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2286)]
So, so,

##### **Geohot** [[00:38:09](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2289)]
Thank

##### **Chenyu** [[00:38:10](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2290)]
you. Let's, let's discuss this. It was a meal PM or in a channel is fine. Let me know what you need. I think it's just nice to have a record. We should still continue with what we are doing, like other people for all. Just making sure our submission would be accepted.

##### **Chenyu** [[00:38:27](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2307)]
Oh yeah.

##### **Geohot** [[00:38:29](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2309)]
I don't know why they could. How's a BKC thing.

##### **Wozeparrot** [[00:38:34](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2314)]
I got the Dropbox link. Oh, I will do that tomorrow.

##### **Geohot** [[00:38:42](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2322)]
It's just the firmware that

##### **Chenyu** [[00:38:43](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2323)]
will fix the tiny MD? Hopefully.

##### **Geohot** [[00:38:47](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2327)]
Hopefully. It's some unreleased.

##### **Geohot** [[00:38:50](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2330)]
Great.

##### **Geohot** [[00:38:52](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2332)]
They didn't explain the issue at all. They just said, install this unreleased branched firmware and maybe it'll fix it.

##### **Chenyu** [[00:38:59](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2339)]
If you still owe your data.

##### **Chenyu** [[00:39:03](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2343)]
They

##### **Geohot** [[00:39:04](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2344)]
sent us $40,000. So, you know, I have my data for way less.

##### **Chenyu** [[00:39:10](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2350)]
Sounds good. I'll get those machines.

##### **Chenyu** [[00:39:14](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2354)]
They did fix the issue. Otherwise, it's annoying that everyone needs to cram on one machine.

##### **Geohot** [[00:39:19](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2359)]
That issue. And then also, do you see any issues with switching Lama to MXFP4?

##### **Geohot** [[00:39:28](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2368)]
They used MXFP4 in their runs?

##### **Wozeparrot** [[00:39:34](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2374)]
As far as I know, AMD didn't submit, but one of their partners did.

##### **Geohot** [[00:39:39](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2379)]
The AMD run is... I don't know if we're already matching that, but the AMD run is...

##### **Geohot** [[00:39:49](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2389)]
Fast. Very fast.

##### **Geohot** [[00:39:53](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2393)]
In the latest round. So you say that's not MXFP4?

##### **Wozeparrot** [[00:39:58](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2398)]
I can check.

##### **Wozeparrot** [[00:40:01](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2401)]
And we had this whole D-type discussion during the review session.

##### **Geohot** [[00:40:12](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2412)]
Yeah, I mean, it's not like their partners are that much faster.

##### **Wozeparrot** [[00:40:16](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2416)]
And it's possible they're using MXFP4.

##### **Geohot** [[00:40:21](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2421)]
I just want to figure out what these runs are using.

##### **Unknown** [[00:40:27](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2427)]
Yeah.

##### **Wozeparrot** [[00:40:33](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2433)]
Yeah, MXFP4.

##### **Geohot** [[00:40:35](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2435)]
That's MXFP4. Wait, so our step time of 1.28 is to match the FP8 or the FP4 one?

##### **Geohot** [[00:40:45](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2445)]
FP8. Yeah. That's to match their FPA time. But the new times are FP4 times.

##### **Qazalin** [[00:40:51](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2451)]
New times are MXFP4.

##### **Geohot** [[00:40:53](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2453)]
MXFP4. Okay, cool. And then do you have any ideas how hard it would be to switch?

##### **Geohot** [[00:40:58](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2458)]
It's just the general switch. I have not worked.

##### **Wozeparrot** [[00:41:01](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2461)]
Yeah, we would need a gem. HipKittens doesn't have any infrastructure right now at all for MXFP4.

##### **Geohot** [[00:41:08](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2468)]
We're using a HipKittens gem?

##### **Qazalin** [[00:41:11](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2471)]
We are using HipKittens, yes.

##### **Geohot** [[00:41:14](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2474)]
Got it.

##### **Qazalin** [[00:41:14](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2474)]
I can look into switching it. Not sure.

##### **Geohot** [[00:41:17](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2477)]
This is not the... Yeah, let's just make sure we upstream the stuff we have.

##### **Geohot** [[00:41:25](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2485)]
This is the kind of thing where the longer we wait, the easier it will get. Because HipKittens will just do it for us.

##### **Geohot** [[00:41:33](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2493)]
So that's good. And we want to LAMD that we're doing GPT -OSS in FP8, get them to give us times for FP8, and then switch to FP4. Hey,

##### **Nimlgen** [[00:41:43](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2503)]
we did it fast.

##### **Geohot** [[00:41:46](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2506)]
Cool, yeah. It seems like there's no infrastructure for it yet. No rush on this. Let's just beat their FP8 time.

##### **Geohot** [[00:41:54](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2514)]
Okay. Are we going to fix the coverage issue?

##### **Wozeparrot** [[00:42:00](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2520)]
I've basically been shipping random

##### **Geohot** [[00:42:04](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2524)]
parts and seeing if they match.

##### **Wozeparrot** [[00:42:15](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2535)]
Right now, the only part that doesn't match reference

##### **Geohot** [[00:42:19](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2539)]
is Flash Attempt.

##### **Qazalin** [[00:42:27](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2547)]
Yeah.

##### **Geohot** [[00:42:29](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2549)]
I can totally believe that the convergence is some numerical stability issue in Flash Attention.

##### **Qazalin** [[00:42:38](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2558)]
I

##### **Geohot** [[00:42:39](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2559)]
see. Okay.

##### **Geohot** [[00:42:49](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2569)]
Sounds good.

##### **Geohot** [[00:42:52](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2572)]
I don't know what to

##### **Chenyu** [[00:42:53](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2573)]
add, but it sounds good. Let's get something, Trent.

##### **Chenyu** [[00:42:56](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2576)]
Yeah. At

##### **Geohot** [[00:42:57](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2577)]
least it's a more reasonable cycle time.

##### **Chenyu** [[00:42:59](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2579)]
10 hours. Yeah. It's a lot better than 12 days.

##### **Geohot** [[00:43:05](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2585)]
Oh, yeah. The LAMD of 4 or 5 days. Yeah. I've got to get on them about that contract. But we're definitely getting a GPT-OSS contract. They promised to me by email.

##### **Chenyu** [[00:43:17](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2597)]
It's also nice to prepare for MOE training now, since everyone is converging on big MOE training. Yes.

##### **Geohot** [[00:43:25](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2605)]
I mean, I kind of like the idea of us being able to not train from scratch, but we distilled Kimmy into a...

##### **Geohot** [[00:43:33](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2613)]
I think it's like distilled Kimmy into Quinn. How much better would Quinn get?

##### **Chenyu** [[00:43:37](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2617)]
We would know after the new Quinn

##### **Geohot** [[00:43:40](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2620)]
is out. I bet if you did... Well, but the new Quinn is going to be big, right? Like, I bet if you just literally took the little Quinn and distilled Kimmy into it, it would get a lot better.

##### **Wozeparrot** [[00:43:48](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2628)]
Wait, do you think they're not going to release any small models? They would have a smaller one. No,

##### **Geohot** [[00:43:53](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2633)]
they will, but they're so Quinn-y. I don't want it to be Quinn-y.

##### **Chenyu** [[00:43:59](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2639)]
And you can fine-tune from there.

##### **Geohot** [[00:44:02](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2642)]
Yeah, yeah, yeah, yeah. Fine-tune from there. Let them do the pre-train, but I don't want them to behave like Quinns. I want them to behave like...

##### **Geohot** [[00:44:10](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2650)]
Or maybe it's better to distill GLM. GLM is so good. Good size.

##### **Geohot** [[00:44:16](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2656)]
Yeah. Okay.

##### **Geohot** [[00:44:18](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2658)]
Oh, sounds good. GLM knows how to listen. Quinn

##### **Qazalin** [[00:44:21](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2661)]
doesn't know how to listen.

##### **Geohot** [[00:44:22](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2662)]
Yeah.

##### **Geohot** [[00:44:25](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2665)]
Okay, sounds good. Moving on.

##### **Geohot** [[00:44:34](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2674)]
Start with...

##### **Chenyu** [[00:44:35](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2675)]
What's the higher training block?

##### **Flata** [[00:44:39](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2679)]
Yeah, I think I re-based recently, and it ran out of memory, but then I started using the SunTree type BFloat 16, and it did fix it.

##### **Flata** [[00:44:50](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2690)]
But it's definitely a lot longer. It's taking a lot longer to train. So what I did was that I added the free intermediate for now, just to kind of disable it, free some memory space. And then hopefully I can get back to updating the config for the correctness one.

##### **Geohot** [[00:45:06](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2706)]
There's probably a bug. If changing some deep type shouldn't change your memory usage. If it is, there's probably some bug.

##### **Chenyu** [[00:45:14](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2714)]
It also affects your or reduced D type, right? Yeah. So it's like the things you transfer between GPUs.

##### **Geohot** [[00:45:24](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2724)]
Oh, you're right. So some by itself shouldn't... On multi, it will affect it. On not multi, it won't. Yeah. I don't

##### **Chenyu** [[00:45:32](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2732)]
know what extent it is, but it's plausible.

##### **Geohot** [[00:45:34](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2734)]
Yeah. I mean, you almost want that to be two different D types.

##### **Geohot** [[00:45:39](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2739)]
Right? Like you could imagine doing your some D type where it's fast on your local GPU in...

##### **Geohot** [[00:45:45](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2745)]
32 and then... Yeah. We certainly support

##### **Chenyu** [[00:45:48](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2748)]
that. You can write that in your or reduced code.

##### **Geohot** [[00:45:52](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2752)]
Yeah. Yeah. Okay. Sounds good. Oh, but then this will fix the WAME issue, right? Like the reason it got slow is because we don't have WAME that's summoned to BF16.

##### **Geohot** [[00:46:02](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2762)]
You might be able to just fix that. Like maybe if you're just, maybe you can just add it. It's like three lines. But if you can't, the problem with the some D type is not that the some D type in the kernel needs to change. You probably want to keep that flow 32. You just want the all reduced D type to be the smaller one. So you use half the RAM for that and half the copy bandwidth.

##### **Chenyu** [[00:46:24](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2784)]
Discuss with LOM. We might already have something that look like that. If all your memory saving is coming from all reduce, then I think you can just add a cast or two in all reduce code and that probably would just work.

##### **Flata** [[00:46:38](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2798)]
Okay. Sounds good. I can take a look.

##### **B1tg** [[00:46:40](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2800)]
Cool.

##### **B1tg** [[00:46:43](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2803)]
What else do we have here?

##### **Geohot** [[00:46:44](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2804)]
We have an LOM. Any progress B1TG or I guess Elliot's not here, but on running Kimmy in LLM?

##### **Qazalin** [[00:47:02](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2822)]
Hello? Hi.

##### **B1tg** [[00:47:06](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2826)]
It was a LLM shot PR few weeks ago.

##### **Geohot** [[00:47:13](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2833)]
Is there a PR that I got a review for this? I think it's pretty good.

##### **B1tg** [[00:47:19](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2839)]
I didn't update it for a while.

##### **Geohot** [[00:47:23](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2843)]
Oh, but are we getting 100 tokens per second?

##### **Unknown** [[00:47:31](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2851)]
Oh,

##### **Geohot** [[00:47:32](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2852)]
you have.

##### **B1tg** [[00:47:35](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2855)]
It's basically only implement the tensor parameterized shard.

##### **Geohot** [[00:47:47](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2867)]
Got it. Yeah. So what we got to get to for the bounty is 100 tokens per second. Tensor parallel didn't just make it that fast.

##### **Geohot** [[00:48:01](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2881)]
And then also how much of this can be broken out? Like I see there's now a simplify inside the reshape.

##### **Geohot** [[00:48:10](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2890)]
What's that helping with? Why do we need it?

##### **Geohot** [[00:48:17](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2897)]
I'm talking about like it's simplify. But yeah, I mean, that bounty is still yours. If you can get this stuff upstreamed and it hits over 100 tokens per second and decode.

##### **B1tg** [[00:48:31](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2911)]
It seems we didn't favor Beam anymore.

##### **B1tg** [[00:48:39](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2919)]
So maybe we need to.

##### **Chenyu** [[00:48:43](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2923)]
I

##### **Geohot** [[00:48:43](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2923)]
mean, you're welcome to use Beam. 100 tokens per second is really very conservative. If token parallel is working. If tensor parallel is working.

##### **B1tg** [[00:48:55](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2935)]
I hear some issue that the symbolic box cause the Beam can find the faster kernel.

##### **Geohot** [[00:49:08](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2948)]
Let's see. Yeah. Yeah. This is this is the kind of stuff we got to.

##### **Geohot** [[00:49:15](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2955)]
We got to fix. But also everything should be usable in open code now too. So I merged all the stuff into LLM so you can actually test this in open code.

##### **B1tg** [[00:49:25](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2965)]
Okay.

##### **Geohot** [[00:49:26](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2966)]
Tool calling works.

##### **Geohot** [[00:49:30](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2970)]
Yeah. I have a few other quality of life improvements to LLM. But yeah.

##### **Chenyu** [[00:49:34](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2974)]
Cool. Bounty is still yours. If we

##### **Geohot** [[00:49:37](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2977)]
can get that stuff merged and it meets the performance target. Yeah.

##### **Geohot** [[00:49:44](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2984)]
I'm not sure what we're going to do with this one. I think it's going to be

##### **Chrism** [[00:49:50](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2990)]
interesting. I'm not sure. I'm not sure. Yeah.

##### **Reina** [[00:49:52](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2992)]
I'm not sure. I'm not sure.

##### **Qazalin** [[00:49:56](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2996)]
I think

##### **Chrism** [[00:49:56](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2996)]
we're going to

##### **Qazalin** [[00:49:56](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2996)]
have

##### **Chrism** [[00:49:56](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2996)]
to do that.

##### **Qazalin** [[00:49:57](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=2997)]
Yeah.

##### **Geohot** [[00:50:00](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3000)]
I'm excited to get that merged.

##### **Geohot** [[00:50:07](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3007)]
I'll check out your branch and I'll have a slide in my presentation out with the exit six assembly back and we will have the RDNA 31.

##### **Geohot** [[00:50:16](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3016)]
That'd be awesome. Okay.

##### **B1tg** [[00:50:18](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3018)]
That's good. Anything from Comma?

##### **Geohot** [[00:50:21](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3021)]
I don't think so.

##### **Chrism** [[00:50:23](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3023)]
So excited about your CPU.

##### **Chenyu** [[00:50:26](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3026)]
Yeah. Yeah. Yeah. I'm happy with big model.

##### **Chenyu** [[00:50:30](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3030)]
I haven't been

##### **Chrism** [[00:50:31](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3031)]
driving on it. Oh, I mean, in terms of support.

##### **Chrism** [[00:50:35](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3035)]
Oh, as far as I know. Yeah. I

##### **Geohot** [[00:50:38](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3038)]
think that isn't the problem with big model. Big model is the problem with big model.

##### **Chenyu** [[00:50:43](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3043)]
Hey, turns out we're another bottleneck.

##### **Geohot** [[00:50:45](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3045)]
Yeah.

##### **Chenyu** [[00:50:51](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3051)]
I think that's pretty much it. Unless you have other closing work.

##### **Geohot** [[00:50:56](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3056)]
I also have a question.

##### **Geohot** [[00:51:02](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3062)]
I think that in the right instance we did 20,

##### **Chrism** [[00:51:09](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3069)]
onyx free update with the summary

##### **Unknown** [[00:51:17](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3077)]
command You want

##### **Chrism** [[00:51:17](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3077)]
it to speed

##### **Unknown** [[00:51:18](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3078)]
up coping? The thing he's thorough

##### **Chrism** [[00:51:18](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3078)]
about is communication so that bits of the same

##### **Geohot** [[00:51:21](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3081)]
codec being developed is just right here. Yeah. Qualcomm compiler.

##### **Geohot** [[00:51:28](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3088)]
Nor depicts inefficiency in the Qualcomm compiler. No, the Codex thing didn't do any onyx stitching.

##### **Geohot** [[00:51:35](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3095)]
Also, that PR that I merged this morning was interesting. The one that adds those detaches.

##### **Chenyu** [[00:51:43](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3103)]
Yeah, I have a prototype for that.

##### **Geohot** [[00:51:46](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3106)]
Oh, to make it automatic?

##### **Chenyu** [[00:51:47](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3107)]
Yeah.

##### **Geohot** [[00:51:49](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3109)]
Do you know how to do it?

##### **Chenyu** [[00:51:52](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3112)]
Yes, it's one of my old

##### **Chenyu** [[00:51:55](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3115)]
changes, and you also commented on that.

##### **Geohot** [[00:51:57](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3117)]
Yeah, I commented on your old change asking the same question. I'm always asking this question. I'm like, why do we need to make these things explicit? It should be able to find it, but either way, I'm happy to merge that because that's a clean...

##### **Chenyu** [[00:52:06](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3126)]
I think this is possible. If anyone is interested, you can read my old change. It's in a similar shape, except that we're probably going to rewrite RangeRefine at some point, so I didn't really pursue that.

##### **Chenyu** [[00:52:20](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3140)]
Yeah.

##### **Geohot** [[00:52:23](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3143)]
But yeah. Little change.

##### **Chenyu** [[00:52:25](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3145)]
Yeah. And I think generally for other kind of change, it's nice that people are using agents to find improvements or speed up or things.

##### **Chenyu** [[00:52:38](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3158)]
Just you need to polish more in terms of the PR you are opening.

##### **Geohot** [[00:52:43](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3163)]
Yeah.

##### **Chenyu** [[00:52:43](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3163)]
A lot of times, I understand the intention was nice, but as a maintainer, it's also impossible for us to say, okay, this is bad because of x, y, z reasons.

##### **Chrism** [[00:52:55](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3175)]
We don't have time for that,

##### **Geohot** [[00:52:57](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3177)]
really. It's really, really hard. Unless it's like a one-line change that the agent found, it's very, very hard to ask, is this good or not? Because the process that produced it was inhuman, right? Like, I don't know.

##### **Geohot** [[00:53:19](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3199)]
It's broken in a sense of this wasn't even the right place to look. But it does something and it speeds it up. But it's like, do we want this? I don't know.

##### **Geohot** [[00:53:32](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3212)]
Um, yeah, no, that's why I like even if even if this PR that I just linked was found by an agent, I don't care.

##### **Geohot** [[00:53:42](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3222)]
Um, so I don't know why there's those tensor manual seeds there. They should have complained about those.

##### **Chenyu** [[00:53:50](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3230)]
Oh, I have no idea. Yeah. Agent. Crap.

##### **Chenyu** [[00:53:58](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3238)]
I mean, this is a little part of this kind of hard to communicate as an open source project, because as a mentor, we certainly know a lot more for what things should be and what things already there. Well, is it? Is it?

##### **Geohot** [[00:54:12](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3252)]
Is it? Is it? Agent crap? Or because, like, did anyone think through why you actually need those manual seeds? You don't. It doesn't even check the output.

##### **Geohot** [[00:54:20](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3260)]
Don't even need a. Grand end there. I don't think. I don't think run linear does. Anything. I think you could just literally use empty. You know, T.

##### **Chenyu** [[00:54:27](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3267)]
Yeah. So it's the same thing. Yes, we probably did put some crap there and that sees into your agents like generates F. But the solution is to fix the crabs with pudding.

##### **Geohot** [[00:54:38](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3278)]
Exactly. Exactly. If there's a leak in your bathroom ceiling and you put a bucket under it and you find yourself building an automatic bucket emptying system, it's time to fix the leak in your bathroom ceiling.

##### **Chenyu** [[00:54:51](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3291)]
Yeah, this pattern is certainly true. There are. A lot of contiguous that does nothing and a lot of. Escalade literally does nothing.

##### **Geohot** [[00:55:01](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3301)]
If

##### **Chenyu** [[00:55:01](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3301)]
you're interested, you can look into deleting or trim those things that will also be valuable because those are like easily adjusted by why it's

##### **Geohot** [[00:55:10](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3310)]
good for the project,

##### **Chenyu** [[00:55:10](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3310)]
right?

##### **Geohot** [[00:55:11](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3311)]
It's years who I would hire immediately at tiny grad. If you can take my codec slop PRC, I did the fun part with the AI slop and you take the slop PR and you clean it up and make it mergeable.

##### **Geohot** [[00:55:25](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3325)]
That's a valuable employee.

##### **Geohot** [[00:55:27](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3327)]
And you're like, that's that's what we want to hire. You know, just just can you take the slop and can you make can you extract good can you extract diamonds from, you know, crap?

##### **Geohot** [[00:55:39](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3339)]
Yeah, that that that stuff and don't just use an agent to do it because it's. Yeah,

##### **Chenyu** [[00:55:45](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3345)]
the agent will add like 50 lines of comments. That says nothing.

##### **Geohot** [[00:55:48](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3348)]
Agents love whenever I see these verbose descriptions that like, you know, it says that. Print hello. And there's like four lines of comments above it. This invokes the print function which uses the hello. I added the hello print to the.

##### **Wozeparrot** [[00:56:03](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3363)]
Okay.

##### **Wozeparrot** [[00:56:05](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3365)]
Some

##### **Geohot** [[00:56:05](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3365)]
humans do that too, and they're slop humans. And we shouldn't just, you know, pick on AI here.

##### **Chenyu** [[00:56:11](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3371)]
No, we pick on the behavior and the results. That's right. What produce those? Yeah.

##### **Geohot** [[00:56:17](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3377)]
No, AI is a shorthand for just no slop. I don't care if you use AI, but. If it looks like. AI. I don't want it.

##### **Geohot** [[00:56:26](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3386)]
I'm one of those, you know, philosophically two things are the same if they're the same. Doesn't matter what the process was that produced that. However.

##### **Chenyu** [[00:56:35](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3395)]
Shock typing.

##### **Geohot** [[00:56:36](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3396)]
Like what?

##### **Chenyu** [[00:56:37](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3397)]
Like, I think.

##### **Geohot** [[00:56:41](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3401)]
No, I don't. I wish Python had a real type system, but you can't have everything. And someday we'll rewrite tiny, great and lean.

##### **Chenyu** [[00:56:49](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3409)]
Great. Sounds good. Okay. That's it for this meeting. Thank you, everyone. The next week. Bye bye.

##### **Geohot** [[00:56:54](https://www.youtube.com/watch?v=Rsl-Gtifyuc&t=3414)]
Bye.
