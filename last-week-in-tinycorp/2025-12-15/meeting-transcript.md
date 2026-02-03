# 2025-12-15 Meeting

### Meeting Agenda

**Time:** 9am Monday San Diego time
- company update
- LLaMA training priority
- grad acc, jit
- flash attention
- mi300/350 stability
- fast gemm, viz
- fp8 training
- image dtype / ctype
- other bounties

### Audio

[Youtube Link](https://www.youtube.com/watch?v=_mJIF112c5k)

### Highlights

- **[Company Update](#nimlgen-000016)**: Sold two more Blackwell boxes.
- **[TinyBox Shipping Reliability](#geohot-000021)**: TinyBox Red was down; adding “fragile” drop-indicator stickers that change color if mishandled.
- **[Hardware Vision: “Pay-to-flop” GPU Racks](#geohot-000044)**: Long-term plan is to sell racks of GPUs (no full computers), abstracting away GPU/vendor details and optimizing cost-per-$ across components (GPUs, PCI switches, enclosures, networking).
- **[LLaMA/Lava Training Priorities & Deadline](#chenyu-000214)**: Two targets—an ~8B model (trainable on 1 GPU) and a much larger model for 8× MI350; mid-May deadline; needs flash attention (8K context) and correct gradient accumulation.
- **[Gradient Accumulation Should Match Exactly](#geohot-000404)**: Expect accumulation to be equivalent to non-accumulation (aside from numeric differences), so discrepancies indicate a bug.
- **[Float16 vs BF16 Concern](#geohot-000519)**: Surprise that BERT is using float16 (not bfloat16), raising numeric stability concerns during accumulation/debugging.
- **[JIT “Foot-guns” & Guardrails](#geohot-000639)**: Known JIT pitfalls were merged; plan to add stronger checks so JIT can’t silently produce wrong outputs.
- **[Validate JIT Inputs / Buffers](#geohot-000709)**: Add verification that all JIT inputs are in correct format/buffered to catch subtle mistakes early.
- **[JIT Must Reject Schedule-Cast Mismatches](#geohot-000758)**: Proposed “ironclad” check: if two runs produce different schedule-casts, JIT should not be accepted (preventing silent incorrectness).
- **[Flash Attention Status](#wozeparrot-000952)**: Flash attention mostly implemented; Q/V gradients working, K-gradient still tricky; currently tested on MI350 and expected to work on MI300 too.
- **[No Silent Flash-Attention Fallback](#geohot-001035)**: If flash attention can’t run (shape/multiple constraints), it should error clearly rather than silently falling back or being wrong.
- **[MI300 Driver Progress](#nimlgen-001728)**: MI300 support merged; remaining work includes warm startup/reset handling and clock tuning (performance close but not yet ideal).
- **[Warm Reset Required](#geohot-001805)**: Must fix warm reset—can’t require a full reset between tinygrad runs; MI300/MI350 expected to be very similar.
- **[XGMI Reset & Unified Address Space Notes](#nimlgen-001940)**: XGMI systems require coordinated reset across all GPUs; each GPU can see other GPUs’ physical addresses (unified space), with a page-table “system flag” steering PCI vs XGMI traffic.
- **[All-Reduce Bandwidth as Next Target](#geohot-002145)**: Start testing/optimizing all-reduce bandwidth; topology isn’t a simple ring, may need different algorithms; also want graceful fallback when XGMI isn’t available.
- **[Firmware Emulator & Replacement Firmware Work](#geohot-002531)**: Built an emulator for firmware (E4/E5 commands working) and iterating on replacement firmware using the emulator as a stable reference loop.
- **[Viz Improvements](#qazalin-002636)**: Added a kernel scoreboard (all kernels + counters in one view) and focused on benchmarking “hip kittens” against internal code.
- **[Fast GEMM Not Correct Yet](#qazalin-002719)**: Fast GEMM attempts are producing incorrect results; suggestion to find a fast kernel that’s readable/profileable (Mojo kernel noted as promising).
- **[Make Assembly Easier to Read via Visualization](#geohot-002959)**: Assembly is hard to follow due to jump targets; proposed visualizing basic blocks/edges (IDA-style) using existing graph tooling.
- **[Multi-User / Multi-Process MMU Crash Repro](#b1tg-003434)**: Reported reproducible MMU crashes when training on multi-GPU and another process opens/uses the AMD device; shared a minimal repro.
- **[Crash Reproduces Even Without the IOCTL](#geohot-003954)**: Confirmed the MMU crash can happen with two normal tinygrad processes even after commenting out the specific ioctl in the repro, suggesting deeper driver/runtime instability.
- **[FP8 Training: Contiguous to Avoid Slow Fusion](#b1tg-004315)**: Adding `contiguous` before/after linear improved step time (avoids slow fused “gate” pattern); reported ~7% memory savings and speed improvements.
- **[Custom FP8 Backward vs Multi](#geohot-004710)**: Unsure whether multi sharding works with custom kernels/backward paths; plan to add a dedicated multi test for custom kernels.
- **[Image DType Alignment Strategy](#chrism-005055)**: Image dtype requires width to be 64-byte aligned; plan is to pad at the cast boundary (where image dtype is introduced) rather than enforcing everywhere.
- **[Remove ctypes Struct Overhead](#chrism-005828)**: PR to remove/replace ctypes structure usage for speed and cleaner API; avoid silent wrongness (assertive behavior), accept minor limitations (e.g., signed bitfields).
- **[GitHub Runner Zombie Processes](#geohot-010512)**: Timeouts can leave child processes running; fix via “defense in depth” (kill script at job start + investigate Python multiprocessing + GitHub cleanup behavior).
- **[TinyGrad App LLM: Memory-Speed & Minimal OpenAI Server](#geohot-010719)**: App LLM now reaches near memory bandwidth with fixes; added a minimal OpenAI-compatible server flag; plans include Qwen support and improving prefill performance.

### Transcript
##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=_mJIF112c5k&t=0)]
Okay, welcome everyone to our, I think, conference meeting. So next week will be new meeting number one. But anyway, let's start with company update.

##### **Nimlgen** [[00:00:16](https://www.youtube.com/watch?v=_mJIF112c5k&t=16)]
We sold two more Blackwell boxes, so we're selling a lot of those.

##### **Geohot** [[00:00:21](https://www.youtube.com/watch?v=_mJIF112c5k&t=21)]
But TinyBox Red was down, we've been skipping. So we're going to put fragile stickers on the box that change color if the boxes drop.

##### **Nimlgen** [[00:00:31](https://www.youtube.com/watch?v=_mJIF112c5k&t=31)]
So that was the main thing we had to deal with there. Yeah, I don't think things are going pretty well on the TinyBox front.

##### **Geohot** [[00:00:44](https://www.youtube.com/watch?v=_mJIF112c5k&t=44)]
I mean, I posted that thing about the new hardware. That's eventually what I want to sell. I just want to sell racks of GPUs, no computers. Just GPUs. Racks, PCI switches, Ethernet cards, you know, a pay-to-flop, an exo-flop that you can control from a single computer. That's kind of where our hardware is going. And we can switch out pieces with our own pieces, figure out what we're overpaying for. Are we overpaying for GPUs? Are we overpaying for PCI switches? Are we overpaying for metal boxes? Just drive the cost of everything as well as possible. Come on, that's a pay-to-flop. Let's sell interchangeable contracts. I bought this. I can have any GPU in them. And it's just a question of, you know, cost per dollar, gigabytes per second per dollar, gigabytes per dollar. You know, reduce these things to the raw specs. But I think in order to reduce the things to the raw specs, we have to get it to the point that this is actually abstracted. Nobody wants it abstracted. AMD doesn't want it abstracted. Nvidia doesn't want it abstracted. They want you to think about what kind of computer you're using. And we want to make sure that you do not have to think about what kind of computer you're using. So that is the long-term vision of TinyCraft and TinyCore to sell boxes that you never have to think about what type of GPU is not.

##### **Nimlgen** [[00:02:04](https://www.youtube.com/watch?v=_mJIF112c5k&t=124)]
Okay. Great.

##### **Nimlgen** [[00:02:13](https://www.youtube.com/watch?v=_mJIF112c5k&t=133)]
Okay.

##### **Chenyu** [[00:02:14](https://www.youtube.com/watch?v=_mJIF112c5k&t=134)]
Let's move on to Lava training. We can talk about prioritization. So two main targets. One of them is training 8B model, which is small enough to be able to train on one GPU. Then there's 4 or 5B, the very big Lava, that should be trained on 8 or MI350. That's the contract. And the deadline is like May 10th or something like that, mid-May. So I think to make 8B training, we need flash attention. Because memory to train like 8K window is big. Then in general, we need gradient accumulation to work correctly. It's a must for the big Lava and it's nice to have for smaller Lava. So I can talk more about the gradient accumulation. I have been working on that, applying the gradient accumulation on BERT this last week and find a bunch of issues. I'm not sure if you guys are familiar with the gradient accumulation, but I'm sure you guys are familiar with the gradient accumulation. So I want to start with BERT, just because I know much we have trained a lot of BERT wrongs. So I know what the loss should be look like because I find it very tricky to debug something like silently fail. And you really only notice after an hour of training. That's pretty annoying. So for now, I have a gradient accumulation that. I think is working. If you, if you split the mini badge and the optimizer stats, I think it's going to work. It's going to be a little bit of a challenge. So I'm going to take that into account. But it only works if I call the mini badge once. And this is very weird. I think something is not updated correctly.

##### **Geohot** [[00:04:04](https://www.youtube.com/watch?v=_mJIF112c5k&t=244)]
We should be able to compare it perfectly, right? Like gradient accumulation, if you're not using Batstorm, it should be exactly equal, except for numeric instability.

##### **Chenyu** [[00:04:13](https://www.youtube.com/watch?v=_mJIF112c5k&t=253)]
Yes. So for very small tests, it all works. Very weird. So any, any smaller tests, it's going to be a little bit of a challenge. I mean, you can �hairin this just to be I mean, you can extend the line so I guess you can just let them be aroundável in kind of match. That's why it's very weird. But anyway, I I updated the backward behavior to use a sign. That's the. Meep. So that's one.

##### **Geohot** [[00:04:46](https://www.youtube.com/watch?v=_mJIF112c5k&t=286)]
When you're testing it without the accumulation, are you just setting the accumulation to one, or are you testing a totally different code path? Because it could be something like this.

##### **Chenyu** [[00:04:55](https://www.youtube.com/watch?v=_mJIF112c5k&t=295)]
I set the accumulation to one.

##### **Geohot** [[00:04:57](https://www.youtube.com/watch?v=_mJIF112c5k&t=297)]
And that worked?

##### **Chenyu** [[00:04:59](https://www.youtube.com/watch?v=_mJIF112c5k&t=299)]
Yes. I mean, work is a stretch, because it trends to a much better eval, but it doesn't trend to the end because of other numerical issues. You can maybe change some numericals, maybe not use float16. But that looks much correct.

##### **Geohot** [[00:05:19](https://www.youtube.com/watch?v=_mJIF112c5k&t=319)]
Oh, wait. We're using float16? We're not using bfloat16?

##### **Chenyu** [[00:05:24](https://www.youtube.com/watch?v=_mJIF112c5k&t=324)]
We don't. Bert was training fine with float16.

##### **Geohot** [[00:05:28](https://www.youtube.com/watch?v=_mJIF112c5k&t=328)]
I mean, yeah, but float16 is. No, no, no.

##### **Chenyu** [[00:05:32](https://www.youtube.com/watch?v=_mJIF112c5k&t=332)]
So it cannot. I understand that there are somewhere divided by the gradient accumulation number. Right. So it's a bit worse. But it should only affect convergence a bit and not having eval basically being 0. Eval being 0 is just wrong, I think.

##### **Geohot** [[00:05:50](https://www.youtube.com/watch?v=_mJIF112c5k&t=350)]
Yeah, no, it definitely shouldn't be 0, sure. If you're saying it's zero, but you're saying it's converging worse, I can believe that.

##### **Chenyu** [[00:05:56](https://www.youtube.com/watch?v=_mJIF112c5k&t=356)]
Yeah, yeah, yeah. So I have some tests, some fit, foot gone. I think that pretty much align with my expectation now. I also have some tests, like tests like smallerBert and smallerBert with fit and gradient accumulation, making sure the gradient numbers are correct, as if it has no jit and fit into a single batch. And all those all match. So I will probably merge those tests later as well. But for now, it's in a very weird state that I can probably fit more. But that's where I am now.

##### **Nimlgen** [[00:06:37](https://www.youtube.com/watch?v=_mJIF112c5k&t=397)]
OK. Thank you.

##### **Geohot** [[00:06:39](https://www.youtube.com/watch?v=_mJIF112c5k&t=399)]
I merged that jit, foot gone thing. I mean, that's all the ones Claude found. They're like the known ones. But they're all kind of obvious or impossible.

##### **Chenyu** [[00:06:49](https://www.youtube.com/watch?v=_mJIF112c5k&t=409)]
Yeah, so yeah, yeah. So I think it would be nice to have some asserts saying, I don't know what's the best way to do this, because I don't know what's the definition for obvious things that needs to be updated but not updating or not tracked correctly.

##### **Geohot** [[00:07:09](https://www.youtube.com/watch?v=_mJIF112c5k&t=429)]
Yeah, I mean, I can at least, yeah, what I can do is I can add some stuff to check all the inputs to the jit and make sure their format is correct. Because right now, we're only checking some of them. And this default one kind of broke with the ShapeTracker. I can definitely work on that this week, which will help you. Basically, it's like if you did something for weight, say you multiplied a weight by two on one of your jits,

##### **Nimlgen** [[00:07:29](https://www.youtube.com/watch?v=_mJIF112c5k&t=449)]
we can detect that and be like, no, no, no, you messed it up. So the inputs we explicitly read, we're going to have to do this.

##### **Geohot** [[00:07:39](https://www.youtube.com/watch?v=_mJIF112c5k&t=459)]
We need to show that we realize. And I'll leave those that it realizes. But on the other ones, I'll just run a quick pass to detect if any of them are not buffered.

##### **Chenyu** [[00:07:47](https://www.youtube.com/watch?v=_mJIF112c5k&t=467)]
Yeah, I think something like that would definitely be helpful. I think having jits just output something slightly wrong, especially in a very big model training run, is very hard to work with.

##### **Geohot** [[00:07:58](https://www.youtube.com/watch?v=_mJIF112c5k&t=478)]
Yeah, OK, I can work on a lot of that. I can also another like kind of what I should really add to the jit is just make sure that it runs, like, Like, two runs have the same schedule cast before we JIT them? Things without the JIT should be a lot faster now that we have schedule cast.

##### **Chenyu** [[00:08:17](https://www.youtube.com/watch?v=_mJIF112c5k&t=497)]
It's just tricky if you want to do the BERT training. I tried that without JIT, and it's, I don't know, it's very slow. It's still really slow. So, I let it run overnight so that I at least have something to compare with. But no, it's just too slow.

##### **Nimlgen** [[00:08:36](https://www.youtube.com/watch?v=_mJIF112c5k&t=516)]
Okay.

##### **Geohot** [[00:08:37](https://www.youtube.com/watch?v=_mJIF112c5k&t=517)]
Yeah, I'll look into that. I'll look into seeing if we can do.. I mean, I'd really like to do it at the schedule cast level, because if the JIT is capturing two different schedule casts, it should not accept the JIT. Like, it shouldn't JIT if they're..

##### **Chenyu** [[00:08:48](https://www.youtube.com/watch?v=_mJIF112c5k&t=528)]
Yeah, I think that makes sense.

##### **Geohot** [[00:08:50](https://www.youtube.com/watch?v=_mJIF112c5k&t=530)]
If the schedule cast is not changing. Yeah, and that's kind of like an ironclad way to do it. Like, that's.. It guarantees if there's different schedule casts, the JIT can never be correct. If they're the same schedule cast, it can still be wrong. But.. At least we can detect all of them, so..

##### **Nimlgen** [[00:09:09](https://www.youtube.com/watch?v=_mJIF112c5k&t=549)]
Cool.

##### **Chenyu** [[00:09:10](https://www.youtube.com/watch?v=_mJIF112c5k&t=550)]
Yeah. Yeah. The goal here is we have BERT working. I think this is similar to the strategy for float8. We first make it work on this much smaller thing. Then once we understand all the Fugong training lemmas should be, like, easier than BERT. BERT is slightly annoying with some, like, encoder, decoder stuff. I should.. Yeah. Once we fix these, lemma should be good. And I think we can talk about flash attention next. I think that's, like, very big to unlock some memory thing for 8K Windows.

##### **Wozeparrot** [[00:09:52](https://www.youtube.com/watch?v=_mJIF112c5k&t=592)]
So for flash attention, it's mostly there. I showed how to get it in today. Gradient for Q and V are working, and K is just being annoying because it's the most complicated gradient to do.

##### **Nimlgen** [[00:10:09](https://www.youtube.com/watch?v=_mJIF112c5k&t=609)]
But, yeah. I mean, it should just be in today.

##### **Geohot** [[00:10:13](https://www.youtube.com/watch?v=_mJIF112c5k&t=613)]
Great. Does it work on both the 300 and 350?

##### **Wozeparrot** [[00:10:17](https://www.youtube.com/watch?v=_mJIF112c5k&t=617)]
I've only been testing on 350. I haven't been testing on 300. But it should work on 300.

##### **Geohot** [[00:10:23](https://www.youtube.com/watch?v=_mJIF112c5k&t=623)]
Cool. Yeah, no, it would be good to try both. And then is it good about asserting if it's not the right multiple and stuff?

##### **Wozeparrot** [[00:10:33](https://www.youtube.com/watch?v=_mJIF112c5k&t=633)]
Not right now, but that's easy to add.

##### **Nimlgen** [[00:10:35](https://www.youtube.com/watch?v=_mJIF112c5k&t=635)]
Well, it's not. So, yeah. So, I'm going to try it out.

##### **Geohot** [[00:10:35](https://www.youtube.com/watch?v=_mJIF112c5k&t=635)]
Cool. Yeah, it just shouldn't be silently wrong, and it shouldn't silently fall back. Like, if it can't do the flash attention, it should say, I cannot do this flash attention. If you set a flag.

##### **Nimlgen** [[00:10:45](https://www.youtube.com/watch?v=_mJIF112c5k&t=645)]
Cool.

##### **Nimlgen** [[00:10:46](https://www.youtube.com/watch?v=_mJIF112c5k&t=646)]
And does it use the memory? Does it use the last memory? It should. Okay. I mean, it has to, yeah. That was the whole point of this. It's explicitly doing the buffering, so there's no way it can use. Yeah, that's good to check.

##### **Geohot** [[00:11:09](https://www.youtube.com/watch?v=_mJIF112c5k&t=669)]
Did the thing I was talking about work with the backward? Where you store the other tensor and, like, a tensor empty, and then..

##### **Nimlgen** [[00:11:14](https://www.youtube.com/watch?v=_mJIF112c5k&t=674)]
Yeah, that works fine.

##### **Nimlgen** [[00:11:16](https://www.youtube.com/watch?v=_mJIF112c5k&t=676)]
Great.

##### **Chenyu** [[00:11:18](https://www.youtube.com/watch?v=_mJIF112c5k&t=678)]
Oh, speaking of empty, I think I list in the test, I think JIT has some weird behavior with respect to the empty input, just because empty is represented differently or something like that. It's minor annoyance, not a real issue. Yeah.

##### **Geohot** [[00:11:37](https://www.youtube.com/watch?v=_mJIF112c5k&t=697)]
And any test you can give me, I will work on.. I'm here to, like, support this as best as I can. I think that's probably my best role. So I'm here to work on JIT foot guns this week. Yeah, I'll do the JIT schedule test, kind of quasi-merger, which should be a pretty universal way to catch a lot of bugs.

##### **Chenyu** [[00:11:56](https://www.youtube.com/watch?v=_mJIF112c5k&t=716)]
Great.

##### **Geohot** [[00:11:59](https://www.youtube.com/watch?v=_mJIF112c5k&t=719)]
Any tests you want to give me that are failing, anything you're like, I don't know how to deal with this, hopefully I was helpful with that other one about the.. It's basically, you have to realize the buffers on the batch norm. That's why the MLS broke.

##### **Chenyu** [[00:12:12](https://www.youtube.com/watch?v=_mJIF112c5k&t=732)]
Yeah, that I understand. And let's also cloud code figure out. So that was pretty cool.

##### **Geohot** [[00:12:17](https://www.youtube.com/watch?v=_mJIF112c5k&t=737)]
Yeah. Yeah. I don't know. I think if I'm using one cloud code, I'm less productive. If I can use three cloud codes and keep all the state in my mind, then I'm more productive with it.

##### **Chenyu** [[00:12:33](https://www.youtube.com/watch?v=_mJIF112c5k&t=753)]
Are you buying the $200? Oh, yeah.

##### **Geohot** [[00:12:37](https://www.youtube.com/watch?v=_mJIF112c5k&t=757)]
Feel free to buy the $200 one with tiny-credit credit cards. I think it's still worth it. Okay. Not only am I buying the $200 one, I'm exceeding the $200 one. Don't buy extra. Extra usage is a real rip off though. But I may buy two $200 accounts if I keep using it like those.

##### **Nimlgen** [[00:12:56](https://www.youtube.com/watch?v=_mJIF112c5k&t=776)]
Okay. Cool. I think this applies to other employees.

##### **Chenyu** [[00:13:04](https://www.youtube.com/watch?v=_mJIF112c5k&t=784)]
Cool. Cool. I'm going to buy this useful.

##### **Geohot** [[00:13:07](https://www.youtube.com/watch?v=_mJIF112c5k&t=787)]
Yeah, absolutely. I'm happy to buy anyone here. Well, I'll start with the $20 subscription. And then if you max out the $20 subscription, you can get the $100 one and then get the $200 one. It's totally worth it.

##### **Chenyu** [[00:13:18](https://www.youtube.com/watch?v=_mJIF112c5k&t=798)]
Oh, there's a $100 one?

##### **Geohot** [[00:13:19](https://www.youtube.com/watch?v=_mJIF112c5k&t=799)]
There's a $100 one too. Yeah. Yeah. Okay. Interesting. The $100 one is I think 10x more than the 20. And then the $200 one is 4x more than the 10. I don't know if you'd believe any of it. But if you try to use it without their subscription, if you try to like directly use the API, it's going to be a little bit more expensive. Yeah. I mean, I think it's totally worth it. I think we also have to stay very, very vigilant about not committing lots of crap to the repo. I think the TinyGrad philosophy is more apt than ever in the world of vibe coding. I think we've prepared for this in many ways.

##### **Chenyu** [[00:13:54](https://www.youtube.com/watch?v=_mJIF112c5k&t=834)]
Yeah. It's definitely good to keep the repos small so that you can read it. But I think another benefit is reading how Cloud Code use TinyGrad helps. It helps us to work on the documentation or the error message a lot because you will see how Cloud Code struggle and you can easily see other people using TinyGrad struggle in a similar way. And I think that's a good place to think about how to improve the user experience.

##### **Geohot** [[00:14:23](https://www.youtube.com/watch?v=_mJIF112c5k&t=863)]
Agreed. Yeah. It's an absolutely wonderful playtester. Cool. TinyGrad. So good. Even an LLM can use it. But I think we got a lot of things right. I felt such a shift last week. I realized that I'm going to have to change how I think about software engineering and how I do a lot of this stuff. But I think the core TinyGrad principles are more accurate than ever because LLMs generate tons of code and then they can't read the tons of code that they generate.

##### **Nimlgen** [[00:15:00](https://www.youtube.com/watch?v=_mJIF112c5k&t=900)]
Yeah.

##### **Geohot** [[00:15:05](https://www.youtube.com/watch?v=_mJIF112c5k&t=905)]
So yeah, I don't know how much better.. I don't know what would happen if I tried to get it to fix an issue or dork.

##### **Nimlgen** [[00:15:12](https://www.youtube.com/watch?v=_mJIF112c5k&t=912)]
I'm not even sure what it would do. Would it build dork?

##### **Geohot** [[00:15:22](https://www.youtube.com/watch?v=_mJIF112c5k&t=922)]
Just sit there and compile dork? I don't know about that.

##### **Chenyu** [[00:15:25](https://www.youtube.com/watch?v=_mJIF112c5k&t=925)]
I don't know. I feel my Cloud Code wastes a lot of tokens just trying to install dork.

##### **Geohot** [[00:15:33](https://www.youtube.com/watch?v=_mJIF112c5k&t=933)]
Yeah. I think we also need.. Yeah. I do want to work on tests. Like PyTest. You should just be able to type PyTest and auto and that's it. It's like under a minute on your computer.

##### **Nimlgen** [[00:15:47](https://www.youtube.com/watch?v=_mJIF112c5k&t=947)]
I think it's under a minute on Macs. I think it's like two minutes on my computer. That doesn't sound correct, but sure.

##### **Geohot** [[00:15:59](https://www.youtube.com/watch?v=_mJIF112c5k&t=959)]
Yeah. Everyone should test that. We have that channel for it now. Test failure. All the tests should be passing locally on your computer because that's what's really important for these Cloud Code things to work. If we can make a small test leak, a small repo, it would be very judgmental, judicious about what we let in.

##### **Nimlgen** [[00:16:25](https://www.youtube.com/watch?v=_mJIF112c5k&t=985)]
Opinionated. Opinionated, yeah. But I have..

##### **Geohot** [[00:16:32](https://www.youtube.com/watch?v=_mJIF112c5k&t=992)]
I don't know. Something happened last week and I feel like I've.. I don't know.

##### **Nimlgen** [[00:16:35](https://www.youtube.com/watch?v=_mJIF112c5k&t=995)]
I don't know.

##### **Geohot** [[00:16:35](https://www.youtube.com/watch?v=_mJIF112c5k&t=995)]
We've kind of seen the future and accept that, like, the identics coding workflows are going to really be here to stay.

##### **Chenyu** [[00:16:43](https://www.youtube.com/watch?v=_mJIF112c5k&t=1003)]
Great. So, yeah. Encourage everyone to give it a test. Yeah, if any.. You'd be really fast.

##### **Geohot** [[00:16:54](https://www.youtube.com/watch?v=_mJIF112c5k&t=1014)]
DM me if you want to buy it and you don't have access to it, and I will give you a credit card number.

##### **Nimlgen** [[00:17:03](https://www.youtube.com/watch?v=_mJIF112c5k&t=1023)]
If you work here.

##### **Nimlgen** [[00:17:04](https://www.youtube.com/watch?v=_mJIF112c5k&t=1024)]
Yeah. I'm in a hurry right now.

##### **Chenyu** [[00:17:05](https://www.youtube.com/watch?v=_mJIF112c5k&t=1025)]
Okay, great. And I think the following three is more, it's also like essential and definitely helps for the goal. That's the MI-353 drivers, the FastJam and the CloudState. So we can start with the drivers.

##### **Nimlgen** [[00:17:28](https://www.youtube.com/watch?v=_mJIF112c5k&t=1048)]
Yeah, so merged MI-300 support. Still several things to do, including the annoying warm startup, which is missing right now. And yeah, also we'll tune clocks. I mean, speed is pretty close to the AMD GPU, but still. I mean, maybe 5% worth, the AMD GPU. So yeah, I'm also going to look into this.

##### **Nimlgen** [[00:18:03](https://www.youtube.com/watch?v=_mJIF112c5k&t=1083)]
Yeah.

##### **Geohot** [[00:18:05](https://www.youtube.com/watch?v=_mJIF112c5k&t=1085)]
Yeah, I tested it, it worked. I think the warm reset thing obviously has to be fixed. We can't have to reset it between every boot of tinygrad. And then MI-300 and MI-350 are almost the same.

##### **Nimlgen** [[00:18:26](https://www.youtube.com/watch?v=_mJIF112c5k&t=1106)]
Yeah, it should be pretty easy to port these. I mean, GFX, all major models are the same.

##### **Geohot** [[00:18:36](https://www.youtube.com/watch?v=_mJIF112c5k&t=1116)]
Great. Do you know if they're different on 250, just out of curiosity?

##### **Nimlgen** [[00:18:41](https://www.youtube.com/watch?v=_mJIF112c5k&t=1121)]
250, yeah, it should be different.

##### **Geohot** [[00:18:45](https://www.youtube.com/watch?v=_mJIF112c5k&t=1125)]
250 is different, okay.

##### **Nimlgen** [[00:18:46](https://www.youtube.com/watch?v=_mJIF112c5k&t=1126)]
I know. I need to check the GFX version.

##### **Geohot** [[00:18:50](https://www.youtube.com/watch?v=_mJIF112c5k&t=1130)]
Yeah. No, I don't think we should. We should wait. We should wait time on 250. I know that one guy bought one and like, it's probably the cheapest way to get 128 gigs of HBM, but yeah, no, it's not worth it. Yeah. And then I think also working on scheduling stuff for both the HVAC and for the interleaving of all that stuff being used and stuff. Yeah, I think we got to start working on all of the juice speeds. Yeah. Yeah. Maybe we start not using the DMA engine or price of things where we like, you know, leave the DMA engine differently, overlap differently, but I think that's going to become a big bottleneck in training.

##### **Nimlgen** [[00:19:40](https://www.youtube.com/watch?v=_mJIF112c5k&t=1180)]
Yes. Also, actually, we now have a separate script to reset MI-300 machines, actually, because you need to call the mode one reset at the same time on all machines.

##### **Geohot** [[00:19:54](https://www.youtube.com/watch?v=_mJIF112c5k&t=1194)]
Yeah. Yeah. It's on the high-reset script.

##### **Nimlgen** [[00:20:00](https://www.youtube.com/watch?v=_mJIF112c5k&t=1200)]
Yeah. So, no, our obstructions are not really good to implement this as easy as I am reset right now.

##### **Nimlgen** [[00:20:12](https://www.youtube.com/watch?v=_mJIF112c5k&t=1212)]
Yeah. Is it because of the PCI link that they all need to be reset together or what's the issue?

##### **Nimlgen** [[00:20:20](https://www.youtube.com/watch?v=_mJIF112c5k&t=1220)]
Yeah. Actually, because with these XGMI systems, you have to reset all of these. Yeah. Also, I want to try XGMI. I mean, actually, it's like all GPUs without any extension sees the physical addresses, all of other GPUs. So, I don't know. It would be really easy to replace PCI addresses, like to do P2P with the XGMI addresses. I know. Oh, yeah. This would..

##### **Geohot** [[00:20:53](https://www.youtube.com/watch?v=_mJIF112c5k&t=1253)]
How does this work? Do they show up as different addresses once over XGMI? Like, if I just have it mapped in, can I, like, set a flag in the page table and say whether it goes over XGMI or PCI?

##### **Nimlgen** [[00:21:05](https://www.youtube.com/watch?v=_mJIF112c5k&t=1265)]
I mean, every GPU sees the whole.. all other physical addresses of all other GPUs. Like, it's the unified space. You just have the outside.

##### **Geohot** [[00:21:17](https://www.youtube.com/watch?v=_mJIF112c5k&t=1277)]
If I do an access, is that access over XGMI or is it over PCI?

##### **Nimlgen** [[00:21:25](https://www.youtube.com/watch?v=_mJIF112c5k&t=1285)]
So, if you set the system flag, it goes over PCI. If no system flag, it will go, like, locally if this physical address is local or just through the XGMI.

##### **Geohot** [[00:21:38](https://www.youtube.com/watch?v=_mJIF112c5k&t=1298)]
Got it. Okay. So, the system flag is a flag on the page table entry.

##### **SPEAKER_05** [[00:21:42](https://www.youtube.com/watch?v=_mJIF112c5k&t=1302)]
Yeah. Yeah.

##### **Geohot** [[00:21:45](https://www.youtube.com/watch?v=_mJIF112c5k&t=1305)]
Yeah. I mean, I think we just want to start playing with, like, making sure we can get high.. Just do, like, the same way you did the test for the copy in and copy out. Just start doing tests on the all-reduce to make sure we're getting the full all-reduce bandwidth. I don't know if it's.. I know they're connected differently. I mean, they're not really connected in a ring, so we might need a different kind of all-reduce for them.

##### **Nimlgen** [[00:22:08](https://www.youtube.com/watch?v=_mJIF112c5k&t=1328)]
Yeah. All-reduce, whatever that is.

##### **Nimlgen** [[00:22:15](https://www.youtube.com/watch?v=_mJIF112c5k&t=1335)]
Yeah. Okay. After fixing everything and adding in my 350, yeah, I'll.. I'll look into XGMI.

##### **Geohot** [[00:22:25](https://www.youtube.com/watch?v=_mJIF112c5k&t=1345)]
Yeah. I mean, just basically, like, all-reduce bandwidth should be.. I don't think.. Yeah. I don't think we have to worry about, like, XGMI versus non-XGMI yet, but just getting all-reduce bandwidth. Although, falling back from XGMI would be nice for making the tests work on my computer.

##### **Nimlgen** [[00:22:42](https://www.youtube.com/watch?v=_mJIF112c5k&t=1362)]
Yeah.

##### **Geohot** [[00:22:45](https://www.youtube.com/watch?v=_mJIF112c5k&t=1365)]
Yeah. I mean, I think we should kind of implement the same thing that HIP does, which is just, if it can't open the XGMI, it doesn't fail. It just.. It's just.. It's a flag saying XGMI not supported, and then we just go over CCIE.

##### **Nimlgen** [[00:22:59](https://www.youtube.com/watch?v=_mJIF112c5k&t=1379)]
And then if CCIE is not supported, too bad.

##### **Nimlgen** [[00:23:09](https://www.youtube.com/watch?v=_mJIF112c5k&t=1389)]
Okay.

##### **Nimlgen** [[00:23:09](https://www.youtube.com/watch?v=_mJIF112c5k&t=1389)]
I mean, not CCIE, but with a kernel. Okay.

##### **Nimlgen** [[00:23:16](https://www.youtube.com/watch?v=_mJIF112c5k&t=1396)]
Cool. Yeah.

##### **Geohot** [[00:23:17](https://www.youtube.com/watch?v=_mJIF112c5k&t=1397)]
My priority is my 300, my 350, and the AM driver, but we're getting that to work. Very exciting. Yeah. Well, it sounds like.. Okay. Now it's one less piece of AMD.

##### **Nimlgen** [[00:23:29](https://www.youtube.com/watch?v=_mJIF112c5k&t=1409)]
We just need to tape out our own at my freezer. I tweeted this a few days ago.

##### **Geohot** [[00:23:40](https://www.youtube.com/watch?v=_mJIF112c5k&t=1420)]
I really think that once we get through all of this, that they're going to be really stable with just tiny grads. The hardware of these things is so simple compared to this software. Yeah. When you think about the actual chip design. Like, if you're like, George, you need to design a CPU. Forget it. I can't design a CPU. That's impossible. But design an accelerator for a neural network? I mean, the Tesla people did it in.. The Tesla people designed the first Tesla FSD chip. It was like a three-month project. And then they struggled for the next four years into getting anything to run. On the chip. So. We do that the other way. We struggle for four years to get things to run on other people's chips. And then we spend three months and we tape out the chip. Whatever it is. But first we have to be thinking about, you know, the long-term vision of these drivers. And this is what I always emphasize when I talk about, like, making the drivers run in tiny grads. Is that we can move all of this stuff off of the host machine. So basically the.. Whether we're using the CPU as a PCIe. Bridge or not doesn't matter. But we are able to configure the GPUs in a remote machine. Basically over the network card. And then eventually just replace that CPU with a PCI switch.

##### **Nimlgen** [[00:25:03](https://www.youtube.com/watch?v=_mJIF112c5k&t=1503)]
Does that seem.. Are there any reasons this doesn't work? No, like, theoretically, this should work.

##### **Geohot** [[00:25:18](https://www.youtube.com/watch?v=_mJIF112c5k&t=1518)]
Also, did you check out.. Did you check out the.. The firmware repo at all?

##### **Nimlgen** [[00:25:26](https://www.youtube.com/watch?v=_mJIF112c5k&t=1526)]
Not really deep enough. I just skimmed through the..

##### **Geohot** [[00:25:31](https://www.youtube.com/watch?v=_mJIF112c5k&t=1531)]
Yeah, no, I mean, this is mostly.. I think we've handed this mostly off to Kama. But I now have the full.. I have an emulator for the firmware too. So I'm emulating the firmware. I'm emulating it to the point that the E4 and E5 commands work in the emulator. And now I'm building the replacement firmware and making sure that the commands work in the replacement firmware. I'm going to test more and more. This is like a fun way I've found to like.. Do all this reverse engineering. Or rather, have Cloud Code do the reverse engineering. In such a way that it's reliable. Like, build the emulator. Don't touch the emulator. Work on the code. Work on the emulator on the original firmware. The loop.

##### **SPEAKER_05** [[00:26:12](https://www.youtube.com/watch?v=_mJIF112c5k&t=1572)]
Yeah.

##### **Geohot** [[00:26:12](https://www.youtube.com/watch?v=_mJIF112c5k&t=1572)]
Now that's the full.. That's what we've done with the USB 3. Full dominance over the chip. If you make it work over USB 3.

##### **Nimlgen** [[00:26:21](https://www.youtube.com/watch?v=_mJIF112c5k&t=1581)]
Yeah. Yeah. Yeah. Cool. Okay.

##### **Nimlgen** [[00:26:29](https://www.youtube.com/watch?v=_mJIF112c5k&t=1589)]
Next we have Viz. And the FastGem. For the Viz.

##### **Qazalin** [[00:26:36](https://www.youtube.com/watch?v=_mJIF112c5k&t=1596)]
Viz has some quality of life improvements. There is a kernel scoreboard that you can see at the first graph. It's basically all the kernels in one place with all the counters. It's been really useful. I'm just.. Mostly.. Mostly.. Spending time with hip kittens. And benchmarking those stuff against our code.

##### **Nimlgen** [[00:27:02](https://www.youtube.com/watch?v=_mJIF112c5k&t=1622)]
And also, like, Viz right now starts fast. We're complaining about the LM.c speed that's fast now. Yeah. What did the GEMM work?

##### **Qazalin** [[00:27:19](https://www.youtube.com/watch?v=_mJIF112c5k&t=1639)]
The GEMM.. Isn't correct. Yeah.

##### **Wozeparrot** [[00:27:24](https://www.youtube.com/watch?v=_mJIF112c5k&t=1644)]
That's what I experienced. Because I've tried adding their GEMM into our repo too. And I could just not get it to get correct answers.

##### **Geohot** [[00:27:34](https://www.youtube.com/watch?v=_mJIF112c5k&t=1654)]
So, yeah. I mean, I tried it in their repo and it gave wrong answer. I had to comment out a few of their, like, their, like, work specialization stuff. And, like, eventually I got it to work. But I think that their thing is not correct. And it just happened to work with whatever version of the repo.

##### **Nimlgen** [[00:27:51](https://www.youtube.com/watch?v=_mJIF112c5k&t=1671)]
I didn't have a copy of the version of the compiler that they had. Another interesting..

##### **Geohot** [[00:28:00](https://www.youtube.com/watch?v=_mJIF112c5k&t=1680)]
So, you could also look at the Mojo kernel. The Mojo kernel gets about a pay-to-flop. And seems reliable.

##### **Nimlgen** [[00:28:08](https://www.youtube.com/watch?v=_mJIF112c5k&t=1688)]
I'm not sure what they're doing. But.. Sure. Yeah.

##### **Qazalin** [[00:28:17](https://www.youtube.com/watch?v=_mJIF112c5k&t=1697)]
I think that that would be my approach. Like, find a fast kernel that I can read. Not in raw assembly, something I can read and then profile it.

##### **Geohot** [[00:28:28](https://www.youtube.com/watch?v=_mJIF112c5k&t=1708)]
Yeah, I'm not sure the Mojo one is that readable. And I think their other one is in raw assembly too. I mean, it's unfortunate that it looks like you kind of need assembly in order to get it to not be stupid with the register allocator.

##### **Nimlgen** [[00:28:44](https://www.youtube.com/watch?v=_mJIF112c5k&t=1724)]
Or at least register pinning.

##### **Geohot** [[00:28:51](https://www.youtube.com/watch?v=_mJIF112c5k&t=1731)]
When I played with this on stream, it would just be so wasteful with the registers. It would do all these moves. And I'm like, why is it doing this?

##### **Nimlgen** [[00:28:58](https://www.youtube.com/watch?v=_mJIF112c5k&t=1738)]
But yeah, I mean, I like that general approach.

##### **Geohot** [[00:29:05](https://www.youtube.com/watch?v=_mJIF112c5k&t=1745)]
That's some fast kernel. Even if it is an assembly, right?

##### **Nimlgen** [[00:29:09](https://www.youtube.com/watch?v=_mJIF112c5k&t=1749)]
Because fundamentally, all the SQTT stuff is on assembly.

##### **Qazalin** [[00:29:21](https://www.youtube.com/watch?v=_mJIF112c5k&t=1761)]
Yeah, I think that would be my last resort. And the problem is that's shared, but I can't read it. Even if the machine can execute it.

##### **Nimlgen** [[00:29:32](https://www.youtube.com/watch?v=_mJIF112c5k&t=1772)]
What's hard to read?

##### **Qazalin** [[00:29:40](https://www.youtube.com/watch?v=_mJIF112c5k&t=1780)]
For me, the jumps are really hard to reason about. Like I had this problem with the emulator too. Like, okay, where did it jump? With SQTT, it's nicer. Because you can see the instrument. Instruction stream. But still.

##### **Nimlgen** [[00:29:56](https://www.youtube.com/watch?v=_mJIF112c5k&t=1796)]
Yeah. You almost want a..

##### **Geohot** [[00:29:59](https://www.youtube.com/watch?v=_mJIF112c5k&t=1799)]
Like, you almost want a dialect somewhere between C and assembly. Where the loops look like C loops. And you can still do.. So another thing that I found annoying in the assembly is it just puts all these instructions. That are just like sequentially adding the registers. Which could totally be a loop. But then not have.. Like, still be a perfect.. Like, assembly is a perfect one-to-one to machine code. Whereas C is not. It would be interesting to think about what, like, an intermediate dialect would look like. I don't know. If there's some way we could just kind of like.. Or, have you ever seen, like, the.. Have you ever seen, like, Aida?

##### **Nimlgen** [[00:30:43](https://www.youtube.com/watch?v=_mJIF112c5k&t=1843)]
You know, like, Aida the contemplator? No. No. Look it up.

##### **Geohot** [[00:30:53](https://www.youtube.com/watch?v=_mJIF112c5k&t=1853)]
We may want to do like that for the assembly. So do you know what a basic block is?

##### **Nimlgen** [[00:31:00](https://www.youtube.com/watch?v=_mJIF112c5k&t=1860)]
Sure, yeah.

##### **Geohot** [[00:31:02](https://www.youtube.com/watch?v=_mJIF112c5k&t=1862)]
Yeah, I mean, it may be worth breaking.. If you're finding the loops hard to read. I find this hard to read, too. Like, the way that objgum outputs the assembly with just having, like, L jump 12. Okay, that's 12.

##### **Qazalin** [[00:31:12](https://www.youtube.com/watch?v=_mJIF112c5k&t=1872)]
Where's 12? Where's 12?

##### **Geohot** [[00:31:14](https://www.youtube.com/watch?v=_mJIF112c5k&t=1874)]
I'm looking for 12, right? So what you could do.. And this is all a visualization thing. And I think it's worth doing. is you can break the code into basic blocks like IDOC.

##### **Nimlgen** [[00:31:27](https://www.youtube.com/watch?v=_mJIF112c5k&t=1887)]
Let me show you. If you search for IDOC, you'll see what it looks like.

##### **Geohot** [[00:31:36](https://www.youtube.com/watch?v=_mJIF112c5k&t=1896)]
Remember, CPU code has a lot more branches than GPU code. But I think you might want to make the visualizer of the assembler look like this. And it's pretty perfect because it can reuse all of our existing graph logic. Like it's not something that's different. It's just, it's vis basically.

##### **Chrism** [[00:31:56](https://www.youtube.com/watch?v=_mJIF112c5k&t=1916)]
Even like objjump visualized jumps also goes a long way.

##### **Geohot** [[00:32:01](https://www.youtube.com/watch?v=_mJIF112c5k&t=1921)]
Yeah, maybe we just objjump visualized jumps and just put that in. Does it draw like arrows and stuff?

##### **Chrism** [[00:32:07](https://www.youtube.com/watch?v=_mJIF112c5k&t=1927)]
Yeah, it does. It just puts them on the side.

##### **Geohot** [[00:32:09](https://www.youtube.com/watch?v=_mJIF112c5k&t=1929)]
Yeah, that would be cool. Yeah, we already have a full like graph visualizer. So if we just put the basic blocks inside, instead of graph like inside of things like that, I think it would look cool.

##### **Nimlgen** [[00:32:22](https://www.youtube.com/watch?v=_mJIF112c5k&t=1942)]
It'd be like a lot easier to see. We can certainly start with the simplest thing.

##### **Geohot** [[00:32:30](https://www.youtube.com/watch?v=_mJIF112c5k&t=1950)]
Yeah, so the question was like, like kind of more of this, like if you find the assembly hard to read, do you think this is inherent to the assembly

##### **Nimlgen** [[00:32:39](https://www.youtube.com/watch?v=_mJIF112c5k&t=1959)]
or do you think this is a visualization issue? Visualization issue. Right, let's improve the visualizing. Right, like we can improve visualizing. All right, say that again.

##### **Qazalin** [[00:32:56](https://www.youtube.com/watch?v=_mJIF112c5k&t=1976)]
The assembly is trivial, like every instruction I can reason about it.

##### **Nimlgen** [[00:33:02](https://www.youtube.com/watch?v=_mJIF112c5k&t=1982)]
Chris, you can read that.

##### **Chrism** [[00:33:04](https://www.youtube.com/watch?v=_mJIF112c5k&t=1984)]
That one's pretty bad, but that's the example.

##### **Nimlgen** [[00:33:07](https://www.youtube.com/watch?v=_mJIF112c5k&t=1987)]
Yeah, sure.

##### **Geohot** [[00:33:09](https://www.youtube.com/watch?v=_mJIF112c5k&t=1989)]
I mean, it's certainly better than 12.

##### **Qazalin** [[00:33:14](https://www.youtube.com/watch?v=_mJIF112c5k&t=1994)]
Now you have to follow this line with the dashes.

##### **Chrism** [[00:33:19](https://www.youtube.com/watch?v=_mJIF112c5k&t=1999)]
Yeah, okay. That one's a pretty bad example, but hopefully the GPU code isn't so bad.

##### **Geohot** [[00:33:26](https://www.youtube.com/watch?v=_mJIF112c5k&t=2006)]
Yeah, but I think anything we can do. I also have, so this is my tool that I wrote a long time ago, called Hero.

##### **Nimlgen** [[00:33:38](https://www.youtube.com/watch?v=_mJIF112c5k&t=2018)]
It never really did have a graph view.

##### **Geohot** [[00:33:41](https://www.youtube.com/watch?v=_mJIF112c5k&t=2021)]
It did have a graph view too. I don't know. I guess I never really used it. Yeah, I mean, breaking the basic blocks up, into graph nodes, or adding arrows is all better than GUM12.

##### **Nimlgen** [[00:33:55](https://www.youtube.com/watch?v=_mJIF112c5k&t=2035)]
Yeah, that's good.

##### **Nimlgen** [[00:34:03](https://www.youtube.com/watch?v=_mJIF112c5k&t=2043)]
Okay.

##### **Chenyu** [[00:34:12](https://www.youtube.com/watch?v=_mJIF112c5k&t=2052)]
So that was crash scan. And do you want to do that? Do you have anything update for the float 8? I saw that you have one GPU training.

##### **Nimlgen** [[00:34:26](https://www.youtube.com/watch?v=_mJIF112c5k&t=2066)]
Oh.

##### **B1tg** [[00:34:30](https://www.youtube.com/watch?v=_mJIF112c5k&t=2070)]
Can you hear me?

##### **Chenyu** [[00:34:31](https://www.youtube.com/watch?v=_mJIF112c5k&t=2071)]
Oh, yes.

##### **Nimlgen** [[00:34:33](https://www.youtube.com/watch?v=_mJIF112c5k&t=2073)]
Oh.

##### **B1tg** [[00:34:34](https://www.youtube.com/watch?v=_mJIF112c5k&t=2074)]
First, I want to talk about MMU repo. So now when a train runs on more than one GPU, you do, you do anything to the two GPU, like create a tensor can cause the MMU. Even open the KFD and do a simple IOCTL. I have a one-fail repo in the channel. Not sure Nimjin want a repo like this.

##### **Nimlgen** [[00:35:13](https://www.youtube.com/watch?v=_mJIF112c5k&t=2113)]
Yes. That's great. If you have a small repo of the MMU failure. Yeah. Nimjin, have you checked that one?

##### **Nimlgen** [[00:35:28](https://www.youtube.com/watch?v=_mJIF112c5k&t=2128)]
No.

##### **Nimlgen** [[00:35:30](https://www.youtube.com/watch?v=_mJIF112c5k&t=2130)]
Wait, which one is it?

##### **Geohot** [[00:35:32](https://www.youtube.com/watch?v=_mJIF112c5k&t=2132)]
I didn't see this either.

##### **Chenyu** [[00:35:33](https://www.youtube.com/watch?v=_mJIF112c5k&t=2133)]
The one in BERT channel.

##### **B1tg** [[00:35:36](https://www.youtube.com/watch?v=_mJIF112c5k&t=2136)]
And they are perfect. But as,

##### **SPEAKER_05** [[00:35:41](https://www.youtube.com/watch?v=_mJIF112c5k&t=2141)]
and now basically,

##### **B1tg** [[00:35:43](https://www.youtube.com/watch?v=_mJIF112c5k&t=2143)]
if I was only user on the, I don't know, on the MIS350. And I run the train. It goes well. If other, other user come here to do something like a run a simple test script, the GPU at crashed.

##### **Nimlgen** [[00:36:08](https://www.youtube.com/watch?v=_mJIF112c5k&t=2168)]
No,

##### **Geohot** [[00:36:17](https://www.youtube.com/watch?v=_mJIF112c5k&t=2177)]
No, I don't exactly follow this. It's making an iOctal? What is KFDIOC runtime-enabled now?

##### **B1tg** [[00:36:25](https://www.youtube.com/watch?v=_mJIF112c5k&t=2185)]
This is taken from the KFDIOC code. Like if you create a tensor to do real.. OpenTensor on GPU, this will be called. I just put here as a simple repo.

##### **Nimlgen** [[00:36:54](https://www.youtube.com/watch?v=_mJIF112c5k&t=2214)]
I mean, our code that's crashing clearly isn't doing that. What?

##### **Geohot** [[00:37:05](https://www.youtube.com/watch?v=_mJIF112c5k&t=2225)]
I mean, our code that's crashing clearly isn't.. I don't understand exactly how.. If I run this, I'll get the MMU crash.

##### **Nimlgen** [[00:37:16](https://www.youtube.com/watch?v=_mJIF112c5k&t=2236)]
Yes. I'm trying it now. And then what if I comment out the iOctal? It'll crash or not?

##### **B1tg** [[00:37:30](https://www.youtube.com/watch?v=_mJIF112c5k&t=2250)]
You have tried it?

##### **Geohot** [[00:37:33](https://www.youtube.com/watch?v=_mJIF112c5k&t=2253)]
I'm trying it now.

##### **Nimlgen** [[00:37:36](https://www.youtube.com/watch?v=_mJIF112c5k&t=2256)]
Yeah.

##### **Nimlgen** [[00:37:37](https://www.youtube.com/watch?v=_mJIF112c5k&t=2257)]
You can see the.. I can see the log in the T message. Yeah. I mean, I definitely see the crash in D method.

##### **Geohot** [[00:38:08](https://www.youtube.com/watch?v=_mJIF112c5k&t=2288)]
What happens if I comment out the iOctal?

##### **B1tg** [[00:38:14](https://www.youtube.com/watch?v=_mJIF112c5k&t=2294)]
This should be okay. The repo script just shows that if you run a train and another user to use 10G to open the AMD device, a crash happens.

##### **Nimlgen** [[00:38:33](https://www.youtube.com/watch?v=_mJIF112c5k&t=2313)]
Oh. So as long as you have 10G, you can run the crash. So if we put a lock on it, you think that would fix it?

##### **B1tg** [[00:38:42](https://www.youtube.com/watch?v=_mJIF112c5k&t=2322)]
Yeah.

##### **Nimlgen** [[00:38:44](https://www.youtube.com/watch?v=_mJIF112c5k&t=2324)]
Okay.

##### **B1tg** [[00:38:45](https://www.youtube.com/watch?v=_mJIF112c5k&t=2325)]
I don't know how the GPU multi-user works. So..

##### **Geohot** [[00:38:52](https://www.youtube.com/watch?v=_mJIF112c5k&t=2332)]
If I comment out the iOctal and I run this two times, is that gonna cause a problem?

##### **B1tg** [[00:39:00](https://www.youtube.com/watch?v=_mJIF112c5k&t=2340)]
No. If you run the train on a multi-tpu and.. Then in another terminal, you develop a tinygrad, run some test, it can trigger the bug.

##### **Nimlgen** [[00:39:21](https://www.youtube.com/watch?v=_mJIF112c5k&t=2361)]
It is okay on the.. Which machine?

##### **B1tg** [[00:39:31](https://www.youtube.com/watch?v=_mJIF112c5k&t=2371)]
AMD 300. 300 is old.

##### **Geohot** [[00:39:36](https://www.youtube.com/watch?v=_mJIF112c5k&t=2376)]
I'm reproducing this for you. It's right now on the 300. I commented out all of the.. I commented out the iOctal, and I'm just running two copies of that.

##### **Nimlgen** [[00:39:47](https://www.youtube.com/watch?v=_mJIF112c5k&t=2387)]
And it's causing the fault.

##### **Geohot** [[00:39:54](https://www.youtube.com/watch?v=_mJIF112c5k&t=2394)]
I took your MMU crash script, I commented out the iOctal, and I just ran it in two different Tmoxes, and I see the crash. Yeah. So.. Yeah, Nimilden. Is this something we're doing? Is this something we're doing wrong? Or is this something that..

##### **Nimlgen** [[00:40:12](https://www.youtube.com/watch?v=_mJIF112c5k&t=2412)]
Is broken in the AMD driver?

##### **B1tg** [[00:40:19](https://www.youtube.com/watch?v=_mJIF112c5k&t=2419)]
The iOctal is basically what we do in the.. When we open the AMD GPU, we have this code.

##### **Geohot** [[00:40:32](https://www.youtube.com/watch?v=_mJIF112c5k&t=2432)]
Oh, but yeah, exactly.

##### **B1tg** [[00:40:34](https://www.youtube.com/watch?v=_mJIF112c5k&t=2434)]
Yes. Yes.

##### **Geohot** [[00:40:36](https://www.youtube.com/watch?v=_mJIF112c5k&t=2436)]
What I'm saying is.. I commented out the.. Yeah, I commented out the iOctal, and I just ran normal TinyGrad in two processes, and I get the crash. Now it looks like I broke the whole computer. Yeah, I mean, and Nimilden, is there anything we're doing wrong?

##### **Nimlgen** [[00:40:59](https://www.youtube.com/watch?v=_mJIF112c5k&t=2459)]
Actually, I mean, no idea about that. I mean, I haven't reported it with, like, a lot of people. But it's weird. I've seen, like, two parallel pits, but.. Actually, what I've seen before, it was pretty strange, and I think it's something related to the.. Maybe.. Something preemption or something like that, because it was non-deterministic in different kernels, and I know, I can look into that. That's definitely easy example to follow. But actually, for B1TG, have you tried this with heap?

##### **B1tg** [[00:41:36](https://www.youtube.com/watch?v=_mJIF112c5k&t=2496)]
Oh, I didn't.

##### **Nimlgen** [[00:41:37](https://www.youtube.com/watch?v=_mJIF112c5k&t=2497)]
Let's reproduce that with hip. I'll try it with hip right now.

##### **Chenyu** [[00:41:49](https://www.youtube.com/watch?v=_mJIF112c5k&t=2509)]
Previously, when I hit MMU fold, I tried it with hip, and hip was fine. I don't know if this is a SM issue.

##### **Geohot** [[00:41:57](https://www.youtube.com/watch?v=_mJIF112c5k&t=2517)]
Yeah, I mean, this could also just be a totally different issue. I don't know. I think the real strategy here is just use our driver. We'll just wait for our driver and really debug it if we can reproduce it there. And if we can't reproduce it there, AMD is multi. Anything stops just doesn't really seem to work. If it ever tries to do one of these CSWRs, I've never seen that actually work.

##### **Nimlgen** [[00:42:23](https://www.youtube.com/watch?v=_mJIF112c5k&t=2543)]
Or it's so full of race conditions. Okay. So we will follow up on.. this to make sure..

##### **Chenyu** [[00:42:35](https://www.youtube.com/watch?v=_mJIF112c5k&t=2555)]
I think everyone can reproduce this now.

##### **Nimlgen** [[00:42:40](https://www.youtube.com/watch?v=_mJIF112c5k&t=2560)]
I mean, this could also be a different issue. Like, MMU crash is a really generic thing. Yeah, I don't know. It just looks poorly done.

##### **Geohot** [[00:42:58](https://www.youtube.com/watch?v=_mJIF112c5k&t=2578)]
I don't know. Now I have to reboot the whole computer. It crashed and didn't recover.

##### **Nimlgen** [[00:43:05](https://www.youtube.com/watch?v=_mJIF112c5k&t=2585)]
So I don't know.

##### **Nimlgen** [[00:43:09](https://www.youtube.com/watch?v=_mJIF112c5k&t=2589)]
Okay.

##### **Nimlgen** [[00:43:14](https://www.youtube.com/watch?v=_mJIF112c5k&t=2594)]
So..

##### **B1tg** [[00:43:15](https://www.youtube.com/watch?v=_mJIF112c5k&t=2595)]
And for the MP.. FP8, I add some continuous before and after the linear. There's a step time reduced, like, cut behind. I think this is the regression we have before. I see the last time we submit the MLPath train, we have the speed like half.

##### **Chenyu** [[00:43:51](https://www.youtube.com/watch?v=_mJIF112c5k&t=2631)]
I'm 85% sure it's Renderfy. Where did you add the contiguous? Maybe you can open the PR for that.

##### **SPEAKER_05** [[00:44:00](https://www.youtube.com/watch?v=_mJIF112c5k&t=2640)]
Okay.

##### **B1tg** [[00:44:02](https://www.youtube.com/watch?v=_mJIF112c5k&t=2642)]
So, like, after linear, if we don't add the continuous, some ops fused and the kernel slow. Yeah, I think it's.. It's a little bit of an issue.

##### **Chenyu** [[00:44:19](https://www.youtube.com/watch?v=_mJIF112c5k&t=2659)]
Yeah. It takes too much time or something like that.

##### **Geohot** [[00:44:23](https://www.youtube.com/watch?v=_mJIF112c5k&t=2663)]
I know when you're doing the gate thing, the gate.. This is like a known.. I had to fix this in Apps.LLM, too. When you do a gate, it's multiple. It multiplies the.LU linear times the other linear, and it will fuse those two together. And you want to put a continuous there. Otherwise, the exogenous fuses no longer uses the tensor core.

##### **B1tg** [[00:44:45](https://www.youtube.com/watch?v=_mJIF112c5k&t=2685)]
Yes, yes. It even uses the tensor core. It backheats it slower.

##### **Geohot** [[00:44:52](https://www.youtube.com/watch?v=_mJIF112c5k&t=2692)]
Yeah, no, there's one fusion, the gate fusion. When you're multiplying the output of two multiplied matrices, it will fuse this. And it makes it slower. I mean, by every reasonable looking at it, you should want to fuse them, but the code generation does not work well when they're fused. So I don't know. If it's a continuous, then it's fine.

##### **Nimlgen** [[00:45:20](https://www.youtube.com/watch?v=_mJIF112c5k&t=2720)]
It's a code generation. It's a long term.

##### **B1tg** [[00:45:25](https://www.youtube.com/watch?v=_mJIF112c5k&t=2725)]
Okay. And after this, I found the..

##### **Nimlgen** [[00:45:30](https://www.youtube.com/watch?v=_mJIF112c5k&t=2730)]
Back to the code.

##### **B1tg** [[00:45:31](https://www.youtube.com/watch?v=_mJIF112c5k&t=2731)]
I made the.. I write the custom kernel to add the three mat mail in the linear or happened in the FP8. And now it's 10% fast and like a 7% memory. Then the half. That's a custom backward function not work with mouse.

##### **Nimlgen** [[00:46:07](https://www.youtube.com/watch?v=_mJIF112c5k&t=2767)]
So I didn't try to with like a six or a GPU. Is this something we should support?

##### **Geohot** [[00:46:26](https://www.youtube.com/watch?v=_mJIF112c5k&t=2786)]
It depends how your custom backward work. If you're doing a custom backward, you should support it. If you're doing a true custom kernel, no, you can't. I mean, it can't do that, right? Like multi can't go through a custom kernel.

##### **Nimlgen** [[00:46:41](https://www.youtube.com/watch?v=_mJIF112c5k&t=2801)]
That'll be interesting when you get the flash attention. So

##### **Nimlgen** [[00:46:46](https://www.youtube.com/watch?v=_mJIF112c5k&t=2806)]
Yeah.

##### **Chenyu** [[00:46:47](https://www.youtube.com/watch?v=_mJIF112c5k&t=2807)]
Does the current flash attention work with multi or will it needs to work with multi, but does it work with multi now?

##### **Nimlgen** [[00:46:55](https://www.youtube.com/watch?v=_mJIF112c5k&t=2815)]
Yeah.

##### **Nimlgen** [[00:47:02](https://www.youtube.com/watch?v=_mJIF112c5k&t=2822)]
I think it's a good question. Most likely, we've tried. I have not tried.

##### **Geohot** [[00:47:10](https://www.youtube.com/watch?v=_mJIF112c5k&t=2830)]
So the way that multi currently work is you have this op called multi that effectively does the sharding. There's a graph right past it does the charting.

##### **Nimlgen** [[00:47:27](https://www.youtube.com/watch?v=_mJIF112c5k&t=2847)]
So it's not clear. It's not clear.

##### **Geohot** [[00:47:29](https://www.youtube.com/watch?v=_mJIF112c5k&t=2849)]
If no one else wants to look at this, I can look into this to see if multi works with custom kernel.

##### **Nimlgen** [[00:47:37](https://www.youtube.com/watch?v=_mJIF112c5k&t=2857)]
It's not clear to me that it won't. But it needs to work. Yeah. Okay. Yeah.

##### **Geohot** [[00:47:49](https://www.youtube.com/watch?v=_mJIF112c5k&t=2869)]
I can write the multi test for custom kernel. It should work.

##### **Nimlgen** [[00:47:54](https://www.youtube.com/watch?v=_mJIF112c5k&t=2874)]
Yeah.

##### **B1tg** [[00:47:57](https://www.youtube.com/watch?v=_mJIF112c5k&t=2877)]
Okay. Okay.

##### **Geohot** [[00:47:58](https://www.youtube.com/watch?v=_mJIF112c5k&t=2878)]
I mean, it shouldn't have anything to do with backwards, right? Like that's all done before gradients are all done before multi. So yeah, I mean, I'm just not sure if multi works at all with custom kernel, but I see no reason it shouldn't.

##### **B1tg** [[00:48:12](https://www.youtube.com/watch?v=_mJIF112c5k&t=2892)]
If we, if I don't use the custom kernel, I can't do the FP. It's a in the backward function. So I need to. Yeah.

##### **Nimlgen** [[00:48:24](https://www.youtube.com/watch?v=_mJIF112c5k&t=2904)]
Yeah.

##### **Chenyu** [[00:48:25](https://www.youtube.com/watch?v=_mJIF112c5k&t=2905)]
Yeah. Sounds good. So I think what we can do here is we can certainly open up PR or like, and I can reproduce the one GPU training with FP8 and a separate thing for the MI300 or MI350 drivers and another separate thing for the multi backward.

##### **B1tg** [[00:48:52](https://www.youtube.com/watch?v=_mJIF112c5k&t=2932)]
Okay. Yeah. Uh, and uh, and asking one, two ads is, uh, um, that for BERT large, Oh, Okay. I can do that. except for your real. schöne geography. And then I think one truth is. If the input feature less than 2k, consider the quantization cost, FP8 can't get faster. But I think for a bigger model like LAMA, it's a bigger size. So FP8 should work well with LAMA.

##### **Chenyu** [[00:49:59](https://www.youtube.com/watch?v=_mJIF112c5k&t=2999)]
Yeah, I think it's good enough here that we can use FP8 for some of these memos. When we try LAMA, we will certainly test more on this. I think this is just a good proof of concept that this can work. And what you're doing here on BERT could translate well into LAMA as well. I won't worry too much, and we will check these D-type data when we have LAMA turning around.

##### **SPEAKER_05** [[00:50:34](https://www.youtube.com/watch?v=_mJIF112c5k&t=3034)]
Okay.

##### **Nimlgen** [[00:50:37](https://www.youtube.com/watch?v=_mJIF112c5k&t=3037)]
Yeah, I mean, 7% memory save is.. Yeah. Looks pretty good. Okay. Thank you so much.

##### **Chenyu** [[00:50:52](https://www.youtube.com/watch?v=_mJIF112c5k&t=3052)]
Next we have the C-type and image D-type stuff.

##### **Chrism** [[00:50:55](https://www.youtube.com/watch?v=_mJIF112c5k&t=3055)]
Yeah. So I mentioned this a little bit in general, the image D-type stuff. But yeah, I mean, there's that requirement that width be 64 byte aligned. I'm totally fine with that.

##### **Nimlgen** [[00:51:09](https://www.youtube.com/watch?v=_mJIF112c5k&t=3069)]
Yeah, well, I think that's a good point.

##### **Nimlgen** [[00:51:10](https://www.youtube.com/watch?v=_mJIF112c5k&t=3070)]
I think it's a good point.

##### **Chrism** [[00:51:11](https://www.youtube.com/watch?v=_mJIF112c5k&t=3071)]
So when you say R-card coding, do you mean padding to that size?

##### **Geohot** [[00:51:15](https://www.youtube.com/watch?v=_mJIF112c5k&t=3075)]
I mean, so okay, right now, when you think about what like ImageCom, like what the function is doing, ImageCom is doing a bunch of transformations to both the input and output matrix, make them currently casting to image D-type. So basically, every place that you cast to image D-type, you can do whatever you want, whether it's pad or slice or whatever, to make it behave correctly.

##### **Chrism** [[00:51:40](https://www.youtube.com/watch?v=_mJIF112c5k&t=3100)]
Okay. Yeah, that makes sense. Yeah, I guess probably what you want to do is you just want to pad it then. Yeah, yeah.

##### **Geohot** [[00:51:46](https://www.youtube.com/watch?v=_mJIF112c5k&t=3106)]
You just pad it there and then you, I mean, it could work obviously without image with padding, and then it could automatically find the image thing, only if you have all those things correct, and that's okay.

##### **Chrism** [[00:51:58](https://www.youtube.com/watch?v=_mJIF112c5k&t=3118)]
Yeah. Okay. That makes sense. I did test it on, I did test like the alignment requirement on, and apparently on NVIDIA, there's no alignment requirement, which is, I guess, nice. But I haven't yet to test it on an AMD GPU, but on a 5090 at least, there's no alignment requirement.

##### **Geohot** [[00:52:17](https://www.youtube.com/watch?v=_mJIF112c5k&t=3137)]
Yeah, I mean, also, if the alignment requirement on something is 128, then we just made it 128, right? Yeah, that's true. Like, it's not that worried about wasting bytes.

##### **Chrism** [[00:52:26](https://www.youtube.com/watch?v=_mJIF112c5k&t=3146)]
That's true. Yeah. And then, oh yeah, the other thing that's worth pointing out is I think previously when we were creating brand new images and then copying into them using like a, we had a kernel that would just basically copy into the new image. I think what it was doing was it was probably doing some sort of like space filling curve to tile the data into the buffer, such that when you draw from the cache, you draw like stuff above you and below you as well, rather than just drawing everything in a line. So we might see a performance decrease by using the copying, like the zero copy create image from D type, or create image from buffer. So that's worth keeping in mind.

##### **Geohot** [[00:53:06](https://www.youtube.com/watch?v=_mJIF112c5k&t=3186)]
I really don't think that's correct. I don't think I, yeah, I really don't think it's using any kind of space filling curve. I mean, you, because you can create buffers from images. I used to save the images, like just basically copy them out and they were just continuous. So I don't think there's anything fancy.

##### **Chrism** [[00:53:25](https://www.youtube.com/watch?v=_mJIF112c5k&t=3205)]
Oh, okay, great. Yeah, I noticed there's some stuff in Mesa.

##### **Nimlgen** [[00:53:28](https://www.youtube.com/watch?v=_mJIF112c5k&t=3208)]
Yeah.

##### **Geohot** [[00:53:30](https://www.youtube.com/watch?v=_mJIF112c5k&t=3210)]
Sure. I mean, you can implement that on top, but as far as I know, it's just normal memory ordering.

##### **Chrism** [[00:53:36](https://www.youtube.com/watch?v=_mJIF112c5k&t=3216)]
Yeah. It's like, there's, there, there, there's, there's a lot of stuff in Mesa. Yeah. So it's, it's sometimes set launch parameters that are like, oh, this is like a, like, like specifically relating to the sampler when they configure the sampler. Sometimes they say like, oh, this is like not tiled or this one is tiled in this word way. So it seems like it may be, there may be hardware support for this, but I don't, I don't know exactly. I, I, I haven't looked into that in great detail. I guess it's worth noticing if we see, I guess to really be able to tell what's going on, it would be nice to have some sort of performance counter here for Qualcomm as well to, to, to, to say like, oh, you know, like the, the cache hit rate went way down.

##### **Geohot** [[00:54:13](https://www.youtube.com/watch?v=_mJIF112c5k&t=3253)]
Yeah. I mean, you can also just look at the speed. The speed is pretty much the same. I'm pretty sure it's all continuous. The other interesting thing that these things have, but I don't think we should do it now, is they have a compressor.

##### **Nimlgen** [[00:54:26](https://www.youtube.com/watch?v=_mJIF112c5k&t=3266)]
Yeah.

##### **Geohot** [[00:54:26](https://www.youtube.com/watch?v=_mJIF112c5k&t=3266)]
They have a lossless compressor. It's called like UHWC or something. Yeah.

##### **Chrism** [[00:54:31](https://www.youtube.com/watch?v=_mJIF112c5k&t=3271)]
Yeah. Yeah. I read a little bit about that.

##### **Geohot** [[00:54:35](https://www.youtube.com/watch?v=_mJIF112c5k&t=3275)]
Yeah. I wouldn't worry about any of that. I would just like put them in like the most boring, like, like, like, like, like, like, boring, normal memory order, do the alignment that's required. And then the main thing that we gain in just the, just the cache is what's getting us all the benefit, I think.

##### **Chrism** [[00:54:48](https://www.youtube.com/watch?v=_mJIF112c5k&t=3288)]
Yeah. And from, from what I understand, the, the compressor works with the unified L2 cache. So the L1 cache doesn't, there's no compression going on between, you know, the GPU and the L1 cache.

##### **Geohot** [[00:55:00](https://www.youtube.com/watch?v=_mJIF112c5k&t=3300)]
Point to that. So yeah, I'm wondering if it's faster. I mean, it'll use up RAM, but other than that, we don't care about that actually at all.

##### **Chrism** [[00:55:09](https://www.youtube.com/watch?v=_mJIF112c5k&t=3309)]
Yeah. Okay. So that's, that's the deal with that. I think that's everything related to that.

##### **Chenyu** [[00:55:16](https://www.youtube.com/watch?v=_mJIF112c5k&t=3316)]
Yeah.

##### **Chrism** [[00:55:16](https://www.youtube.com/watch?v=_mJIF112c5k&t=3316)]
I mean, I saw there's some logic. Oh, sorry.

##### **Chenyu** [[00:55:19](https://www.youtube.com/watch?v=_mJIF112c5k&t=3319)]
Oh, sorry. You finished first.

##### **Chrism** [[00:55:21](https://www.youtube.com/watch?v=_mJIF112c5k&t=3321)]
Yeah. Well, so the, the, the, there's some logic in the ops QCOM backend that has to do with like it's, it has additional requirements, not just the alignments. And I didn't totally understand what was going on with that. I don't know. I'm not sure if we wrote that code. I don't know if that's NimbleGen's code or not. I'm not sure if that's someone else's code. Cause it looked pretty old. I went into the git blame and it looked pretty old. But anyway, I'll, I'll let me.

##### **Nimlgen** [[00:55:51](https://www.youtube.com/watch?v=_mJIF112c5k&t=3351)]
Yeah. So actually there is some alignment logic to much open CL. So, and actually it's mostly for performance. So because I think we had some problems with. Yeah. That's a good point. We had some problems with cache. We had some problems with cache, and it was like, oh, why is it not, you know, like, what Yeah. Yeah. I think that's a good point. Yeah.

##### **Nimlgen** [[00:56:20](https://www.youtube.com/watch?v=_mJIF112c5k&t=3380)]
Let me send it. It's in the allocator, I think.

##### **Geohot** [[00:56:24](https://www.youtube.com/watch?v=_mJIF112c5k&t=3384)]
You mean the pitch align stuff.

##### **Chrism** [[00:56:28](https://www.youtube.com/watch?v=_mJIF112c5k&t=3388)]
Yeah. Yeah. It's both the pitch alignment, but then there's also something in there about like, oh yeah, here, here. This like the pitch add, you see that online. I'll send it. It's online, 334.

##### **Nimlgen** [[00:56:48](https://www.youtube.com/watch?v=_mJIF112c5k&t=3408)]
This stuff. I think that's all performance stuff, right? Where did you post this? General. Yeah.

##### **Nimlgen** [[00:57:13](https://www.youtube.com/watch?v=_mJIF112c5k&t=3433)]
Yeah, I mean, granularity is what I saw in OpenCL. I know it's like hardware requirement or not. I believe it's hardware requirement.

##### **Chrism** [[00:57:23](https://www.youtube.com/watch?v=_mJIF112c5k&t=3443)]
Yeah, that's a hardware requirement. Yeah.

##### **Nimlgen** [[00:57:25](https://www.youtube.com/watch?v=_mJIF112c5k&t=3445)]
Yeah.

##### **Chrism** [[00:57:27](https://www.youtube.com/watch?v=_mJIF112c5k&t=3447)]
But the pitch add? I think that strikes me as performance stuff.

##### **Geohot** [[00:57:32](https://www.youtube.com/watch?v=_mJIF112c5k&t=3452)]
Yeah. Yeah. Comment it out and just attack it.

##### **Chrism** [[00:57:38](https://www.youtube.com/watch?v=_mJIF112c5k&t=3458)]
Yeah, I did comment it out. But I was like, oh, well, maybe, I don't know, maybe there's some like weird edge case that I didn't test. But when I commented it out, it was fine.

##### **Nimlgen** [[00:57:46](https://www.youtube.com/watch?v=_mJIF112c5k&t=3466)]
Cool.

##### **Chrism** [[00:57:48](https://www.youtube.com/watch?v=_mJIF112c5k&t=3468)]
Yeah, OK. So I think that's everything for the image stuff. I can also talk about the C type stuff. But Chengyu, did you have something to say?

##### **Chenyu** [[00:57:58](https://www.youtube.com/watch?v=_mJIF112c5k&t=3478)]
No. I reverted one of your CDL change because it was causing issues. Yeah. And now it's out. So I don't know what's happening. So feel free to try to re-enable that. I think also GitHub network was having some weird issue with influx over the weekend. Maybe that's related.

##### **Chrism** [[00:58:19](https://www.youtube.com/watch?v=_mJIF112c5k&t=3499)]
No, I looked into that this morning. It was a real issue. But I fixed it. So I have that PR ready to go. OK.

##### **Nimlgen** [[00:58:28](https://www.youtube.com/watch?v=_mJIF112c5k&t=3508)]
OK.

##### **Chrism** [[00:58:28](https://www.youtube.com/watch?v=_mJIF112c5k&t=3508)]
It should be fixed. I think whatever machine that's running on, that benchmark doesn't run the setup TinyGrad script. So it has an old version of TinyMesa, which doesn't matter because it doesn't use any TinyMesa stuff. But it does have an old version of TinyMesa. And the issue would not have happened if it didn't have the old version of TinyMesa. But it's also good for me to catch OS errors in the loader. Yeah. So anyway, that's ready to redo. Yeah. And then I have a PR open to remove C-type structure pretty much entirely. I haven't benchmarked it, but it should be a lot faster. And yeah, I'll try and benchmark it before I merge it and make sure that it actually is. But I think the API looks a lot nicer. The only thing is that the API, maybe for designing your own, if you wanted to quickly prototype, interrupt something with C, maybe it's a little bit more annoying because you have to specify the alt, and then you're done. So I think that's a good thing. And then I think it's a good thing that we're able to offset into the structure. But in general, it appears to work for everything that we do. I'll obviously run all the tests and the benchmark tests before I merge that. But yeah, the only thing, there's one thing that I noticed. Yeah.

##### **Geohot** [[00:59:40](https://www.youtube.com/watch?v=_mJIF112c5k&t=3580)]
I'm not worried about having it. Nobody should be hand coding these things anyway. It should all be auto-gen. If you really want to prototype your own C structure, you should just write a header file and then run auto-gen on it.

##### **Chrism** [[00:59:50](https://www.youtube.com/watch?v=_mJIF112c5k&t=3590)]
Yeah, that's true. That's a good point. Yeah, the one thing that it doesn't support is, I signed bit fields. But these are pretty jank. And I don't think we rely on any code that relies on signed bit fields.

##### **Nimlgen** [[01:00:01](https://www.youtube.com/watch?v=_mJIF112c5k&t=3601)]
As long as it's not silently wrong and be assertive, it's all fine. Cool.

##### **Chrism** [[01:00:10](https://www.youtube.com/watch?v=_mJIF112c5k&t=3610)]
Yeah, that's the deal with that. So removing the C type structure would be great. Eventually, it might be nice to remove CDLL entirely. Right now, we just wrap it, which I will need to do to replace C type structure also. Because if you have a function that returns a structure, C types needs to know about it so that it can put space on the stack for you to actually have that structure that returns.

##### **Nimlgen** [[01:00:37](https://www.youtube.com/watch?v=_mJIF112c5k&t=3637)]
But yeah, it should be good.

##### **Geohot** [[01:00:42](https://www.youtube.com/watch?v=_mJIF112c5k&t=3642)]
Anything can return a structure on the stack?

##### **Nimlgen** [[01:00:46](https://www.youtube.com/watch?v=_mJIF112c5k&t=3646)]
Yeah, if you have a function that returns a structure, right? Doesn't it? It puts it on the stack, doesn't it? Honestly, I've never thought about this. Pretty sure that's true.

##### **Geohot** [[01:00:59](https://www.youtube.com/watch?v=_mJIF112c5k&t=3659)]
I think I totally believe you. I'm just not sure. I think about the ABI. I know ARM's ABI really well. And it just puts the return value in R0, sometimes R0 and R1. I have no idea what it does with the structure.

##### **Chrism** [[01:01:14](https://www.youtube.com/watch?v=_mJIF112c5k&t=3674)]
Well, I didn't do this. And I had stuff crashing. So I have to imagine that it was clobbering the return address.

##### **Geohot** [[01:01:22](https://www.youtube.com/watch?v=_mJIF112c5k&t=3682)]
Interesting. Yeah, OK. Cool. So yeah, write a test and do whatever you need.

##### **Chrism** [[01:01:26](https://www.youtube.com/watch?v=_mJIF112c5k&t=3686)]
Yeah. But yeah, that should be good. It's a little annoying because now we have to cast to a C-type structure at the very end. But it should be fast because it's just like we're making a dummy C-type structure. But eventually, it would be nice to remove that entirely. We'll just have to replace DLopen, I guess. Yeah.

##### **Geohot** [[01:01:44](https://www.youtube.com/watch?v=_mJIF112c5k&t=3704)]
When you say cast to a C-type structure, it's not actually a structure with a field. It's just like a dummy structure that just has a number of bytes, right?

##### **Chrism** [[01:01:50](https://www.youtube.com/watch?v=_mJIF112c5k&t=3710)]
Yes. Yeah. Yeah.

##### **Nimlgen** [[01:01:51](https://www.youtube.com/watch?v=_mJIF112c5k&t=3711)]
OK.

##### **Chrism** [[01:01:52](https://www.youtube.com/watch?v=_mJIF112c5k&t=3712)]
No. Replacing DLopen, I was thinking about it. It's much more complicated. You either have to interface with libffi or you have to generate assembly yourself because you need to like if it's a float, then that's different from if it's an integer.

##### **Geohot** [[01:02:08](https://www.youtube.com/watch?v=_mJIF112c5k&t=3728)]
Yeah. We definitely don't want to start dealing with ABIs ourselves. Definitely not.

##### **Chrism** [[01:02:14](https://www.youtube.com/watch?v=_mJIF112c5k&t=3734)]
Yeah. So that's either libffi or just using C-types.

##### **Geohot** [[01:02:19](https://www.youtube.com/watch?v=_mJIF112c5k&t=3739)]
Libffi is fine. Yeah. Yeah. Is libffi linked to Python usually?

##### **Chrism** [[01:02:25](https://www.youtube.com/watch?v=_mJIF112c5k&t=3745)]
I think I would assume that's C. I haven't read the C-types code fully yet, but I would assume that that's the way it does it.

##### **Geohot** [[01:02:32](https://www.youtube.com/watch?v=_mJIF112c5k&t=3752)]
I also think that that's just totally fine if you want to do that C-type structure dummy thing to make it slightly slower when you're returning a structure. I'm not worried about that at all. I definitely do not want to start having things be different depending on the ABI of the system, right? Like someone has a power-to-C system, yeah. But if it's a wrong group, then I just file it.

##### **Nimlgen** [[01:02:50](https://www.youtube.com/watch?v=_mJIF112c5k&t=3770)]
Yeah. OK.

##### **Geohot** [[01:02:51](https://www.youtube.com/watch?v=_mJIF112c5k&t=3771)]
Yeah.

##### **Nimlgen** [[01:02:51](https://www.youtube.com/watch?v=_mJIF112c5k&t=3771)]
That makes sense. Yeah. I think that's it. So that's everything we have on the agenda. There are a couple of other times. Those, that's not covered. Oh, what happened to TinyMAC1?

##### **Geohot** [[01:03:21](https://www.youtube.com/watch?v=_mJIF112c5k&t=3801)]
It just had the log taken. Oh, no.

##### **Nimlgen** [[01:03:24](https://www.youtube.com/watch?v=_mJIF112c5k&t=3804)]
Oh, now it's fixed? I just need to run that script next time? I mean, it looks like it was just a.

##### **Nimlgen** [[01:03:36](https://www.youtube.com/watch?v=_mJIF112c5k&t=3816)]
Yeah. So there was a style pit. And we see this from time to time on the right as well. But on the right, we have a script to kill selling pits. And sometimes it helps. But I don't know. I mean, ideally, GitHub runner should just kill all the child pits. But it doesn't do that. I know.

##### **Geohot** [[01:04:06](https://www.youtube.com/watch?v=_mJIF112c5k&t=3846)]
Why doesn't it? I would think it would do that too. Are they somehow getting detached? Are we not running with the right zombie flag or something? Or are we using shells? I think. I mean, I don't like there's that flag for some process in Python for whether something is a child process or not.

##### **Nimlgen** [[01:04:36](https://www.youtube.com/watch?v=_mJIF112c5k&t=3876)]
I can check this next time. Yeah. We could do this.

##### **Geohot** [[01:04:41](https://www.youtube.com/watch?v=_mJIF112c5k&t=3881)]
Yeah, daemon. Daemon is the flag I'm thinking of.

##### **Nimlgen** [[01:04:44](https://www.youtube.com/watch?v=_mJIF112c5k&t=3884)]
I think most of these pits are from the BEAM search. Like when we. We call multi processing. But actually, I try to. I don't know why. I just try to fix this with some flags for GitHub runners. Like to kill the whole group. But. I mean, yeah.

##### **Geohot** [[01:05:12](https://www.youtube.com/watch?v=_mJIF112c5k&t=3912)]
But this is a bug, obviously. Like whenever we talk about action investigations and Swift teeth, right? Like first off, Python shouldn't be leaving cell processes around. Second off, GitHub should be killing them. And third off, we should have some script that detects this when it starts the runner and kills everything. I think we can fix this with like mitigations all across the stack. I think maybe the best thing to do now would be to just write a script that runs at the beginning of the GitHub actions run that does that else off and then kills all the Python or just kills all the Python.

##### **Chenyu** [[01:05:43](https://www.youtube.com/watch?v=_mJIF112c5k&t=3943)]
We already have that for the red runners. Benchmark.

##### **Geohot** [[01:05:49](https://www.youtube.com/watch?v=_mJIF112c5k&t=3949)]
Yeah. We've got to put on the map.

##### **Chenyu** [[01:05:50](https://www.youtube.com/watch?v=_mJIF112c5k&t=3950)]
I feel. But let's try.

##### **Geohot** [[01:05:54](https://www.youtube.com/watch?v=_mJIF112c5k&t=3954)]
Got it. Yeah. We can just move that to the Mac.

##### **Nimlgen** [[01:05:57](https://www.youtube.com/watch?v=_mJIF112c5k&t=3957)]
Yeah.

##### **Chenyu** [[01:05:58](https://www.youtube.com/watch?v=_mJIF112c5k&t=3958)]
I think I did something. But again, yeah.

##### **Geohot** [[01:06:02](https://www.youtube.com/watch?v=_mJIF112c5k&t=3962)]
It's a big thing because we really need defense and depth here. Right. Like this is this is failing at three levels. First off, there's a reset of script. Second off, why is Python leaving around cell properties? And third off, why is GitHub not killing them? Right. Like this can be dealt with at three different levels and it's getting past all three. So I think we can do that. If someone can find a repro for when those beams are being killed. I mean, I wrote that code. I hate the Python processing. I always feel like this happens. I've never found a way to make it reliable. I don't know if I'm doing something wrong. I don't know.

##### **Nimlgen** [[01:06:35](https://www.youtube.com/watch?v=_mJIF112c5k&t=3995)]
I think it happens since the if the job just timeouts.

##### **Geohot** [[01:06:42](https://www.youtube.com/watch?v=_mJIF112c5k&t=4002)]
Oh, okay. So it is then a GitHub related issue. I mean, it's just not killing it correctly. Yeah.

##### **Nimlgen** [[01:06:47](https://www.youtube.com/watch?v=_mJIF112c5k&t=4007)]
Yeah.

##### **Geohot** [[01:06:48](https://www.youtube.com/watch?v=_mJIF112c5k&t=4008)]
I'll look into how the action center is killing it if it's the BEAM thing.

##### **Nimlgen** [[01:06:56](https://www.youtube.com/watch?v=_mJIF112c5k&t=4016)]
But either way, short term, let's just move that kill script from red and I'll put it on that. Okay. Anything else worth mentioning? We cover everything. Oh, you want to talk about your app? Is it ready? Oh, the LLM app? Yeah. Yeah.

##### **Geohot** [[01:07:19](https://www.youtube.com/watch?v=_mJIF112c5k&t=4039)]
So I just made some small improvements to it. So TinyGrad app LLM now gets pretty much the memory bandwidth of the computer with two fixes to speed. I also added a serve flag, which is a very minimal OpenAI API server. And yeah, I think I'm going to add Qen support as well. You know, just so it's actually usable, hopefully as an LLM thing, which is a little bit more complicated. But yeah, I think it's still not getting the pre-fill very well. So we have to get pre-fill. I can look into that too. I think a lot of these things are just good. Good things in general to have a beautifully clean LLM server that's like really minimal. I've been working really hard to keep that file readable. But yeah, I think it's a real use case, especially if we can start to run the big model, especially if we can start to run these mixture of experts models on the big AMD GPUs, because none of them work. They're trying to do a lot of work on the big AMD GPUs, but they're not doing a lot of work. I've been working on VLLM. I tried SELang, and none of them work for big Qen. None of them work for DLM. So it would be really cool if TinyGuard could run those at memory speed. And then there's the issue of all the little qualms. Right now we're just putting it all in Flux16. So making the little qualms actually read fast.

##### **Nimlgen** [[01:08:38](https://www.youtube.com/watch?v=_mJIF112c5k&t=4118)]
That's a whole different issue.

##### **Nimlgen** [[01:08:42](https://www.youtube.com/watch?v=_mJIF112c5k&t=4122)]
Cool. Yeah.

##### **Nimlgen** [[01:08:45](https://www.youtube.com/watch?v=_mJIF112c5k&t=4125)]
Okay. So I think that's it. That's it for this meeting. Thank you everyone. See you next week.

##### **Nimlgen** [[01:08:52](https://www.youtube.com/watch?v=_mJIF112c5k&t=4132)]
Bye.
