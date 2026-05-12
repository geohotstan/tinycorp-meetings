# 2026-05-11 Meeting

### Meeting Agenda

**Time:** new meeting #19, 5/11 9am Monday San Diego time
- company update
- divmod change
- viz
- index gate refactor
- autogen
- buffer jit refactor
- mlperf llama
- issues, comma happiness


### Audio

[Youtube Link](https://www.youtube.com/watch?v=umHATMs0HDA)

### Highlights

- **[Company Update](#geohot-000006)**: Exa Box made progress; a shipping container is likely arriving this week, will be placed in back, and will include batteries to time-shift power.
- **[Contributing Policy](#geohot-000222)**: New PR policy asks contributors to explain why their PR should be merged; AI-generated or misunderstood PRs may lead to GitHub bans.
- **[Divmod / UOp Spec](#geohot-000523)**: The goal is to keep the middle of tinygrad’s “hourglass” UOp pipeline simple and enforce that certain ops do not appear during optimization passes.
- **[Tensor Cleanup / Winograd](#chenyu-000710)**: Chenyu is exploring moving image and Winograd logic into rewrite rules, including 3x3 through 7x7 Winograd expressed with matrices.
- **[Rewrite Rule Direction](#geohot-000811)**: Rewrite rules should be separated into deterministic dialect-changing transformations versus heuristic same-dialect optimizations like Winograd or image rewrites.
- **[Viz / Agent Kernel Work](#qazalin-001153)**: GPT-5.5 sped up LLaMA kernels but broke convergence, highlighting the need to constrain agent search to safe transformations rather than only verifying after the fact.
- **[Kimi and Qwen Speedups](#geohot-001839)**: The team wants Kimi merged and sped up because it is more practically useful than Qwen, enabling tinygrad to eventually speed itself up.
- **[AMD Copy Matmul](#qazalin-001943)**: A branch fixes bank conflicts in copy matmul and improves performance from about 80 TFLOPS to 90 TFLOPS, though tuning still matters.
- **[Index Gate / dtype Refactor](#geohot-002326)**: Work on removing `dtype.vec` led to moving gates onto loads and stores, rethinking image indexing, and clarifying the boundary between optimization and instruction selection.
- **[Implicit dtype Promotion](#geohot-002604)**: The team discussed making dtype promotion implicit, similar to broadcasting, with only source UOps and explicit casts defining dtype changes.
- **[Autogen / Offline Firmware](#chrism-003254)**: AM and NV backends now rely more on local `/lib/firmware` instead of downloading files, with PMC YAML autogen remaining as a cleanup item.
- **[CI Reliability](#geohot-003741)**: Random GitHub CI crashes are suspected to involve memory pressure or timeouts; the team wants better diagnostics with tools like `faulthandler` and pytest timeouts.
- **[HCQ2](#nimlgen-003942)**: HCQ2 now runs on AMD with `HCQ2=1`, lowering to HCQ command buffers, while the next work is graph/disk support and refactoring away extra classes.
- **[MLPerf / Next Training Goals](#geohot-004643)**: The MLPerf submission is in at about 33% worse than AMD, and the next focus is training 8B MP, then moving toward a converged 70B run.

### Transcript
##### **Geohot** [[00:00:00](https://www.youtube.com/watch?v=umHATMs0HDA&t=0)]
Welcome.

##### **Geohot** [[00:00:01](https://www.youtube.com/watch?v=umHATMs0HDA&t=1)]
We start with company update.

##### **Geohot** [[00:00:06](https://www.youtube.com/watch?v=umHATMs0HDA&t=6)]
Progress on the Exa Box last week. I'm going to get a shipping container probably this week. Where are we going to put it? In back. We're actually going to spray paint on the ground room for two.

##### **Geohot** [[00:00:26](https://www.youtube.com/watch?v=umHATMs0HDA&t=26)]
The Exa Box is also going to have some batteries in it.

##### **Geohot** [[00:00:30](https://www.youtube.com/watch?v=umHATMs0HDA&t=30)]
So we can time-shift power. Yeah, the price of 5090s is upsetting.

##### **Geohot** [[00:00:40](https://www.youtube.com/watch?v=umHATMs0HDA&t=40)]
We should have bought way more 5090s. But then there were actually two things to buy that were better than 5090s. Like AMD stock. We could have just bought AMD stock. But then even better to buy than AMD stock was RAM. We could have bought RAM.

##### **Geohot** [[00:00:55](https://www.youtube.com/watch?v=umHATMs0HDA&t=55)]
Or just buy Micron.

##### **Geohot** [[00:00:58](https://www.youtube.com/watch?v=umHATMs0HDA&t=58)]
Has that gone up? Wait.

##### **Qazalin** [[00:01:00](https://www.youtube.com/watch?v=umHATMs0HDA&t=60)]
Yeah. Hold on.

##### **Chenyu** [[00:01:02](https://www.youtube.com/watch?v=umHATMs0HDA&t=62)]
Every time you want to buy the hardware, you can also buy the company.

##### **Geohot** [[00:01:05](https://www.youtube.com/watch?v=umHATMs0HDA&t=65)]
That's easier than stockpiling RAM. Yeah. That and Chestnut progress. We have a lot of Chestnuts now.

##### **Chenyu** [[00:01:19](https://www.youtube.com/watch?v=umHATMs0HDA&t=79)]
Oh, we don't launch it this week? Oh, no. Next week?

##### **Qazalin** [[00:01:23](https://www.youtube.com/watch?v=umHATMs0HDA&t=83)]
No.

##### **Chenyu** [[00:01:23](https://www.youtube.com/watch?v=umHATMs0HDA&t=83)]
Okay. Soonish.

##### **Geohot** [[00:01:25](https://www.youtube.com/watch?v=umHATMs0HDA&t=85)]
Yeah. I mean, I don't know. We could launch it and do like a pre-order or whatever. I don't know. But no, it basically comes down to what you want your margins to be. You can trade off price for speed, and I told everyone to just make it cheaper.

##### **Geohot** [[00:01:43](https://www.youtube.com/watch?v=umHATMs0HDA&t=103)]
But how cheap is cheaper?

##### **Geohot** [[00:01:47](https://www.youtube.com/watch?v=umHATMs0HDA&t=107)]
We can go with where the real margins are, but.

##### **Geohot** [[00:01:48](https://www.youtube.com/watch?v=umHATMs0HDA&t=108)]
No, yeah.

##### **Geohot** [[00:01:54](https://www.youtube.com/watch?v=umHATMs0HDA&t=114)]
You end up paying like 30% more if you want it soon.

##### **Geohot** [[00:02:00](https://www.youtube.com/watch?v=umHATMs0HDA&t=120)]
I see. Also, for various reasons. Yeah, I mean, is that worth it? I don't know.

##### **Chenyu** [[00:02:08](https://www.youtube.com/watch?v=umHATMs0HDA&t=128)]
I don't know.

##### **Qazalin** [[00:02:10](https://www.youtube.com/watch?v=umHATMs0HDA&t=130)]
OK.

##### **Chenyu** [[00:02:12](https://www.youtube.com/watch?v=umHATMs0HDA&t=132)]
Anything you want to comment on the contributing policy you just added?

##### **Geohot** [[00:02:19](https://www.youtube.com/watch?v=umHATMs0HDA&t=139)]
Oh, yeah.

##### **Geohot** [[00:02:22](https://www.youtube.com/watch?v=umHATMs0HDA&t=142)]
I don't know. I mean, the problem with saying anything about it is it's the people who don't listen in the first place. Every single open source project is going through this. I see this on Hacker News all the time, where it's just like, we're just absolutely done dealing with AI. Please don't submit any PRs you don't understand. You're not helping. It's like, I get it. I get it. AI so easily fools you into thinking you understand something. Not everybody's going to be robust to this. It's not even like these people are malicious or trying to pull one over on us. They genuinely think they understand.

##### **Geohot** [[00:03:07](https://www.youtube.com/watch?v=umHATMs0HDA&t=187)]
They just don't. So yeah, that's the new policy. Please include a sentence or two about why you want the PR merged. And if you're submitting a PR you don't fully understand, having carefully read it, you'll be banned from GitHub.

##### **Geohot** [[00:03:23](https://www.youtube.com/watch?v=umHATMs0HDA&t=203)]
Not everyone can help themselves with AI.

##### **Qazalin** [[00:03:27](https://www.youtube.com/watch?v=umHATMs0HDA&t=207)]
OK.

##### **Geohot** [[00:03:30](https://www.youtube.com/watch?v=umHATMs0HDA&t=210)]
Now let's move on to the next one.

##### **Chenyu** [[00:03:33](https://www.youtube.com/watch?v=umHATMs0HDA&t=213)]
This is my change.

##### **Geohot** [[00:03:37](https://www.youtube.com/watch?v=umHATMs0HDA&t=217)]
So I changed all the divmods, almost all the divmods,

##### **Geohot** [[00:03:42](https://www.youtube.com/watch?v=umHATMs0HDA&t=222)]
before late UOp mixin now?

##### **Chenyu** [[00:03:51](https://www.youtube.com/watch?v=umHATMs0HDA&t=231)]
I say almost, because there's one place that if you just call the truncate, you will get the C div and C mod directly.

##### **Geohot** [[00:04:02](https://www.youtube.com/watch?v=umHATMs0HDA&t=242)]
That'll violate the new spec.

##### **Chenyu** [[00:04:04](https://www.youtube.com/watch?v=umHATMs0HDA&t=244)]
OK. I keep that for the same reason that we keep the shift left and shift right. Technically, you can also change left too, but we keep those.

##### **Geohot** [[00:04:18](https://www.youtube.com/watch?v=umHATMs0HDA&t=258)]
Well, no, I'm not sure that's true. The problem with shift left is you actually can't express shift left as a multiply. You can only express shift left by a constant as a multiply.

##### **Geohot** [[00:04:34](https://www.youtube.com/watch?v=umHATMs0HDA&t=274)]
Actually, you can't. Wait.

##### **Chenyu** [[00:04:35](https://www.youtube.com/watch?v=umHATMs0HDA&t=275)]
Sure, we don't use that? Even if you do a shift by a constant, its canonical form has two forms, right?

##### **Geohot** [[00:04:47](https://www.youtube.com/watch?v=umHATMs0HDA&t=287)]
Yeah.

##### **Chenyu** [[00:04:48](https://www.youtube.com/watch?v=umHATMs0HDA&t=288)]
But anyway, I can make that change. It's just now our simplifier is not good enough to find that pattern. And I don't really know what that pattern looks like. Basically, you want this to be represented in lower form, even if you want to truncate. But magically, after you write it back to the form, your correction term will cancel out. That's what we want. I don't have a good solution now.

##### **Geohot** [[00:05:17](https://www.youtube.com/watch?v=umHATMs0HDA&t=317)]
And that's why it's kept that way. Yeah, I mean, I think that this is really

##### **Geohot** [[00:05:23](https://www.youtube.com/watch?v=umHATMs0HDA&t=323)]
what we want to tighten with the spec. The question is not, so if you think of tinygrad as this big hourglass-style shape, there's a lot of stuff in the front, a lot of stuff in the back. Then when we're in this whole middle, this whole chunky middle, that's where we really want to check the spec. That's where we really want the spec to stay solidly simple. It's not that we need less ops. The ops can exist, whatever. By the time we get to CodeGen, who cares? Who cares if there's a sub-op or something? But we just don't want these to ever show up when we're doing passes. And we need to start enforcing that.

##### **Chenyu** [[00:05:59](https://www.youtube.com/watch?v=umHATMs0HDA&t=359)]
OK. Yeah, I'm fine with that. I just don't have a good way now. Because it's only for the cases that in late rewrite, you have more complicated stuff. Sometimes you don't want to simplify those expressions. For example, for the e comp for some of the sine, what is it called, transcendental thingy, sine, log, exp, we really don't want any reorder for that because it's more stable the way we express it. But then we start to have this div into a lower div, into a C div with a correction term. This time, we want it to cancel out with a previous correction term. I don't have a clean solution for that. Maybe it's just not enough to have just one late rewrite. We need to make that better.

##### **Geohot** [[00:07:00](https://www.youtube.com/watch?v=umHATMs0HDA&t=420)]
Anyway, that's it there.

##### **Qazalin** [[00:07:06](https://www.youtube.com/watch?v=umHATMs0HDA&t=426)]
OK.

##### **Chenyu** [[00:07:10](https://www.youtube.com/watch?v=umHATMs0HDA&t=430)]
This week, I was thinking about what to do with the rest of the tensor. I have some ideas. And I tried some of the stuff to remove things, either into rewrite rules or just see if I have ways to delete those. Two of the biggest things is one is image. Image is a big chunk. Another is Winograd. I also tried Winograd as a rewrite rule, which is pretty fun. I add from 3 by 3 all the way to like 7 by 7 Winograd. And everything can be expressed in a nice way. You just add a few matrices, and it would just match those and rewrite. I just need to think more if that's a good way to write it. I don't want to just move Winograd to mixin.

##### **Geohot** [[00:08:09](https://www.youtube.com/watch?v=umHATMs0HDA&t=489)]
Winograd.

##### **Geohot** [[00:08:11](https://www.youtube.com/watch?v=umHATMs0HDA&t=491)]
Yeah, it would be really nice to have that as a rewrite rule. Also, the image stuff as a rewrite rule. I mean, the image stuff is kind of a, this all gets to this idea, like those are heuristic rewrite rules. This gets to the idea of like we're overloading the rewrite engine to mean two things. There's the rewrite engine that are deterministic transformations from basically one dialect to another dialect. They're not exactly dialects. And it's a lot better than it being dialects because the problem with dealing with dialects is these things are no longer like reentrant. You can't like rerun it again. It's like, oh, I already lowered to that dialect. Sorry, like there's no way you can edit. Like you should be able to add a permute to basically assembly code, and it should figure out what to do if we do a good job with this.

##### **Geohot** [[00:09:09](https://www.youtube.com/watch?v=umHATMs0HDA&t=549)]
But we should still separate the concept of rewrite rules

##### **Geohot** [[00:09:14](https://www.youtube.com/watch?v=umHATMs0HDA&t=554)]
that change dialects versus rewrite rules that like Winograd or like image, which stay in the same dialect, but apply some heuristic transformations.

##### **Chenyu** [[00:09:28](https://www.youtube.com/watch?v=umHATMs0HDA&t=568)]
Yes. I think that's what I meant maybe a year ago for the smallest set of rewrite rules that generates output.

##### **Geohot** [[00:09:38](https://www.youtube.com/watch?v=umHATMs0HDA&t=578)]
Yeah. Like we're getting there. And actually, it's funny how we're getting there. We're getting there not through pruning of rewrite rules. We're getting there by most of the rewrite rules

##### **Geohot** [[00:09:49](https://www.youtube.com/watch?v=umHATMs0HDA&t=589)]
just kind of like don't do anything anymore.

##### **Geohot** [[00:09:54](https://www.youtube.com/watch?v=umHATMs0HDA&t=594)]
Well, OK.

##### **Geohot** [[00:09:55](https://www.youtube.com/watch?v=umHATMs0HDA&t=595)]
So like take like if you run with NOOPT,

##### **Geohot** [[00:10:03](https://www.youtube.com/watch?v=umHATMs0HDA&t=603)]
most of the rewrite rules barely trigger anymore. There used to be think about think about all the stuff that used to like manipulate movement ops, right? Just like move movement ops around and like, oh, you can like pass a reduce through a pass, a reshape through a permute. You can collapse it into a view. All that stuff is gone.

##### **Chenyu** [[00:10:22](https://www.youtube.com/watch?v=umHATMs0HDA&t=622)]
Gone because there's a rewrite rule in rangeify that rewrites these.

##### **Geohot** [[00:10:26](https://www.youtube.com/watch?v=umHATMs0HDA&t=626)]
There's one thing called indexing. And indexing actually, rangeify is crap, but indexing is good. Indexing is direct and pretty simple. Yeah, no, I mean, we replace it with this like concept instead of with like movement. You can't remove the concept. Of course, the concept still has to run. It's a dialect transformation. Or take like linearizer. Think about what the linearizer is now versus what the linearizer used to be. The linearizer used to be this thing that would create these like end blocks and all of these like weird things. Now it's like it's a toposort. So you're still going to need stuff like indexing and the linearizer.

##### **Geohot** [[00:11:10](https://www.youtube.com/watch?v=umHATMs0HDA&t=670)]
Those almost aren't rewrite rules. So I mean, all the rewrite rules that actually used to like change stuff.

##### **Geohot** [[00:11:20](https://www.youtube.com/watch?v=umHATMs0HDA&t=680)]
OK, OK.

##### **Geohot** [[00:11:20](https://www.youtube.com/watch?v=umHATMs0HDA&t=680)]
They're kind of gone. We've replaced it with these few deterministic like stages. So yeah, I mean, to ask the question, like what's the minimum rewrite rule? The answer is kind of like no rewrite rule. Like today, if you just do indexing and linearization,

##### **Geohot** [[00:11:37](https://www.youtube.com/watch?v=umHATMs0HDA&t=697)]
that's a program. Anyway, let's move on. Next is viz.

##### **Qazalin** [[00:11:53](https://www.youtube.com/watch?v=umHATMs0HDA&t=713)]
So I had GPT-5.5 work on the kernels in LLaMA. I posted the Weights & Biases run in there. It got it too fast. But as you see, it didn't even ever converge. So it broke it. Yes, but there's no way for me to actually give feedback to the agents that it's broken.

##### **Geohot** [[00:12:25](https://www.youtube.com/watch?v=umHATMs0HDA&t=745)]
You know why?

##### **Geohot** [[00:12:26](https://www.youtube.com/watch?v=umHATMs0HDA&t=746)]
Like what broke?

##### **Qazalin** [[00:12:29](https://www.youtube.com/watch?v=umHATMs0HDA&t=749)]
No, that's the problem, right? I think like there's two parts of this agentic loop. One part is like giving the agent tools to give itself feedback about what is changing and seeing the effects in the kernels. I think I did that last week. But now it's more about verifying that the changes are actually correct.

##### **Chenyu** [[00:12:50](https://www.youtube.com/watch?v=umHATMs0HDA&t=770)]
I mean, there are types of changes like you can just look at the change and know it's equivalent. And there are other types that when you make a change, you know the behavior is not exactly the same. And sometimes you wouldn't know if it's prone to an error. You know, like what kind of a changing are we talking here? Because it would be very weird if you are telling me the agent find different ways to compile the code, the same code, and now it behaves differently.

##### **Geohot** [[00:13:18](https://www.youtube.com/watch?v=umHATMs0HDA&t=798)]
Well, I mean, it probably just introduced a bug, right?

##### **Geohot** [[00:13:22](https://www.youtube.com/watch?v=umHATMs0HDA&t=802)]
That's exactly right.

##### **Qazalin** [[00:13:23](https://www.youtube.com/watch?v=umHATMs0HDA&t=803)]
It introduced a bug. The agent was trying to remove the kernels that were doing the copies.

##### **Chenyu** [[00:13:31](https://www.youtube.com/watch?v=umHATMs0HDA&t=811)]
Yeah, but it would also be weird that if we just remove some copies and all the behaviors are different. Because it's very hard for me to understand when you say agent did something and now it doesn't converge. And the natural question is what did it change? And how can this?

##### **Geohot** [[00:13:47](https://www.youtube.com/watch?v=umHATMs0HDA&t=827)]
Yeah.

##### **Chenyu** [[00:13:48](https://www.youtube.com/watch?v=umHATMs0HDA&t=828)]
What kind of behavior change are we talking here?

##### **Geohot** [[00:13:50](https://www.youtube.com/watch?v=umHATMs0HDA&t=830)]
Yeah, I think that the answer to this problem is not like trying to build tools for it to check that it didn't break anything. I think the answer to this problem is just to constrain its search space to the way that it can't break things. Like there's safe transformations you can make to a graph. But I think that we're already submitted for LLaMA. So I think that let's not focus on LLaMA. Let's instead focus on I think GEMM kernels.

##### **Geohot** [[00:14:24](https://www.youtube.com/watch?v=umHATMs0HDA&t=864)]
Like I want to start seeing this yield kernels that are better than the best ones in the world.

##### **Qazalin** [[00:14:36](https://www.youtube.com/watch?v=umHATMs0HDA&t=876)]
You would have to go to assembly for that, right?

##### **Geohot** [[00:14:40](https://www.youtube.com/watch?v=umHATMs0HDA&t=880)]
Well, that's fine. Yeah. I mean, are you sure we have to go to assembly? Pretty sure.

##### **Chenyu** [[00:14:53](https://www.youtube.com/watch?v=umHATMs0HDA&t=893)]
Are you sure if we go to assembly, you would generate a kernel that's the fastest? That's a different question.

##### **Qazalin** [[00:14:59](https://www.youtube.com/watch?v=umHATMs0HDA&t=899)]
I mean, I'm kind of observing.

##### **Chenyu** [[00:15:01](https://www.youtube.com/watch?v=umHATMs0HDA&t=901)]
Because I would also imagine other people try the same thing in assembly to start with.

##### **Qazalin** [[00:15:07](https://www.youtube.com/watch?v=umHATMs0HDA&t=907)]
AMD's highest performing kernels are assembly.

##### **Geohot** [[00:15:11](https://www.youtube.com/watch?v=umHATMs0HDA&t=911)]
Oh, yeah. No, I mean, you're right. Yeah, the AMD ones kind of are. Yeah, I mean, OK, then maybe instead of that, focus on the like basically cleaning up that Qwen speedup.

##### **Qazalin** [[00:15:29](https://www.youtube.com/watch?v=umHATMs0HDA&t=929)]
Exactly. I think that's what I'm going to do. Like more high-level schedule, some amount of kernel that gets a reasonable performance with C at best. Yeah. Yeah. Yeah.

##### **Geohot** [[00:15:44](https://www.youtube.com/watch?v=umHATMs0HDA&t=944)]
Yeah. And then I would sort of, yeah, have to go through that. Yeah.

##### **Chenyu** [[00:15:45](https://www.youtube.com/watch?v=umHATMs0HDA&t=945)]
And if it's not as good, at least understand, or in the tools somewhere, it will show why it's not as good. I mean, sometimes it's a trade-off that we just don't support certain ways of writing certain stuff. But it's good to know that that's all the reasons why these are different, and not others'

##### **Geohot** [[00:16:03](https://www.youtube.com/watch?v=umHATMs0HDA&t=963)]
minor stuff.

##### **Geohot** [[00:16:09](https://www.youtube.com/watch?v=umHATMs0HDA&t=969)]
I'm going to start, OK, I have a bunch of things to do. But I guess we really do got to merge assembly if we want AMD GEMMs. We have to merge our own lowering pipeline to assembly. I don't think there is much value in just having the agent mess with the assembly code.

##### **Geohot** [[00:16:33](https://www.youtube.com/watch?v=umHATMs0HDA&t=993)]
OK.

##### **Geohot** [[00:16:34](https://www.youtube.com/watch?v=umHATMs0HDA&t=994)]
Agreed. Yeah.

##### **Geohot** [[00:16:36](https://www.youtube.com/watch?v=umHATMs0HDA&t=996)]
But yeah, OK.

##### **Geohot** [[00:16:37](https://www.youtube.com/watch?v=umHATMs0HDA&t=997)]
So I think that LLaMA is probably too much. But LLM inference and asking the question, not just how much can it speed it up, but how many tokens did I spend? We want to reduce token spend. We have this like it's a velocity. It's like tokens per token per second. How many tokens do we spend to improve things by 10 tokens per second?

##### **Geohot** [[00:17:05](https://www.youtube.com/watch?v=umHATMs0HDA&t=1025)]
Do you measure that?

##### **Geohot** [[00:17:07](https://www.youtube.com/watch?v=umHATMs0HDA&t=1027)]
I have a budget of $50.

##### **Geohot** [[00:17:10](https://www.youtube.com/watch?v=umHATMs0HDA&t=1030)]
200,000 tokens?

##### **Geohot** [[00:17:12](https://www.youtube.com/watch?v=umHATMs0HDA&t=1032)]
I say I check out tinygrad master. I say speed up Qwen.

##### **Geohot** [[00:17:17](https://www.youtube.com/watch?v=umHATMs0HDA&t=1037)]
Seconds per token. I have 200,000 tokens of GPT or something.

##### **Geohot** [[00:17:25](https://www.youtube.com/watch?v=umHATMs0HDA&t=1045)]
It's a very difficult problem.

##### **Geohot** [[00:17:28](https://www.youtube.com/watch?v=umHATMs0HDA&t=1048)]
Why? It's like with KernelBench.

##### **Geohot** [[00:17:34](https://www.youtube.com/watch?v=umHATMs0HDA&t=1054)]
Have you seen KernelBench?

##### **Geohot** [[00:17:37](https://www.youtube.com/watch?v=umHATMs0HDA&t=1057)]
Oh, which one? They are just . I don't know.

##### **Geohot** [[00:17:42](https://www.youtube.com/watch?v=umHATMs0HDA&t=1062)]
KernelBench is like.

##### **Geohot** [[00:17:49](https://www.youtube.com/watch?v=umHATMs0HDA&t=1069)]
OK, maybe. I don't know. I feel that's too difficult to optimize for.

##### **Geohot** [[00:17:58](https://www.youtube.com/watch?v=umHATMs0HDA&t=1078)]
We already did it. Did you hear the one that gets like 200-something tokens per second on Mac? Yeah, that's fine.

##### **Geohot** [[00:18:09](https://www.youtube.com/watch?v=umHATMs0HDA&t=1089)]
Yeah.

##### **Chenyu** [[00:18:10](https://www.youtube.com/watch?v=umHATMs0HDA&t=1090)]
I mean, having a budget and trying to optimize per that budget, I feel is so difficult.

##### **Geohot** [[00:18:16](https://www.youtube.com/watch?v=umHATMs0HDA&t=1096)]
Why? I mean, everyone always has a budget. It's just a question of what it is. OK, I don't know too much about this.

##### **Geohot** [[00:18:26](https://www.youtube.com/watch?v=umHATMs0HDA&t=1106)]
But yeah, I mean, does this seem like a reasonable direction to go? I agree that we have to wait, that GEMMs are blocked on assembly.

##### **Geohot** [[00:18:34](https://www.youtube.com/watch?v=umHATMs0HDA&t=1114)]
I think it's reasonable, yeah.

##### **Geohot** [[00:18:37](https://www.youtube.com/watch?v=umHATMs0HDA&t=1117)]
Cool.

##### **Geohot** [[00:18:39](https://www.youtube.com/watch?v=umHATMs0HDA&t=1119)]
Yeah, I want to get the Kimi stuff merged too, because I'd really like, speeding up Kimi has value.

##### **Qazalin** [[00:18:47](https://www.youtube.com/watch?v=umHATMs0HDA&t=1127)]
Oh, yes, Kimi is unusable in the MI300s, MI200s.

##### **Geohot** [[00:18:52](https://www.youtube.com/watch?v=umHATMs0HDA&t=1132)]
You think you can deal with getting that merged?

##### **Geohot** [[00:18:56](https://www.youtube.com/watch?v=umHATMs0HDA&t=1136)]
Mm-hmm. Yeah.

##### **Geohot** [[00:18:59](https://www.youtube.com/watch?v=umHATMs0HDA&t=1139)]
Yeah. Yeah, Kimi, I mean, because like, speeding up Qwen is like fun, but like nobody uses Qwens. If you could speed up Kimi, that's actually usable.

##### **Geohot** [[00:19:07](https://www.youtube.com/watch?v=umHATMs0HDA&t=1147)]
Mm-hmm.

##### **Geohot** [[00:19:09](https://www.youtube.com/watch?v=umHATMs0HDA&t=1149)]
Yeah. So let's get Kimi merged. Let's speed that up. And then we get the real fun of having the thing speed itself

##### **Geohot** [[00:19:17](https://www.youtube.com/watch?v=umHATMs0HDA&t=1157)]
up.

##### **Geohot** [[00:19:22](https://www.youtube.com/watch?v=umHATMs0HDA&t=1162)]
Like using GPT-5.5 is great, but we don't own GPT-5.5.

##### **Geohot** [[00:19:30](https://www.youtube.com/watch?v=umHATMs0HDA&t=1170)]
tinygrad can't speed itself up with GPT-5.5.

##### **Geohot** [[00:19:37](https://www.youtube.com/watch?v=umHATMs0HDA&t=1177)]
Did you fix the bank conflicts in copy matmul?

##### **Qazalin** [[00:19:43](https://www.youtube.com/watch?v=umHATMs0HDA&t=1183)]
There's a branch for it. It's fixed, and it's a little faster. Like 80 teraflops to 90 teraflops. Cool.

##### **Geohot** [[00:19:51](https://www.youtube.com/watch?v=umHATMs0HDA&t=1191)]
Any reason not to merge it?

##### **Qazalin** [[00:19:54](https://www.youtube.com/watch?v=umHATMs0HDA&t=1194)]
I'm still looking at it, because you don't always want to have zero bank conflicts. And there's this tuning that you have to do. I almost think I would let the LLM autotune. Mm-hmm. Because what can happen if you optimize too much for the bank conflicts, you'll end up having gathered LDS accesses, and you'll have more transactions for memory for the same amount.

##### **Geohot** [[00:20:26](https://www.youtube.com/watch?v=umHATMs0HDA&t=1226)]
Want to get that too?

##### **Qazalin** [[00:20:29](https://www.youtube.com/watch?v=umHATMs0HDA&t=1229)]
Oh, we can. It can do that. It just looks at the PMC counters and figures it out very fast.

##### **Geohot** [[00:20:35](https://www.youtube.com/watch?v=umHATMs0HDA&t=1235)]
Yeah, I mean, let's do that. Forgetting about ASM. You're right. We're not going to get state-of-the-art kernels, but we can still improve AMD copy matmul a lot.

##### **Qazalin** [[00:20:48](https://www.youtube.com/watch?v=umHATMs0HDA&t=1248)]
That's good. I was thinking it's an argument to the AMD copy matmul that just adjusts itself based on the shape of the GEMM and what your budget is.

##### **Geohot** [[00:21:00](https://www.youtube.com/watch?v=umHATMs0HDA&t=1260)]
No, I mean, I would just write one thing that's good. I wouldn't worry about making it too generic. But yeah, I mean, I see this fix for the bank conflict. I think it looks pretty good.

##### **Geohot** [[00:21:13](https://www.youtube.com/watch?v=umHATMs0HDA&t=1273)]
Mm-hmm. LDS.

##### **Geohot** [[00:21:23](https://www.youtube.com/watch?v=umHATMs0HDA&t=1283)]
Oh, god, I can't read this. How much space are we wasting? What's the percent overhead?

##### **Qazalin** [[00:21:31](https://www.youtube.com/watch?v=umHATMs0HDA&t=1291)]
Percent overhead for this one? Oh, this one's very tiny, because you see it's faster. It's faster. Like when I tried to over-optimize with higher block sizes, it actually got slower to have less bank conflicts. But this one got it to zero and it's faster. This took like five minutes with GPT-5.5. I was kind of shocked. It's so fast. Yeah. Cool.

##### **Geohot** [[00:21:59](https://www.youtube.com/watch?v=umHATMs0HDA&t=1319)]
Yeah. Oh, yeah. Let's get Kimi merged, and let's start speeding up Kimi.

##### **Qazalin** [[00:22:04](https://www.youtube.com/watch?v=umHATMs0HDA&t=1324)]
Yeah. I think that's more reasonable than any assembly, I believe, near term. Right? Yeah.

##### **Geohot** [[00:22:14](https://www.youtube.com/watch?v=umHATMs0HDA&t=1334)]
Yeah, no. And then when we get to MLPerf, we'll talk about 45B. But OK.

##### **Geohot** [[00:22:19](https://www.youtube.com/watch?v=umHATMs0HDA&t=1339)]
Can we also put this on benchmarks?

##### **Geohot** [[00:22:23](https://www.youtube.com/watch?v=umHATMs0HDA&t=1343)]
So whatever.

##### **Geohot** [[00:22:25](https://www.youtube.com/watch?v=umHATMs0HDA&t=1345)]
Oh, yeah, yeah. Can you add? Yeah, can you add copy matmul?

##### **Geohot** [[00:22:29](https://www.youtube.com/watch?v=umHATMs0HDA&t=1349)]
We have a benchmark, right?

##### **Geohot** [[00:22:36](https://www.youtube.com/watch?v=umHATMs0HDA&t=1356)]
Yeah.

##### **Chenyu** [[00:22:39](https://www.youtube.com/watch?v=umHATMs0HDA&t=1359)]
We probably want to remove some of the very old LLaMA. Agreed. Agreed.

##### **Geohot** [[00:22:44](https://www.youtube.com/watch?v=umHATMs0HDA&t=1364)]
Why is TinyRed, are none of the Reds taking jobs?

##### **Chenyu** [[00:22:49](https://www.youtube.com/watch?v=umHATMs0HDA&t=1369)]
One is running MLPerf.

##### **Wozeparrot** [[00:22:51](https://www.youtube.com/watch?v=umHATMs0HDA&t=1371)]
I think the other one just need tokens again.

##### **Geohot** [[00:22:57](https://www.youtube.com/watch?v=umHATMs0HDA&t=1377)]
They're the ones that need tokens?

##### **Geohot** [[00:22:58](https://www.youtube.com/watch?v=umHATMs0HDA&t=1378)]
Oh, GitHub tokens? Yeah.

##### **Geohot** [[00:23:01](https://www.youtube.com/watch?v=umHATMs0HDA&t=1381)]
Why did they lose their GitHub tokens? Where'd they go?

##### **Geohot** [[00:23:08](https://www.youtube.com/watch?v=umHATMs0HDA&t=1388)]
Let's fix this after the meeting?

##### **Geohot** [[00:23:09](https://www.youtube.com/watch?v=umHATMs0HDA&t=1389)]
Yeah, we'll fix that in a minute. OK.

##### **Geohot** [[00:23:14](https://www.youtube.com/watch?v=umHATMs0HDA&t=1394)]
Next. Next, that's your stuff.

##### **Geohot** [[00:23:21](https://www.youtube.com/watch?v=umHATMs0HDA&t=1401)]
I don't know what that is.

##### **Geohot** [[00:23:23](https://www.youtube.com/watch?v=umHATMs0HDA&t=1403)]
Yeah, I don't know what that is. OK.

##### **Geohot** [[00:23:26](https://www.youtube.com/watch?v=umHATMs0HDA&t=1406)]
Yeah, so OK. You want to remove dtype.vec, right? So the first thing you realize about removing dtype.vec is that it's pretty clean, except for in one place. There's one place where we use dtype.vec to mean something different, and that's in the indexes for images. So we use dtype.vec to represent the XY pair in the index for images. So you're like, OK, first I need to remove that. But then you realize that you can't really remove that, because the index in CodeGen is semantically different from the earlier index. You can't do 2D indexing. OK. So you can't do 2D indexing in the indexing in CodeGen, because there can be an optional gate added to the end of it. So then you ask, well, there really shouldn't be a gate on index ever. You want the gate to be on the load and the store. So I moved the gate to the load and the store, painfully. But that's done. Because there really shouldn't even be a load and a store. There should just be a store. A store is the only operation that has side effects. So it makes sense that you just gate a store. Nothing else in tinygrad has any side effects. So yeah. We now have gates on load and store. Then I start to work on removing actually. So you can do the indexing on images as a 2D index. The image should just have the shape of the image, even probably including the 4. And then it's really a 3D index. It's the x, the y, and then the range from 0 to 3. Or like a VCONST from 0 to 3, which says that it's expanded. So yeah. That is where the image index should go. Then you start to try to do this. And lots of weird things just break. And you realize that there's not really a clear separation right now between instruction selection and generic rewrite transformations. So we have two that are basically generic rewrite transformations. There is the dtype decomposition. So the dtype decomposition is generic. The dtype decomposition is not anything to do with instruction selection. You can actually do that in the beginning. And then there's not just the dtype decomposition. There's also the lowering from the weakints. And the lowering from the weakints is awful. It's so much wrong.

##### **Geohot** [[00:26:02](https://www.youtube.com/watch?v=umHATMs0HDA&t=1562)]
It's terrible.

##### **Geohot** [[00:26:04](https://www.youtube.com/watch?v=umHATMs0HDA&t=1564)]
Yeah. So I want that to be gone. And then, yeah. But then you realize that you don't just want to get rid of the lowering from the weakints. You actually want the entire, the same way that we should make broadcasting implicit, we should make dtype promotion implicit.

##### **Geohot** [[00:26:22](https://www.youtube.com/watch?v=umHATMs0HDA&t=1582)]
And I'm curious what your opinion is on that. Like if I do an int plus a long, should that be allowed?

##### **Geohot** [[00:26:29](https://www.youtube.com/watch?v=umHATMs0HDA&t=1589)]
Or do I need the explicit cast?

##### **Geohot** [[00:26:33](https://www.youtube.com/watch?v=umHATMs0HDA&t=1593)]
I think it's fine.

##### **Geohot** [[00:26:35](https://www.youtube.com/watch?v=umHATMs0HDA&t=1595)]
Just do implicit promotion.

##### **Chenyu** [[00:26:38](https://www.youtube.com/watch?v=umHATMs0HDA&t=1598)]
This is the similar reason to the shape.

##### **Geohot** [[00:26:42](https://www.youtube.com/watch?v=umHATMs0HDA&t=1602)]
It's broadcasting. Yeah. So we want to basically move like dtype promotion and broadcasting into ops and not have to make them explicit because this makes a whole lot of things a lot simpler. Like you're not in these like bad intermediate states, which is what so much of that weakint promoter is.

##### **Qazalin** [[00:27:03](https://www.youtube.com/watch?v=umHATMs0HDA&t=1623)]
Yeah.

##### **Geohot** [[00:27:03](https://www.youtube.com/watch?v=umHATMs0HDA&t=1623)]
It does. Like 90% of it can be deleted once you have this. Yeah. You just need to occasionally look and be like, oh, I see. OK. Well, this one is going to overflow. So let me just add some casts, right? Because those have to be explicit casts. So then I just get into all of this. And I just get frustrated because all tests will pass. And I realize that most of the reason these tests start to fail is because we don't have a very clear separation between the middle optimization chunk and instruction selection. So then I started working on making that explicit. And I'm working on a rewrite of spec. So the diagram for tinygrad to always think about is like, it's like an hourglass with a thick rectangular middle. So we have all of these massive things on the front end of the hourglass, things like convolutions, things like matmuls, things like every ONNX op. And then that all gets funneled down into UOps. And then we have all these transformations on UOps that just do UOp to UOp transformations. And then at the end, we have the things that actually say, OK, you know, you can use things like sub. You can use things like you have to do your, even the expander of like something like x. The expander of something like x actually is still completely in UOp language. So that's a transformation that can go anywhere. Same as the dtype ones, right? These are not instruction selection things. And they need to be treated as such. They need to be treated as part of optimization, not as part of instruction selection. Then we do get to things that are instruction selection, like even maybe adding load. Load is kind of like it's an instruction. It's not like the dtype transformation. The dtype transformation, I could do in Tensor. I can't add load in Tensor. So that becomes the delineation marker. I played around with Lean for a bit to be like, oh, can I write the UOps in Lean and prove things about them? But this turns out to be useless. It doesn't help you. The problem isn't that we need to prove things about UOps. The problem is that we just need to be more careful about where we introduce certain UOps and remove certain UOps.

##### **Chenyu** [[00:29:32](https://www.youtube.com/watch?v=umHATMs0HDA&t=1772)]
So, yeah, that's how I end up. And don't, you know, don't just add stuff to a shapetracker and say it will be all fine. It's impossible to remove load.

##### **Geohot** [[00:29:43](https://www.youtube.com/watch?v=umHATMs0HDA&t=1783)]
No, I know. I know. No, no, no. I'm doing it. I'm doing it manually, very slowly, adding one rule at a time. And then like when I add a rule that's bad, I write a comment about how it needs to be removed. And I just think that it's going to be a long grind, but we have to go through and remove. I mean, now I merged the spec into tinygrad. Now we actually have spec. So like we have like a basic reference for like where things should go. And then, yeah, there's a bunch of implementation details that are crap. But like, they're going to go away. So, yeah, you know, you start out with like, oh, remove dtype.vec. But then you realize that it's not removed. Like, sure, could I force it through and remove dtype.vec? I could. But I'm not sure what that would do. But yeah, dtype.vec will eventually be removed. And then we're left with a much tighter description of the whole language. And that's another like escape hatch that we don't need. In fact, dtype in general is a whole escape hatch we don't need. dtype should not live on UOps.

##### **Geohot** [[00:30:43](https://www.youtube.com/watch?v=umHATMs0HDA&t=1843)]
dtype should be implicit.

##### **Geohot** [[00:30:48](https://www.youtube.com/watch?v=umHATMs0HDA&t=1848)]
The only UOps that should change dtypes are like buffer views, consts, and casts.

##### **Geohot** [[00:30:55](https://www.youtube.com/watch?v=umHATMs0HDA&t=1855)]
There are source UOps. There are source UOps that initialize a dtype. And then there's cast.

##### **Chrism** [[00:31:00](https://www.youtube.com/watch?v=umHATMs0HDA&t=1860)]
What if you have one of these things like an expanding multiply? Where you have like two int32s and you multiply them together and you get int64 out?

##### **Geohot** [[00:31:08](https://www.youtube.com/watch?v=umHATMs0HDA&t=1868)]
I think that that's not what we do.

##### **Chrism** [[00:31:11](https://www.youtube.com/watch?v=umHATMs0HDA&t=1871)]
Yeah, we don't. But this is something that hardware can do, right?

##### **Geohot** [[00:31:15](https://www.youtube.com/watch?v=umHATMs0HDA&t=1875)]
Yeah, then I would just put that as cast to int64 before the multiply.

##### **Chrism** [[00:31:19](https://www.youtube.com/watch?v=umHATMs0HDA&t=1879)]
Before the multiply.

##### **Geohot** [[00:31:20](https://www.youtube.com/watch?v=umHATMs0HDA&t=1880)]
I'll put it before, right?

##### **Chenyu** [[00:31:21](https://www.youtube.com/watch?v=umHATMs0HDA&t=1881)]
Yeah, yeah. Basically, there's only a very small set of UOps that tells you what the dtype should be. The ones that initiate some kind of buffer or buffer-like. I don't know our name for that now. And explicitly cast into something else. And everything else can be inferred.

##### **Geohot** [[00:31:48](https://www.youtube.com/watch?v=umHATMs0HDA&t=1908)]
Yeah, yeah. No, there's some that will like. But then we can also always do that. We can always do this like once you get down to the instruction level. Once you're down to the instruction level, instructions can override dtypes and stuff. But the dtype override becomes explicit and not required on each thing. Like this UOp changes the dtype. It's just a different way of writing. Like all these production rules basically become recursive properties. I want to add one more recursive property too. I want to add address space as a recursive property. We have kept that. That's been on the dtype as well. Like we have this dtype pointer which can tell you what address space it's in. And why is that in the dtype? Yeah, why is that in the dtype? Why is that in the dtype?

##### **Chenyu** [[00:32:35](https://www.youtube.com/watch?v=umHATMs0HDA&t=1955)]
I don't know. There is enough weird code that says, "oh, UOps do things differently if it's a pointer."

##### **Qazalin** [[00:32:46](https://www.youtube.com/watch?v=umHATMs0HDA&t=1966)]
OK.

##### **Chenyu** [[00:32:46](https://www.youtube.com/watch?v=umHATMs0HDA&t=1966)]
A pointer needs to be. OK, great. I think we are on a good direction. Yes. And we can move on to your stuff.

##### **Chrism** [[00:32:54](https://www.youtube.com/watch?v=umHATMs0HDA&t=1974)]
Yeah. Yeah. So the big thing I did this week was making AM and NV less dependent on the internet. So right now, assuming you have the right files in `/lib/firmware`, if you run with AM, you won't download anything. The one remaining thing is PMC. So if you run with `PMC=1`, then you still download stuff. And so we can autogen that as well. It's a YAML file, not a header. It's a little annoying. But I mean, depending on PyYAML at autogen time seems like probably fine. Or we can do it with regex. That's what we do now.

##### **Geohot** [[00:33:33](https://www.youtube.com/watch?v=umHATMs0HDA&t=2013)]
At autogen time is fine. If you're including it, yeah. The requirements to re-autogen everything can include PyYAML and Clang and like, you know, these like kind of tier one requirements that are like, that's not weird. Like.

##### **Qazalin** [[00:33:49](https://www.youtube.com/watch?v=umHATMs0HDA&t=2029)]
Yeah.

##### **Chrism** [[00:33:49](https://www.youtube.com/watch?v=umHATMs0HDA&t=2029)]
Probably better than having the regex thing that we have right now.

##### **Geohot** [[00:33:52](https://www.youtube.com/watch?v=umHATMs0HDA&t=2032)]
Oh, yeah, yeah.

##### **Chrism** [[00:33:54](https://www.youtube.com/watch?v=umHATMs0HDA&t=2034)]
And I did some similar work for NV. So we look at `/lib/firmware` as well now as opposed to downloading the like NVIDIA files from open-gpu-kernel-modules. I was also looking at getting other register definitions as well, which are nice and organized compared to AMD's. So it should be a lot easier. Yeah. NVIDIA's. Yeah. To autogen those.

##### **Chenyu** [[00:34:21](https://www.youtube.com/watch?v=umHATMs0HDA&t=2061)]
So in terms of downloading stuff, is Comma happy now?

##### **Chrism** [[00:34:26](https://www.youtube.com/watch?v=umHATMs0HDA&t=2066)]
From what I understand, yeah. They need to ship a new AGNOS with the `/lib/firmware` stuff. But.

##### **Chenyu** [[00:34:33](https://www.youtube.com/watch?v=umHATMs0HDA&t=2073)]
But they are going to do that. They are happy with it.

##### **Chrism** [[00:34:35](https://www.youtube.com/watch?v=umHATMs0HDA&t=2075)]
Yes. From what I understand, the next AGNOS release will have this and everything should work.

##### **Geohot** [[00:34:40](https://www.youtube.com/watch?v=umHATMs0HDA&t=2080)]
Yeah. We're not going to start including AMD firmware blah blah. Yeah.

##### **Chenyu** [[00:34:43](https://www.youtube.com/watch?v=umHATMs0HDA&t=2083)]
Because that was part of the motivation to do this. Yes. Yeah. Yeah. No.

##### **Chrism** [[00:34:50](https://www.youtube.com/watch?v=umHATMs0HDA&t=2090)]
I mean, I'll bump their, I'll bump tinygrad in openpilot again today. And the past, I did that last week and the week before, and there weren't any issues. So doing that. Yeah. So trying to clean up tests. We had that on the board with the goals for the timings for each test. But.

##### **Geohot** [[00:35:14](https://www.youtube.com/watch?v=umHATMs0HDA&t=2114)]
Sorry. Yeah.

##### **Chrism** [[00:35:16](https://www.youtube.com/watch?v=umHATMs0HDA&t=2116)]
That's right. Anyway. In general, it definitely needs to be faster. And yeah. I mean, on my Mac right now, it's a little bit slow. And also definitely in CI, it takes like, you know, almost 15 minutes. GitHub is just broken.

##### **Chenyu** [[00:35:32](https://www.youtube.com/watch?v=umHATMs0HDA&t=2132)]
Every time when we have a random crash, I'm like 85% sure it's just GitHub being broken.

##### **Geohot** [[00:35:38](https://www.youtube.com/watch?v=umHATMs0HDA&t=2138)]
Yeah. No. No way. Okay. So.

##### **Chenyu** [[00:35:41](https://www.youtube.com/watch?v=umHATMs0HDA&t=2141)]
It never breaks on my machine. Yes. It never breaks on our machine, only CI.

##### **Geohot** [[00:35:47](https://www.youtube.com/watch?v=umHATMs0HDA&t=2147)]
Two basic types of crashes that we see in GitHub. There's the type where the GitHub internet sucks. And that's actually just like the GitHub internet sucks.

##### **Chenyu** [[00:35:56](https://www.youtube.com/watch?v=umHATMs0HDA&t=2156)]
The GitHub machine sucks.

##### **Geohot** [[00:35:58](https://www.youtube.com/watch?v=umHATMs0HDA&t=2158)]
The ones where like one of the LLVM tasks will crash. This is not GitHub.

##### **Chenyu** [[00:36:04](https://www.youtube.com/watch?v=umHATMs0HDA&t=2164)]
So. My other hypothesis is we just at some point used too much RAM.

##### **Geohot** [[00:36:11](https://www.youtube.com/watch?v=umHATMs0HDA&t=2171)]
That's I think more like.

##### **Chenyu** [[00:36:12](https://www.youtube.com/watch?v=umHATMs0HDA&t=2172)]
But. Yeah. You shouldn't crash. And the fact that you crash is like this virtual machine setup sucks. No.

##### **Geohot** [[00:36:20](https://www.youtube.com/watch?v=umHATMs0HDA&t=2180)]
I mean, I think that it's very possible that malloc is returning zero. Like malloc can return zero. People don't like remember this, but it can.

##### **Chrism** [[00:36:29](https://www.youtube.com/watch?v=umHATMs0HDA&t=2189)]
Well, we can check, right? You can check to see if. What is it called? Like the setting in Linux that says malloc never returns zero. Yeah.

##### **Geohot** [[00:36:41](https://www.youtube.com/watch?v=umHATMs0HDA&t=2201)]
I think we should look into this. Right. I, I, my, my guess, my top guess for those random GitHub crashes is out of memory.

##### **Chenyu** [[00:36:49](https://www.youtube.com/watch?v=umHATMs0HDA&t=2209)]
I think it is because I check lists. I check how many things we use per test and trying to put the heavy ones together and see if it triggers crash more likely.

##### **Geohot** [[00:37:00](https://www.youtube.com/watch?v=umHATMs0HDA&t=2220)]
But I mean, that's like the main difference between your local machine and our CI machines. Our CI machines have gigabytes and gigabytes of memory. And that's. I don't have any.

##### **Chenyu** [[00:37:10](https://www.youtube.com/watch?v=umHATMs0HDA&t=2230)]
But yeah. So you can. If you are interested. A few tests, especially the ones that test with real GGUF thingy, they use a lot of memory because we keep the decoded model somewhere. The actual model is referenced that we compare. You can instrument these tests and like print how many nbytes you use. I think it's very close to some limits and that might be why it's flaky and sometimes it crashed. But just because our CI and local split.

##### **Geohot** [[00:37:41](https://www.youtube.com/watch?v=umHATMs0HDA&t=2261)]
We should also like, like use faulthandler or something like when it crashes, we should be able to, it shouldn't just say segmentation fault.

##### **Chenyu** [[00:37:47](https://www.youtube.com/watch?v=umHATMs0HDA&t=2267)]
We can say why. No, I think let's pick. I don't know. Sometimes maybe it's just timeout and our timeouts, the timeout we set is not very useful. Yes. I think now if we timeout, it just crashed. Yeah. We should set up timeout in pytest probably. Yeah. I think that's part of the improving test in general. Yeah. We should just look into like the memory usage and the timeout crash.

##### **Geohot** [[00:38:12](https://www.youtube.com/watch?v=umHATMs0HDA&t=2292)]
But I'll say this about the GitHub runners. This is worth fixing. These are not like, like sometimes being put in an adversarial environment is just stupid. But I generally think the GitHub adversarial environment is kind of good. It's like kind of good. Like it forces you to think about these edge cases that you wouldn't otherwise think about. It's not that the computers are broken and randomly executed instruction wrong.

##### **Chenyu** [[00:38:37](https://www.youtube.com/watch?v=umHATMs0HDA&t=2317)]
Well, I think it's more. Sometimes you're just randomly being put on the crap machine that crashes more often.

##### **Geohot** [[00:38:44](https://www.youtube.com/watch?v=umHATMs0HDA&t=2324)]
I think you're put on the crap machine that has less gigs of RAM.

##### **Chenyu** [[00:38:48](https://www.youtube.com/watch?v=umHATMs0HDA&t=2328)]
That's not true. Right. These are hosted runners and they should set a boundary like fine. And that if you are within the allowed limit, it shouldn't crash.

##### **Geohot** [[00:38:57](https://www.youtube.com/watch?v=umHATMs0HDA&t=2337)]
Yeah.

##### **Chenyu** [[00:38:57](https://www.youtube.com/watch?v=umHATMs0HDA&t=2337)]
I'm pretty sure we are within the allowed limit.

##### **Geohot** [[00:39:00](https://www.youtube.com/watch?v=umHATMs0HDA&t=2340)]
I don't think we are. I think that what happens is like there are so many different race conditions that can expose to. Like when you run it on your machine, you're not going to crash. You're not going to hit race conditions because your machine is. Yeah, it's a great machine. You're the only one on it, right? No, I load test that. No, but even if you load test it, right? Like the GitHub.

##### **Chenyu** [[00:39:19](https://www.youtube.com/watch?v=umHATMs0HDA&t=2359)]
Yeah, that's what I mean by if you don't do the virtualization fine and it does weird stuff, then maybe no, right? Anyway, we can improve all those. We all want tests to be more reliable and faster. So let's go that direction and we can move on next to a buffer refactor.

##### **Nimlgen** [[00:39:42](https://www.youtube.com/watch?v=umHATMs0HDA&t=2382)]
So I've been working on HCQ2 this week. So I merged some runtime and HCQ implementation to extra for now. So it's possible to run this on AMD with `HCQ2=1`. So, yeah, it lowers down to the HCQ command buffers. And then it just builds the C launcher with these patches. Yeah. So I think this week I'll work on the new graph and disks.

##### **Geohot** [[00:40:31](https://www.youtube.com/watch?v=umHATMs0HDA&t=2431)]
Look at HCQ2 now. I mean, it still has a lot of these classes.

##### **Nimlgen** [[00:40:37](https://www.youtube.com/watch?v=umHATMs0HDA&t=2437)]
Need these classes?

##### **Geohot** [[00:40:41](https://www.youtube.com/watch?v=umHATMs0HDA&t=2441)]
Um.

##### **Nimlgen** [[00:40:44](https://www.youtube.com/watch?v=umHATMs0HDA&t=2444)]
No, I mean, it actually doesn't need this. I mean, but for the program, it's actually implem... I mean, like to make this work with beam with. Yeah, but actually, that's like also should be refactored.

##### **Geohot** [[00:41:00](https://www.youtube.com/watch?v=umHATMs0HDA&t=2460)]
I think we got it. Yeah, I think that it's worth like before you do the migration of all of these things to HCQ2. I think it's worth doing those refactors. Like the basic ideas here are correct. Okay. You're gonna, you're gonna like lower the command buffers. You're gonna, you're gonna resolve the actual like the refs. But yeah, I want those classes like gone.

##### **Geohot** [[00:41:35](https://www.youtube.com/watch?v=umHATMs0HDA&t=2495)]
Have HCQCompiled. We shouldn't have HCQProgram. We should all be... Yeah. So HCQProgram...

##### **Geohot** [[00:41:48](https://www.youtube.com/watch?v=umHATMs0HDA&t=2508)]
Yeah. It should be gone.

##### **Geohot** [[00:41:51](https://www.youtube.com/watch?v=umHATMs0HDA&t=2511)]
Yeah.

##### **Geohot** [[00:41:52](https://www.youtube.com/watch?v=umHATMs0HDA&t=2512)]
Um. The only difference like in. Yeah. The order. Yeah. I would implement this. Um.

##### **Geohot** [[00:42:08](https://www.youtube.com/watch?v=umHATMs0HDA&t=2528)]
Let's see.

##### **Geohot** [[00:42:09](https://www.youtube.com/watch?v=umHATMs0HDA&t=2529)]
Let's see this. Okay. And then ops_amd2 is like doing like a, is your AMD inner PM4 basically like the running of the.

##### **Nimlgen** [[00:42:20](https://www.youtube.com/watch?v=umHATMs0HDA&t=2540)]
Yeah. I mean. It's reasonable. It's not in the best shape like ops_amd2. But. Yeah. It basically has some of the pattern matching to run.

##### **Geohot** [[00:42:33](https://www.youtube.com/watch?v=umHATMs0HDA&t=2553)]
I mean, I like that that that pattern reminds me of what you have in in realize now. I think that pattern is basically correct. Yeah.

##### **Nimlgen** [[00:42:41](https://www.youtube.com/watch?v=umHATMs0HDA&t=2561)]
So basically. Yeah. So actually the idea and not this PR but before that I had. So actually this HCQ was implemented like in the, it was like the extension of the realize. So, and I didn't use this HCQProgram class. But yeah, basically it was kind of hard to glue this with beam and with other things and timings. But yeah, I'll, I'll do that.

##### **Geohot** [[00:43:20](https://www.youtube.com/watch?v=umHATMs0HDA&t=2600)]
I mean, we want to, we're eventually going to get to a point. I think after the refactor, we're just going to want to increase our per second we can run. Once we have a good, a good separation of like how to patch a program and turn it into a time, it should kind of be like that's a rewrite rule, right?

##### **Geohot** [[00:43:48](https://www.youtube.com/watch?v=umHATMs0HDA&t=2628)]
Literally rewrite the program to a float.

##### **Geohot** [[00:43:55](https://www.youtube.com/watch?v=umHATMs0HDA&t=2635)]
Yeah.

##### **Geohot** [[00:43:55](https://www.youtube.com/watch?v=umHATMs0HDA&t=2635)]
I mean.

##### **Geohot** [[00:43:57](https://www.youtube.com/watch?v=umHATMs0HDA&t=2637)]
Like. That might be too cute for now. But kind of like the basic thing that I imagine for beam is that you generate like all these graphs, compile them all, and then there's some step that lowers the program to a float, adds in the float. Probably doesn't lower it, but it just says like, you know, here's your, here's your canonical.

##### **Geohot** [[00:44:25](https://www.youtube.com/watch?v=umHATMs0HDA&t=2665)]
Timing. Like, yeah, like as a rewrite rule, right?

##### **Geohot** [[00:44:34](https://www.youtube.com/watch?v=umHATMs0HDA&t=2674)]
Imagine or imagine it just being in ProgramSpec, right? Like imagine just adding to ProgramSpec the program timings.

##### **Geohot** [[00:44:45](https://www.youtube.com/watch?v=umHATMs0HDA&t=2685)]
Yeah.

##### **Geohot** [[00:44:46](https://www.youtube.com/watch?v=umHATMs0HDA&t=2686)]
Like an idea to kind of talk about like how, right, because like you already added like beam to ProgramSpec and I think that's the right place for it. But like imagine also adding like the return value of beam to ProgramSpec. Just like, yeah, I ran it six times and here are the timings.

##### **Geohot** [[00:45:05](https://www.youtube.com/watch?v=umHATMs0HDA&t=2705)]
Yeah. Yeah.

##### **Nimlgen** [[00:45:07](https://www.youtube.com/watch?v=umHATMs0HDA&t=2707)]
I actually thought of something like that. I thought that like run_realize could return timings and just use it inside beam.

##### **Geohot** [[00:45:22](https://www.youtube.com/watch?v=umHATMs0HDA&t=2722)]
Instead of the function even like returning the timings. I guess. Like it still returns a UOp. It's just like a rewritten UOp with the timings attached to it.

##### **Geohot** [[00:45:35](https://www.youtube.com/watch?v=umHATMs0HDA&t=2735)]
Yeah. Yeah. Okay. Yeah. Cool.

##### **Geohot** [[00:45:41](https://www.youtube.com/watch?v=umHATMs0HDA&t=2741)]
Yeah. Just to, you know, to keep in mind like what the North Star of all this stuff is too, is we want to get to the point where like the GPU driver is on a GPU, so that one GPU can bring up another GPU.

##### **Qazalin** [[00:46:01](https://www.youtube.com/watch?v=umHATMs0HDA&t=2761)]
Yeah.

##### **Geohot** [[00:46:02](https://www.youtube.com/watch?v=umHATMs0HDA&t=2762)]
Yeah. Yeah.

##### **Nimlgen** [[00:46:05](https://www.youtube.com/watch?v=umHATMs0HDA&t=2765)]
I think it's already kind of possible. You just need to change CPU to AMD. It will render launcher for the AMD backend as a kernel.

##### **Geohot** [[00:46:18](https://www.youtube.com/watch?v=umHATMs0HDA&t=2778)]
You think that's possible in the HCQ2 stuff right now?

##### **Nimlgen** [[00:46:22](https://www.youtube.com/watch?v=umHATMs0HDA&t=2782)]
Yeah. Yeah. Yeah. I mean, it definitely works. It works for Python. So you can kind of switch with these backends.

##### **Geohot** [[00:46:34](https://www.youtube.com/watch?v=umHATMs0HDA&t=2794)]
Cool. Yeah. Good progress.

##### **Geohot** [[00:46:43](https://www.youtube.com/watch?v=umHATMs0HDA&t=2803)]
We are submitted for MLPerf.

##### **Chenyu** [[00:46:50](https://www.youtube.com/watch?v=umHATMs0HDA&t=2810)]
Just like three hours and seven minutes.

##### **Wozeparrot** [[00:46:53](https://www.youtube.com/watch?v=umHATMs0HDA&t=2813)]
Three hours. Four minutes.

##### **Chenyu** [[00:46:56](https://www.youtube.com/watch?v=umHATMs0HDA&t=2816)]
Seven minutes. Yeah.

##### **Wozeparrot** [[00:46:57](https://www.youtube.com/watch?v=umHATMs0HDA&t=2817)]
Seven minutes. Right.

##### **Qazalin** [[00:46:59](https://www.youtube.com/watch?v=umHATMs0HDA&t=2819)]
Yeah.

##### **Geohot** [[00:47:00](https://www.youtube.com/watch?v=umHATMs0HDA&t=2820)]
So we're 33% worse than AMD.

##### **Qazalin** [[00:47:06](https://www.youtube.com/watch?v=umHATMs0HDA&t=2826)]
Yep.

##### **Chenyu** [[00:47:07](https://www.youtube.com/watch?v=umHATMs0HDA&t=2827)]
I didn't check your branch. The one you put in the submission form is just pretty much master. It was just master. Everything is in master.

##### **Geohot** [[00:47:20](https://www.youtube.com/watch?v=umHATMs0HDA&t=2840)]
Oh, yeah.

##### **Qazalin** [[00:47:22](https://www.youtube.com/watch?v=umHATMs0HDA&t=2842)]
Yeah. Yeah. Yeah.

##### **Geohot** [[00:47:24](https://www.youtube.com/watch?v=umHATMs0HDA&t=2844)]
You just add something on the.

##### **Geohot** [[00:47:31](https://www.youtube.com/watch?v=umHATMs0HDA&t=2851)]
I'm not sure if the branch you added is also uploaded to GitHub.

##### **Chenyu** [[00:47:40](https://www.youtube.com/watch?v=umHATMs0HDA&t=2860)]
Previously, every time after I submit, I will push the branch there. So in case people want to check it just from the GitHub, they can see it.

##### **Wozeparrot** [[00:47:50](https://www.youtube.com/watch?v=umHATMs0HDA&t=2870)]
Yeah, I can do that.

##### **Chenyu** [[00:47:53](https://www.youtube.com/watch?v=umHATMs0HDA&t=2873)]
All right. So I think that's, we doubt anyone reviewing our thing would really run it, but it's always good to just add some version on our public.

##### **Geohot** [[00:48:06](https://www.youtube.com/watch?v=umHATMs0HDA&t=2886)]
Yeah, that makes sense. I think.

##### **Geohot** [[00:48:15](https://www.youtube.com/watch?v=umHATMs0HDA&t=2895)]
So you got 45B next.

##### **Wozeparrot** [[00:48:19](https://www.youtube.com/watch?v=umHATMs0HDA&t=2899)]
Yeah. 45B next.

##### **Geohot** [[00:48:22](https://www.youtube.com/watch?v=umHATMs0HDA&t=2902)]
Maybe 70B first.

##### **Wozeparrot** [[00:48:23](https://www.youtube.com/watch?v=umHATMs0HDA&t=2903)]
70B.

##### **Geohot** [[00:48:24](https://www.youtube.com/watch?v=umHATMs0HDA&t=2904)]
I think the goal this week is to train 8B MP.

##### **Geohot** [[00:48:34](https://www.youtube.com/watch?v=umHATMs0HDA&t=2914)]
No.

##### **Geohot** [[00:48:35](https://www.youtube.com/watch?v=umHATMs0HDA&t=2915)]
I think that's it.

##### **Wozeparrot** [[00:48:38](https://www.youtube.com/watch?v=umHATMs0HDA&t=2918)]
And then if that happens, then I'll do 70B. It works. Yeah, it used to work.

##### **Chenyu** [[00:48:43](https://www.youtube.com/watch?v=umHATMs0HDA&t=2923)]
Yeah.

##### **Wozeparrot** [[00:48:43](https://www.youtube.com/watch?v=umHATMs0HDA&t=2923)]
So I mean, well, with all the custom changes.

##### **Geohot** [[00:48:48](https://www.youtube.com/watch?v=umHATMs0HDA&t=2928)]
Yeah. That's the main thing. Yeah. Yeah. But yeah, no, I mean, what I want to see is in like, maybe like two weeks, I want to

##### **Geohot** [[00:49:00](https://www.youtube.com/watch?v=umHATMs0HDA&t=2940)]
see a converged 70B.

##### **Wozeparrot** [[00:49:02](https://www.youtube.com/watch?v=umHATMs0HDA&t=2942)]
Yeah. And then I also want to start porting the custom kernels to UOps.

##### **Geohot** [[00:49:11](https://www.youtube.com/watch?v=umHATMs0HDA&t=2951)]
Which ones?

##### **Wozeparrot** [[00:49:13](https://www.youtube.com/watch?v=umHATMs0HDA&t=2953)]
A lot of them are the ones that don't.

##### **Geohot** [[00:49:18](https://www.youtube.com/watch?v=umHATMs0HDA&t=2958)]
I think most of them are fairly simple. I don't know. I think most of them are not that complex.

##### **Geohot** [[00:49:28](https://www.youtube.com/watch?v=umHATMs0HDA&t=2968)]
I mean, I think in terms of priority, probably is better to just focus on 70B because

##### **Chenyu** [[00:49:35](https://www.youtube.com/watch?v=umHATMs0HDA&t=2975)]
these like translations are truly simple and just like mechanical translation. It's probably fine to wait a bit until we know what every one of those look like, especially for the 45B.

##### **Geohot** [[00:49:51](https://www.youtube.com/watch?v=umHATMs0HDA&t=2991)]
Yeah. I think we can also just take them out. I think that like, I'm fine with like, it's good that we got the time that we got, but like, if we just don't do the custom kernels for now, it shouldn't be that much slower. Right. We leave like flash attention and GEMM, but.

##### **Wozeparrot** [[00:50:05](https://www.youtube.com/watch?v=umHATMs0HDA&t=3005)]
Yeah. With just flash attention and GEMM it's fine. Some of the custom kernels save memory too, because we fuse more ops.

##### **Chenyu** [[00:50:13](https://www.youtube.com/watch?v=umHATMs0HDA&t=3013)]
Yeah. But those are the parts that we really want to see if we can bake that into our scheduler or the parts that we determine is.

##### **Geohot** [[00:50:24](https://www.youtube.com/watch?v=umHATMs0HDA&t=3024)]
Yeah.

##### **Chenyu** [[00:50:24](https://www.youtube.com/watch?v=umHATMs0HDA&t=3024)]
Yeah.

##### **Geohot** [[00:50:24](https://www.youtube.com/watch?v=umHATMs0HDA&t=3024)]
No, I agree. I don't, I don't think that rewriting, I think we should probably just take them out and then like we need or add a comment about how like, yeah, you can like put this back in and save memory. Okay.

##### **Chenyu** [[00:50:36](https://www.youtube.com/watch?v=umHATMs0HDA&t=3036)]
Because, because all these, I imagine would just work. I think along with Qazalin's work on making things more accessible to agents, you would imagine these GPT, Claude Code will just get better in a few months. Yeah. And the things we need to prepare now is kind of a translation task for what's before and what we want it to look like, which we have here, and we have our current UOp structure and we know kind of this custom kernel is fast. We use this for like mechanical rules. Even if it's not possible now, I imagine it will get a lot easier a few months later, having a comment make it easy to see like what we have now and what you have tried to be the best.

##### **Geohot** [[00:51:26](https://www.youtube.com/watch?v=umHATMs0HDA&t=3086)]
We good enough?

##### **Chenyu** [[00:51:27](https://www.youtube.com/watch?v=umHATMs0HDA&t=3087)]
We don't really need to make a change?

##### **Geohot** [[00:51:30](https://www.youtube.com/watch?v=umHATMs0HDA&t=3090)]
Great. We should simplify, and we should just focus on getting the big ones to train and worrying less about the speed. Yeah, I think also these things that are going to get you, you're like, oh, yeah, you can do this like fusion, and you can save memory. You can also just do this with gradient checkpointing. Use call and like change what we gradient checkpoint, and then the memory will all come back.

##### **Geohot** [[00:51:54](https://www.youtube.com/watch?v=umHATMs0HDA&t=3114)]
It'll be so negligible.

##### **Chenyu** [[00:52:01](https://www.youtube.com/watch?v=umHATMs0HDA&t=3121)]
I think the priority is to get 70B training and making sure we can run 45B. Yes. Because like the next deadline, the real deadline. The next deadline. Yes.

##### **Geohot** [[00:52:13](https://www.youtube.com/watch?v=umHATMs0HDA&t=3133)]
We know yet if it's going to be, they're going to remove it?

##### **Chenyu** [[00:52:16](https://www.youtube.com/watch?v=umHATMs0HDA&t=3136)]
I think they are going to remove it, but again, we are just, we are still in this run, right? So we would know better. Right.

##### **Geohot** [[00:52:23](https://www.youtube.com/watch?v=umHATMs0HDA&t=3143)]
I doubt it's going to be removed. AMD is for some reason sending us new computers.

##### **Wozeparrot** [[00:52:30](https://www.youtube.com/watch?v=umHATMs0HDA&t=3150)]
Yeah, I thought they were sending us GPUs. From the meeting I had with them, it seemed like they were just sending us GPUs.

##### **Geohot** [[00:52:36](https://www.youtube.com/watch?v=umHATMs0HDA&t=3156)]
Is what you told me? That's what I thought. I don't know. It's baffling to me that they're going to like build some MI300 boxes because like one GPU has a badly soldered voltage regulator or something.

##### **Chenyu** [[00:52:51](https://www.youtube.com/watch?v=umHATMs0HDA&t=3171)]
I take that as a good thing. Yeah. Just making sure we will have the machine that's good enough for our next submission and prioritize having our model trained with custom kernels.

##### **Geohot** [[00:53:06](https://www.youtube.com/watch?v=umHATMs0HDA&t=3186)]
We can keep the, we'll try to keep the three MI350 machines.

##### **Chenyu** [[00:53:11](https://www.youtube.com/watch?v=umHATMs0HDA&t=3191)]
OK. So. Issues. Comma happy? Is Comma happy?

##### **Chrism** [[00:53:20](https://www.youtube.com/watch?v=umHATMs0HDA&t=3200)]
One thing that Comma did mention that would be nice to have is being able to cross compile. So be able to compile for the AMD, like the USB GPU, without it plugged in. This would be a nice feature that they want to have. Can't do that. Like this is not something that we support. It's like something that we could definitely support, especially after HCQ2.

##### **Geohot** [[00:53:41](https://www.youtube.com/watch?v=umHATMs0HDA&t=3221)]
Yeah.

##### **Chrism** [[00:53:43](https://www.youtube.com/watch?v=umHATMs0HDA&t=3223)]
Worth, I guess, worth keeping that in mind

##### **Geohot** [[00:53:45](https://www.youtube.com/watch?v=umHATMs0HDA&t=3225)]
as a potential use case.

##### **Geohot** [[00:53:51](https://www.youtube.com/watch?v=umHATMs0HDA&t=3231)]
I've also been talking with Comma about training

##### **Geohot** [[00:53:54](https://www.youtube.com/watch?v=umHATMs0HDA&t=3234)]
their big foundation model. There's nothing that they're doing that we're not already dealing with in our LLaMA trainer. It's amazing how much, in the last five months, we've just sort of learned about training these things, how to do inference on the latest ones.

##### **Geohot** [[00:54:21](https://www.youtube.com/watch?v=umHATMs0HDA&t=3261)]
The gap between us and the state of the art of LLMs is closing.

##### **Geohot** [[00:54:31](https://www.youtube.com/watch?v=umHATMs0HDA&t=3271)]
Like it was, think about how many years,

##### **Geohot** [[00:54:35](https://www.youtube.com/watch?v=umHATMs0HDA&t=3275)]
like think about when we were training BERT, how many years old BERT was.

##### **Geohot** [[00:54:43](https://www.youtube.com/watch?v=umHATMs0HDA&t=3283)]
Now it's like, yeah, LLaMA training is still old, but the stuff that we're doing inference on is the absolute latest stuff. We have inference now on LLaMA and Qwen. OK, there's like one little generation ahead, the DeepSeek V4 stuff. But like, OK, what, we're six months behind now? Compared to when we were like years behind.

##### **Chenyu** [[00:55:09](https://www.youtube.com/watch?v=umHATMs0HDA&t=3309)]
Technically, it's also just out for six months,

##### **Geohot** [[00:55:11](https://www.youtube.com/watch?v=umHATMs0HDA&t=3311)]
so you cannot be left behind. Well, that's what I'm saying, right? We're like catching up to this, which is cool. I see the path for the first time to like replacing Comma's trainer.

##### **Geohot** [[00:55:29](https://www.youtube.com/watch?v=umHATMs0HDA&t=3329)]
They do. Hold on.

##### **Geohot** [[00:55:34](https://www.youtube.com/watch?v=umHATMs0HDA&t=3334)]
Sounds good.

##### **Geohot** [[00:55:35](https://www.youtube.com/watch?v=umHATMs0HDA&t=3335)]
I see Comma's here. Does Comma have any comment?

##### **Chenyu** [[00:55:42](https://www.youtube.com/watch?v=umHATMs0HDA&t=3342)]
No, I do not have any comment. I am also excited to use more tinygrad. I need to get more people working on trying to port more parts of our stack to tinygrad. I think some inference parts in the training stack can for sure be tinygrad. The last thing we were discussing was replacing our ONNX runtime with tinygrad.

##### **Chenyu** [[00:56:06](https://www.youtube.com/watch?v=umHATMs0HDA&t=3366)]
Oh, the one that, because Torch was magically like a few times faster, so you used Torch?

##### **Chenyu** [[00:56:13](https://www.youtube.com/watch?v=umHATMs0HDA&t=3373)]
Yes. Well, currently we use Torch and ONNX runtime. And for the speed critical stuff, we use Torch. OK. But if tinygrad was the same speed based on ONNX graphs as Torch, this would be much preferable.

##### **Geohot** [[00:56:28](https://www.youtube.com/watch?v=umHATMs0HDA&t=3388)]
On NVIDIA? On AMD, we're the same speed.

##### **Chenyu** [[00:56:32](https://www.youtube.com/watch?v=umHATMs0HDA&t=3392)]
I see. But currently, tinygrad is already faster than ONNX runtime. So we're hoping we can port ONNX runtime to tinygrad. And then maybe sometime in the future, we can port the PyTorch stuff.

##### **Geohot** [[00:56:44](https://www.youtube.com/watch?v=umHATMs0HDA&t=3404)]
Bar is low in ONNX runtime.

##### **Chenyu** [[00:56:47](https://www.youtube.com/watch?v=umHATMs0HDA&t=3407)]
Exactly. So we can start there.

##### **Geohot** [[00:56:49](https://www.youtube.com/watch?v=umHATMs0HDA&t=3409)]
With Torch and torch.compile, the bar is quite high. That's quite good.

##### **Chenyu** [[00:56:56](https://www.youtube.com/watch?v=umHATMs0HDA&t=3416)]
Yeah, but I mean, it's really, really ugly, right? Like you need to save the code. It's kind of disgusting. It's fast. Yeah. Yeah, so we'll try to start soon with porting the ONNX runtime stuff. And then we'll, if we have any complaints.

##### **Geohot** [[00:57:14](https://www.youtube.com/watch?v=umHATMs0HDA&t=3434)]
TJ, any comments on Kimi?

##### **Qazalin** [[00:57:17](https://www.youtube.com/watch?v=umHATMs0HDA&t=3437)]
No. Okay. Okay. Hello.

##### **Geohot** [[00:57:26](https://www.youtube.com/watch?v=umHATMs0HDA&t=3446)]
Hi.

##### **Qazalin** [[00:57:27](https://www.youtube.com/watch?v=umHATMs0HDA&t=3447)]
Hi.

##### **B1tg** [[00:57:28](https://www.youtube.com/watch?v=umHATMs0HDA&t=3448)]
Oh, I think Kimi is good to merge. It's a little slower now. And I just found our AMD backend. And for the AQL packet, we set the fence scope always to be system.

##### **Geohot** [[00:58:00](https://www.youtube.com/watch?v=umHATMs0HDA&t=3480)]
You set the fence scope?

##### **B1tg** [[00:58:02](https://www.youtube.com/watch?v=umHATMs0HDA&t=3482)]
Yes. The fence scope system.

##### **Geohot** [[00:58:13](https://www.youtube.com/watch?v=umHATMs0HDA&t=3493)]
Oh, yeah, yeah, yeah.

##### **B1tg** [[00:58:15](https://www.youtube.com/watch?v=umHATMs0HDA&t=3495)]
And it can be fence scope agent sometimes. It has potential 10% speedup.

##### **Geohot** [[00:58:29](https://www.youtube.com/watch?v=umHATMs0HDA&t=3509)]
I think let's, before we focus on the speed, let's focus on getting this merged. How much of your LLM shard support PR can you split into things that are like bug fixes versus things that are like new functionality? A lot of like, I see. Like a lot of things just being more precise about the device. Just do those things as a separate PR.

##### **B1tg** [[00:58:57](https://www.youtube.com/watch?v=umHATMs0HDA&t=3537)]
I think they have bugs. Maybe some cleanup PR first.

##### **Geohot** [[00:59:06](https://www.youtube.com/watch?v=umHATMs0HDA&t=3546)]
Great. Let's do a cleanup PR. Let's get that merged. And then I can really review the shard support stuff. There's another PR in there about all the device stuff that we have to clean up.

##### **Geohot** [[00:59:28](https://www.youtube.com/watch?v=umHATMs0HDA&t=3568)]
For this meeting.

##### **Geohot** [[00:59:30](https://www.youtube.com/watch?v=umHATMs0HDA&t=3570)]
FL was here for a minute. He got something that took agents a long time. Yeah. Great.

##### **Chenyu** [[00:59:36](https://www.youtube.com/watch?v=umHATMs0HDA&t=3576)]
Okay. Yeah. Okay. Thank you everyone. See you next week. Bye. Bye.
