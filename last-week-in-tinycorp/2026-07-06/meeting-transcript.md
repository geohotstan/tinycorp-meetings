# 2026-07-06 Meeting

### Meeting Agenda

**Time:** new meeting #27, 7/6 9am Monday San Diego time
- company update
- CI updates
- HCQ2
- tensor.py, cleanups, requires_grad
- new codegen
- VIZ LLaMA schedule
- MLPerf GPT-OSS
- bounties, issues, comma happiness, GLM


### Audio

[Youtube Link](https://www.youtube.com/watch?v=_dLCuB4EV3E)

### Highlights

- **[Company Update](#geohot-000007)**: The Exa Box container arrived in Palmer’s back parking lot; the team is planning power via a generator, with an external chiller connected by cold-water and hot-water pipes.
- **[TinyBox Pro / Blackwell](#geohot-000007)**: The first TinyBox Pro with Blackwell is built, but the 5090 trays leave too much spacing and push cards to around 90°C, so trays need a redesign before shipment.
- **[Affordable MI300 Inference Hardware](#geohot-000007)**: The team is talking with AMD about buying “slightly broken” MI300s to build lower-cost inference boxes that would likely require tinygrad’s driver and target GLM at several hundred tokens per second.
- **[CI Updates](#chrism-000339)**: Benchmarks were split into many smaller pieces; Metal failures with interactivity warnings should be reported in the CI failures channel instead of silently rerun.
- **[Rusticl for CL Runtime](#chrism-000339)**: The CL runtime now uses Mesa’s Rusticl, which appears faster, but an out-of-bounds indexing issue is believed to be a Rusticl bug and will likely be skipped only on CL with a Mesa bug link.
- **[dtype Decomps and Slice Removal](#chrism-001238)**: Chrism plans to refactor dtype decompositions, and Geohot suggests pairing it with removing `Ops.SLICE` by expressing it as shrink plus bitcast.
- **[HCQ2 Rewrite](#nimlgen-001619)**: HCQ2’s rewrite was merged with explicit schedule and link passes; scheduling is cleaner and cached, while link-stage caching remains the main remaining work.
- **[HCQ2 Testing and Spec Cleanup](#geohot-002011)**: Geohot emphasized making HCQ2 follow the UOp spec rather than merely working accidentally, and suggested using a Python-backed submit path in the mock GPU for better tests.
- **[requires_grad / Stale Graph Handling](#chenyu-002835)**: Chenyu discussed bringing back `requires_grad`, but the group leaned toward a more general buffer-versioning approach that raises when realizing a graph with stale buffer versions.
- **[Broadcasting and Movement Ops](#geohot-003701)**: Geohot proposed making broadcasting more central, with expand inserting dimensions on the left and reduce removing them, trading some reshapes for more explicit permutes.
- **[New Codegen](#geohot-004157)**: The two codegens were merged, cutting roughly 100 real lines and removing ops like `UNROLL`, `CONTRACT`, `GEP`, and vector-concat-style lane movement ops.
- **[VIZ LLaMA Schedule](#qazalin-004613)**: The best LLaMA run improved to 2h 23m 11s from 2h 37m the previous week, with remaining work focused on SDMA overlap spikes and possible GPU power or thermal throttling.
- **[MLPerf GPT-OSS](#wozeparrot-005829)**: GPT-OSS has working forward, backward, and training-step code at small sizes, but needs flash attention support for head dim 64, attention sinks, sliding-window attention, and eventually grouped GEMM for MoE training.
- **[Comma, GLM, and RDNA Assembly](#chrism-010331)**: Comma appears happy after performance improvements and GLM deployment, RDNA assembly bounty work is progressing, and chat.comma.life is running with an internal push away from Anthropic spend.

### Transcript
##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=0)]
I think we're going to go start it. Welcome everyone. Let's start with company update.

##### **Geohot** [[00:00:07](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=7)]
We got the container for the Exa Box. There's a big container in Palmer's back parking lot now. Yeah, we're talking about how to get power for it. I think we're gonna get a generator. The chiller is external from the Exa Box, so we need that too. It's just gonna have like two pipes, two like four inch pipes, water in, water out, cold water in, hot water out. Order processing is going pretty well. Working on the first TinyBox Pro with Blackwell. So we built it, but the trays we used for the 5090s don't really work. The trays we used for the 5090s put too much space in between the cards, so the cards were getting up to like 90 degrees. So it's not acceptable. We got a... We got to redo the trays. BF, the person who ordered that happens to be in here. Should be about another like two weeks. Want to make sure all the thermals are good on that. Yeah, and we're talking with AMD about buying... I think we can talk about this. We're talking with AMD about buying a slightly broken MI300. So maybe we can buy some slightly broken MI300s. We can sell some affordable inference hardware. We'll have to use tinygrad. It'll only probably work with a tinygrad driver. But you know, what's the cheapest we can build a box that runs GLM at like a couple hundred tokens per second? And I'm curious what people would pay for that. Like would people pay like a hundred grand? Would people pay 50 grand for a box that could run GLM at several hundred tokens per second?

##### **Qazalin** [[00:01:55](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=115)]
Yeah, I think that's a good question.

##### **Chenyu** [[00:01:57](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=117)]
Yeah, that's kind of it.

##### **Geohot** [[00:02:06](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=126)]
Do we need two, or just one?

##### **Geohot** [[00:02:11](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=131)]
One. I've been texting the guy who sent us the pre-order money. He hasn't gotten back to me yet. I don't know what he wants in his box. You know, some people have more money than time. Okay. Yeah, yeah. No, we're definitely gonna start. We're gonna start with one. Where it is, I'm not really sure we have space for two. We'll build one at a time.

##### **Chenyu** [[00:02:37](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=157)]
I mean, once you build it, supposedly you can move to somewhere else?

##### **Geohot** [[00:02:42](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=162)]
That's the idea. Yeah, yeah. We have to buy or rent a generator. So we have enough power for it.

##### **Geohot** [[00:02:53](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=173)]
I think we'll start building it out. We'll get racks. We'll bolt them to the floor. Okay.

##### **Chenyu** [[00:02:59](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=179)]
And the expensive GPUs.

##### **Geohot** [[00:03:02](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=182)]
Well, that's the other problem. Yeah, yeah, yeah. This is another reason I hope these slightly broken GPUs come through. We'll have GPUs to put in the box. Right now, we kind of don't. Took the last two 5090s for some complicated reason.

##### **Chenyu** [[00:03:20](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=200)]
Are we GPU poor enough?

##### **Chenyu** [[00:03:23](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=203)]
Well, we have a lot of GPUs. They're just used. Okay. Great. Anyway, let's move on. This is a reverse order. So we will start with CI updates.

##### **Chrism** [[00:03:39](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=219)]
Yeah. So, I mean, the big thing is I split up the benchmarks into many smaller pieces. If you see the Metal one fail, especially with that, like the impacting interactivity warning or whatever, you send a message in the CI failures channel rather than just rerunning it. Because for a while I thought I had to fix that. And then I realized it came up again. It's hard for me to know if it's failed again if you just click rerun. And then it doesn't show up when you scroll through the history that it's failed. But I think that should be fixed. If it fails again, then I'll look into it a little bit more. And the other big thing that I changed was our CL runtime that we use is now using Mesa's Rusticl, which seems to be a lot faster, which is nice. Yeah, I saw that it caused that one issue with the indexing out of bounds.

##### **Geohot** [[00:04:45](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=285)]
Well, that's a real bug. We need to fix that anyway.

##### **Chrism** [[00:04:47](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=287)]
No, that's a bug in Rusticl. I knew about that, but it didn't fail when I ran it. And so I assumed it was deterministic. And if it didn't fail when I ran it, that was fine. But apparently it's not deterministic.

##### **Chenyu** [[00:04:59](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=299)]
Yeah, what's the bug in Rusticl? Let's just get it fixed upstream. Are you sure about that?

##### **Chrism** [[00:05:09](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=309)]
I'm pretty sure. I have an issue opened. I can look at it again. But do you think that tinygrad is generating CL code that does actually read out of bounds?

##### **Chenyu** [[00:05:19](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=319)]
Yeah. So if you see...

##### **Chenyu** [[00:05:21](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=321)]
I don't remember if I put this in my attempt to fix.

##### **Chenyu** [[00:05:28](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=328)]
But I think it's basically generating some form of valid. Then if you read like just a pointer plus some potentially big number. And I don't think in CL there's a thing saying... What's the behavior of that? And compiler can prefetch that address. I think you need that.

##### **Chrism** [[00:05:59](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=359)]
There legitimately is a bug in Rusticl where if you index a buffer using a value from another buffer, it legitimately will read out of bounds. Even if you put a guard that you put... You don't necessarily have to say like you put it inside an if statement. It will execute both sides of the if statement.

##### **Chenyu** [[00:06:21](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=381)]
Yeah. That's a real bug.

##### **Chenyu** [[00:06:27](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=387)]
That I get. I'm just not sure if this valid and drop the clamp on index. It's fine. Looks like it's fine.

##### **Geohot** [[00:06:40](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=400)]
I tend to also think... Like we have check out of bounds. I tend to also think that... Our check out of bounds use that valid.

##### **Chenyu** [[00:06:50](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=410)]
So it assumes when you load, you cannot preload without checking the valid. Yeah, but wait, it's going to totally check the valid. It moves the valid to the load. It's like a data pointer plus some like 12 gig.

##### **Geohot** [[00:07:07](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=427)]
But I have all the clamping logic for that. There's tests for this. I think that it's the Rusticl bug.

##### **Chenyu** [[00:07:16](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=436)]
We have to test for this.

##### **Chenyu** [[00:07:18](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=438)]
Yeah, I mean...

##### **Chrism** [[00:07:19](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=439)]
It's the Rusticl bug. Rusticl bug. It was definitely a Rusticl bug. And so unless something has changed in the codegen since I looked today, then I would be surprised

##### **Chenyu** [[00:07:27](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=447)]
if this wasn't their bug.

##### **Qazalin** [[00:07:31](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=451)]
Okay.

##### **Chenyu** [[00:07:33](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=453)]
Sounds good. But what do we do with that? Let's just...

##### **Chrism** [[00:07:38](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=458)]
We should probably just skip it only for CL. And I'll put a link... I'll change it so it just skips for CL and put a link to the... To the bug tracker for Mesa.

##### **Chenyu** [[00:07:52](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=472)]
Sounds good.

##### **Chrism** [[00:07:55](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=475)]
Yeah, those are the big changes. We also... So TinyMesa is added as a dependency, an extra dependency in that project, which should make it easier for comma to switch to using IR3 instead of Qualcomm CL. And so that's not a big change. So I think that's nice. That's just distributed by PyPI. And I just pre-compile the wheels and then it just downloads. So but if there's some backend... I don't know. It supports Linux, AMD64 and ARM64 and macOS ARM.

##### **Chenyu** [[00:08:48](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=528)]
Okay.

##### **Chenyu** [[00:08:56](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=536)]
Any other thoughts to make benchmark faster?

##### **Geohot** [[00:09:02](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=542)]
I think now the slowest one is the LLM because it beams everything from scratch.

##### **Chenyu** [[00:09:11](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=551)]
Hello? Hello?

##### **Geohot** [[00:09:14](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=554)]
I can't believe how bad this is. Is it a billion dollar company?

##### **Chenyu** [[00:09:21](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=561)]
Is it good now? Hello? Hello? Hello? We can hear you. Hello? Hello? Okay.

##### **Chrism** [[00:09:40](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=580)]
Cool. Okay. I don't know how much people are going to hear what I said, but that's mostly... I don't know. Yeah.

##### **Qazalin** [[00:09:54](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=594)]
Hello?

##### **Chenyu** [[00:09:56](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=596)]
Okay. I didn't hear anything.

##### **Chenyu** [[00:09:58](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=598)]
Might be my issues.

##### **Chrism** [[00:10:01](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=601)]
Okay. Well, wait. Can you hear me now? Yes. Okay. You didn't hear anything at all that I said?

##### **Chenyu** [[00:10:09](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=609)]
No. I asked if we can make benchmark faster and I didn't hear the response.

##### **Chrism** [[00:10:16](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=616)]
Oh, oh. Okay. I couldn't hear that. Okay. All right. So, yeah. So, slowest benchmarks, I think, are the LLM benchmarks.

##### **Geohot** [[00:10:26](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=626)]
The LLM for AMD and NV. But I think part of making benchmark faster is just kind of making tinygrad faster at this point. Like, it's not... The LLM one that's like running LLaMA and running Qwen, like, this is not... That's a normal thing.

##### **Qazalin** [[00:10:46](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=646)]
Yeah. Yeah. Yeah. Yeah.

##### **Geohot** [[00:10:50](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=650)]
I mean, it's hard to really say that...

##### **Qazalin** [[00:10:55](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=655)]
Yeah.

##### **Geohot** [[00:10:55](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=655)]
We have to just speed everything up.

##### **Qazalin** [[00:10:58](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=658)]
Yeah.

##### **Geohot** [[00:11:02](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=662)]
I mean, we could put in stats how long those take in.

##### **Chrism** [[00:11:05](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=665)]
That might be useful. The problem is it might be a little bit noisy.

##### **Geohot** [[00:11:08](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=668)]
Yeah. I mean, it's running BEAM, too. Like, BEAM is just really slow.

##### **Chenyu** [[00:11:15](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=675)]
Is LLaMA also comma benchmark slowish?

##### **Geohot** [[00:11:19](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=679)]
Well, that's because it's running on a crappy little comma. Yeah. Yes.

##### **Chenyu** [[00:11:29](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=689)]
Okay. I mean, the solution might be just make tinygrad in general faster, but...

##### **Geohot** [[00:11:36](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=696)]
Yeah. Yeah. Hopefully, some of these... I mean, like, CodeGen is running symbolic a whole bunch of times now. I think we can get it to a point... Like, as things get closer to the spec, we can have... We can have pattern matchers that are just kind of always included. Because right now, we'll do things like we'll run some pass, and then we'll run symbolic. And if we run that pass with symbolic, I think they'll just be faster.

##### **Chenyu** [[00:12:10](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=730)]
Okay. Sounds good. Yeah.

##### **Chenyu** [[00:12:12](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=732)]
I mean, I learned a lot that I certainly benefit from regular CI being a lot faster, so that's pretty nice.

##### **Chrism** [[00:12:19](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=739)]
Mm-hmm. Yeah.

##### **Chenyu** [[00:12:21](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=741)]
Yeah. That also caused me using my fork less, because it's faster if I just open the PR.

##### **Chenyu** [[00:12:28](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=748)]
Oh, yeah.

##### **Qazalin** [[00:12:31](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=751)]
Cool.

##### **Chenyu** [[00:12:34](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=754)]
Anything else? What are we going to work on next?

##### **Chrism** [[00:12:38](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=758)]
Probably this week, I'm gonna have to try and refactor dtype decomps. Yeah.

##### **Chenyu** [[00:12:46](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=766)]
That's kind of messy. And...

##### **Geohot** [[00:12:50](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=770)]
Yeah, I think with that, you should also do slice removal. So we have a thing called slice that is a combination of shrink and bitcast. It used to be buffer view, but there's no reason it shouldn't be shrink and bitcast. And I think it's actually really related to the dtype thing. Cool. It's the same basic idea. All right. You want to have one?

##### **Chrism** [[00:13:11](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=791)]
Yeah.

##### **Geohot** [[00:13:12](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=792)]
You're changing your dtypes, and that should just kind of be okay. Mm-hmm. So you should all just have normal shape semantics. You also, with this, probably have to consider the bitcast. It's a little annoying about how you want to deal with the ones. Yeah. I think... Yeah. So if you bitcast from something that's like two uint16s down to one uint32, should the shape be zero rank or one rank? Yeah. Oh. I don't have an obvious answer. I think it's just kind of where it works the best. Yeah. Yeah. It's probably one rank. Matching Torch probably makes more sense. But match JAX.

##### **Geohot** [[00:13:57](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=837)]
That's always good.

##### **Chenyu** [[00:14:00](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=840)]
I think you will also encounter annoying things in split store.

##### **Chenyu** [[00:14:10](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=850)]
What's split store? So I tried to find something that's not split.

##### **Chenyu** [[00:14:15](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=855)]
But if I had an attempt to remove Ops.SLICE with shrink, there are just some intermediate representations that's slightly annoying.

##### **Geohot** [[00:14:25](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=865)]
Yeah. Oh, I see. Yeah. I cleaned this up a little bit. I mean, it's better than it used to be.

##### **Chenyu** [[00:14:30](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=870)]
Every time there's an op that is Ops.SLICE through a special case, you know there'll be...

##### **Geohot** [[00:14:36](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=876)]
Yeah. Yeah. Yeah. Yeah. Yeah. Well, no, I mean that's been the whole codegen project. There's no more really special cases anymore for movement ops.

##### **Geohot** [[00:14:44](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=884)]
When they've been removed, there's no real case.

##### **Geohot** [[00:14:48](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=888)]
And when all the special cases for movement ops are completely gone, including we need to support load without index. Like right now we insist that load the index, but you shouldn't need an index.

##### **Geohot** [[00:15:04](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=904)]
How do you know where you are loading from?

##### **Chenyu** [[00:15:07](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=907)]
The whole buffer. Right?

##### **Geohot** [[00:15:14](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=914)]
Like think about what the semantics of that and see, right? Indexing zero is basically the same thing as... What if you have a buffer that's just size one and you index zero?

##### **Chenyu** [[00:15:27](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=927)]
It doesn't really do anything.

##### **Qazalin** [[00:15:33](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=933)]
But

##### **Chenyu** [[00:15:36](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=936)]
you'll be pretty good with that.

##### **Geohot** [[00:15:37](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=937)]
Like I refactored the renderers to generate the size of the load is a function of the load, not a function of the movement op.

##### **Geohot** [[00:15:47](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=947)]
Oh, that was pretty good. Yeah. Recasts, dtypes. Okay. And then the thing that we always talk about, which is ops should support ops.

##### **Chenyu** [[00:15:59](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=959)]
Oh, great.

##### **Geohot** [[00:16:00](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=960)]
Yeah.

##### **Chenyu** [[00:16:01](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=961)]
Yeah. Well, I figured out what to do about the load cache.

##### **Chenyu** [[00:16:07](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=967)]
So I'm going to just go ahead and run the test. Sounds good.

##### **Chenyu** [[00:16:11](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=971)]
Let's move on. Next is HCQ2.

##### **Nimlgen** [[00:16:19](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=979)]
So this week I merged the rewrite. So as I said, we have two explicit passes, like the schedule and link. Schedule is a lot cleaner now, and it also has cache. So the Python speed is a lot better. So I'm still working on adding cache to the link stage. So basically the current plan is to. So basically there is a now there is a special pass that can decide if we just want to do patches during link time, like in Python or just runtime. So I think for JIT, I'll do link time.

##### **Chenyu** [[00:17:10](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1030)]
And like for like regular kernels, it will be in runtime.

##### **Nimlgen** [[00:17:17](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1037)]
So like the C program will just fill up the command buffer and. Yeah, basically that's it for HCQ backends.

##### **Geohot** [[00:17:33](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1053)]
Yeah. So the code looks pretty clean. I'm looking at `hcq2.py`. Do we have an idea on how it compares in line count to the old HCQ stuff?

##### **Nimlgen** [[00:17:43](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1063)]
It's a lot better since this file is the replacement for like `hcq.py` in the graph. I think it's at least 200 lines less, maybe 300.

##### **Geohot** [[00:18:00](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1080)]
Yeah, I mean, do we have a way for this to support metal? Is it clear how it's going to support metal? Yeah.

##### **Nimlgen** [[00:18:13](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1093)]
Yeah. So basically we have the custom function submit, which has sources of the HCQIR, like the program or some wait instructions and dependencies. So yeah. And just for Metal, we just... We'll build the C function with UOps, which can just call this Metal. I mean, C functions basically like the Metal C functions.

##### **Geohot** [[00:18:50](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1130)]
Yeah, it definitely looks. It definitely seems faster too. I just ran it. Usually HCQ2 is really slow. I'm not sure which.

##### **Geohot** [[00:18:58](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1138)]
Yeah. So.

##### **Nimlgen** [[00:19:03](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1143)]
Yeah. So. And I've trained like, see if it works. I mean, it works correctly. So the only thing to fix is yeah, the HCQ link. So just to add cache there. Because currently just resolve all the all the patches. Like for copies and for small kernels.

##### **Geohot** [[00:19:27](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1167)]
Oh, I see. A.

##### **Geohot** [[00:19:30](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1170)]
Ton of stuff. I'm looking at an HCQ's commit and I see ton of stuff. I also see like usage of shrink where I think it should be index. I think it's really important to make sure that all these things are like following the spec. That happens to be allowed because of broadcasting. Those shrinks should really be an index, I think.

##### **Qazalin** [[00:20:06](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1206)]
I think.

##### **Chenyu** [[00:20:08](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1208)]
Yeah. Yeah. That makes sense.

##### **Nimlgen** [[00:20:11](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1211)]
Yeah.

##### **Geohot** [[00:20:11](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1211)]
Yeah. And I wonder how many other things there are like that. Like I would spend time to really make sure that all of this HCQ stuff is following the spec for the UOps. And not, you know, just happening to work. What I found is the more we stick to the spec, like the easier it just becomes to reason about rewrite rules. Yeah. Yeah.

##### **Qazalin** [[00:20:34](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1234)]
Yeah. Yeah.

##### **Geohot** [[00:20:35](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1235)]
Oh, I see. Yeah. So I'm looking at the input and shrink and then at some point it's getting rewritten

##### **Geohot** [[00:20:39](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1239)]
to to index. Cool. Yeah. I like that.

##### **Chenyu** [[00:20:47](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1247)]
It's going through the normal normal codegen path.

##### **Geohot** [[00:21:02](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1262)]
Interesting. I mean, I also see a ton of, maybe it has to be this way. Like, why is this? Why are those not load, right? Or why are those not long writes? Why is data 76? Yeah.

##### **Nimlgen** [[00:21:23](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1283)]
Yeah. Basically because like the AMD. Like the PM four is like.

##### **Chenyu** [[00:21:30](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1290)]
Word size is like 32 bits. So it just builds. I mean, it's just built.

##### **Geohot** [[00:21:40](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1300)]
I see. But this part. Yeah. Yeah. Yeah. dtype undecomp, right. Yeah. No, no, no. That totally makes sense from the HCQ perspective. Yeah. And then we can we can like undecomp that later to have that become a single store. We can look for that pattern. But cool. Yeah. Seems good. We're still on track for this sprint to have this merged.

##### **Nimlgen** [[00:22:06](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1326)]
Yeah. Yeah.

##### **Geohot** [[00:22:08](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1328)]
Yeah. It's fine to it's fine to have both too. Like I wouldn't I wouldn't make deleting HCQ a complete prerequisite for this. It's okay if like some of them are HCQ2, some of them are HCQ, and we finish the migration with it in master because what's annoying now I imagine is I don't think this stuff

##### **Geohot** [[00:22:26](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1346)]
is is this stuff tested now?

##### **Nimlgen** [[00:22:31](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1351)]
Not really. Yeah.

##### **Qazalin** [[00:22:33](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1353)]
Yeah.

##### **Nimlgen** [[00:22:34](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1354)]
I mean, I have some like unit tests, but yeah.

##### **Geohot** [[00:22:37](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1357)]
Yeah.

##### **Nimlgen** [[00:22:38](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1358)]
But they're not running CI, right?

##### **Geohot** [[00:22:39](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1359)]
Like how often do my code changes break this for you?

##### **Nimlgen** [[00:22:44](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1364)]
I mean, twice.

##### **Geohot** [[00:22:46](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1366)]
Twice. Okay.

##### **Nimlgen** [[00:22:47](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1367)]
But but yeah, I need to think like how to change the mock GPU to run this.

##### **Qazalin** [[00:22:56](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1376)]
Cool.

##### **Geohot** [[00:22:58](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1378)]
Yeah. Is there any reason the mock GPU shouldn't run this?

##### **Geohot** [[00:23:00](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1380)]
I mean, it should all be like a lower level of abstraction than this, right?

##### **Chenyu** [[00:23:04](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1384)]
Uh,

##### **Geohot** [[00:23:08](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1388)]
I'll think about that, but I'm not sure if it works right now.

##### **Chenyu** [[00:23:15](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1395)]
Let's see. I mean that I don't have extra ideas.

##### **Nimlgen** [[00:23:22](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1402)]
Yeah, it doesn't work because it just intercepts doorbell rings with like tracking memory views and these things.

##### **Geohot** [[00:23:33](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1413)]
Maybe what you can do is run the submit with the Python backend in the mock.

##### **Nimlgen** [[00:23:43](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1423)]
Yeah, probably, yeah.

##### **Geohot** [[00:23:45](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1425)]
Yeah, I think that would work, right? Because it's hard to actually intercept real C things. But if we just run that with a different backend, right?

##### **Geohot** [[00:23:52](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1432)]
That's a cool test as well.

##### **Geohot** [[00:23:58](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1438)]
Run that with a backend where we can intercept. We should also update just for readability purposes. I imagine those things are the actual addresses, those big negative numbers.

##### **Nimlgen** [[00:24:12](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1452)]
Actually, no. I mean, I have a UOp from buffer, which can create a UOp from the buffer class. And that's just the ID to not make them unique. Oh, it's the Python ID. Yeah.

##### **Geohot** [[00:24:35](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1475)]
Let's see. I mean, in theory, I could imagine the slot of the buffer being the memory address if it's allocated.

##### **Geohot** [[00:24:47](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1487)]
I don't know.

##### **Geohot** [[00:24:47](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1487)]
Maybe that doesn't work. I also see `get_addr` is taking a device name.

##### **Geohot** [[00:24:55](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1495)]
Why is that? I don't know.

##### **Nimlgen** [[00:25:01](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1501)]
I think initially because, I mean, we can have, like, for example, buffers allocated on the AMD. I mean, basically, like, to map buffers from one device, which is like a buffer from one device. We can get the address of this buffer on another device. That makes sense. Yeah.

##### **Geohot** [[00:25:26](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1526)]
I think there's a bit more to think through. Like, is there a clear spec for what `get_addr` is?

##### **Chenyu** [[00:25:39](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1539)]
So, it basically should return, like, uint64 when resolved.

##### **Geohot** [[00:25:48](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1548)]
I see you did add it to the spec. It's in the spec. `get_addr`: lower buf to its address on device dev.

##### **Chenyu** [[00:26:00](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1560)]
Hmm.

##### **Geohot** [[00:26:06](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1566)]
On device dev, just in case we have to do, like, address translation?

##### **Nimlgen** [[00:26:12](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1572)]
Yeah. We're just mapping. Like, here we have the CPU buffer. And, like, this buffer allocated on the CPU, and we just get the buffer on the AMD. So, like, we can use it. Like, the GPU can use it. Oh, interesting. Yeah. Yeah.

##### **Geohot** [[00:26:30](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1590)]
I see.

##### **Nimlgen** [[00:26:30](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1590)]
I see.

##### **Geohot** [[00:26:31](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1591)]
So, that `get_addr` is effectively just making sure it's mapped. Like, the mapping.

##### **Nimlgen** [[00:26:35](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1595)]
Yeah.

##### **Geohot** [[00:26:36](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1596)]
Yeah, yeah. Making sure it's mapped on the GPU at that address. So, then, `get_addr`, then, is the return device type?

##### **Chenyu** [[00:26:46](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1606)]
The return device type is still CPU, though.

##### **Geohot** [[00:26:55](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1615)]
So, what do you mean return device type? Okay. So, `.device` on that UOp is still CPU.

##### **Nimlgen** [[00:27:05](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1625)]
I should take that, yeah.

##### **Geohot** [[00:27:08](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1628)]
Yeah. It also doesn't have a... I assume you want it to move to ALU. Like, it doesn't have a... So, that's... The green square means that the addrspace is global. Okay. So, that's... I assume `get_addr` is kind of like a load. I mean, it's interesting. It's not like... This is just like... The more that we stick to the spec, the easier this will all be to, like, just write later and make things work. Because I found that we've done, like, so much thrashing in tinygrad's history because we didn't have a clear spec for things. Then, you change one thing, and then it doesn't work.

##### **Chenyu** [[00:27:58](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1678)]
But, you know, I don't mean to particularly... nitpick about this. Oh, seems like pretty good progress. Yeah. Excited to have it merged. Sounds good.

##### **Geohot** [[00:28:23](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1703)]
Anything else?

##### **Chenyu** [[00:28:26](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1706)]
No.

##### **Qazalin** [[00:28:30](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1710)]
Okay.

##### **Geohot** [[00:28:31](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1711)]
Let's move on.

##### **Chenyu** [[00:28:33](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1713)]
Next is my stuff.

##### **Chenyu** [[00:28:35](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1715)]
I did a bunch of cleanups. I removed Ops.DEVICE.

##### **Chenyu** [[00:28:42](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1722)]
And after there just being, I also removed the...

##### **Geohot** [[00:28:45](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1725)]
Not removed, but, like, I removed the CONTRACT and UNROLL.

##### **Chenyu** [[00:28:54](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1734)]
I have this. I... I have this. So I want to bring back requires_grad.

##### **Chenyu** [[00:29:03](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1743)]
I think that's... Yeah. So I read this. I didn't totally understand.

##### **Chenyu** [[00:29:19](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1759)]
So basically, we previously said we can remove it because there's no issue letting these grad hang around even if like no one uses it. So the bug from the cross-schedule thing is, if your current SINK destroys some tensor, you want all other tensors, not in this SINK, but depends on the thing you're going to destroy, scheduled before this SINK. So you want to pull those in.

##### **Geohot** [[00:30:00](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1800)]
Yeah, but we should be able to do this using the tensor machinery. I'm not sure we have to bring grad back, right?

##### **Chenyu** [[00:30:06](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1806)]
The issue is this mechanism will also realize the dangling grad, even if it has no other reader, just because it exists. Because those grads, because with every update, we are going to update the model weight. And the grad depends on previous version of the model weight. Yes. So if our logic is every time our SINK is going to destroy something, also schedule everything that depends on it, then we will also schedule a grad, even if there is no consumer for the load.

##### **Geohot** [[00:30:47](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1847)]
Wait, but it totally shouldn't do that.

##### **Chenyu** [[00:30:50](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1850)]
We shouldn't tell it. Can you tell the difference between the two cases?

##### **Geohot** [[00:30:57](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1857)]
Like apply. Apply map to tensor shouldn't trigger any realizes. It just moves. It just makes sure that the buffers stay up to date.

##### **Chenyu** [[00:31:09](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1869)]
So how do you fix if your current SINK is going to destroy some or overwrite some tensor or buffer, and you have some other hanging lazy other SINK that depends

##### **Geohot** [[00:31:25](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1885)]
on the old version of that buffer?

##### **Chenyu** [[00:31:32](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1892)]
So the crux of that bug, the previous reuse seed, is because the old version of the seed, some other random rand depends on that. So we cannot just run the later one first without running the first one.

##### **Qazalin** [[00:31:57](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1917)]
OK.

##### **Chenyu** [[00:31:59](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1919)]
I don't follow that.

##### **Chenyu** [[00:32:03](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1923)]
So you have a random seed zero. And you have random seed one. And you have your tensor zero that depends on seed zero and tensor one that depends on seed one. So now both tensor zero and tensor one are lazy. So if you realize tensor zero, then realize tensor one is fine. Because the seed got updated correctly.

##### **Geohot** [[00:32:30](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1950)]
Yeah, if you realize in the other order, it'll be different, sure.

##### **Geohot** [[00:32:38](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1958)]
So that's not fine, I think. I mean, yeah, this...

##### **Geohot** [[00:32:44](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1964)]
I don't exactly know how this relates to requires_grad. Yes, this is a known problem. Obviously, if you like... So, yeah. Your realization over...

##### **Chenyu** [[00:32:54](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1974)]
So I think the ideal or the properties that we try very hard to maintain on these assigned stuff is your output should be the same as if you eagerly realize every line.

##### **Chenyu** [[00:33:13](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1993)]
I don't think we can always enforce that, right?

##### **Chenyu** [[00:33:16](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=1996)]
We can certainly always enforce that. Yeah.

##### **Geohot** [[00:33:21](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2001)]
Well, no, but like, if you have a buffer, right?

##### **Geohot** [[00:33:24](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2004)]
Whenever you have an actual buffer, like, that buffer can always change underneath you. Sure. And we kind of just accept that?

##### **Chenyu** [[00:33:40](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2020)]
What do you mean?

##### **Geohot** [[00:33:42](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2022)]
I mean, the other choice that we could do is we could just invalidate the graph.

##### **Qazalin** [[00:33:46](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2026)]
Yeah.

##### **Geohot** [[00:33:51](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2031)]
And then we could just make it so that if you do the second realize before the first realize, and you try to do the first realize, it just says sorry.

##### **Geohot** [[00:34:01](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2041)]
Like, this is stale.

##### **Chenyu** [[00:34:08](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2048)]
Yeah. Yeah.

##### **Qazalin** [[00:34:10](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2050)]
Yeah. Yeah. Yeah.

##### **Chenyu** [[00:34:46](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2086)]
It's probably fine. Yeah. I just don't exactly know, my concern with bringing back requires_grad to deal with this is this seems like a generic problem that we have to deal with that isn't specific to the grad.

##### **Geohot** [[00:34:54](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2094)]
I would prefer to raise for this if we could detect it. I mean, this is a universal problem, right? Like you can fix this with requires_grad.

##### **Chenyu** [[00:35:03](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2103)]
I would imagine the way to fix this is to go through old tensors and making sure when you are going to write and overwrite something, making sure everything that depends on it is in the same. Otherwise just raise. Some version of that seems right.

##### **Geohot** [[00:35:19](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2119)]
like we have some, it's the thing you always want, it's buffer generations

##### **Chenyu** [[00:35:26](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2126)]
buffer generation buffer version

##### **Geohot** [[00:35:29](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2129)]
buffer version, yeah, we stick like basically a version on the buffer and then that version gets updated when the buffer is updated and then we see if you're trying to realize a graph that still has the old buffer version baked into it. We have a pass called validate_buffers, so like you can put the buffer version in the graph in the UOp graph and then when you actually go to realize that UOp graph, it checks to make sure the buffer version actually matches the version of the real buffer

##### **Geohot** [[00:36:05](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2165)]
if it doesn't, it raises

##### **Chenyu** [[00:36:10](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2170)]
okay, sounds good

##### **Chenyu** [[00:36:11](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2171)]
I need to think more about just how easy it is to raise but raising it sounds good

##### **Geohot** [[00:36:20](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2180)]
yeah, I think we have to. I like that that is like a behavioral invariant, like we can't always promise that it's going to be the same as eager realization, but we can raise if it's not

##### **Chenyu** [[00:36:35](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2195)]
yeah, that sounds good

##### **Chenyu** [[00:36:37](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2197)]
because the only annoying path is you don't know and things just suddenly go wrong. Yeah.

##### **Qazalin** [[00:36:45](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2205)]
okay

##### **Chenyu** [[00:36:50](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2210)]
so I think I'm also

##### **Chenyu** [[00:36:52](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2212)]
I also see your change to the allow broadcasting. That's probably something I can work on.

##### **Geohot** [[00:37:01](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2221)]
oh yeah we should be able to start doing broadcasting everywhere, yeah so broadcasting is required in the new expander the new expander is now five lines and the reason it's five lines is because it just uses broadcasting

##### **Chenyu** [[00:37:14](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2234)]
yeah yeah

##### **Geohot** [[00:37:17](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2237)]
oh, the other thing I kind of want to talk about about broadcasting quickly is like so like I moved I changed reduce to remove the the ones we could also change reduce to instead of taking a list of axes we could have it only remove axes from the left side

##### **Chenyu** [[00:37:44](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2264)]
and then just take a count is there a specific benefit

##### **Geohot** [[00:37:57](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2277)]
well

##### **Chenyu** [[00:37:58](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2278)]
these two are equivalent

##### **Geohot** [[00:37:59](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2279)]
the thing that then becomes interesting I agree that they're equivalent I think that the count one is more restrictive which is good and then we can also start thinking about writing expand like that so instead of expand I'm going to take a count on a number so instead of turning ones into like a bigger shape we can have expand just insert dimensions on the left hand side that are the expanded dimensions

##### **Chenyu** [[00:38:26](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2306)]
yeah so I really want that as a high-level API. We currently don't have that.

##### **Geohot** [[00:38:35](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2315)]
No, but I think we might want it to be the low-level API like the high-level API we can make whatever insert some extra movement ops who cares but the advantages to making that work is that at the low level movement op is now expand is the exact opposite of reduce, right? So if I have expand, insert three axes on the left, and then I have reduce with three, it removes those.

##### **Geohot** [[00:38:57](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2337)]
In principle, that sounds pretty good.

##### **Geohot** [[00:39:01](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2341)]
Yeah, yeah. I'm quite interested in doing it. And I feel like.

##### **Chenyu** [[00:39:06](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2346)]
Are they concerned that's bad?

##### **Geohot** [[00:39:09](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2349)]
Well, it adds movement ops, and it adds some permutes. It adds some permutes, but it removes some reshapes.

##### **Chenyu** [[00:39:17](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2357)]
Why do you have permute?

##### **Geohot** [[00:39:20](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2360)]
Because if you want to expand a middle axis, right? You expand and insert the axes on the left, and then you have to permute them to put them in the place you want.

##### **Qazalin** [[00:39:35](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2375)]
Huh.

##### **Geohot** [[00:39:37](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2377)]
Think about the convolution construction, right? So for the convolutions right now, you have to expand. You have to expand the height and width dimension to go through the whole thing. But we first do a reshape where we add ones next to the height and width dimension, and then we do an expand, which turns those ones into the height and width. The alternative would be expand, where we insert the height and the width on the left, and then we permute them to put them in the right place.

##### **Chenyu** [[00:40:05](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2405)]
Then we follow it up with a reshape, which puts them together. Overall, I think it would create a few more movement ops,

##### **Geohot** [[00:40:20](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2420)]
but there'd be less reshapes, and it's just an overall simpler thing to understand, right? Because right now, we have expand. It's like, what does it mean to insert the dimension in the middle? It doesn't really mean anything. It's effectively just a copy where we insert the number. I kind of like this, like, everything happens on the left-hand side thing, right? Like, stack adds a dimension on the left-hand side. Index removes one. Expand inserts dimensions on the left-hand side. Reduce removes them.

##### **Chenyu** [[00:40:49](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2449)]
Yeah.

##### **Geohot** [[00:40:52](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2452)]
I'll play with that. I'm just curious if you see, like, a major permute.

##### **Chenyu** [[00:40:58](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2458)]
I think overall, permute is preferred than reshape because reshape is too free. Reshape is what? Reshape is very free in terms of spec and the space that you can construct with it. Yeah.

##### **Geohot** [[00:41:12](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2472)]
Reshape is the most annoying thing to deal with.

##### **Chenyu** [[00:41:14](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2474)]
Yeah. So if it's just some reshape becomes some permute, that sounds not too bad?

##### **Geohot** [[00:41:21](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2481)]
Yeah. Right now, almost everywhere we use expand, we have this pattern where we first reshape to add ones. Reshaping to add ones isn't really a real reshape, but we don't really use it like a reshape. And then you have to treat it like a reshape. That could be the most awful reshape ever when you reshape a tensor that's 67 by 66 into 66 by 67. Yes.

##### **Chenyu** [[00:41:43](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2503)]
OK.

##### **Geohot** [[00:41:44](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2504)]
OK. Yeah. I'll play with it.

##### **Chenyu** [[00:41:46](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2506)]
OK.

##### **Chenyu** [[00:41:49](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2509)]
Okay, I digress a little bit. We can use that as a gateway to move on to the new codegen.

##### **Qazalin** [[00:41:56](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2516)]
Cool.

##### **Geohot** [[00:41:57](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2517)]
Yeah. I changed. So yeah. I changed reduce to remove the ones. I got to update the spec. Two codegens merged. It overall worked out to be about a 100 line reduction, like a real 100 line reduction. And removal of tons of ops. No more UNROLL, CONTRACT. You remove the last ones on the tensor cores. GEP is gone. GEP is just index. Got rid of VCAT and the other stupid one that I can't even remember. All this stuff is just like kind of nonsense. The new expander and devectorizer are quite simple. I mean, the first thing that actually took me a long time wasn't rewriting the expander and the devectorizer. Those were pretty easy. The annoying part was two things. One, the old devectorizer conflated two issues. It conflated the devectorization of ALU ops with the coalescing of loads. So first, I just did a big refactor where I moved all load coalescing and image stuff to after the devectorizer. And that was a lot easier to write. And then the other thing that was a little bit annoying was just the fusion of tensor cores. So we have these tensor cores where the tensor core WMMA instruction supports an accumulation as well as the multiply. But that accumulation is done in a vector dtype. Or not a vector dtype, but that accumulation is done on a shape, which is different from the rest of everything in GPU. So you can't really use the devectorizer. So that's actually still not perfect. There's still a few times when the thing isn't really fusing into the accumulator. And it was there before. It's just not a regression. But yeah, there's a little bit of annoyance there. But overall, I think there's just a lot more cleanups to do. I can finally remove all of that rewrite into new style stuff. We have that thing in index that needs to be removed with PtrDType. That's the last major blocker from just getting rid of PtrDType. PtrDType can go. dtype.vec. The only place it's still really used is x86. So I've got to deal with that. And then after dtype.vec and PtrDType are removed, I think we could actually just remove dtype entirely from the UOp. So hopefully that'll happen. I think this week's aggressive on that. But I think this week it's actually plausible to get rid of vec or PtrDType and then add some assertions to say where the types don't match. So where the dtype doesn't match, the vector.

##### **Geohot** [[00:44:39](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2679)]
The vector. I'll write the production rules and those static checks.

##### **Chenyu** [[00:44:45](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2685)]
Cool. Sounds good. It certainly feels nice to remove the ops that I never understood. And now I don't need to understand.

##### **Geohot** [[00:44:54](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2694)]
So that's great. They were nonsense. They were just. You know, I read this thing about coding is not this process of writing code. Coding is this process of developing a language. Like we're developing a language to talk about this kind of stuff. And I think that the unification of lanes with buffers is something that doesn't exist anywhere. Everything keeps these separate concepts. There's separate concepts in LLVM. There's separate concepts in CUDA.

##### **Geohot** [[00:45:32](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2732)]
There's separate concepts in C. But there's no reason for them to be. It's the same idea.

##### **Geohot** [[00:45:39](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2739)]
Yeah. We effectively had two entire shape systems. And then what those ops were that you didn't understand were like crappy movements. They were like movement ops that weren't real movement ops. That only applied on lanes. And C has all of this too. So now we're moving beyond the state of the art in doing.

##### **Chenyu** [[00:46:02](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2762)]
Great. I always feel good to do that. And let's move on to LLaMA schedule. How fast are we now?

##### **Qazalin** [[00:46:13](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2773)]
My best run I shared here is 2 hours and 23 minutes and 11 seconds.

##### **Chenyu** [[00:46:22](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2782)]
Great.

##### **Qazalin** [[00:46:23](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2783)]
For the last week, we were at 2 hours and 37 minutes. So yeah.

##### **Geohot** [[00:46:30](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2790)]
How much time did we lose last time?

##### **Qazalin** [[00:46:36](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2796)]
We were at 2 hours and 37.

##### **Geohot** [[00:46:38](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2798)]
So we lost like. We lost like a lot of time. 2 hours 37. How about before that? Like how much time are we losing a week? And what does the derivative of that look like?

##### **Qazalin** [[00:46:47](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2807)]
We're losing about 15 a week. And this has continued. Last like two weeks ago, we were at 2 hours and 50. So yeah.

##### **Geohot** [[00:46:59](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2819)]
Nice. All right. All right. Let's keep it up. But when are we going to be at zero?

##### **Qazalin** [[00:47:04](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2824)]
All right. So I'll share the screenshot. It's clear where we're messing up. If you see this a little bit, zoom out to the end, you see that AMD is idle and SDMA is active.

##### **Chrism** [[00:47:18](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2838)]
Yeah.

##### **Qazalin** [[00:47:19](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2839)]
And AMD is just sitting doing nothing. So it's interesting. I found a bug last week where we were all-reducing about 200 times. We have eight buffers that we need to all-reduce, but we are reducing about 200 times because like we were slicing them. So I fixed it. The way I fixed it was I moved everything to the end. So I do a very big all-reduce. Like I all-reduce a buffer that's 900 megabytes and I'm copying that over like 60 gigabytes a second to the other GPU. So yeah.

##### **Geohot** [[00:48:02](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2882)]
Yeah. Because we're stacking the tensor together, we can't overlap the communication with the backward path.

##### **Qazalin** [[00:48:11](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2891)]
Exactly. Exactly. That's the problem. That's the problem. We can, but it's not going to work. So I'll share this other fun thing because this, I tried it today. Great is if you overlap SDMAs, like you do a bunch of small SDMAs and you overlap them with the backward. So you do it like this. This is how it looks like in this. And like if you benchmark this, this is fast. But like you see like this is doing a bunch of like small SDMAs. Yeah. Yeah.

##### **Geohot** [[00:48:49](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2929)]
Yeah.

##### **Qazalin** [[00:48:49](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2929)]
Nicely overlap. So it looks nice, but it's terrible. Well, it looks like spiky.

##### **Geohot** [[00:48:57](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2937)]
It looks like it's sometimes faster, but then it spikes up.

##### **Qazalin** [[00:49:02](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2942)]
Yeah. This is spiky. Spiky.

##### **Geohot** [[00:49:05](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2945)]
Why is it spiky?

##### **Qazalin** [[00:49:07](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2947)]
No idea. But I've just observed this. This is empirical.

##### **Geohot** [[00:49:12](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2952)]
Interesting. But yeah, yeah. No, I mean, we have to do it this way. We have to do it with the small ones because we have to overlap that.

##### **Qazalin** [[00:49:20](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2960)]
I'm trying to like find a sweet spot where I can like do it small enough, but not too small that it gets spiky. I don't know the root cause of the spikiness. I don't think I have the tools to see about that.

##### **Geohot** [[00:49:36](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=2976)]
I would root cause the spikiness and then we could figure out like, cause yeah, I mean, this is maybe something we can fix in our driver or maybe HCQ2 fixes it. There's no fundamental reason that it should be, that it should be spiky. Interesting. Literally like a, like a, like a dispatch issue. But yeah, I mean the, the small kernels are definitely more correct than the big ones at the end. We can't do the big ones at the end. We have to do it incrementally. We gotta make sure it's nice while we do it.

##### **Geohot** [[00:50:02](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3002)]
Yeah.

##### **Geohot** [[00:50:09](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3009)]
Yeah. Only root cause spikiness. All right. So if we're, if we're, if we're losing 15 minutes a week in 10 weeks, it will be zero

##### **Geohot** [[00:50:17](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3017)]
time.

##### **Qazalin** [[00:50:22](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3022)]
Well, we gotta get to the baseline with AMD. I think after this, after I fix the spikiness, we'll get to the baseline because we're at 1.52 and they are at 1.3, 1.4. Yeah.

##### **Geohot** [[00:50:37](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3037)]
So yeah, we need to get to ours first. Yeah. Yeah. I mean, that'll just be a question of a good, I think, I think we'll be perfectly lined up to start rewriting the kernels in our stuff, start to push the kernels beyond what they're doing once we get rid of all these. Yeah, once we're at the baseline.

##### **Qazalin** [[00:51:04](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3064)]
Working on a branch. Or try to like get to baseline and then merge things into master in a clean way and high level way.

##### **Geohot** [[00:51:16](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3076)]
Yeah. Yeah. Nimlgen, do you have any ideas what the spikiness is?

##### **Chenyu** [[00:51:23](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3083)]
Yeah.

##### **Nimlgen** [[00:51:24](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3084)]
So basically I think you can check there is so these, so basically then there is wait. You just need to load some memory and this four is like the delay, like how many, I mean, it's something related to the clocks of the GPU, like how many, like four multiply by some value, I think 250 clocks or something like that. You should wait. So there is similar for PM4. So no, if you like have a lot of small dependencies and they just fighting for the same signal, so it can be just thrashing.

##### **Geohot** [[00:52:08](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3128)]
How do we fix this?

##### **Nimlgen** [[00:52:16](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3136)]
I know we can try like to change this value and see if it's like, has any impact on the result. And if yes, I think we can think about that.

##### **Geohot** [[00:52:31](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3151)]
Yeah. Yeah. Yeah.

##### **Geohot** [[00:52:33](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3153)]
Qazalin, maybe the idea is to get a small, get a small reproduction of this.

##### **Qazalin** [[00:52:38](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3158)]
Small reproduction. I've tried. Yeah. I'm trying to do it.

##### **Geohot** [[00:52:42](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3162)]
Yeah. Yeah. Cause I mean, I think this is definitely a driver issue, right? Cause there shouldn't be like no, no consistent kernel should cause spikiness. Also, why are the steps fast at the beginning and then they get slow? Is that thermals?

##### **Qazalin** [[00:53:02](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3182)]
Oh yeah. I think that's thermals.

##### **Wozeparrot** [[00:53:04](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3184)]
It's not thermals.

##### **Qazalin** [[00:53:05](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3185)]
Like our GEMMs get slower.

##### **Wozeparrot** [[00:53:08](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3188)]
What was better? It's not thermals? No. Last time I, this behavior is known at least to me and I posted about it in the channel when I was doing 8B runs. It's the GPUs are power limiting.

##### **Geohot** [[00:53:22](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3202)]
That's probably thermals, right?

##### **Chenyu** [[00:53:26](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3206)]
At least it's not thermal throttling.

##### **Geohot** [[00:53:30](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3210)]
It's power throttling. Interesting.

##### **Geohot** [[00:53:33](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3213)]
Why, why would that, that like, what's like the real time on this? If we put like real time on the X axis.

##### **Chenyu** [[00:53:47](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3227)]
So it looks like there's like 10% more speed if we can figure out how to make it not do that. Yeah.

##### **Wozeparrot** [[00:54:04](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3244)]
I mean, you'll see it start throttling within like the first, the first 50 steps or like

##### **Chenyu** [[00:54:09](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3249)]
a couple of minutes. This has to be thermals then. It doesn't make any sense.

##### **Qazalin** [[00:54:31](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3271)]
Yeah. Yeah.

##### **Chenyu** [[00:54:37](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3277)]
I don't know if I can figure it out.

##### **Qazalin** [[00:54:40](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3280)]
What's doing this?

##### **Geohot** [[00:54:41](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3281)]
If it, if it's not, if it's not thermals, like do we know the clocks? Are the clocks getting slower?

##### **Chenyu** [[00:54:48](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3288)]
Can we just add clocks to this graph?

##### **Geohot** [[00:54:58](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3298)]
But yeah, I don't know. We can talk about this later, but yeah, either way it looks.

##### **Chenyu** [[00:55:01](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3301)]
It's taking forever. It's taking forever. Yeah.

##### **Geohot** [[00:55:03](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3303)]
Yeah. Cool. It looks like in addition to the spikes, it looks like there's another free 10% somewhere. That's just the GPU slowing down for no reason. If it's thermals, I will go get bigger fans.

##### **Qazalin** [[00:55:18](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3318)]
I'll try to tell with some AMD SMI or something.

##### **Wozeparrot** [[00:55:23](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3323)]
The one concern I have for the fast runs, you're converging a little fast.

##### **Geohot** [[00:55:33](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3333)]
Why is that a concern?

##### **Chenyu** [[00:55:37](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3337)]
And we're faster. It's faster than RCP.

##### **Geohot** [[00:55:42](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3342)]
What's RCP?

##### **Wozeparrot** [[00:55:44](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3344)]
RCP is the eval step after the one that these runs are ending at.

##### **Geohot** [[00:55:52](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3352)]
Is this a bad thing? Is this valid or not?

##### **Chenyu** [[00:55:59](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3359)]
It's not valid.

##### **Chenyu** [[00:56:00](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3360)]
If it's not valid, it's not valid. If it's faster than RCP, they'll probably just normalize it. I think when we compare these, it's probably more meaningful to compare per step or something with fixed steps.

##### **Geohot** [[00:56:14](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3374)]
Yeah. Yeah. It seems fine. It seems like we're still doing the right thing. We're making it faster regardless of like, we can figure out where we actually stand for the real submission. But yeah, I mean, I want to clean up these spikes. Do the backwards pass correctly, and then figure out what this throttling is. Because MLPerf doesn't care how big a fan I get. I have big fans. I have very large fans. I will go get them.

##### **Qazalin** [[00:56:46](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3406)]
One note I will add on the step, as Wozeparrot also mentioned. It sometimes converges in more steps, which is like more absolute time. So I only compare when these step times are exactly the same, like the step count is exactly the same. But yeah, sometimes it just takes more steps.

##### **Geohot** [[00:57:08](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3428)]
Don't worry about the other thing. Like step time and correctness. We'll deal with this.

##### **Geohot** [[00:57:14](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3434)]
Yeah.

##### **Qazalin** [[00:57:16](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3436)]
My target is pretty much step time 1.38, 1.4 by end of sprint. Yeah. We're like wasting 60 milliseconds on just SDMA that makes GPUs, makes compute idle. So I think once I figure out.

##### **Chenyu** [[00:57:41](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3461)]
Should be better. Yeah. That's all.

##### **Qazalin** [[00:57:45](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3465)]
Okay. One last thing I'll add. Sorry. I know, George, you were complaining about the labels on the nodes in this. Like the indexes we're rendering, right? Yeah. Yeah. So I think it would really help if you can like share the repro.

##### **Geohot** [[00:58:02](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3482)]
Yeah. Yeah. Yeah. I'll. Now that new codegen's merged, I'll have some real repros today.

##### **Chenyu** [[00:58:08](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3488)]
Yeah. Thanks. Okay. Next. GPT-OSS.

##### **Wozeparrot** [[00:58:20](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3500)]
Has Andy responded?

##### **Geohot** [[00:58:24](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3504)]
Oh, yeah. No, we're fine with GPT-OSS. Yeah. They're going to rewrite the contract.

##### **Qazalin** [[00:58:28](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3508)]
Yeah. Yeah.

##### **Wozeparrot** [[00:58:29](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3509)]
Yeah. So we have a working forward, backward, and I have a working training step in my thing in my PR. But you have to have the layers really low and the sequence length really low. So we're missing flash attention and GEMM. So our existing flash attention doesn't work because GPT-OSS doesn't use head dim 128. It uses head dim 64. And it also has an attention sink.

##### **Qazalin** [[00:58:57](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3537)]
So we're missing flash attention and GEMM.

##### **Geohot** [[00:59:00](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3540)]
So we're missing flash attention and GEMM. Uh, how hard is it to fix this?

##### **Geohot** [[00:59:08](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3548)]
I mean, the GEMM, I'm not that worried about because that's just speed, but for flash attention, we got to fix the, um,

##### **Wozeparrot** [[00:59:17](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3557)]
I need to look into the flash attention still. GEMM is a little more annoying. For MoE training, you really want a grouped GEMM.

##### **Geohot** [[00:59:32](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3572)]
Or else you're just going to end up with a bunch of

##### **Geohot** [[00:59:33](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3573)]
I mean, I just want to get something trained as soon as we possibly can. Like we got to with the correct sequence that I picked. We got to, we got to fix the flash attention.

##### **Geohot** [[00:59:41](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3581)]
Yeah.

##### **Geohot** [[00:59:43](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3583)]
Uh, yeah. So this is, this is from AMD. We're good on GPT-OSS. It's definitely happening. It's just a question of what times they're going to give us. We'll see.

##### **Wozeparrot** [[00:59:54](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3594)]
Yeah. For MoE pretraining, you really want a grouped GEMM. I think you're running a lot of extra GEMM compute. Because you'll be running the experts, even for tokens that don't need the experts, and you just mask them out.

##### **Geohot** [[01:00:14](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3614)]
I see.

##### **Geohot** [[01:00:17](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3617)]
Yeah. I'm a lot more confident in our codegen starting to work for GEMM than I am for flash attention.

##### **Chenyu** [[01:00:29](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3629)]
I think our codegen could start to work for grouped GEMM.

##### **Geohot** [[01:00:34](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3634)]
Uh, it'd be fast for grouped GEMM somewhat soon. I don't see it being fast for. So it's just that we got to update it to work for 64 and not 128.

##### **Wozeparrot** [[01:00:45](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3645)]
And support the attention sink.

##### **Chenyu** [[01:00:48](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3648)]
What's attention sink?

##### **Wozeparrot** [[01:00:51](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3651)]
They add an extra term into the softmax. Yeah.

##### **Qazalin** [[01:00:55](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3655)]
Yeah. Yeah.

##### **Wozeparrot** [[01:00:58](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3658)]
Oh, that because. Oh, they also use sliding window attention. Every even layer is sliding window attention. Not full.

##### **Chenyu** [[01:01:06](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3666)]
I see.

##### **Wozeparrot** [[01:01:08](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3668)]
And then your attention sink essentially becomes a global token that the sliding window can store information in.

##### **Chenyu** [[01:01:17](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3677)]
Do you have an eval script?

##### **Chenyu** [[01:01:22](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3682)]
In the sense that I understand that training would probably be out of frame. But I would expect, since we have the model, it should eval the trained model and give

##### **Chenyu** [[01:01:33](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3693)]
the correct eval number. I don't know if they don't have a published model.

##### **Wozeparrot** [[01:01:46](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3706)]
But we can just use whatever one that OpenAI published.

##### **Chenyu** [[01:01:55](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3715)]
I mean, it doesn't need to be a fully-trained model. I'm just curious, since when you train yours, you need to eval.

##### **Geohot** [[01:02:03](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3723)]
Do we have anything that shows the model works? I don't know.

##### **Wozeparrot** [[01:02:10](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3730)]
I mean, you can run the model file, and it runs the forward-backward pass. It works like how FlatLlama does.

##### **Chenyu** [[01:02:17](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3737)]
OK.

##### **Geohot** [[01:02:19](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3739)]
But yeah, we've got to get eval. Let's just get it on the real model. Make sure it's correct.

##### **Chenyu** [[01:02:26](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3746)]
Yeah, I think this is similar to all our previous MLPerf. We will have the model implementation, and we have eval to make sure the implementation is correct. And then there's training that follows.

##### **Wozeparrot** [[01:02:41](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3761)]
Overall, this benchmark is pretty bad from MLPerf's side. There's a lot of information that's just missing in the reference implementation.

##### **Chenyu** [[01:03:09](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3789)]
I see. Okay. I think just generally working towards the full thing while thinking about how to make sure the steps are correct, and if we foresee issues, we want to know the issues earlier than later so we can prioritize accordingly.

##### **Geohot** [[01:03:15](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3795)]
Cool.

##### **Chenyu** [[01:03:23](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3803)]
Okay, we're slightly out of time already. Do we have any issue with comma? Are comma happy?

##### **Chrism** [[01:03:31](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3811)]
No, as far as I know, they're happy. I got to double check that they actually bumped us. But they have a good incentive too because we gave them more performance.

##### **Chenyu** [[01:03:44](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3824)]
Great. And there's some work on GLM and some work on RDNA. No, RDNA assembly.

##### **Geohot** [[01:04:00](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3840)]
Yeah, I think the RDNA assembly bounty is coming along nicely. I see Rain in the meeting. Yeah, I think maybe next week if you want to talk about that. Hopefully next week.

##### **Chenyu** [[01:04:10](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3850)]
Hopefully next week it will be at a point where the tests are passing. So that's cool.

##### **Geohot** [[01:04:15](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3855)]
And comma is happy with the GLM we have stood up. Just got to make sure it stays stable. But yeah, they've all been using it. We have like chat.comma.life now, and there's a ban inside comma on paying Anthropic any money.

##### **Chenyu** [[01:04:36](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3876)]
Sounds good. Anything else for the meeting? I don't think so.

##### **Chenyu** [[01:04:44](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3884)]
That's it for this one. Thank you. See you next week. Bye bye.

##### **Geohot** [[01:04:47](https://www.youtube.com/watch?v=_dLCuB4EV3E&t=3887)]
Bye.
