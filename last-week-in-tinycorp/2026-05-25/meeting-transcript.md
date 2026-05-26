# 2026-05-25 Meeting

### Meeting Agenda

**Time:** new meeting #21, 5/25 9am Monday San Diego time
- company update
- MLPerf LLaMA
- viz
- HCQ2
- requires_grad, deviceless const
- assembly, dtype.vec
- CI and tests improvements
- bounties, issues, Comma happiness


### Audio

[Youtube Link](https://www.youtube.com/watch?v=g8SHLqz6AHw)

### Highlights

- **[Company Update](#geohot-000010)**: TinyBox Blackwell pricing must rise because Blackwell GPU supplier pricing increased from about $8,600 to $10,700 per card, pushing the box price up by roughly $8,000 to around $73,000.

- **[AI Policy](#geohot-000222)**: The team reiterated a strict “no AI-looking work” policy: AI use that results in untrusted, low-quality, or unread code can lead to bans, even if calibrated high performers may still use tools carefully.

- **[Hardware Support Policy](#geohot-000647)**: Issues involving unsupported docks will be closed; the official policy is to support only the company’s own dock, with a possible docs page for supported GPUs such as RDNA3+ and Ampere+.

- **[MLPerf and LLaMA Scaling](#wozeparrot-000833)**: An 8B model-parallel run completed but was slow at about 25 hours; the next step is to try 70B, while 405B is currently limited mainly by CPU memory usage.

- **[LLaMA Kernel Optimization](#qazalin-001352)**: Qazalin is porting custom LLaMA C kernels into UOps and pushing toward a sub-two-hour run; two kernels are already merged without regressions, and one upcoming UOp kernel beats C speed.

- **[VIZ Cleanup After VCONST Removal](#geohot-001745)**: With `VCONST` removed, VIZ now shows excessive stack/const nodes feeding movement ops; the requested fix is client-side filtering that hides only stack consts feeding movement ops.

- **[HCQ2 Multi-Device Command Buffers](#nimlgen-002235)**: HCQ2 multi-device work now handles per-device buffer addresses with stacked const/table-style substitution, while future optimizations may use shared virtual addresses or computed address formulas.

- **[HCQ2 Scheduling Direction](#geohot-003620)**: HCQ2 should move away from one schedule per kernel; the target is one graph rewrite per schedule or doorbell ring, with graph rewrite calls remaining O(1) relative to the number of kernels.

- **[`requires_grad` Removal](#chenyu-004031)**: `requires_grad` has been removed; tensors can lazily have gradients, while optimizers now use an `is_param` flag to decide which tensors are parameters.

- **[Deviceless Const Refactor](#chenyu-004120)**: Constants are being made device-free and inline-only; `Tensor.from_uop` was removed, `Tensor.full/ones/zeros` will return buffers by default, and `Tensor.const` or `buffer=False` keeps fusible constants.

- **[Assembly and `dtype.vec`](#geohot-005027)**: x86 assembly landed under `DEV=CPU:x86`, clarifying the need for explicit register allocation and instruction selection; meanwhile, `dtype.vec` removal is pushing vector loads toward buffer views.

- **[CI and Test Cleanup](#chrism-005714)**: Core tinygrad no longer depends on `getenv("CI")`, dtype support moved onto renderers, and the test suite is being cleaned up into clearer categories: unit correctness, backend/renderer tests, and application tests.

- **[Comma IMAGE/Rangeify Bug](#chenyu-010203)**: A Comma-facing IMAGE/rangeify issue appears tied to key collisions and non-unique ranges, especially with duplicate reduce endings; a quick hack exists, but the underlying cause may be upstream.

- **[Sharding Regression and Custom Kernels](#b1tg-010637)**: B1tg found sharding became slower after rangeify and was advised to build a minimal repro; for Kimi decode speedups, UOps are preferred over HIP custom kernels unless tinygrad cannot express the needed packed int-level operation.

### Transcript
##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=0)]
Hey, welcome everyone. So let's get started. Company update to open.

##### **Geohot** [[00:00:10](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=10)]
Yeah, I'm going to raise prices of the boxes today. We got a whole bunch of orders in at the last minute. Our price on the Blackwell GPUs is going from like $8,600 to like $10,700. So I literally have to raise the price of the box $8,000. And that even lowers our profit margin. So yeah, we also got an order for a TinyBox Pro Blackwell. I don't know if they've paid yet. I'm kind of half hoping they won't pay, because then we don't have to figure out how to build that machine. But yeah, we got a whole bunch of orders this week. And yeah, no, I mean, we actually have to raise prices. Like our supplier said we could get, I think we got 24 cards at the other price. But yeah, they're just going up.

##### **Chenyu** [[00:00:57](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=57)]
So $73,000 something.

##### **Geohot** [[00:01:03](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=63)]
Basically, yeah. Expensive. Yeah, insane. What's up?

##### **Geohot** [[00:01:10](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=70)]
Yeah, if you want to buy right now. Right now is literally your last chance if you want to buy a TinyBox at the current prices before I go into Shopify and change it. I don't think we've actually sold all 24. I mean, I think we sold like 16.

##### **Wozeparrot** [[00:01:26](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=86)]
So in effect, like eight more GPUs. So is Red price also going up?

##### **Geohot** [[00:01:32](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=92)]
Not as far as I know. I also have two reds in stock.

##### **Geohot** [[00:01:39](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=99)]
I don't think GDDR6 went up that much. I think DDR6, GDDR6, and DDR4 share a lot. It's not like you can reuse those processes for HBM and stuff. So I really think it's just the RAM cost. Oh, I see all these tweets about how CXMT is going to flood the market.

##### **Wozeparrot** [[00:01:59](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=119)]
I thought Corsair was going to start shipping DIMMs with CXMT memory on them.

##### **Geohot** [[00:02:04](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=124)]
Yeah. Um, I don't know. I got to look in the market and see, like, we can make DIMMs. How hard is it to make a DIMM?

##### **Wozeparrot** [[00:02:19](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=139)]
Uh, yeah.

##### **Geohot** [[00:02:21](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=141)]
Yeah.

##### **Geohot** [[00:02:22](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=142)]
That, uh, what else? Um, yeah, we have to have a strictly no AI policy. Like again, it's not that you can't use AI, but if it looks at all like AI, then you're banned. Like your value is to like, like, like I'm going to use AI is not a plan, or I used AI and I trust the output. Like that's not a plan.

##### **Chenyu** [[00:02:54](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=174)]
Yeah. The, the LLaMA. Not LLaMA, like Kimi person.

##### **Geohot** [[00:03:00](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=180)]
I know. I know. Right. And like, I don't want to like be harsh, but I also like, I'm really, um, attuned to this, this time wasting, right? Like, like I feel like what's going to happen. Um, my article did pretty well. I feel like what's going to happen is there's going to be a huge influx of just stuff and the top performers are going to be able to self-regulate pretty well, but the bottom performers aren't. So even though AI might help the top performers a few percent, the net impact of AI and agents is going to be massively negative because the people at the bottom don't self-regulate. The people at the bottom will flood everything with crap. And yeah, so very important that we stay diligent against that. I think we've been doing an okay job, but one whiff of AI equals permaban.

##### **Geohot** [[00:03:52](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=232)]
Do not use it.

##### **Qazalin** [[00:03:59](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=239)]
Right.

##### **Geohot** [[00:04:00](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=240)]
Like, I think that's the problem. That's it. I mean, like, okay.

##### **Geohot** [[00:04:02](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=242)]
I shouldn't say do not use it. Right. Like this is the exact problem, right? You know, this is then you get into like the Dunning-Kruger effect. Right. I say like, well, if you're a high performer and you're carefully calibrated and know how to use AI by all means use AI. I'm not saying.

##### **Chenyu** [[00:04:16](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=256)]
Those people will probably start from there already. So.

##### **Geohot** [[00:04:21](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=261)]
Yeah. I think that if I was running a large tech company right now, I would get AI out of there as fast as I possibly could. Yeah.

##### **Wozeparrot** [[00:04:30](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=270)]
I can't believe Bun merged that migration.

##### **Geohot** [[00:04:33](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=273)]
I know. I know. Like, like, I mean, you know, look, you know, never interrupt your enemy when they're making a mistake. It's kind of kind of funny to see the AI psychosis inside Anthropic. And that gives us a feeling of what to expect from the new models. I don't know, like part of it's just sad to see, but part of it's like, like, yes, this is what happens when you're in a cult and you really just believe your own hype. Oh, we don't read the code. We just ship it, man.

##### **Chenyu** [[00:05:00](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=300)]
No, I read probably like a few thousand lines of that font change because it was fun to read.

##### **Geohot** [[00:05:07](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=307)]
It's awful. They have a whole they have a whole breakdown of like how they're now going through and removing all the unsafe blocks. Right. Like, and this exactly gets to the problem. Like, so there's a test suite and they're like, well, the rewrite passes the test suite. I would agree with this logic. If the AI. Couldn't read the test suite while it was doing a refactor. If they had had the test suite as like a holdout set. And they did the whole refactor and then the test suite passed, I might have some faith in it. But as far as I can tell, they didn't do anything like that. They let the AI just read the tests.

##### **Geohot** [[00:05:47](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=347)]
Yeah, we'll see.

##### **Geohot** [[00:05:48](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=348)]
Yeah. Right. And you can imagine and you can imagine humans doing the rewrite in the other way. You could imagine like a complete holdout test suite. And yeah, passing, but I just cannot possibly imagine that working with AI today.

##### **Geohot** [[00:06:04](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=364)]
So the policy is no AI.

##### **Chenyu** [[00:06:09](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=369)]
The only way to say that. I know that feels like the same as the policy is don't, don't be stupid.

##### **Geohot** [[00:06:19](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=379)]
No, because people don't know if they're being stupid. People know if they're using AI.

##### **Chenyu** [[00:06:24](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=384)]
You also don't know if they are using AI correctly. Unless...

##### **Geohot** [[00:06:27](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=387)]
And that's what I mean. Like the policy is no AI.

##### **Chrism** [[00:06:33](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=393)]
Yeah.

##### **Geohot** [[00:06:35](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=395)]
No AI.

##### **Qazalin** [[00:06:36](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=396)]
Interesting.

##### **Chenyu** [[00:06:40](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=400)]
You closed a bunch of issues. So we are going to only officially support our dock.

##### **Geohot** [[00:06:47](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=407)]
Yeah. Yeah. Yeah. That's another one. Um, I mean, some of those issues, the dock, so those issues probably fall into three categories. There's some that are the dock, there's some that are the GPU choice, and there's some that are bugs in our code. The problem is that's way too hard to disambiguate. So I think our official policy is that we only support our dock. Um, you know, that said, if like someone wants to maintain a page, talk about what other docks are supported, by all means do it. But yeah, I think our policy is that we close all those issues. Um,

##### **Chenyu** [[00:07:24](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=444)]
We have similar policies for the GPUs that we support.

##### **Geohot** [[00:07:30](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=450)]
I mean, we should, we should. So I think for GPUs, we should probably put a, uh, I mean, basically like anything with RDNA3 and up and anything that's Ampere or up, we should support.

##### **Chrism** [[00:07:44](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=464)]
We could probably just add like a doc page. Yeah.

##### **Geohot** [[00:07:47](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=467)]
But then we have to also then disambiguate the dock. We haven't shipped our dock yet.

##### **Chrism** [[00:07:50](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=470)]
Sorry, like, dock.

##### **Geohot** [[00:07:53](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=473)]
No, no, I totally understand. Um, yeah, we should add a docs page that says that. What we should do is actually right now we should just, we have a dock. We support the ADT-UT3G dock. Yeah. Actually, we don't even test that dock anymore. We just test our dock. Never mind. We don't support it. Yeah. Okay.

##### **Geohot** [[00:08:10](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=490)]
We're going to ship our dock soon. That's good enough. Uh, any other level stuff? Oh, you got it.

##### **Chenyu** [[00:08:27](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=507)]
Okay. Yeah. Let's move on. Next is MLPerf and LLaMA.

##### **Wozeparrot** [[00:08:33](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=513)]
Uh, so I did an 8B model parallel run last week. It's pretty slow. 25 hours. I don't know if that's just the shapes are bad.

##### **Geohot** [[00:08:49](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=529)]
Um, I wouldn't worry too much about small shapes.

##### **Geohot** [[00:08:53](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=533)]
I wouldn't worry too much about it being slow. Uh, I think we just got to get 405B training.

##### **Chenyu** [[00:08:59](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=539)]
Same thing for me.

##### **Wozeparrot** [[00:09:03](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=543)]
Yeah. I will start trying for 70B.

##### **Geohot** [[00:09:10](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=550)]
That's a good point. Do 70B first. I mean, that should just work, right?

##### **Wozeparrot** [[00:09:11](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=551)]
Yeah, that should just work. Uh, with the two PRs I have, I merged one. There's another one that does a gather if you go to single device and copy multi, and that fixes memory for 405B.

##### **Chenyu** [[00:09:28](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=568)]
How did you find stuff like that?

##### **Wozeparrot** [[00:09:34](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=574)]
Like this? Yeah, the gather memory one. AI.

##### **Chenyu** [[00:09:42](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=582)]
Okay, no, no. So how did you do that? What's your workflow look like?

##### **Wozeparrot** [[00:09:46](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=586)]
How did I do this? I told Claude that there was a memory issue. Okay. And then I looked in my Git history and realized that I had made a change before that fixed this, and I just never merged it.

##### **Chenyu** [[00:10:03](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=603)]
Okay. So you fixed this before. How did you find this issue first?

##### **Geohot** [[00:10:10](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=610)]
I don't remember.

##### **Chenyu** [[00:10:12](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=612)]
Oh, okay. Well, that doesn't count, right? Yes, you are good, but I'm trying to see if I can replicate that in some other place.

##### **Geohot** [[00:10:24](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=624)]
It's interesting. I read a thing where AI set the record on one of those GPT speedrun things, and the way that it did it was it went through all the PRs and just cherry-picked from like eight of them.

##### **Chenyu** [[00:10:38](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=638)]
Yeah. I mean, that's a legit strategy when you do research. Oh, totally.

##### **Wozeparrot** [[00:10:43](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=643)]
Yeah, you know, AI is very good at that. Okay. I don't know. I still find it's pretty bad looking through big logs. I don't know. I tried to get it. I tried to get it to write release notes, and it was kind of bad at this.

##### **Geohot** [[00:10:58](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=658)]
Oh, yeah. No. Tasteful. Anything that involves taste, it's very bad at.

##### **Wozeparrot** [[00:11:01](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=661)]
But if you wanted to find a needle, the new dev syntax is just bad.

##### **Chenyu** [[00:11:07](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=667)]
Okay. So we should be able to have 70B working.

##### **Wozeparrot** [[00:11:16](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=676)]
Yeah. So the limiting thing on 405B now is CPU memory. At six terabytes of CPU memory used, I think stochastic rounding should cut that a lot because right now it's still master weights. So we're just storing an FP32 copy of weights on CPU. A bulk of the CPU memory is going there.

##### **Geohot** [[00:11:49](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=709)]
You could cut it, but maybe somewhere closer to 50, and then you'd be doing, you could...

##### **Wozeparrot** [[00:11:52](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=712)]
Uh, and MLPerf stuff. I still have to do the reviews. They were a bit behind because they had to remake tracking issues for our stuff after stuff got shuffled around.

##### **Chenyu** [[00:12:11](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=731)]
I think just the review shouldn't take too long.

##### **Wozeparrot** [[00:12:18](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=738)]
Yeah, I mean, I think they just use the standard reference implementation, so it should be fine.

##### **Chenyu** [[00:12:24](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=744)]
Yeah. Just see if there's anything that they might be interested in since they use similar machines. Otherwise, it could be straightforward. I also don't expect other people to really care about our thing.

##### **Geohot** [[00:12:41](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=761)]
Yeah. How are we getting the line counts for the releases? I felt like this has come up before. I mean, what's the problem?

##### **Qazalin** [[00:12:51](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=771)]
Yeah.

##### **Geohot** [[00:12:53](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=773)]
Where did you get that number?

##### **Wozeparrot** [[00:12:55](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=775)]
Oh, if you go to line crisis, the bot runs sc.py on each commit and then it updates the description in line crisis.

##### **Geohot** [[00:13:04](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=784)]
When I run sc.py locally, I get 24,000.

##### **Chenyu** [[00:13:12](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=792)]
Did you include JavaScript?

##### **Geohot** [[00:13:15](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=795)]
Yes.

##### **Wozeparrot** [[00:13:17](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=797)]
Interesting. There's a 1,000-line difference. I know.

##### **Geohot** [[00:13:28](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=808)]
Okay. Anyway, you're welcome to fix that.

##### **Qazalin** [[00:13:35](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=815)]
Anything else for LLaMA?

##### **Geohot** [[00:13:42](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=822)]
Should be all. Okay. Speaking of VIZ, Qazalin.

##### **Qazalin** [[00:13:52](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=832)]
Yeah. So I've been working on getting the custom C kernels in LLaMA into UOps and also making LLaMA go under two hours. We had six custom kernels last week. Two of them are now in master in UOps without any regressions. And I have one more coming up that actually is beating C speed. So that should be done soon. I found a lot of places where we hit decompositions instead of using the actual assembly instructions that are fast on AMD. So I think that's worthwhile. It's just cleaning up C style and adding those operations. For example, we don't use max at all in our...

##### **Geohot** [[00:14:45](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=885)]
We don't use max. You mean we're using like the `where` construction?

##### **Qazalin** [[00:14:48](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=888)]
Yeah, we're using the condition. It ends up lowering to cndmask in LLVM, and it's very slow. Like that mask change alone is a 10% speed difference.

##### **Geohot** [[00:15:01](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=901)]
Interesting. Where are these? Okay, there are extra LLaMA kernels.

##### **Qazalin** [[00:15:09](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=909)]
Oh, yes. There are extra LLaMA kernels.

##### **Geohot** [[00:15:12](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=912)]
Let's see what the overall UOp kernels look like.

##### **Geohot** [[00:15:22](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=922)]
I think I broke my colors in my editor. Cool. Okay. And yeah, there's no regressions on these speed-wise?

##### **Geohot** [[00:15:35](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=935)]
Are you using beam to search?

##### **Qazalin** [[00:15:45](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=945)]
For one of them? Yes. For the other one, I tried beam. It's slow. And I really tried to make it work with UOps. The difference is a three hours and 20 minutes run versus a two hour and 50 minutes run. So I can merge the one that's simpler and didn't use beam.

##### **Geohot** [[00:16:07](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=967)]
I see. Okay, so here you're using, like I'm looking at your quantize FP8 delayed. I see you're using unroll specifically.

##### **Qazalin** [[00:16:19](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=979)]
Yes. And UPCAST is an empty op. I'm just disabling that.

##### **Geohot** [[00:16:23](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=983)]
Yeah, I mean, the question is like, like, how are you finding the syntax, right? Because the goal of this project isn't just to port these kernels. The goal of these projects is to make syntactical improvements to the UOps.

##### **Qazalin** [[00:16:40](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1000)]
Yeah, I had one syntax improvement merged so far. It was gated LDS loads. So before, if you had gated LDS load stores, you couldn't use the get-item syntax. You would have to use like `index(..., ptr=True)` because the gates wouldn't flow in the devectorizer. I merged something to fix that. But other than that, it was pretty easy to work with the syntax. Even the LLMs just did it. GPT-5 pretty much can do it if I push it hard enough.

##### **Geohot** [[00:17:15](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1035)]
Yeah, I mean, these look readable. I mean, I don't totally know, what is this while step?

##### **Qazalin** [[00:17:28](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1048)]
I mean, you could write it in another way, too. But it's basically a Python unroll of the UOps, right?

##### **Geohot** [[00:17:36](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1056)]
Interesting.

##### **Qazalin** [[00:17:37](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1057)]
Yeah. I find it pretty clean in general.

##### **Geohot** [[00:17:45](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1065)]
Yeah, no, I mean, I think this is a good project. Yeah, let's keep pushing for two hours. The other thing I want you to look at is, so I deleted VCONST last week.

##### **Geohot** [[00:17:56](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1076)]
Mm hmm.

##### **Geohot** [[00:17:58](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1078)]
And one of the annoying things about this. So now it's just stack and const. It's a great cleanup. You suggested it. There's no reason that we should have a separate op VCONST. It's basically duplicate logic with stack const everywhere. But now the VIZ looks bad for movement ops because the movement ops have stacks and const on them. I want you to fix VIZ so that those stacks and const go away, but only on a movement op. I don't want all stacked const to go away. I only want stack const that feed into a movement op to go away. And this is kind of hard to do with the current way that we do filtering. Also, client-side filtering is always better than server-side filtering for this kind of stuff, because it's nice to have the toggles to hide. Right now we should basically move all the op-hiding logic out of the server and into the client.

##### **Geohot** [[00:19:01](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1141)]
Mm hmm.

##### **Geohot** [[00:19:02](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1142)]
But yeah, if you could take a look at what movement ops have become and kind of clean that up.

##### **Geohot** [[00:19:08](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1148)]
Okay.

##### **Geohot** [[00:19:09](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1149)]
Yeah, just so we don't see stacks and const pointing to every reshape and expand and stuff.

##### **Chenyu** [[00:19:15](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1155)]
Maybe you can put an example command in the VIZ channel later.

##### **Geohot** [[00:19:20](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1160)]
Yeah, sure.

##### **Qazalin** [[00:19:21](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1161)]
Okay.

##### **Geohot** [[00:19:26](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1166)]
Yeah, look into that. Agreed, the client side is better.

##### **Wozeparrot** [[00:19:32](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1172)]
Anything else?

##### **Geohot** [[00:19:35](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1175)]
Oh, yeah. Has test_tiny now imported CI? Who did this?

##### **Chrism** [[00:19:41](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1181)]
Oh, I did.

##### **Qazalin** [[00:19:42](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1182)]
No. It needs PYTHONPATH now. I'm sad too. No, no, no, no. That's got to go.

##### **Chenyu** [[00:19:48](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1188)]
Why? What broke?

##### **Chrism** [[00:19:51](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1191)]
It previously imported CI. I just imported it from...

##### **Chenyu** [[00:19:54](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1194)]
Let's discuss CI flag specifically later. Okay.

##### **Qazalin** [[00:19:59](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1199)]
I'll just mention I'll share the MLPerf in the MLPerf channel, the breakdown of LLaMA. Okay. Currently, this is the breakdown. I've been working very hard on getting a faster GEMM. AMD's ones aren't as slow. We're even slower than what they have. And our GEMMs are only getting like 60%, 67% max. So that would be.

##### **Geohot** [[00:20:29](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1229)]
I mean, we know that two hours is possible, right? Like we have an existence proof. So I'd be interested in just figuring out what GEMM they used. If our GEMM is the same speed as theirs, I wouldn't keep pushing on that. If our GEMM is slower than that, we should figure out why.

##### **Geohot** [[00:20:44](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1244)]
Yeah.

##### **Geohot** [[00:20:44](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1244)]
You know, saying that it's 60, 70% max, like, I mean, sure, theoretical, right? But just the way that stuff works, it may be very, very hard to get higher. If there's no existence proof that higher exists, that's probably not where we should be focused. We should be focused on whatever AMD actually did, because we know that's possible and we can just copy it.

##### **Qazalin** [[00:21:07](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1267)]
I might have to go to assembly for that. But yeah.

##### **Geohot** [[00:21:11](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1271)]
Yeah. Yeah. Yeah. Yeah. I mean, we should flag the kernels that are in assembly and be like, well, this one's going to require assembly and we'll get there.

##### **Geohot** [[00:21:21](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1281)]
Have you tried to run their thing?

##### **Qazalin** [[00:21:31](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1291)]
Not their whole MLPerf, but I have their repo cloned and built their kernels.

##### **Chenyu** [[00:21:37](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1297)]
I think a natural step after having breakdown like this is just to like, are we like fundamentally doing something wrong? It's similar to a copy thing, something probably shouldn't just shouldn't exist at all.

##### **Geohot** [[00:21:53](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1313)]
It's probable.

##### **Qazalin** [[00:21:54](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1314)]
I mean, like, there's a clear path to getting to two hours. We need to get some of this stuff out of the auto-generated into custom kernels. Some of them are just bad kernels. But the GEMM and FlashAttention specifically, I think I can pull from assembly that the MLPerf submission from AMD uses as well.

##### **Geohot** [[00:22:20](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1340)]
And we'll get to shard.

##### **Qazalin** [[00:22:26](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1346)]
Good.

##### **Geohot** [[00:22:28](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1348)]
Okay, next, moving on to HCQ2.

##### **Nimlgen** [[00:22:35](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1355)]
So I've been working on multi for HCQ2 this week. So currently, the whole schedule does not depend on the device count at all, but the problem arises later since the addresses of the multi buffers of each part are different now. And we can improve this for AMD but not for CUDA, because CUDA uses a unified memory space.

##### **Geohot** [[00:23:13](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1393)]
So, I mean, basically, they are not... I'm not following this. Sorry.

##### **Geohot** [[00:23:22](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1402)]
So what's the problem?

##### **Wozeparrot** [[00:23:24](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1404)]
What doesn't work?

##### **Nimlgen** [[00:23:29](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1409)]
So, I mean, in the command buffers, we have some addresses, like to the kernel arguments, to the buffers and things. And the idea is that on different devices, this address can be different. My idea was that we can completely share the same command buffer between devices. But since addresses are different, I mean, we can patch this.

##### **Geohot** [[00:24:01](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1441)]
Well, I can see how I would do this is by putting all the addresses in a tensor, like in a bunch of stacked consts, and then using an index based on the device count.

##### **Nimlgen** [[00:24:14](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1454)]
Yeah. I do exactly that right now. But actually, I thought that in the future for AMD, for the multi buffer for all these parts, they can have the same virtual address.

##### **Geohot** [[00:24:34](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1474)]
Yeah, no, I mean, that's definitely an optimization. But I don't think we can get out of supporting the things having different addresses. I mean, again, also for them to have the same virtual address would require the MMU to be on. So I think the way to think about this is like, we have this kind of set of UOps that can be quote-unquote compiled by the graph rewrite engine. And that will include things like indexing into a stack. So when it's actually compiled, when it's actually copied to the device, the command buffer exists in some abstract UOp form. Then some graph rewrite comes in that substitutes the variable device num for the actual concrete device num, runs some stuff on it, and then creates a command buffer that's specific to that device. You could imagine it also, in order to deal with this O of one, O of N problem. If you truly have a completely different address on each device, it's going to be O of N. But there's another way to get it to be O of one that still doesn't need an MMU. Sure, you could use the MMU and you could map them all to the same virtual address. But you could also have just some mathematical function that computes the address, right? Like say all the GPUs are just at like, you know, one followed by eight zeros, two followed by eight zeros, three followed by eight zeros, right? You could imagine that device num is just a variable and you could multiply it.

##### **Qazalin** [[00:26:16](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1576)]
Yeah.

##### **Geohot** [[00:26:18](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1578)]
That's still O of one. Yeah, I mean, that's possible, but yeah.

##### **Geohot** [[00:26:28](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1588)]
Okay.

##### **Geohot** [[00:26:30](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1590)]
Well, I mean, I think we want to.

##### **Geohot** [[00:26:32](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1592)]
Yeah, it's a question if we want to do physical or virtual addresses. Kind of up to you for whatever like is easier.

##### **Geohot** [[00:26:42](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1602)]
Yeah, I see.

##### **Nimlgen** [[00:26:45](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1605)]
So yeah, the current implementation is the table.

##### **Geohot** [[00:26:52](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1612)]
Yeah. By the table, you mean like stack const? Yeah.

##### **Nimlgen** [[00:27:04](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1624)]
So in simple words, how this works right now. When I create, for example, I need a timeline address and I just have the not-realized buffer, which has several devices, like a tuple of devices. And after that I just have a rule which will bufferize this placeholder buffer with mstack and the real buffers behind the mstack.

##### **Geohot** [[00:27:41](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1661)]
Did I expect HCQ2 to work? I just ran `HCQ2=1` and it's hanging.

##### **Geohot** [[00:27:50](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1670)]
Oh, it eventually worked. I'm not sure I merged all the changes which are outside of HCQ2. Yeah. Can I see these? Can I see these command buffers in VIZ?

##### **Qazalin** [[00:28:27](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1707)]
Yeah. Yeah. Yeah. Yeah. Yeah.

##### **Nimlgen** [[00:30:37](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1837)]
I can see that. I don't see that.

##### **Geohot** [[00:30:44](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1844)]
Latest master. Let's see. HCQ schedule in VIZ.

##### **Geohot** [[00:30:52](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1852)]
Oh, let me just say `DEV=AMD` in case it's actually... Okay. This is kind of an annoying bug, in general, that has tripped me up a whole bunch of times. So it's not a bug in HCQ. Well, I mean, it is. But I didn't know that it wasn't actually running on the AMD device. It was running on some other device.

##### **Geohot** [[00:31:15](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1875)]
So I just see AMD0 does not exist. Must have a laptop. If I do `HCQ2=0`, it doesn't do this. Yeah, yeah, it only works for AMD, I believe. Oh, it only works for AMD. Okay. Let me see.

##### **Geohot** [[00:31:48](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1908)]
What's the issue with AMD? Oh, yeah, okay. I ran it on a TinyBox. Now I see HCQ schedule. Cool.

##### **Geohot** [[00:31:57](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1917)]
So this HCQ schedule is running for each kernel. Yeah. Why? Why isn't it one graph rewrite for all of them? Oh, maybe it's actually submitting like that.

##### **Geohot** [[00:32:20](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1940)]
Is it one HCQ schedule per realize, or is it multiple HCQ schedules per realize?

##### **Nimlgen** [[00:32:27](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1947)]
No, actually in runtime currently there is one HCQ. I mean, in runtime it just compiles these like this schedule is per kernel. In graph, it just takes all the kernels and has one schedule.

##### **Geohot** [[00:32:47](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1967)]
I see. Yeah, I mean, we probably shouldn't have that, right? It should probably be one. Like, I'll post what I'm seeing right now. And I'm seeing, I think, way too many schedules. Yeah.

##### **Geohot** [[00:33:04](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1984)]
I think it's just going to be really slow.

##### **Geohot** [[00:33:13](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=1993)]
I don't know how many times this thing is actually calling realize. But for each call to realize, basically, there should only be one HCQ schedule.

##### **Geohot** [[00:33:27](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2007)]
Yeah, I see. Okay. But I mean, it could be. I'll think about that.

##### **Nimlgen** [[00:33:45](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2025)]
But basically, we can have like different, like in runtime, we can have interleaved AMD kernels and CPU kernels.

##### **Geohot** [[00:33:58](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2038)]
Yeah. No, that's fine. Here, I mean, I should just run something. Let me run test_mnist instead of... Something's really slow doing this though. test_mnist took six seconds. Yeah. I mean, there's tons and tons of HCQ schedules being submitted here.

##### **Geohot** [[00:34:22](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2062)]
This is for test_mnist. There's just no way we can afford to do all these graph rewrites. This has to be kind of like one thing. I don't see any submits later on either. I only see some submits at the top. But yeah, you see what I'm saying? Like why do we see all these HCQ schedules?

##### **Nimlgen** [[00:35:11](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2111)]
Yeah, so basically, I just take one kernel and just run the schedule and build the C submit program for it.

##### **Geohot** [[00:35:24](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2124)]
But yeah, I don't think it should be this, right? I think it should be for one graph you build the program. Like we have the normal schedule.

##### **Geohot** [[00:35:40](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2140)]
There shouldn't be more. I mean, maybe there could be like a few more HCQ schedules if you're dealing with the fact that it has to go to different devices. Like yeah, there can be like one main schedule, and there can be like then one HCQ schedule per device. But there can't be one HCQ schedule per kernel.

##### **Qazalin** [[00:36:05](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2165)]
Yeah.

##### **Geohot** [[00:36:09](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2169)]
Okay, yeah. I'll think about that. But yeah.

##### **Geohot** [[00:36:20](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2180)]
And think about basically, like there should be the same number of HCQ schedules as there are doorbell rings. Like when you're about to ring the doorbell, that's when everything should be scheduled, when the command buffer should be built.

##### **Nimlgen** [[00:36:33](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2193)]
So that's exactly that. I mean, because we just execute kernel one by one. I mean, that's runtime, they're not graphed.

##### **Geohot** [[00:36:48](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2208)]
Yeah. Okay. Okay. Okay. We have to just stop doing that. It should just automatically become graphed. Yeah. Is there any downside to that? Um, I think no.

##### **Geohot** [[00:37:07](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2227)]
I see why this is happening, right? I see what invariant you preserved here. Historically we've been submitting the kernels to the GPU one at a time if they're not in a graph. But this kind of stuff is absurdly slow, right? One schedule should be one graph. There should be no more distinction between the two. Even if you want to do something like not put it all in a single command buffer, even if it's like three command buffers that you want to split just so you could submit small ones early, that should still basically be one graph rewrite to compile them all to command buffers.

##### **Nimlgen** [[00:37:50](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2270)]
Yeah, but okay, I mean, that's not implemented. But basically that's the feature, to just use graphs in this schedule.

##### **Geohot** [[00:38:02](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2282)]
But I'm saying go even further with this. The other feature should kind of be gone. There shouldn't really be a way to do it without graphs.

##### **Geohot** [[00:38:15](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2295)]
yeah

##### **Geohot** [[00:38:16](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2296)]
Yeah, it's kind of like, sure, you can always just say that what I'm basically doing is submitting 30 graphs of size one. And of course that should always work. But there should basically no longer be a distinction between graphed and ungraphed. There should just be like, I have 30 kernels to submit. Of course I'm going to submit them in a batch unless I set some flag to not do that.

##### **Wozeparrot** [[00:38:37](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2317)]
Okay, I'll test that.

##### **Geohot** [[00:38:40](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2320)]
Basically, maybe the current...

##### **Wozeparrot** [[00:38:42](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2322)]
Yeah, there's a lot of copies too.

##### **Geohot** [[00:38:48](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2328)]
All right, go ahead. I didn't get you. Show the current output.

##### **Nimlgen** [[00:39:07](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2347)]
Um, no, it actually takes some time for the graph to be built, but if it's cached, it may be fine.

##### **Geohot** [[00:39:13](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2353)]
Yeah, I'll do that. But we should focus on, it's just important that it's O of one graph rewrites for a schedule, not for a kernel.

##### **Geohot** [[00:39:29](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2369)]
Like the number of calls you make to the graph rewrite function should not grow with the number of kernels in the graph. Yeah. Um,

##### **Nimlgen** [[00:39:42](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2382)]
I mean, they're kind of the same because the more kernels you have, the more patches you have, the more rewrites you do.

##### **Geohot** [[00:39:51](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2391)]
But that's different. That's the number of UOps, not the number of rewrites. Right. The number of rule triggers can be O of N, but the number of calls to the function `graph_rewrite` needs to be O of one.

##### **Geohot** [[00:40:07](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2407)]
Okay. You see the distinction?

##### **Wozeparrot** [[00:40:13](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2413)]
Yeah, of course you're going to need patches that are O of N. That's really fine.

##### **Qazalin** [[00:40:17](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2417)]
Okay.

##### **B1tg** [[00:40:21](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2421)]
You know, it's general.

##### **Qazalin** [[00:40:30](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2430)]
Okay.

##### **Chenyu** [[00:40:31](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2431)]
Okay, let's move on. Next is my stuff. So, made a bunch of changes to tensor.py, specifically to `requires_grad`. Now, `requires_grad` is removed. Under the hood, everything can have a grad. It really depends on if you use such grad or not. It's lazy. And the replacement in terms of optimizer is a different field called `is_param`. So that's just a flag for the optimizer to know if it should include things as a param.

##### **Geohot** [[00:41:17](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2477)]
Yeah, I think that's a super reasonable way to do it.

##### **Chenyu** [[00:41:20](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2480)]
Yeah, so I think that is done. That's why I closed the issue for that. Then the next big thing I was working on and still work on is deviceless const. So the idea is const is always inline, so it should not have a device. For now, const can have a unique const and a device source. So the eventual goal is to remove those, and const should always just be the same. A few things that I have done: for now, if you construct a tensor const, it doesn't have a device in it. And I also removed `Tensor.from_uop`. That was a specific function that just doesn't make sense. It was there because the symbolic shape of const didn't have a device, but const was requiring a device, something like that. So that is done. A near-term API change would be if you call `Tensor.full`, `Tensor.ones`, `Tensor.zeros`, we would just add a clone at the end to those functions. So you get a buffer instead of a const. We discussed about this. I think this pretty much falls into users' expectation when they write this, especially with a weight. And if you want a fusible const, like how you would do in Winograd or in other cases, like you want an inlineable const, then you just call `Tensor.const` and you will get that. I also added a flag called `buffer` to `full`. So if you call `buffer=False`, then it also does the const, then reshape, then expand for you. So you've got a fusible version of that. The current bottleneck is invalids and anonymous buffer and function.py, because there are certain assumptions about that mechanism that rely on the unique const. So I don't quite know, is there any ongoing plan to that?

##### **Geohot** [[00:43:53](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2633)]
I don't think anonymous buffers actually work. I think if there's any stuff for anonymous buffers, we could rip it out. So the real answer to anonymous buffers isn't some carefully constructed store after thing with an anonymous buffer. We can just delete all that. That's just wrong. That should just be replaced by load. Like load is an anonymous buffer. But for now, I don't think we use that logic in anything. We can just rip it out.

##### **Chenyu** [[00:44:19](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2659)]
No, we use that logic for everything. What do you mean? For what? So you can see my invalid-is-empty PR. We use that to build in function.py.

##### **Geohot** [[00:44:38](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2678)]
Invalid is empty.

##### **Chenyu** [[00:44:40](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2680)]
Yeah, basically all the, where we call invalids to do stuff.

##### **Geohot** [[00:44:46](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2686)]
Yeah.

##### **Chenyu** [[00:44:47](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2687)]
I just replace it with empty and make it work. That seems totally fine. Yeah, because we were discussing about this, and I remember at some point you said empty should be invalid. Yeah, empty should be invalid. So if that looks good to you, I'm going to clean those up and probably delete invalid, unless we still want that mechanism somewhere.

##### **Geohot** [[00:45:17](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2717)]
We can't get rid of invalid, I don't think. Oh.

##### **Chenyu** [[00:45:21](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2721)]
Now it's just empty.

##### **Geohot** [[00:45:23](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2723)]
Oh, oh, like, yeah.

##### **Geohot** [[00:45:27](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2727)]
Yeah, that's fine. OK. Yeah, that's fine.

##### **Chenyu** [[00:45:32](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2732)]
OK, OK, OK. Yeah, I was thinking about this.

##### **Qazalin** [[00:45:37](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2737)]
Oh.

##### **Geohot** [[00:45:39](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2739)]
The other thing to move to mixins is gradient. We have a mixin for gradient that also moves gradient.py there. Sure. Notably not backward. Backward stays in tensor. Gradient should be a UOp-friendly method.

##### **Chenyu** [[00:46:00](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2760)]
You want gradient in mixin or gradient in gradient.py?

##### **Geohot** [[00:46:04](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2764)]
I want gradient.py. I want all that logic to go to mixin. And yeah.

##### **Qazalin** [[00:46:10](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2770)]
That's good.

##### **Geohot** [[00:46:11](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2771)]
Yeah. Right? Like.

##### **Chenyu** [[00:46:12](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2772)]
Yeah. It should just work, right? It's just given a function and takes the gradient so far.

##### **Geohot** [[00:46:17](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2777)]
Yeah, yeah, yeah. It's just calling tensor in a few places, creating that tensor with a 1.0. That should special all the fucking UOps.

##### **Chenyu** [[00:46:26](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2786)]
Okay, sounds good. Yeah, I think this should be the last. I mean, invalid was the last place that we have const. We certainly use unique const, but I think that's also the only place that const has a buffer. Sorry, const has a device. So once we remove those, should be able to keep just const with const.

##### **Geohot** [[00:46:53](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2813)]
Right.

##### **Geohot** [[00:46:54](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2814)]
Super happy for that to be deleted.

##### **Chenyu** [[00:46:57](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2817)]
I think it's pretty nice. Also, you don't expect to update function.py anytime soon, right? There are a few commented-out lines that I don't know if you want to have or not have.

##### **Geohot** [[00:47:15](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2835)]
Yeah, I mean, function.py exists in this liminal space between the old JIT and the new JIT. The lines that like, yeah, the lines that like add contiguous and assign the output, I don't exactly know how to resolve all of that yet.

##### **Chenyu** [[00:47:36](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2856)]
So my take is I would try my best to simplify those. And if I find something out that doesn't break anything and I think it's cleaner, I would just merge it. Is that fine?

##### **Geohot** [[00:47:55](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2875)]
Yeah, I think that's right. I think that preserving the kind of logic, right?

##### **Chenyu** [[00:48:05](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2885)]
Yeah, you also see some like, `allow_device` equals to something, something bug. There's a flag for that. Right. I think that's a bug.

##### **Geohot** [[00:48:14](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2894)]
So I mean, what's happening there is these things are not actually pure and they're opening the device for various reasons.

##### **Chenyu** [[00:48:27](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2907)]
No, but it doesn't open any device now. Okay, then maybe you can remove that. Maybe it's fixed. Yeah, I mean, it was some const.

##### **Geohot** [[00:48:33](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2913)]
That's great. Great. And I'd love to delete that device and function bug crap.

##### **Chenyu** [[00:48:37](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2917)]
Yeah, OK. OK, then I will clean up that as part of this refactor. Yeah.

##### **Qazalin** [[00:48:43](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2923)]
Yeah.

##### **Geohot** [[00:48:44](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2924)]
But the basic thing, I mean, we have an unclear distinction right now between function and call and what it means to be stateless and stateful. I think this will help once we finally understand load a bit more because you need anonymous stores. You can have anonymous stores in a function. You just can't have named stores in a function because a named store has side effects.

##### **Chenyu** [[00:49:13](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2953)]
Yeah.

##### **Geohot** [[00:49:13](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=2953)]
And I think that's where the load doesn't have side effects. And there's a really key distinction there. When we start to tighten that idea up, the basic invariant is that function has no side effects and call has side effects. Function allows you to return stuff. Call does not. And then it's also like the decorator is called function, which makes it a little bit confusing. But we need something like this. I tried really hard to do without this, but you can't because it's a different complexity order, the ability to have hierarchy. There's a reason that every programming language supports something that looks like functions, because it gives you hierarchy. And this hierarchy turns O of N into N log N.

##### **Geohot** [[00:50:12](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3012)]
Okay. All right.

##### **Chenyu** [[00:50:15](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3015)]
I think I know what to do next and we can move on to the next point. You had, like, assembly.

##### **Qazalin** [[00:50:25](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3025)]
Yeah.

##### **Geohot** [[00:50:27](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3027)]
So I merged x86 assembly. I think that there's a bunch of things that aren't great. There's a bunch of fragile things in that code. But it's not exactly the fault of the code, and it has more to do with that `dtype.vec` is a problem. These constructions where like in assembly, very often you don't say load two floats. You say load 64 bits. So there's this distinction that's not so clear in assembly. I think a lot of the matching rules are very verbose. But again, some of this is like I have to look and see a better way to write it. But I think the big victory with getting assembly merged is that it's very clear where two things live. One is the register allocator and one is instruction selection. And instruction selection and register allocators are not abstract concepts. They're something that you need to do and you need to think about. And I think it's important that we think about them as soon as possible. So right now we have something called the memory planner. That's basically a register allocator. We have decompositions, which are basically a form of instruction selection. So yeah, I mean, we already have things that look like this. But it's important to make these things explicit, to get us out of this "oh, but then you just dump it into LLVM" mindset. Because a lot of what tinygrad is doing can also be done by LLVM. And you can take LLVM and, like any of our graph rewrite passes, you can have it do a lot or you can have it do a little. So it's nice to actually have an end-to-end path that has zero LLVM, and continuing to work on that and clean it up I think is important. Yeah. That's assembly. It works. `DEV=CPU:x86`. And then for `dtype.vec`, you know, removing that forces a lot of questions. So `dtype.vec` is used in a few places that aren't where you think it's used. There's the obvious place where it's used for arithmetic, and this is equivalent to shape. If I have like a `dtype.vec(4)` plus `dtype.vec(4)`, I get a `dtype.vec(4)` out. That is equivalent to a shape of four, shape of four, shape of four out. There's two places where it's being used that don't match that idea. One is in images, and that one's fixed. So we used to use 2D indexing in images with a `dtype.vec(2)`. This is fixed to actually be proper two-dimensional indexing. And then the other one that I'm working on now is the one where we do a load of four contiguous elements. So we can do, like a load four in a GPU is a real instruction. This can't exactly be an index because the index would require you to specify four addresses. And that's of course not what a load four on the GPU actually does. The load four on the GPU requires you to have one address, and then it loads four from it. So historically, we've done that with `dtype.vec`. We've had an index, which is a pointer dtype, and then we dereference that and we get the underlying shape of the dtype, which is just insane. And the fact that you can put pointer before the vec and pointer after the vec and it means something different, I mean, yes, it's like this in C as well, but that doesn't really make it okay. So my plan now is to move that to buffer view because buffer view is that exact thing that we're talking about. Buffer view is basically saying I have an offset into a buffer and I'm taking a certain number of elements from that offset and those elements must be contiguous. So I'll be able to use a buffer view, and then by putting a load on that buffer view, I can load four contiguous elements in the same way a load four does. And this also allows you to load four without... So one of the problems with using index, you're like, okay, I could just use index. It could be like a two-dimensional index and I'll reshape it first. But what if you want to load four from index seven? There's no real way to do that with index. I mean, you could specify seven, eight, nine, ten. But now you have this const and you've got to check it, and this is really complex. It's much easier to just say, okay, that's a buffer view with size four, offset seven, load, done. It can be my week this week. One more long slog to the removal of `dtype.vec`, but it's good. It clarifies some things. And then you also get into like, okay, `dtype.vec`.

##### **Qazalin** [[00:55:28](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3328)]
OK.

##### **Geohot** [[00:55:28](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3328)]
Buffer view and bitcast, are those the same thing? Are those different things?

##### **Chenyu** [[00:55:34](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3334)]
Do you want to do a shape-changing bit cast? OK.

##### **Geohot** [[00:55:37](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3337)]
So bitcast means two things. Shape-changing bitcast should not exist as an op. Shape-changing bitcast is buffer view. If you want to change your shape, the only way to do it is with buffer view. But the question is, why does a buffer view only have to live on a buffer? But the idea of shape-changing bitcast definitely should not exist. In fact, there's even a question: should bitcast exist at all? And I'm going to look into how it's used. But buffer view also lets you change the dtypes.

##### **Chenyu** [[00:56:10](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3370)]
That would be nice. One of the things that's left on tensor.py is all of the bitcast on disk.

##### **Geohot** [[00:56:21](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3381)]
Yeah, I'll think about it on disk. I'll think about it. I'll talk to LLMs a bit. I'll understand how C++ dealt with this. I'm not that familiar with the latest. If you ask me what reinterpret cast meant, I'd fail that class. So I'm going to look into how other languages have dealt with this. Sounds good. And the way that you do a bitcast in C is actually by assigning something to a buffer, dereffing the buffer, and then referencing the buffer, and then dereffing the buffer as a different type. So yeah.

##### **Chrism** [[00:56:55](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3415)]
That awful thing with unions.

##### **Geohot** [[00:56:57](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3417)]
Yeah, yeah, yeah. You can also do it with unions. But that doesn't actually always work. Okay. The union doesn't actually guarantee that, but yeah, whatever.

##### **Chenyu** [[00:57:05](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3425)]
Anyway, looking forward to that.

##### **Geohot** [[00:57:07](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3427)]
Accurate.

##### **Chenyu** [[00:57:08](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3428)]
Yeah. Let's move on to CI and test.

##### **Chrism** [[00:57:14](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3434)]
Yeah. Yeah, so the reason that there was that stupid thing in test_tiny is it did previously depend on `getenv("CI")`, but I removed all of `getenv("CI")` from core tinygrad. And I wanted to delete it from tinygrad helpers because then there's less temptation to add it back somewhere.

##### **Geohot** [[00:57:33](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3453)]
I want to remove from all the tests. So any test that doesn't pass in CI should just be deleted.

##### **Chrism** [[00:57:37](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3457)]
Yeah. Yeah, so that's the solution to make that one not require PYTHONPATH. The other thing I did was, at least within the core tinygrad, removed `is_dtype_supported`. So instead, now you have your renderer and then you can call supported dtypes on it, and then it gives you a set of the supported dtypes. And so that's nice because that code, `is_dtype_supported`, was pretty hacky and unreliable. So hopefully, it's a lot more reliable now. And yeah, so then I also started cleaning up some of the tests. For instance, a lot of test randomness, I moved that into unit. Not all of it, but most of it has moved into unit now. So that should make it a little faster. And there's also just some general looking at some of the slow tests and trying to figure out whether or not they were really needed. But yeah, that's still an ongoing project to figure out whether or not tests are necessary and just clean them up if they're not, if we don't really need them, or if they're testing stuff that's silly to test. Yeah, I think that's most of it. I have some ideas about how to do fuzzing. But I feel like before I add more tests, maybe I should try and clean up the old ones.

##### **Geohot** [[00:59:08](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3548)]
Yeah, definitely do that. There are two things. I think that makes a lot of sense to put on the renderer: `is_op_supported`, `is_dtype_supported`.

##### **Chrism** [[00:59:18](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3558)]
There's no `is_op_supported`, but there probably should be.

##### **Geohot** [[00:59:20](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3560)]
There is an `is_op_supported`. We just call out the, we look in the op spec. Yes. Yes, we should have a method on renderer. The idea of a renderer saying I support these dtypes, I support these ops, is a universal that's going to be in the end system. You have this idea, right?

##### **Chrism** [[00:59:34](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3574)]
There's some question about, and I think this is like an OpenCL idea, but I bet it exists for other renderers, is like, okay, so you can support a dtype, but you can only support loads and stores with the dtype, and you can't support math on the dtype? Yeah. So.

##### **Geohot** [[00:59:50](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3590)]
We can have that distinction. That's fine. Yeah, okay. The point is that these should be renderer methods, not global methods that check the renderer string name.

##### **Chrism** [[00:59:56](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3596)]
Yeah. Yes, for sure.

##### **Geohot** [[00:59:59](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3599)]
Yeah, no, I also want you to unify tests. I mean, I know that I broke them apart, and I think that it was worth thinking about, but we should think about how to reunify test/unit and test/null. Okay. So the distinction right now is that test/nulls don't require any device, and unit requires some device. You know, null is a subset of some device. I think that we should basically just split tests into two categories, which are tests that we want to test on every backend, and then tests that we can test on one backend and be confident that they're right across everything.

##### **Chrism** [[01:00:26](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3626)]
Yeah, I did this for the randomness stuff, where I was like, okay, as long as they all apparently support randomness, then all of the behaviors of saying, oh, well, randomness needs to be normal is probably preserved, assuming randomness is preserved.

##### **Geohot** [[01:00:39](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3639)]
Yeah, and then I think we do have this third kind of tests as well, which are still unit tests. They're definitely all a subset of unit tests, but they're kind of like application tests. The whole AMD emulator is kind of a tinygrad application. LLM is kind of a tinygrad application. So yeah, we have unit tests which test correctness of tinygrad. We have backend tests which test the correctness of renderers. And then we have application tests which kind of almost exist outside tinygrad, not outside tinygrad, but they're not tinygrad tests. And every time that we get a failure only in an application test, if the bug is in tinygrad, that's bad. If the bug is in that application, it's fine.

##### **Chrism** [[01:01:28](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3688)]
Yeah, yeah, for sure. Yeah, that makes sense. And that applies to like the ONNX frontend as well.

##### **Geohot** [[01:01:33](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3693)]
Exactly. ONNX is an application test. Right. And yeah, we really treat that as a very bad thing. An application test fails because of a bug in tinygrad; let our invariants work.

##### **Chrism** [[01:01:47](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3707)]
Yeah, for sure. Yeah, that means that testing is not relevant to the rest of testing.

##### **Geohot** [[01:01:54](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3714)]
Yeah, I think that's kind of it.

##### **B1tg** [[01:02:01](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3721)]
Yeah, it's,

##### **Chenyu** [[01:02:03](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3723)]
What time is... Oh, Comma happiness. Oh, yeah. We have a bug with IMAGE and rangeify. Everyone's complaining that one of the models that he added a bunch of layers to is wrong. I just put a very quick hack for it, but I think something is wrong there.

##### **Geohot** [[01:02:25](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3745)]
I saw your fix and I didn't understand it. I don't even understand how IMAGE can break rangeify.

##### **Chenyu** [[01:02:31](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3751)]
So the way IMAGE creates range, I think in that context, there was an assumption that every range is unique. And that's not true.

##### **Geohot** [[01:02:43](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3763)]
IMAGE creates range?

##### **Chenyu** [[01:02:47](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3767)]
So,

##### **Qazalin** [[01:02:48](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3768)]
yeah, I think that's a good question.

##### **Chenyu** [[01:02:49](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3769)]
Basically in that function, there is a key collision. And IMAGE creates that. And why that's the case, I'm not sure. But that was the cause of the issue. Thank you for fixing that. If you disable UOp cache, then that's also fixed. Even worse. Yeah. So,

##### **Geohot** [[01:03:13](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3793)]
oh, I see. Yeah.

##### **Geohot** [[01:03:15](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3795)]
IMAGE hack. Yeah.

##### **Chenyu** [[01:03:19](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3799)]
So, uh, I was,

##### **Geohot** [[01:03:21](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3801)]
I was sick and I tried to read this and I couldn't.

##### **Chenyu** [[01:03:26](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3806)]
I have,

##### **Geohot** [[01:03:27](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3807)]
I still can't read this.

##### **Chenyu** [[01:03:31](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3811)]
Yeah. I mean, oh,

##### **Geohot** [[01:03:33](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3813)]
Oh, is this happening because there's two reduces ending the same?

##### **Chenyu** [[01:03:38](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3818)]
Yes.

##### **Geohot** [[01:03:39](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3819)]
Yeah. That shouldn't be possible.

##### **Chenyu** [[01:03:43](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3823)]
That's possible the way we write float16 thingy. I see. Okay. So that's kind of out of spec, but kind of it's broken now. So, yeah.

##### **Qazalin** [[01:03:55](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3835)]
Yeah.

##### **Chenyu** [[01:03:55](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3835)]
Uh, I mean, it's probably not clear if we want to do anything about this now, but

##### **Geohot** [[01:04:03](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3843)]
I don't know. That `if` clause looks like to me...

##### **Chenyu** [[01:04:07](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3847)]
but yeah, I guess.

##### **Geohot** [[01:04:10](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3850)]
Okay.

##### **Chenyu** [[01:04:12](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3852)]
Yeah. So,

##### **Geohot** [[01:04:13](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3853)]
Just do the nested two `any`s, including a `for` and `if`. Why not?

##### **Chenyu** [[01:04:17](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3857)]
Yeah. There was another attempt where I tried to fix this in the reduce context by including that, but that failed some other thing.

##### **Geohot** [[01:04:30](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3870)]
yeah. If,

##### **Chenyu** [[01:04:31](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3871)]
if they are happy with this.

##### **Geohot** [[01:04:33](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3873)]
Yeah. Yeah. Yeah. Okay. Maybe I can take a quick look today. If I just see what it is, because every time I've seen it, every time I've seen this happening where like a range is ended twice by two different reduces, it's usually caused by some like upstream bug.

##### **Chrism** [[01:04:46](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3886)]
Yeah. Um, there's the other thing that Comma was complaining about, which is the JITs, like the duplication in IMAGE.

##### **Geohot** [[01:04:58](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3898)]
Won't fix. I mean, yeah, I think that will fix itself someday once the JIT can basically capture two functions at the same time. But until that can happen, there's not really a fix.

##### **Chrism** [[01:05:12](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3912)]
Oh, Well, the other thing is they could unify their model if they did a symbolic compilation of the warp. But I think that was slow.

##### **Geohot** [[01:05:21](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3921)]
That's a different issue. But no, if they're asking for a quick hack to fix that, I don't know, can they use gzip on the pickle?

##### **Chrism** [[01:05:30](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3930)]
That's what I said.

##### **Geohot** [[01:05:31](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3931)]
Yeah, does that fix it? Is it a RAM issue? Is it a size issue?

##### **Chrism** [[01:05:35](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3935)]
I think, yeah, I told them to run gzip on it, and they said that it worked for one thing, but it didn't work for the other one. So I don't know. But I think gzip accepts an argument about how long to think about compression.

##### **Geohot** [[01:05:45](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3945)]
Yeah, there's a compression level. I don't know if the context... But whatever. That one, I don't have context, but it's a real bug. I can think about that one if Comma is really blocked on that. But really, they should think about how to hold it differently. Yeah.

##### **Chenyu** [[01:06:04](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3964)]
We have anything else? Well, what about the LLaMA 70B fine-tuning thing? I'll defer to you if you think that's good.

##### **Wozeparrot** [[01:06:14](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3974)]
Yeah, I didn't get to take a look last week. I'll take a look this week.

##### **Chenyu** [[01:06:18](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3978)]
Okay. That's good. And I think we still have some open PRs from B1TG for the stuff. So let's try to do something for those.

##### **Geohot** [[01:06:34](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3994)]
Hello?

##### **Qazalin** [[01:06:35](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3995)]
Hi.

##### **B1tg** [[01:06:37](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=3997)]
Hi. I took a look at the sharding regression in the bench history and found this existed since the rangeify default. Before that, shard is faster than no shard.

##### **Chenyu** [[01:07:12](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=4032)]
Yeah, there's certainly a perf regression for sharding. It's nice to address those.

##### **B1tg** [[01:07:18](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=4038)]
Also, there are other commits that make the shard slower, but after rangeify, I'm not sure this is relevant.

##### **Chenyu** [[01:07:33](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=4053)]
It's not very helpful to look at the commit a year ago and say things were good before that. You probably need to find a way to bisect them and fix the issue.

##### **Geohot** [[01:07:46](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=4066)]
Yeah, this probably has to do with the interactions between shrink and copy. But yeah, I would just try to find a minimum repro that did a different thing before that versus now, and then we can look at it.

##### **B1tg** [[01:08:07](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=4087)]
Okay, I also read some llama.cpp code and I found they use the GEMV at the int level, not the half-offloads. I tested with some custom kernel and pushed the Kimi decode speed over 15 tokens per second. Which is the preferred way to upstream the custom kernel? We need to use UOps, not HIP code, now?

##### **Geohot** [[01:08:52](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=4132)]
UOps are preferred. If you can write it in UOps, that's always a lot better than writing it in HIP code. But if there's no way to write it in UOps, then...

##### **B1tg** [[01:09:07](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=4147)]
I mean, speedup needs to fuse those kernels. So you just need a custom kernel.

##### **Chenyu** [[01:09:19](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=4159)]
I think generally if custom kernel is the only way you see to do things and it makes a very big difference, then it's probably worth considering. But if you think that's just temporary, then it's not worth considering. This is very hard to say without a change. But UOps is preferred, unless there's a strong reason that it cannot be done.

##### **Geohot** [[01:09:48](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=4188)]
Yeah, the deeper question here whenever you're thinking of adding a custom kernel is saying, why can't tinygrad output this kernel? I wrote the custom kernel for embedding backwards. And the reason tinygrad can't generate that kernel is because of atomics. There's like a clear, oh, well, here's why tinygrad can't do that.

##### **B1tg** [[01:10:13](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=4213)]
Since we like the packed kernel, it's packed in int.

##### **Geohot** [[01:10:21](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=4221)]
Oh. Well, why? And...

##### **B1tg** [[01:10:27](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=4227)]
It doesn't generate those on this function. And if we want the matrix in the int level, we need those for speedup.

##### **Geohot** [[01:10:42](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=4242)]
Interesting.

##### **Geohot** [[01:10:43](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=4243)]
Okay. I mean, yeah, if it's a custom kernel, it's a custom kernel. But...

##### **B1tg** [[01:10:49](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=4249)]
At the same time, I can make tinygrad generate that code and see if it's fast.

##### **Geohot** [[01:11:03](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=4263)]
Yeah, if it already fits into the existing abstractions. That's kind of the question. But I would focus more on the sharded stuff. The sharded stuff's a lot more like, like, fundamental, right? The sharded stuff, like, it's fundamentally incorrect. Yeah. To put some layers on each GPU. Right? Like, that's just not how we want to do it. We want it sharded. Again, I always like correctness before speed, always.

##### **Geohot** [[01:11:31](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=4291)]
Okay. Okay.

##### **Qazalin** [[01:11:35](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=4295)]
Cool.

##### **Chenyu** [[01:11:37](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=4297)]
I think that's about it for this meeting. Anything else?

##### **Geohot** [[01:11:42](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=4302)]
Nope. We're already over time.

##### **Chenyu** [[01:11:44](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=4304)]
Okay. That's it for today. Thank you, everyone. See you next week. Bye bye.

##### **Geohot** [[01:11:49](https://www.youtube.com/watch?v=g8SHLqz6AHw&t=4309)]
Bye. Bye.
