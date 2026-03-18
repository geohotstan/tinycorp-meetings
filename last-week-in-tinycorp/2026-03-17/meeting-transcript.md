# 2026-03-17 Meeting

### Meeting Agenda

**Time:** new meeting #10, 3/16 9pm Monday San Diego time
- company update, not raise
- llama training
- viz
- drivers
- IMAGE=1
- tiny specs, call, tuple
- new assign, divmod
- other issues, bounties, any comma complaints

### Audio

[Youtube Link](https://www.youtube.com/watch?v=BzXf5_42qU0)

### Highlights

- **[Company update: pursue asymmetric compute strategy, not a raise](#geohot-000006)**: Geohot said the company should not try to compete head-on with hyperscalers by raising money to build a facility; instead, the plan is to find cheaper, underused hardware and deploy compute in storage-container-style “tiny box” systems to gain an asymmetric advantage.
- **[Large-compute buildout can wait until unit economics are clearer](#geohot-000218)**: Geohot cautioned that current compute scarcity may be a bubble, said prices will likely come down, and argued they can raise money later on better terms once they can show a system that pays itself back quickly.
- **[Llama training focus is activation checkpointing via precompile backwards](#geohot-000440)**: Geohot said upcoming tooling will allow wrapping whole layers in `precompile` / `precompile_backwards` so backward passes only rely on function inputs and outputs, recomputing intermediates to save memory and enable clean gradient checkpointing.
- **[405B scheduling improved, but 70B training speed is still a major problem](#wozeparrot-000594)**: Wozeparrot said late all-reduce made 405B scheduling much faster, but a single 70B training step still takes about 8 hours 30 minutes, which Geohot called unacceptable and likely tied to bad GEMM shapes.
- **[CDNA4 viz priorities: emulator coverage, packet tracing, and ALU mapping](#geohot-001270)**: Geohot said the sprint’s main viz goals are getting the CDNA4 emulator and CI tests running for flash attention and GEMMs, plus making ALU packets clickable and tied back to dispatch/instruction views.
- **[Driver progress includes NV/NVCC support and remote PCI work](#wozeparrot-001544)**: The team said they now have full support paths for both AMD and NV, NVCC works with LLaMA, and remote PCI support is close to merge, with plans to use shared remote GPUs such as the Hong Kong office tiny box.
- **[New Apple board is nearing launch](#geohot-001627)**: Geohot said the upcoming Apple board has debugging-friendly features like serial, supports both ATX and 12V input, removes fragile switches, and is likely to launch in roughly six weeks to two months pending mass production.
- **[IMAGE=2 is close enough in compile speed that IMAGE=1 can be removed](#chrism-001829)**: Chrism said compile time for `IMAGE=2` is now only about 30 seconds different from `IMAGE=1`, and the team agreed this is good enough to justify deleting the older path and cleaning up related image-specific code.
- **[OpenPilot/comma may be missing recent tinygrad speedups](#chenyu-001882)**: Chenyu noted OpenPilot appears pinned to a tinygrad version from over a month ago, and Geohot said they need to check with comma because paused updates may mean they have not seen recent performance improvements.
- **[Spec work added multi-output calls, tuple support, and cleaner function boundaries](#geohot-002033)**: Geohot said recent spec work now allows calls to return multiple values through tuples, supports structured function inputs, and is aimed at making `precompile`/function tooling cleaner and more robust.
- **[Assign removal is converging on a store-plus-after model](#chenyu-002396)**: Chenyu explained that `assign` is being replaced by a combination of `store` for side effects and `after` for downstream buffer flow, simplifying semantics and making the graph model more consistent.
- **[“Agentic Viz” direction is to build better docs and tooling for both humans and agents](#geohot-002979)**: The team discussed making viz easier for Claude-like agents by improving the viz README/CLI and treating documentation as operational guidance, with Geohot saying the long-term goal is effectively “auto research, but with tinygrad.”

### Transcript
##### **Geohot** [[00:00:00](https://www.youtube.com/watch?v=BzXf5_42qU0&t=0)]
Welcome. Let's start with company update.

##### **Geohot** [[00:00:06](https://www.youtube.com/watch?v=BzXf5_42qU0&t=6)]
Yeah, so, you know, like, it's very frustrating that AI requires large computers. And I don't want us to fall behind on having large computers, but on any long lead time projects that would be required to get our large computers. Like, I can see a world where all of these sites are bought up. I could see a lot of people just say, OK, we want to buy power capacity at all costs. And then it becomes really important. You make sure we have some. Similar to how we're seeing this happen with compute now, who would have possibly thought that GPUs and memory were appreciating assets. But, you know, when you go to Cuba, cars are depreciating assets.

##### **Geohot** [[00:01:04](https://www.youtube.com/watch?v=BzXf5_42qU0&t=64)]
Then I realized that two things are true.

##### **Geohot** [[00:01:16](https://www.youtube.com/watch?v=BzXf5_42qU0&t=76)]
One, the premium that the hyperscalers are willing to pay is exactly that definitiveness. And there's no way that we could ever compete with these people on that. So actually the strategy of raising and trying to build a facility is doomed to fail to the people who have way more money than you. So you need some asymmetric advantage. And I think what we can do is our asymmetric advantage: we'll be able to find like... my dream for silicon is being able to buy silicon below cost. If we go in through the front door and say we're going to tape out our own chip, we lose to Amazon. But if we're like, hmm, Grok, you know all those chips that you think nobody can use? Well, turns out with tinygrad, we can use them, and it's pretty easy, and we can buy them way below cost. I mean, you already see this today with things like the MI250s. The MI250 is the best compute-per-dollar card you can buy right now, but nobody wants to plug them in. The question is: what's that same strategy for power? And the answer is probably storage containers. We build a computer inside a storage container and then we can deploy that computer anywhere. It's the X-box. You can think about it like a tiny box. And this is an asymmetric advantage over cloud providers and we will be able to likely get power for lower cost than them. We'll be able to get hardware at lower cost than them. And that's how we beat them. But yes, we lose if we try to go in through the front door. So yeah, the money's there though. If we ever decide we need $20 million, I think it would take about two weeks to get it.

##### **Geohot** [[00:03:02](https://www.youtube.com/watch?v=BzXf5_42qU0&t=182)]
Are you using something else?

##### **Chenyu** [[00:03:05](https://www.youtube.com/watch?v=BzXf5_42qU0&t=185)]
Yeah.

##### **Geohot** [[00:03:07](https://www.youtube.com/watch?v=BzXf5_42qU0&t=187)]
Comma is building containers and then we're going to.

##### **Geohot** [[00:03:12](https://www.youtube.com/watch?v=BzXf5_42qU0&t=192)]
Well, so like right now, it's probably not a good idea to build anything. I mean, prices will come down, right? People might say this is the forever supply bottleneck of compute, but that's exactly what people say at the top of a bubble.

##### **Chenyu** [[00:03:31](https://www.youtube.com/watch?v=BzXf5_42qU0&t=211)]
Just saying they're going to sell double, as previously projected.

##### **Geohot** [[00:03:38](https://www.youtube.com/watch?v=BzXf5_42qU0&t=218)]
And Jensen may very well sell double. He's also very inclined to tell you he's going to sell double. Um. But no. I mean, the. It's actually so interesting whenever you look at bubbles like the peak of a bubble at the peak of a bubble. Everybody is always going to say like tulips are only going to go up. We're going to sell double as many tulips next year. Now, it doesn't necessarily mean that the bubble is going to pop. But I just want to note that this is exactly what people say before the bubble pops. And it's also what people say before the bubble doesn't pop. So it gives us no information either way. But, you know, either way. Yeah, we have money if we need it. But I think we can also get money at a better deal if we show unit economics. And if we can. It's like it's a bad deal, but I think we can. If we have the kind of thing where like we can make this thing and it pays itself back in six months. All right, great. Cool. I'll borrow money from any bank.

##### **Geohot** [[00:04:43](https://www.youtube.com/watch?v=BzXf5_42qU0&t=283)]
Why sell equity? Um, so yeah, that's kind of that. The X-box.

##### **Geohot** [[00:04:51](https://www.youtube.com/watch?v=BzXf5_42qU0&t=291)]
We built larger, tiny boxes. It costs a thousand X more money and can be plugged in outside and use a thousand X more power.

##### **Chenyu** [[00:05:05](https://www.youtube.com/watch?v=BzXf5_42qU0&t=305)]
All right. Great.

##### **Chenyu** [[00:05:10](https://www.youtube.com/watch?v=BzXf5_42qU0&t=310)]
Next. Llama training.

##### **Wozeparrot** [[00:05:21](https://www.youtube.com/watch?v=BzXf5_42qU0&t=321)]
So I have the thing for you and I'll have it done today. Okay.

##### **Geohot** [[00:05:45](https://www.youtube.com/watch?v=BzXf5_42qU0&t=345)]
Um, so. So what you need, I think, is so this is all about activation checkpointing.

##### **Wozeparrot** [[00:05:50](https://www.youtube.com/watch?v=BzXf5_42qU0&t=350)]
Yeah, basically.

##### **Chenyu** [[00:05:52](https://www.youtube.com/watch?v=BzXf5_42qU0&t=352)]
Another one that you just mentioned.

##### **Wozeparrot** [[00:05:55](https://www.youtube.com/watch?v=BzXf5_42qU0&t=355)]
We can also. I don't know if sequence parallel fixes all of our memory.

##### **Geohot** [[00:06:01](https://www.youtube.com/watch?v=BzXf5_42qU0&t=361)]
Issues.

##### **SPEAKER_07** [[00:06:05](https://www.youtube.com/watch?v=BzXf5_42qU0&t=365)]
So have you.

##### **Geohot** [[00:06:06](https://www.youtube.com/watch?v=BzXf5_42qU0&t=366)]
Right.

##### **Wozeparrot** [[00:06:09](https://www.youtube.com/watch?v=BzXf5_42qU0&t=369)]
Sequence parallel. Basically, you restart before and after the FFN and attention so that your norm is not duplicated across your GPUs. I tried a much simpler version of this and it didn't seem to save memory, even though it should.

##### **Geohot** [[00:06:33](https://www.youtube.com/watch?v=BzXf5_42qU0&t=393)]
I mean, I think the question to ask is that we need to say exactly what are we saving for each layer on the backwards pass?

##### **Geohot** [[00:06:43](https://www.youtube.com/watch?v=BzXf5_42qU0&t=403)]
Yeah. Do you know that? You know what we're saving and do you know what we want to say?

##### **Wozeparrot** [[00:06:51](https://www.youtube.com/watch?v=BzXf5_42qU0&t=411)]
We should just be saving whatever is going into the layer.

##### **Geohot** [[00:06:58](https://www.youtube.com/watch?v=BzXf5_42qU0&t=418)]
You just want to save one thing.

##### **Geohot** [[00:07:02](https://www.youtube.com/watch?v=BzXf5_42qU0&t=422)]
No, but flash attention saving something for backwards. Do you want to save that too?

##### **Wozeparrot** [[00:07:07](https://www.youtube.com/watch?v=BzXf5_42qU0&t=427)]
Oh, yeah. Other than the implicitly save things for flash attention. It's also possible that we don't save that for flash attention. Yeah. Because if we have the layer input, we just run flash attention forward again to recompute.

##### **Geohot** [[00:07:20](https://www.youtube.com/watch?v=BzXf5_42qU0&t=440)]
Yeah, we could totally do that. So if that's what you want, that will be merged in like a few hours. But you're going to have to fix it for your HK flash attention, because it doesn't work for HK flash attention. The first thing that you need to get working is you want to wrap whatever you want to wrap in function and do `precompile=true`.

##### **Geohot** [[00:07:44](https://www.youtube.com/watch?v=BzXf5_42qU0&t=464)]
Yeah.

##### **Wozeparrot** [[00:07:49](https://www.youtube.com/watch?v=BzXf5_42qU0&t=469)]
So how about branch with the anonymous buffer stuff?

##### **Geohot** [[00:07:54](https://www.youtube.com/watch?v=BzXf5_42qU0&t=474)]
You don't need any anonymous buffer stuff. So get it working with `precompile=true`. And what I'll merge by the end of today is `precompile_backwards=true`. And then `precompile_backwards=true` will save the memory.

##### **Geohot** [[00:08:07](https://www.youtube.com/watch?v=BzXf5_42qU0&t=487)]
Okay.

##### **Geohot** [[00:08:09](https://www.youtube.com/watch?v=BzXf5_42qU0&t=489)]
But you need there's some bug. Oh, yeah. Oh, the anonymous buffers. Oh, you do need anonymous buffers. Yeah. Yeah.

##### **Wozeparrot** [[00:08:18](https://www.youtube.com/watch?v=BzXf5_42qU0&t=498)]
Yeah.

##### **Geohot** [[00:08:20](https://www.youtube.com/watch?v=BzXf5_42qU0&t=500)]
Yeah. Yeah. I'm working right now. Sorry, the tool wasn't quite ready. But the tool will be ready by the end of the day. You basically wrap the entire layer in a `precompile` and in a `precompile_backwards`. And then a `precompile_backwards` will use only the inputs to the function or the outputs to the function. So it promises that it'll only use those two things. It can't take anything from the middle of the function.

##### **Geohot** [[00:08:58](https://www.youtube.com/watch?v=BzXf5_42qU0&t=538)]
And it'll recompute everything basically. That's what you expect. Yeah.

##### **Geohot** [[00:09:06](https://www.youtube.com/watch?v=BzXf5_42qU0&t=546)]
Now, it will use all the inputs to the function. So it'll still use all the weights and KV and all that stuff. Okay. And then if you want to save something, the API is quite simple. And that's why I worked on all the tuple stuff. You just need to make whatever you want to save an output to the function. Even if you don't use that output on the forward pass, it will automatically be used on the backward pass.

##### **Geohot** [[00:09:32](https://www.youtube.com/watch?v=BzXf5_42qU0&t=572)]
I see.

##### **Geohot** [[00:09:34](https://www.youtube.com/watch?v=BzXf5_42qU0&t=574)]
So yeah, we can make sure that API works. I'll merge my test for today. And then if you have any bugs with it, let me know. But that should give you gradient checkpointing in a beautiful clean style. It should also speed everything up. How long is it right now? To run 405B?

##### **Wozeparrot** [[00:09:51](https://www.youtube.com/watch?v=BzXf5_42qU0&t=591)]
To run 405B...

##### **Geohot** [[00:09:54](https://www.youtube.com/watch?v=BzXf5_42qU0&t=594)]
Schedule.

##### **Wozeparrot** [[00:09:54](https://www.youtube.com/watch?v=BzXf5_42qU0&t=594)]
It's much faster with late all reduce. That's why I merged that. It's like actually like cyclable. It still takes like five minutes to schedule.

##### **Geohot** [[00:10:06](https://www.youtube.com/watch?v=BzXf5_42qU0&t=606)]
That's not too bad. I think a lot of this is assign hazards still, which you can actually comment out since there aren't any in the thing. I just made this a tad faster.

##### **Chenyu** [[00:10:17](https://www.youtube.com/watch?v=BzXf5_42qU0&t=617)]
Right. But you can comment it out.

##### **Geohot** [[00:10:20](https://www.youtube.com/watch?v=BzXf5_42qU0&t=620)]
Yeah. Yeah. Or maybe we can have an environment variable for that. Dangerous. Ignore assign hazards equals true.

##### **Chenyu** [[00:10:26](https://www.youtube.com/watch?v=BzXf5_42qU0&t=626)]
How does 70B look like? You run a step. And how long will that take? You could say we run...

##### **Wozeparrot** [[00:10:34](https://www.youtube.com/watch?v=BzXf5_42qU0&t=634)]
Before commas power outage, I ran three steps.

##### **Geohot** [[00:10:39](https://www.youtube.com/watch?v=BzXf5_42qU0&t=639)]
That caused comma's power outage?

##### **Wozeparrot** [[00:10:43](https://www.youtube.com/watch?v=BzXf5_42qU0&t=643)]
I hope that during our 405B run, comma does not have a power outage.

##### **Geohot** [[00:10:48](https://www.youtube.com/watch?v=BzXf5_42qU0&t=648)]
Wait. Was commas power outage caused by the utility or comma?

##### **Wozeparrot** [[00:10:55](https://www.youtube.com/watch?v=BzXf5_42qU0&t=655)]
Utility.

##### **Geohot** [[00:10:56](https://www.youtube.com/watch?v=BzXf5_42qU0&t=656)]
Okay.

##### **Wozeparrot** [[00:10:56](https://www.youtube.com/watch?v=BzXf5_42qU0&t=656)]
The neighbor was also out.

##### **Geohot** [[00:10:58](https://www.youtube.com/watch?v=BzXf5_42qU0&t=658)]
Okay. Great. Are you back now?

##### **Wozeparrot** [[00:11:01](https://www.youtube.com/watch?v=BzXf5_42qU0&t=661)]
I'm not. I go back Wednesday.

##### **Geohot** [[00:11:02](https://www.youtube.com/watch?v=BzXf5_42qU0&t=662)]
Very cool. Yeah. What happened? Also, what happened? What was the incident with our infrastructure? It still looks down.

##### **Wozeparrot** [[00:11:09](https://www.youtube.com/watch?v=BzXf5_42qU0&t=669)]
Yeah. Infrastructure will be fixed. It will be fixed when I'm back Wednesday.

##### **Geohot** [[00:11:12](https://www.youtube.com/watch?v=BzXf5_42qU0&t=672)]
Great. And then can we make sure it doesn't have it again? Yes.

##### **Wozeparrot** [[00:11:16](https://www.youtube.com/watch?v=BzXf5_42qU0&t=676)]
This was on me. I forgot to put the BMC IPs.

##### **Geohot** [[00:11:21](https://www.youtube.com/watch?v=BzXf5_42qU0&t=681)]
For the gateways.

##### **Wozeparrot** [[00:11:22](https://www.youtube.com/watch?v=BzXf5_42qU0&t=682)]
For the gateways.

##### **Geohot** [[00:11:24](https://www.youtube.com/watch?v=BzXf5_42qU0&t=684)]
No worries. Let's just fix it for next time. Okay. What happened to three steps of 70B? Is it wrong?

##### **Wozeparrot** [[00:11:30](https://www.youtube.com/watch?v=BzXf5_42qU0&t=690)]
One step is eight hours and 30 minutes.

##### **Geohot** [[00:11:35](https://www.youtube.com/watch?v=BzXf5_42qU0&t=695)]
What? That sounds pretty long.

##### **Wozeparrot** [[00:11:40](https://www.youtube.com/watch?v=BzXf5_42qU0&t=700)]
Very slow step. Okay. I believe it's hitting bad gem shapes. Last time I checked this, it was hitting bad gem shapes.

##### **Geohot** [[00:11:49](https://www.youtube.com/watch?v=BzXf5_42qU0&t=709)]
Yeah. You need to fix this.

##### **Geohot** [[00:11:52](https://www.youtube.com/watch?v=BzXf5_42qU0&t=712)]
This is a major problem.

##### **Wozeparrot** [[00:11:56](https://www.youtube.com/watch?v=BzXf5_42qU0&t=716)]
405B is not going to be faster than that. 405B hits the same bad GEMM shapes.

##### **Geohot** [[00:12:04](https://www.youtube.com/watch?v=BzXf5_42qU0&t=724)]
Regardless, still eight hours. What?

##### **Wozeparrot** [[00:12:09](https://www.youtube.com/watch?v=BzXf5_42qU0&t=729)]
Yeah. For one step.

##### **Geohot** [[00:12:10](https://www.youtube.com/watch?v=BzXf5_42qU0&t=730)]
What is it? What are you running on? Pentium 2? Okay.

##### **Chenyu** [[00:12:18](https://www.youtube.com/watch?v=BzXf5_42qU0&t=738)]
I don't know. Maybe you don't have enough information to answer this, but you see that it cannot be less slow. Yes. Regardless of a memory issue, that speed is also... Yeah. That's... Yeah. Okay. I mean, if it indeed is like bad single kernel. Yeah. Or single type of kernel, that's easy. It's a lot more safe if you're doing like incredibly bad, but we'll see.

##### **Geohot** [[00:12:49](https://www.youtube.com/watch?v=BzXf5_42qU0&t=769)]
Okay. Sounds good. Next is this. You can actually try real time now. All right. All right. Now. Yeah. I'm going to try this.

##### **Geohot** [[00:13:09](https://www.youtube.com/watch?v=BzXf5_42qU0&t=789)]
Yeah.

##### **Geohot** [[00:13:09](https://www.youtube.com/watch?v=BzXf5_42qU0&t=789)]
So CDNA4... CDNA is good?

##### **Qazalin** [[00:13:14](https://www.youtube.com/watch?v=BzXf5_42qU0&t=794)]
CDNA... I merged something that shows the packets. The only way forward here is if I see the packets and I understand the actual trace that it's giving, because it's not realistic that we're going to match rocprof.

##### **Geohot** [[00:13:33](https://www.youtube.com/watch?v=BzXf5_42qU0&t=813)]
I don't really care about matching rocprof. That's not important to me.

##### **Qazalin** [[00:13:39](https://www.youtube.com/watch?v=BzXf5_42qU0&t=819)]
Yeah. What I'm seeing from CDNA is that it's very different. For example, you have four overlapping MFMA packets with the same timestamp, and that's just not really possible. Like, how can you do four at the same time?

##### **Geohot** [[00:14:05](https://www.youtube.com/watch?v=BzXf5_42qU0&t=845)]
Wait. I think you can do four at the same time. I think that's how the architecture works. I mean, it's a totally different architecture.

##### **Qazalin** [[00:14:15](https://www.youtube.com/watch?v=BzXf5_42qU0&t=855)]
It's also out of order.

##### **Geohot** [[00:14:18](https://www.youtube.com/watch?v=BzXf5_42qU0&t=858)]
Also out of order.

##### **Geohot** [[00:14:19](https://www.youtube.com/watch?v=BzXf5_42qU0&t=859)]
Yeah.

##### **Geohot** [[00:14:23](https://www.youtube.com/watch?v=BzXf5_42qU0&t=863)]
Oh. I just... I see... So, yeah. Realtime works. I see you have name duration. You have start time and timestamp. It should probably be like start cycle or something.

##### **Geohot** [[00:14:37](https://www.youtube.com/watch?v=BzXf5_42qU0&t=877)]
All right. So, yeah.

##### **Geohot** [[00:14:38](https://www.youtube.com/watch?v=BzXf5_42qU0&t=878)]
So, yeah. So, yeah. So, yeah.

##### **Geohot** [[00:14:39](https://www.youtube.com/watch?v=BzXf5_42qU0&t=879)]
It's just the name.

##### **Geohot** [[00:14:40](https://www.youtube.com/watch?v=BzXf5_42qU0&t=880)]
And then also, any progress tying the ALU back to the instruction?

##### **Qazalin** [[00:14:52](https://www.youtube.com/watch?v=BzXf5_42qU0&t=892)]
I didn't do that. I did barriers today.

##### **Geohot** [[00:14:55](https://www.youtube.com/watch?v=BzXf5_42qU0&t=895)]
You did barriers today? I did barriers.

##### **Qazalin** [[00:14:58](https://www.youtube.com/watch?v=BzXf5_42qU0&t=898)]
Yeah. I did barriers.

##### **Geohot** [[00:15:00](https://www.youtube.com/watch?v=BzXf5_42qU0&t=900)]
Let me see barriers. And then how about... I think you... If he's not... If that bounty guy is not finishing that, you should just get that stuff merged.

##### **Qazalin** [[00:15:10](https://www.youtube.com/watch?v=BzXf5_42qU0&t=910)]
I tried it six hours ago and it was still segfaulting. I think I have to finish that myself.

##### **Geohot** [[00:15:16](https://www.youtube.com/watch?v=BzXf5_42qU0&t=916)]
Yeah. Yeah. We don't need to rely on that guy.

##### **Geohot** [[00:15:21](https://www.youtube.com/watch?v=BzXf5_42qU0&t=921)]
What?

##### **Geohot** [[00:15:23](https://www.youtube.com/watch?v=BzXf5_42qU0&t=923)]
Oh.

##### **Geohot** [[00:15:24](https://www.youtube.com/watch?v=BzXf5_42qU0&t=924)]
I don't know. Let's see barriers. Yay. Beautiful.

##### **Geohot** [[00:15:29](https://www.youtube.com/watch?v=BzXf5_42qU0&t=929)]
It looks so wasteful. Did you do a good job figuring out which one belongs to which wave and stuff? Did you... Yeah. Did you extract that logic nicely?

##### **Qazalin** [[00:15:41](https://www.youtube.com/watch?v=BzXf5_42qU0&t=941)]
Which wave group? You know, you can see which ones align, which ones line up, and then you just infer that. Because the hardware surely knows, right?

##### **Geohot** [[00:15:53](https://www.youtube.com/watch?v=BzXf5_42qU0&t=953)]
Right. How did you do this?

##### **Geohot** [[00:15:59](https://www.youtube.com/watch?v=BzXf5_42qU0&t=959)]
You just have to compute it locally from the wave. What do you mean? So I have the pictures in here. Why is that doing... I just posted a picture. Why is that doing that? Yeah, because it's in different workgroups. See? No, they're not.

##### **Geohot** [[00:16:34](https://www.youtube.com/watch?v=BzXf5_42qU0&t=994)]
Those two are in the same work group.

##### **Qazalin** [[00:16:36](https://www.youtube.com/watch?v=BzXf5_42qU0&t=996)]
Are you sure about that?

##### **Geohot** [[00:16:37](https://www.youtube.com/watch?v=BzXf5_42qU0&t=997)]
Yeah.

##### **Qazalin** [[00:16:38](https://www.youtube.com/watch?v=BzXf5_42qU0&t=998)]
Because if it was in the same work group, it would line up.

##### **Geohot** [[00:16:41](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1001)]
I promise you they're in the same work group. Those two.

##### **Geohot** [[00:16:46](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1006)]
Is this AMD asm matmul? Yeah, it's AMD asm matmul. I mean, it can't be.

##### **Qazalin** [[00:16:58](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1018)]
If it's in the same work group, it will look like the first picture in there.

##### **Geohot** [[00:17:02](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1022)]
I know. Most of them are correct, but that one's wrong. There's a bug.

##### **Qazalin** [[00:17:06](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1026)]
There's a bug. All right. I'll look more.

##### **Geohot** [[00:17:09](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1029)]
Yeah, there's a bug.

##### **Qazalin** [[00:17:10](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1030)]
This is what I expect if it's in the same work group.

##### **Geohot** [[00:17:14](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1034)]
No, no, no. I mean, most of them are correct. And I'm not saying that I know the solution to this problem. I'm just saying that it's something I was thinking about. How do you make the barriers line up? So how did you do it?

##### **Qazalin** [[00:17:27](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1047)]
I just wait in the same wave until a new instruction comes in, and then I draw the barrier from the point that the barrier is received, and then the instruction next.

##### **Geohot** [[00:17:40](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1060)]
Oh, yeah, that's the problem, right? Because the barrier might end even though an instruction isn't scheduled. This might be fine. This might be fine as long as it's not some bad heuristic. It's still kind of right.

##### **Qazalin** [[00:17:54](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1074)]
It's the best you can hope for, because you're assuming that the scheduler will do its job all the way.

##### **Geohot** [[00:18:04](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1084)]
Well, you have a barrier. No. I mean, you could technically make an argument that the barrier ends sooner. Right? Like, just because nothing was scheduled doesn't necessarily mean that it's the... Eh, whatever. I think it's fine. I think it's fine. But, yeah. I think CDNA4, take it over from that guy. Get those CDNA4 tests running. I don't know if that's the right word.

##### **Geohot** [[00:18:34](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1114)]
Yeah, syncing up the packet. Thinking like the ALU packet with the... they draw a nice line between them. Executive dispatch, yeah. Cool. I like the barriers. Wow, it's so wasteful. GPU wasting. RDNA4 also completely changed barriers into a signal and a wait. What do you mean by that?

##### **Qazalin** [[00:19:25](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1165)]
So you signal that you're going to issue a barrier, but then you do a bunch of stuff. And then you do a wait barrier, which actually waits.

##### **Geohot** [[00:19:36](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1176)]
There's two instructions for this. Yes, I have the picture if you scroll up, or in the PR. I see what you're saying. Barrier signal. Oh, that's so interesting. Okay, cool. It's a VALU, yes, because it's not immediate. Like it's not per wave. It's per wave, actually. Yeah. I mean, immediates are per wave too, but interesting that that goes to the VALU.

##### **Qazalin** [[00:20:25](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1225)]
Actually, this might be because it's an exact

##### **Geohot** [[00:20:30](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1230)]
zero. Yeah. Is there any future to more CDNA, or are we just gonna

##### **Qazalin** [[00:20:44](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1244)]
for RDNA?

##### **Geohot** [[00:20:46](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1246)]
What do you mean, future more CDNA?

##### **Qazalin** [[00:20:49](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1249)]
I mean, CDNA is pretty different, both the SQTT and

##### **Geohot** [[00:20:55](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1255)]
the model. Oh yeah, I mean, we want it to work.

##### **Geohot** [[00:21:10](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1270)]
I mean, I think the first two priorities this sprint are getting the CDNA4 emulator, testing our flash attention and GEMMs in CI, and being able to click the ALU packet and click the ALU dispatch, and having the

##### **Geohot** [[00:21:31](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1291)]
the ALU and instruction views line up.

##### **Geohot** [[00:21:45](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1305)]
Have you seen AMD call matmul?

##### **Geohot** [[00:21:52](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1312)]
It's in the branch, I think.

##### **Geohot** [[00:22:01](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1321)]
It's just a refined version of AMD UOP matmul. I also put it in Claude and had it do the, like, can we now use our tooling to make kernels that exceed the speed of

##### **Geohot** [[00:22:20](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1340)]
rocBLAS? Like how fast can you make a GEMM? Make sure the tensor cores stay busy. Make sure the what?

##### **Qazalin** [[00:22:47](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1367)]
Tensor cores stay busy.

##### **Geohot** [[00:22:50](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1370)]
Yeah, so make sure the tensor cores stay busy. I think another thing you're going to find: once you get the VALU matching up with the wave, you'll know what instruction type the VALU was, and then you can get it to have the correct duration for WMMA packets.

##### **Qazalin** [[00:23:07](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1387)]
How many cycles WMMA takes.

##### **Geohot** [[00:23:10](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1390)]
Yeah, so right now all the VALUs just have one cycle, even though the WMMA, I believe, occupies the whole VALU for 32. So I don't think you can recover that from the SQTT trace. I think we just have to hard-code that one.

##### **Geohot** [[00:23:27](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1407)]
But WMMA is important enough that it's worth it. I'll merge my WMMA, and then yeah, once you get the packets matched, we can get the durations correct. If we want Claude to use these tools, then it needs formats that Claude can use. Yeah, can we get SQTT CLI working with viz CLI working with SQTT? Super easy.

##### **Geohot** [[00:24:37](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1477)]
Actually, I like that project. I like that as a project even more than making one GEMM fast: making it so Claude can look at the SQTT trace and use it. Yeah, I mean it should be

##### **Geohot** [[00:24:52](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1492)]
80% the same logic as the web one

##### **Geohot** [[00:24:57](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1497)]
##### **Geohot** [[00:25:00](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1500)]
Sounds good. Anything else? I think that's all. Next is drivers.

##### **Wozeparrot** [[00:25:44](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1544)]
Yeah, we also got entitlements now for both AMD and NV. So the only one is

##### **Geohot** [[00:25:51](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1551)]
for the installer, so we're currently

##### **Geohot** [[00:25:55](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1555)]
missing, but I hope we can get this one pretty soon. Yeah. I also landed almost all the pieces for the remote.

##### **Wozeparrot** [[00:26:07](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1567)]
I think I can merge it pretty soon.

##### **Geohot** [[00:26:11](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1571)]
I mean, the PCI remote. And actually, I just tested that NVCC works with LLaMA. So yeah, the NVCC Docker works. Yeah. How big is the Docker? Just curious.

##### **Geohot** [[00:26:33](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1593)]
Just the diff is like 60 megabytes or so. A little less than that.

##### **Geohot** [[00:26:40](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1600)]
Oh, how big is the docker with NVCC in it?

##### **Geohot** [[00:26:43](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1603)]
I don't know.

##### **Geohot** [[00:26:43](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1603)]
I don't know. I don't know. I don't know. I don't know.

##### **Geohot** [[00:26:47](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1607)]
We should test that in CI too. In fact, we might even want to. Yeah, very exciting on the Apple thing.

##### **Geohot** [[00:27:07](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1627)]
For anyone who is in the meeting, you guys get to know we're going to sell these eGPU boards. They have debugging features. They support both ATX power supply and 12-volt inputs. They have a serial port for debugging. That's kind of the big feature. They have some unbreakable advantages over the ADT board, and they just have less weird stuff on them that's going to break. It doesn't have weird switches and dip switches and switches.

##### **Geohot** [[00:27:46](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1666)]
They have a lot of switches on that board, and they're all useless. When do we launch? Probably six weeks, maybe two months even.

##### **Geohot** [[00:28:03](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1683)]
Got to do mass production.

##### **Geohot** [[00:28:05](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1685)]
We're negotiating now for large chip quantities and stuff. We are going to have large chip quantities? Yeah.

##### **Geohot** [[00:28:15](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1695)]
We better sell a lot of these. How exciting is it that you'll get SQTT viz working on a Mac on an AMD GPU?

##### **Geohot** [[00:28:30](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1710)]
It's so beautiful. It's so beautiful. I guess my Claude will be excited. Anything else for drivers? No. I think this week we'll focus on the remote, finish that, hope that will work soon.

##### **Geohot** [[00:29:01](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1741)]
Yeah. Let's get the remote working with that. We have a tiny box in the Hong Kong office, and we're all going to be able to use it remotely. Will it work nicely if multiple people each use a GPU?

##### **Geohot** [[00:29:17](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1757)]
Yeah.

##### **Geohot** [[00:29:18](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1758)]
As long as everyone uses different GPUs. As long as they use different GPUs. Yeah, yeah, yeah. Can you claim when you open the socket which GPU you're going to use?

##### **Geohot** [[00:29:28](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1768)]
Yeah, you can do that. Oh no, I more mean: where are we putting the lock file? We're going to have to do a little bit of a test. Oh, it's the JIT 2.0. Who's doing that?

##### **Geohot** [[00:30:01](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1801)]
Yeah.

##### **Geohot** [[00:30:05](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1805)]
I can finish that.

##### **Geohot** [[00:30:21](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1821)]
Anyway, we can just discuss all that later.

##### **Chenyu** [[00:30:26](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1826)]
Next, do we have image equals to one?

##### **Chrism** [[00:30:29](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1829)]
Yeah. So, I merged this morning. I made DM policy fast.

##### **Geohot** [[00:30:43](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1843)]
Have we deleted IMAGE=2 yet?

##### **Chrism** [[00:30:46](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1846)]
No, I am working on a branch that has that. I don't have a PR open for it yet, but it should be doable. The compile speed is 30 seconds longer than IMAGE=1. Before it was 90 seconds longer, so that's good. So it's like two minutes for IMAGE=1 and two minutes and 30 seconds for IMAGE=2.

##### **Geohot** [[00:31:21](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1881)]
Probably fine.

##### **Chenyu** [[00:31:22](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1882)]
And also, for some reason, I just checked: OpenPilot is still pinned to a tinygrad version from more than a month ago. It seems like they stopped this weekly update dependency thingy, so you probably want to check with someone.

##### **Chrism** [[00:31:37](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1897)]
And see if there's a reason for that.

##### **Chenyu** [[00:31:39](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1899)]
Yeah.

##### **Geohot** [[00:31:40](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1900)]
Yeah. We also got to figure out why that pickle loading is slow.

##### **Chrism** [[00:31:43](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1903)]
Yeah.

##### **Geohot** [[00:31:44](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1904)]
Driver thing. We got to improve the driver.

##### **Wozeparrot** [[00:31:51](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1911)]
I heard why they paused the updates was because rangeify was slow.

##### **Geohot** [[00:31:58](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1918)]
Okay. Well, I will have to ask because I don't know.

##### **Chrism** [[00:32:02](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1922)]
I didn't hear anything about that.

##### **Geohot** [[00:32:03](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1923)]
But yeah, they have to define slow for us and then we'll make it that fast. If we get rid of assign hazards, there's no reason rangeify should be slow.

##### **Geohot** [[00:32:18](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1938)]
So, this whole step we can remove in rangeify if we move the calls instead of bufferize, but wrap each bufferize in a call.

##### **Chenyu** [[00:32:30](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1950)]
So, you need to get this from comma. Let them know that they also didn't update, so they didn't see the speedup. They should see the speedup before it slowed down.

##### **Geohot** [[00:32:43](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1963)]
Yeah. Do that. Okay. Anyway, I think that's...

##### **Chenyu** [[00:32:50](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1970)]
Go delete IMAGE=2.

##### **Chrism** [[00:32:52](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1972)]
Yeah. Yeah. It should be... It should clean up a lot of stuff. There's like... I was going through and like figuring out what we can remove now. And like there's like buffer spec has image in it right now and doesn't need it.

##### **Geohot** [[00:33:05](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1985)]
Yeah. All right. Okay. Anything else? I think that's it.

##### **Geohot** [[00:33:13](https://www.youtube.com/watch?v=BzXf5_42qU0&t=1993)]
Another thing we discussed last night was that there's kind of two steps in each kernel. There's the memory planning step and the codegen step, and we should separate them a little bit more. Image is clearly in the codegen step.

##### **Chrism** [[00:33:26](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2006)]
Yeah. Yeah. Yeah. That's the next step for this: moving a lot of it, specifically image creation, further later.

##### **Geohot** [[00:33:34](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2014)]
Pretty doable. Excited to see the red diff. Great. Okay, next is spec stuff.

##### **Geohot** [[00:33:47](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2027)]
Oh, yeah. I forgot. That's what I did this sprint. I made this spec. Oh, that's going to be last sprint.

##### **Geohot** [[00:33:53](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2033)]
Well, yeah.

##### **Geohot** [[00:33:54](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2034)]
But I worked on the spec. Did I really? Is the spec really that old?

##### **Geohot** [[00:33:57](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2037)]
Yes.

##### **Geohot** [[00:33:59](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2039)]
Wow. Time really does fly. How long have I been working on this spec for? Oh yeah, it was two weeks ago. I didn't make it that fast. All right. Well, I continued to update the spec. The spec is very beautiful. I think at first, when I first wrote the spec, I was like, man, this was like five years of work for this spec. But then you start making the spec longer, and you realize that even in its current five-page state it captures only like a quarter of tinygrad. And then you think about the whole thing being like a 20-page spec, and you realize most of Linux is a 20-page spec, though, if you just had a 20-page spec that defined, like, all right, here's syscalls, here's the file interface, here's the work. So yeah, and most recently I did a bunch of stuff in the beginning of the sprint on LM; we talked about that last week. This week I worked on call and tuple. I did that yesterday. So yeah, call can now return multiple values. All calls are dtype void, but if you want to return values from a call, you can have the body op be a tuple, and then you can put get-tuples on the call to extract parameters. You used to be able to just put a parameter on the call and it would pass it through, but if we ever want to support tuple, there's no reason to support both ways; just keep the extra UOps. So yeah, tuple allows calls to have multiple outputs. You can just put multiple inputs on the call, and that works. So now calls are fully multiple-input, multiple-output. I guess I also worked on AMD call matmul, which is just a cleanup of AMD UOP matmul. It's more refined. You realize that store is the only thing that kind of matters. Multiple times I put the spec into the LMs and said, okay, what's missing? And store, you need atomics too, not at the highest level, but there are some algorithms that are really hard to write without atomic add, like embedding backwards.

##### **Geohot** [[00:36:38](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2198)]
So yeah. Yeah.

##### **Geohot** [[00:36:45](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2205)]
Working on making sure that the function decorator works with `precompile`, `precompile_backwards`. I saw a PR where someone had the function decorator run the function with params instead of running the function with the actual graph. I'm supportive of this.

##### **Chenyu** [[00:37:01](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2221)]
That PR just explodes in terms of complexity. I think now it's really complicated.

##### **Geohot** [[00:37:06](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2226)]
Well, yeah, because they ran LLM on it and didn't think through the cases. But, you know, think through the cases. Haven't looked at the PR in a while, but the idea is basically there: you should be able to run the functions with placeholders, and it also works. So yeah, we have those. And then yeah, tuple will let us do fully structured things from functions too. So I added full structuring to the function input. So now there's an argument called `allow_implicit` for functions. It's true, but I'm going to make it false by default. Basically, if it's false, you can't have buffers that don't come through the inputs to the function. But this is more flexible than you think, because if you put the function decorator on a call method, self is there and it'll call get parameters on self and it'll go in and pull all the self stuff out. And you really want this for... I ran into this problem where if you go right to the buffer, you miss the reshape after the buffer. And missing the reshape after the buffer means that the gradient doesn't work well. But if you go and slice the graph right where the graph branches off from the params, then you get the expand and it puts the contiguous after the expand if you do `precompile`, and then it's bad too.

##### **Chenyu** [[00:38:25](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2305)]
So the issue we discussed yesterday was also that the params is the reshape of the buffer, but my view assign was acting on the buffer, not the reshape of the buffer.

##### **Geohot** [[00:38:38](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2318)]
I see.

##### **Chenyu** [[00:38:38](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2318)]
So I did.

##### **Geohot** [[00:38:43](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2323)]
How?

##### **Chenyu** [[00:38:45](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2325)]
So we have a step that's just a rewrite of the assign version with `after`. So instead of going to the buffer level and using that as your key, you just replace the reshape buffer directly.

##### **Geohot** [[00:39:03](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2343)]
So it's just if it's one reshape, but it's two reshapes.

##### **Chenyu** [[00:39:06](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2346)]
It's the first level that you will see the buffer entity.

##### **Geohot** [[00:39:10](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2350)]
I see. Okay. So that's another. We could, in theory, do that.

##### **Chenyu** [[00:39:14](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2354)]
So that's still not very fully thought through. We have a lot of these methods, like try to get the buffer entity or this list op. These just need to call the same method, so it's the same. But for now, it's better than the previous version.

##### **Geohot** [[00:39:33](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2373)]
So I changed that.

##### **Geohot** [[00:39:36](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2376)]
Okay.

##### **Geohot** [[00:39:38](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2378)]
Anything else?

##### **Geohot** [[00:39:40](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2380)]
Nope.

##### **Geohot** [[00:39:42](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2382)]
Yep. Okay, great. Next. That's my stuff.

##### **Chenyu** [[00:39:56](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2396)]
Yeah, I removed assign. If you look at `Tensor.assign`, it should be very clean now. I also removed a bunch of crap that I put in when I was doing a refactor because I didn't fully know what I was doing. So now assign is a combination of store and after. Store describes the effect of you store something. Then the after is the buffer; it's a new buffer or the new tensors that you pass downstream. So for example, store has dtype void and doesn't have a shape. After has all the properties that the buffer will do, so it can be an input to your downstream stuff. `UOp.assign` is removed because it doesn't make sense to start with; UOp is immutable, so assigning to it... you should always write as a store and after. Then there are still maybe a few places that I want to clean up better, because the way I replaced this is I created a version that replaced it with store-after, made sure it all works, and deleted the assign version. But I can see that in some places the after should just combine better with existing after stuff. But overall I think that works pretty nice. Claude technically wrote every piece of the change, but I also discarded like 99% of the thing and asked Claude to rewrite things again. I think it's very good that I can co-think with Claude, if that makes sense. It's not just Claude clarifying stuff, it's also me clarifying stuff, so that's kind of working.

##### **Geohot** [[00:41:53](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2513)]
This rejection sampling approach works pretty well. Most of the stuff I wrote recently was also the same rejection sampling. It's just you need to keep telling

##### **Chenyu** [[00:42:02](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2522)]
it to think from first principles again, because it starts in those cycles. Also, I don't know, Codex probably solved like two of the bugs that Claude just for some reason could not figure out. I don't know if it's like you need a fresh sub-agent that will fix it, or it's just not smart.

##### **Geohot** [[00:42:21](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2541)]
I often just run another OpenCode on the same thing and just tell it to do it, and it will do okay.

##### **Chenyu** [[00:42:30](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2550)]
I also started to try, because you can use worktrees, right? So I have like two agents and ask them to read each other's diff and criticize why they are doing it bad, and they would seem to work. Does this work? I haven't tried this. Yeah, so I run with like three worktrees because I also need the code that is clean, but that's kind of funny. I think a lot of this really is: if we have a clean spec and we have a way for Claude to understand the change, because you look at how Claude will debug an issue and it is very similar to how we debug stuff. At first you try the tools and you don't like the tools because the tool is not that helpful. Then you start to add prints everywhere because print is always reliable. Then you see the gaps for these tools and you think about how to make this tool, how to make our tooling better, because it will also help humans working on the

##### **Geohot** [[00:43:25](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2605)]
code better. I think that is kind of the direction viz needs to go in. We need to make viz that works well for agents because it is a bit different from what works well for humans. I never used the web version of viz. But yeah, how do you do this without... I'm in viz all the time. I see you in viz all the time. I don't know. I do assign. I think that's pretty good.

##### **Geohot** [[00:43:56](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2636)]
I guess, yeah, the assign thing, yeah. You did that without Viz?

##### **Chenyu** [[00:43:59](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2639)]
I never use viz. I don't understand it. No, I ask Claude to run `viz -1` and tell me what's happening.

##### **Geohot** [[00:44:09](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2649)]
Okay. All right. Good, good, good. You're using Agentic Viz. Yes. The Agentic Viz project.

##### **Chenyu** [[00:44:14](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2654)]
Yeah. So I think you just understand where something is not useful, because if you expect the tools to show the things you expect, maybe sometimes it's hard to see... okay.

##### **Chenyu** [[00:44:34](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2674)]
Okay. Anyway, I also did some improvement to div mod. I think, as we discussed last week, it's slightly faster and slightly cleaner, so probably we'll leave it there. I think there are more opportunities once image two is gone, because I see that for image one on Mac it's actually a lot faster and it finds much better simplification, probably just because it tries to search and not just use a fixed size like that.

##### **Geohot** [[00:45:07](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2707)]
So yeah, probably going to clean up more. I think `Tensor.assign` is very beautiful to look at.

##### **Geohot** [[00:45:18](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2718)]
I mean, yeah, I hope that I can put more detail into the spec for different things and it starts to clarify, and hopefully Claude can use that.

##### **Geohot** [[00:45:32](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2732)]
Yeah, probably. Because the...

##### **Chenyu** [[00:45:34](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2734)]
The biggest thing from the assign removal is you just need to tell it, because sometimes you want to replace that with after when it means the buffer to be read for downstream. Sometimes it means store, because in the buffer-to-store, or whichever you do things with store, it means that effect.

##### **Geohot** [[00:45:56](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2756)]
Did you keep the property that after's parameter zero is always a buffer?

##### **Geohot** [[00:46:02](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2762)]
Yeah. Okay. Great. So if it just roots that, then that's your thing to be read.

##### **Geohot** [[00:46:09](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2769)]
Yeah. I mean, I think there's a bunch of places where particularly around multi. Yes. Multi is still... There's a new... I have some new ideas that I've been working through for multi, but I think that maybe the way to do it will be to like really write the spec beforehand and then have Claude do the mechanical transformation. Like make sure the spec is...

##### **Chenyu** [[00:46:34](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2794)]
Yeah. I think some version of that definitely is helpful. I mean, assign is probably very hard if you just throw it at it, because that's what I tried initially, and after like three hours it's just everything garbage. The better way is... so the actual PR, I think I probably did like four PRs, is gradually from the leaf where you use assign and replace it with store-after, because that's gradual. So you don't need to add all the correct rangeify rules or all the correct indexing rules in the first go. I think that's probably very hard, but going backward, I did one with... the first one I don't remember. There were like two in the code, one in `Tensor.assign`, and one in reduce, so there was an order that doing this would be simpler. So sometimes that's why I don't think Claude can do your prime factor in one shot. But I mean, so far I'm pretty optimistic for the upper bound you can get from agentic coding. So this is not going away. Try to find ways to make your tools work better.

##### **Geohot** [[00:47:55](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2875)]
Yeah. Agentic Viz is the next...

##### **Geohot** [[00:48:02](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2882)]
Any thoughts on agentic Viz?

##### **Chenyu** [[00:48:09](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2889)]
I think just find a problem that you think is difficult. Another good thing with Claude is because it can write so much code, you can think more ambitiously and try to tackle more difficult problems. So just throw a problem at it, see how it struggles, then you will find the gaps in tooling.

##### **Geohot** [[00:48:33](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2913)]
Yeah. Yeah.

##### **Geohot** [[00:48:35](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2915)]
Yeah.

##### **Geohot** [[00:48:36](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2916)]
Yeah.

##### **Geohot** [[00:48:36](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2916)]
Yeah.

##### **Geohot** [[00:48:38](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2918)]
Any agentic Viz thoughts? I think that's a good thing to tackle.

##### **Qazalin** [[00:48:43](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2923)]
Agentic viz, I mean, it's whatever humans find useful.

##### **Geohot** [[00:48:48](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2928)]
How much do you have Claude run Viz?

##### **Geohot** [[00:48:56](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2936)]
For rewrites, a lot. You found that useful? Yes. I think we need...

##### **Geohot** [[00:49:10](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2950)]
We almost do need... I deleted the old `Claude.md` because I thought it was stupid. Oh, you have a `Claude.md`? Yeah. I think that we need some, because I never know what's expected to work. I asked you this week, is there a way to do SQTT from CLI? So what we need to do is recreate auto research,

##### **Geohot** [[00:49:39](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2979)]
but with tinygrad.

##### **Qazalin** [[00:49:48](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2988)]
I have to tell it to use this. It doesn't automatically do it.

##### **Geohot** [[00:49:54](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2994)]
Yeah, I thought it's because we deleted `Claude.md`. We used to have that in `Claude.md`.

##### **Qazalin** [[00:49:59](https://www.youtube.com/watch?v=BzXf5_42qU0&t=2999)]
Yeah, it used to, but `Claude.md` was kind of trash.

##### **Geohot** [[00:50:03](https://www.youtube.com/watch?v=BzXf5_42qU0&t=3003)]
`Claude.md` was bad. Yeah, we want a better `Claude.md`, and we want this to be a skill too.

##### **Chenyu** [[00:50:11](https://www.youtube.com/watch?v=BzXf5_42qU0&t=3011)]
I don't know what a skill is. A skill is just a predefined chunk, saying if you want to do this, load this.

##### **Geohot** [[00:50:17](https://www.youtube.com/watch?v=BzXf5_42qU0&t=3017)]
I think what we want is not a `Claude.md`. I think what we want is a better `extra/viz` README.

##### **Geohot** [[00:50:35](https://www.youtube.com/watch?v=BzXf5_42qU0&t=3035)]
There's already one, but they can make it better. Yeah.

##### **Geohot** [[00:50:40](https://www.youtube.com/watch?v=BzXf5_42qU0&t=3040)]
Yeah, yeah. And then you just tell... I think this can improve. This could be an MD. Make this README usable for humans, and it'll be good for agents too, and extend it to work on SQTT as well.

##### **Geohot** [[00:51:00](https://www.youtube.com/watch?v=BzXf5_42qU0&t=3060)]
Yeah.

##### **Qazalin** [[00:51:01](https://www.youtube.com/watch?v=BzXf5_42qU0&t=3061)]
I think I put a lot of effort into making the arguments nicely documented and everything just verified.

##### **Geohot** [[00:51:14](https://www.youtube.com/watch?v=BzXf5_42qU0&t=3074)]
The CLI itself.

##### **Geohot** [[00:51:19](https://www.youtube.com/watch?v=BzXf5_42qU0&t=3079)]
And actually, yeah, I think when this is done, we just move it out of extra. Just put it in `tinygradviz.py`. There's a terrible README in viz right now.

##### **Qazalin** [[00:51:31](https://www.youtube.com/watch?v=BzXf5_42qU0&t=3091)]
Oh, the nostalgic one? I see.

##### **Geohot** [[00:51:35](https://www.youtube.com/watch?v=BzXf5_42qU0&t=3095)]
Yeah. Yeah. Yeah. Nostalgia, huh? Yeah. But yeah, I think that that's the direction this goes.

##### **Qazalin** [[00:51:51](https://www.youtube.com/watch?v=BzXf5_42qU0&t=3111)]
I mean, the terminal is a UI, basically. I'm using the same stuff that viz web uses to its thing.

##### **Geohot** [[00:52:00](https://www.youtube.com/watch?v=BzXf5_42qU0&t=3120)]
Yeah.

##### **Qazalin** [[00:52:01](https://www.youtube.com/watch?v=BzXf5_42qU0&t=3121)]
Just...

##### **Geohot** [[00:52:03](https://www.youtube.com/watch?v=BzXf5_42qU0&t=3123)]
Skills. Yeah. I think that the skills can double as a README. In general, I don't like any of these agent-y words, like skills and `Claude.md`s and stuff. I think all we want is `tinygradviz.readme.md`, and that's it.

##### **Chenyu** [[00:52:21](https://www.youtube.com/watch?v=BzXf5_42qU0&t=3141)]
Sometimes I put my dinner recipe into `Claude.md`. It works pretty well.

##### **Geohot** [[00:52:25](https://www.youtube.com/watch?v=BzXf5_42qU0&t=3145)]
Dinner recipe? Did it cook? No.

##### **Chenyu** [[00:52:29](https://www.youtube.com/watch?v=BzXf5_42qU0&t=3149)]
I just control Claude by inserting random text I write into `Claude.md` and making sure.

##### **Geohot** [[00:52:37](https://www.youtube.com/watch?v=BzXf5_42qU0&t=3157)]
Yeah.

##### **Geohot** [[00:52:39](https://www.youtube.com/watch?v=BzXf5_42qU0&t=3159)]
We should try this. I was drawing on the board, and Chenyu was like, "George, you think in viz diagrams now."

##### **Geohot** [[00:52:50](https://www.youtube.com/watch?v=BzXf5_42qU0&t=3170)]
These are the things.

##### **Geohot** [[00:52:54](https://www.youtube.com/watch?v=BzXf5_42qU0&t=3174)]
Yeah. Yeah. No, we definitely got to delete this old viz README. I think just move the CLI out of extra whenever you think it's good. And then point to auto research.

##### **Chenyu** [[00:53:09](https://www.youtube.com/watch?v=BzXf5_42qU0&t=3189)]
Yeah, because I think a few things that we are doing pretty well... one is having a good enough test suite. So it's very important to think through all the cases. When I was doing the first version of setitem correction, I just had Codex generating test cases that it thought would break, and it's kind of a fuzz, but very good, because it fuzzes the frontend, fuzzes the usage, and compares the correctness with, I forgot, NumPy or something. And I select a few that I like that are short and useful to the test case. And later when I do the refactor, once it passes all the weird cases, I'm pretty confident that it's correct.

##### **Geohot** [[00:54:04](https://www.youtube.com/watch?v=BzXf5_42qU0&t=3244)]
Another good factor is less lines or less tokens.

##### **Chenyu** [[00:54:09](https://www.youtube.com/watch?v=BzXf5_42qU0&t=3249)]
If you ask Claude to write things with negative lines, it'll try much harder to refactor. So this is not very different from how a human works on this. I just find it pretty useful. You just need to keep yelling at it.

##### **Geohot** [[00:54:30](https://www.youtube.com/watch?v=BzXf5_42qU0&t=3270)]
Yeah. Cool.

##### **Geohot** [[00:54:36](https://www.youtube.com/watch?v=BzXf5_42qU0&t=3276)]
Anything else?

##### **Chenyu** [[00:54:38](https://www.youtube.com/watch?v=BzXf5_42qU0&t=3278)]
Oh, I just banned this random guy because I closed two of his random issues the other day, and all his issues are in some other repos claiming some bad usage.

##### **Geohot** [[00:54:54](https://www.youtube.com/watch?v=BzXf5_42qU0&t=3294)]
Yeah.

##### **Geohot** [[00:54:56](https://www.youtube.com/watch?v=BzXf5_42qU0&t=3296)]
Oh, I didn't read.

##### **Geohot** [[00:54:59](https://www.youtube.com/watch?v=BzXf5_42qU0&t=3299)]
That's good.

##### **Geohot** [[00:55:09](https://www.youtube.com/watch?v=BzXf5_42qU0&t=3309)]
I think that's a setting with the model that you probably know better. I trust that it's right, but what does it even... oh, `norm_top_k_prob`. I see, renormalize the top-k. Yeah. I don't know. I just trust this is right. It's fine. You don't do it.

##### **Geohot** [[00:55:38](https://www.youtube.com/watch?v=BzXf5_42qU0&t=3338)]
It seems straightforward.

##### **Geohot** [[00:55:52](https://www.youtube.com/watch?v=BzXf5_42qU0&t=3352)]
Yeah, no, I mean, Qwen 3.5. Oh, we have it? Yeah. This is great.

##### **Geohot** [[00:56:01](https://www.youtube.com/watch?v=BzXf5_42qU0&t=3361)]
This is great. This is great. I always want to pay him bounties. I don't think I ever paid him for the other bounty. This is amazing. We have Qwen 3.5.

##### **Geohot** [[00:56:16](https://www.youtube.com/watch?v=BzXf5_42qU0&t=3376)]
You're really nasty. I'll see where we can blast. Yeah. I think there should be two different

##### **Geohot** [[00:56:38](https://www.youtube.com/watch?v=BzXf5_42qU0&t=3398)]
classes. It's clean, but... Also, these new models

##### **Chenyu** [[00:56:43](https://www.youtube.com/watch?v=BzXf5_42qU0&t=3403)]
will make slightly different. A very slight difference.

##### **Geohot** [[00:56:49](https://www.youtube.com/watch?v=BzXf5_42qU0&t=3409)]
Different class.

##### **Chenyu** [[00:56:52](https://www.youtube.com/watch?v=BzXf5_42qU0&t=3412)]
Okay, anyway, I'll leave that to you. You can merge it. I don't think we have other open issues or PR threads. Please close your old stuff. Now we have like five pages again; that's a lot of PRs. I will leave the comma communication to Chris so that they update the version. We probably want to do a release sometime this month.

##### **Geohot** [[00:57:19](https://www.youtube.com/watch?v=BzXf5_42qU0&t=3439)]
I think we do that once we have the GPU... GPU and Qwen 3.5. If we have a Qwen 3.5 that's getting 80% of the memory bandwidth on the GPU, that's incredible.

##### **Geohot** [[00:57:34](https://www.youtube.com/watch?v=BzXf5_42qU0&t=3454)]
That's actually very usable for people. We got to improve our MOE stuff. We could write a custom sort. We should try it. We should try it.

##### **Chenyu** [[00:57:55](https://www.youtube.com/watch?v=BzXf5_42qU0&t=3475)]
Another thing I find pretty useful was debug for source code. When I do div mod, I just basically have it print the kernels and read every piece of div mod and say, do you think this can be simplified? Let's give it a try, and we'll find interesting stuff that you probably were too lazy for, because previously you needed to type; now you just ask someone to do a job. Okay, cool. I think that's it for this week. Thank you everyone. Bye-bye. See you next week. Bye.
