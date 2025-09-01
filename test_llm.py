a = """
# 2025-08-25 Meeting

### Meeting Agenda

**Time:** 9am Monday San Diego time
- company updates
- rangeify opt
- bfloat16 alu stuff
- mlperf llama
- viz tool
- drivers
- symbolic
- cloud
- onnx
- other bounties

### Audio

[Youtube Link](https://www.youtube.com/watch?v=KA0h9zmJtcs)

### Highlights

### Transcript
##### **Geohot** [[00:00:00](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=0)]
Welcome to our weekly Monday meeting. Let's get started with company update. Okay, a whole bunch of marketing for the tiny box. Sent an email out.

##### **Chenyu** [[00:00:14](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=14)]
You asked me to do the Twitter thread?

##### **Geohot** [[00:00:17](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=17)]
I did Twitter threads, I did everything. No, I did emails, I did LinkedIn. You know, we went hard on the marketing, so we'll see if that pays off. Uh, yeah, they're getting built now too, so that's good. Got the factories really up and working now.

##### **Geohot** [[00:00:44](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=44)]
Um, yeah, that's all we got. Great. Yeah, we can move more bucks. Hopefully. Hopefully. I hope the marketing works. It did drive a lot of traffic to the website.

##### **Chenyu** [[00:01:07](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=67)]
Uh, conversion rate matters.

##### **Geohot** [[00:01:10](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=70)]
Yeah, well, the conversion rate's been zero so far since yesterday. You know, I don't think it's an impulse purchase.

##### **Chenyu** [[00:01:17](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=77)]
People don't make big spending decisions on Sunday.

##### **Geohot** [[00:01:21](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=81)]
Yeah, yeah, yeah, yeah, yeah. But this week, they're going to be like, oh yes, a tiny box, oh, I want one of those.

##### **Geohot** [[00:01:29](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=89)]
Great. Okay. Okay. That's good. Let's start with Rengify up.

##### **Geohot** [[00:01:39](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=99)]
Yeah, so what I'm working on, what I worked on this weekend, what I'll work on this week is first we have to move the kernel.py to after the lower. I call it post-opt. That should be completely doable. So I've already cleaned up a bunch of things. I added access types to the ranges. So it's pretty, like, decentralized now. And, like, with access types in the ranges, what I can do is, like, I can write a rule for group for reduce. That when it sees a group for reduce in a range, it splits the range and then has one of them be a local and one of them be a loop. So they can all be done really nicely in this, like, decentralized re-art rule manner, except for TensorFlow course. But I have something that works for TensorFlow course. It's just, uh, TensorFlow course are fundamentally annoying because you have to change the loads.

##### **Geohot** [[00:02:40](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=160)]
Like, TensorFlow course are non-local. But it's not too bad. So, yeah. What's the white color in your latest post? The whites are just loops. Yeah. Oh, OK.

##### **Geohot** [[00:02:59](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=179)]
Yeah, so whites are loops. If you look at the red, white, and blue flash attention, the white ones are loops that are not doing reduction.

##### **Geohot** [[00:03:09](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=189)]
OK. So, yeah. That works.

##### **Chenyu** [[00:03:14](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=194)]
That's correct. The first... By the way, I was reading this. Is there a reason why every reduced axis is, like, from the largest to the smallest? What do you mean the largest? The smallest. So the first one is RDX 10. The next is RDX 8. Oh, yeah.

##### **Geohot** [[00:03:34](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=214)]
Well, because it builds its bottom up, right?

##### **Geohot** [[00:03:39](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=219)]
OK. I mean, I kind of understand.

##### **Chenyu** [[00:03:43](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=223)]
It just reads weird.

##### **Geohot** [[00:03:45](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=225)]
Yeah. I mean, we can renumber the ranges to be whatever, or at least label them to be whatever. But it's because the rangeify is done bottom up. So you first assign the stores are 0 through, you know, whatever the length of the store is. And then as we encounter reduce ops moving up the graph, we give them a range. And that's why the one at the top is, like, 10. Yeah.

##### **Chenyu** [[00:04:12](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=252)]
Some reason why GIDX is reversed.

##### **Geohot** [[00:04:15](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=255)]
Last weekend, I spent some time trying to do top-down rangeify.

##### **Geohot** [[00:04:21](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=261)]
But this doesn't work. I mean, I think it's just a matter of time before we get to the bottom. Halite is bottom up.

##### **Chenyu** [[00:04:27](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=267)]
Does it still contain the children and sometimes can be wrong class?

##### **Geohot** [[00:04:36](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=276)]
The top-down one does not need children, no.

##### **Geohot** [[00:04:41](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=281)]
No, by the bottom up, right? It's never wrong. Is it wrong?

##### **Chenyu** [[00:04:49](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=289)]
Oh, I thought you were... Before you mentioned it. I thought you were saying that because it's bottom up, now some caches can be wrong.

##### **Geohot** [[00:04:57](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=297)]
I fixed that. So, yeah, I fixed that. I finally got the children thing working properly. You just need... So it adds two UOPs. It adds one called children and two called child. And then you just have to wait to pass through children until you've seen both child.

##### **Geohot** [[00:05:17](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=317)]
It should never be wrong.

##### **Geohot** [[00:05:20](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=320)]
But the other thing that I'm really excited about... Is the Vmap stuff. So it's really easy, like in the Rangeify world, to create ranges on the overworld. And then they just pretty much work as you'd expect. And this should be a ton more flexible. So it copies Jack's Vmap exactly. But it should be a ton more flexible. Because every tensor can have a different... Like, most of the differences between a lot of the tiny grid stuff... And the Jack stuff is... Jack's operates on a function. Like, when you compute a gradient in Jack's, you don't give it a tensor. You give it a function. So Jack's Vmap is the same thing. You don't give it a tensor. You don't say, like, where the tensor is Vmapped. You just say, here's a function. And then you have to give it a map of axes. But then you can't chain Vmap things. Like, in tiny grid, you should be able to... It should be, like... It should be really easy to do all the layers of an LLM with a couple things. You just need to slice into your weights with your layer index. And then you can just call whatever you want. Call scale... Call attention. Call gem. So... Yeah, I think that that's... When that's subsidized to work, it's going to be great. Yeah. So my plan is, first, post-opt. Which should work with all the existing stuff. So, like, the problem with... You can't do optimizations at the kernel.py layer with rangeify. Because you have ranges. So you have to do optimizations after ranges. But we could do all the normal optimizations after ranges. So that's step one. And then, yeah.

##### **Geohot** [[00:07:07](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=427)]
Then ranges have optimizations. Great. I like it.

##### **Chenyu** [[00:07:12](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=432)]
Are you going to rewrite multi with this later?

##### **Geohot** [[00:07:16](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=436)]
Yeah. Yeah, I think so. I've been thinking about this. So I already have the color picked out. I want it to be, like, a really nice... Like, aquamarine. You know, think of it. Because there shouldn't be anything special about multi, right? If you want something to run on the 6 GPUs, you should just have, like, a 6 in the shape.

##### **Chenyu** [[00:07:36](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=456)]
Yep, yep, yep.

##### **Geohot** [[00:07:39](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=459)]
Yeah, so we'll get there. I think I'm also going to remove... I mean, it's already kind of been done. But I'm going to remove the restriction on axes being in a certain order. Like, upcasts being in a certain place. Locals being in a certain place. We should be able to just put them... Next to the axes that created them.

##### **Geohot** [[00:08:04](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=484)]
Sure.

##### **Chenyu** [[00:08:05](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=485)]
I mean, that sounds much better than what we have now.

##### **Geohot** [[00:08:09](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=489)]
Yeah. I mean, it keeps them in order, right? Like, there's... I started looking at all the opt-ops. And, like, every opt-op is basically just... Except for swap. Is doing some form of...

##### **Geohot** [[00:08:22](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=502)]
Like...

##### **Chenyu** [[00:08:24](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=504)]
Pull some number and create a new axis. And put those numbers in that axis.

##### **Geohot** [[00:08:31](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=511)]
Yeah. But you can... So, the axis comes from an existing axis. So, you can just pull off the existing axis. If you're doing bottom, it'll just go to the right. If you're doing top, it'll go to the left. And then, like, your things will stay in order, mostly.

##### **Chenyu** [[00:08:44](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=524)]
Wait, you want to do to the left?

##### **Geohot** [[00:08:47](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=527)]
If you do top, yeah.

##### **Chenyu** [[00:08:49](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=529)]
Then it's hard to... Under... Understand if one is coming from the one before or one after.

##### **Geohot** [[00:08:57](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=537)]
Well, yeah. I mean, you'll never know.

##### **Chenyu** [[00:08:59](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=539)]
It's not like we can represent it.

##### **Geohot** [[00:09:02](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=542)]
I don't know.

##### **Chenyu** [[00:09:03](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=543)]
Maybe that's why.

##### **Geohot** [[00:09:04](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=544)]
It's still... Like, it keeps things entirely in order. As they get broken down.

##### **Sieds Lykles** [[00:09:09](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=549)]
Yeah.

##### **Geohot** [[00:09:10](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=550)]
I mean, that's an easy change. But... It's just... Yeah, as I've been looking at it, I kind of like that. Oh, I realized, like... Yeah, yeah. So. Post-opt. This week. Then we can delete kernel.py. Well. Okay, almost. I still have kernel.py. I separated generating the optimizations from applying the optimizations.

##### **Geohot** [[00:09:34](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=574)]
Okay.

##### **Geohot** [[00:09:35](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=575)]
But, uh... Yeah. We've got applying the optimizations to go after. I have to write simplify merge adjacent in the new world. There's progress. That's going. And we're going to have beautiful Vmap stuff. Make it all work out. Multi is going to be a Vmap.

##### **Geohot** [[00:09:57](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=597)]
And... And... Okay. Cool, cool. Sounds good.

##### **Chenyu** [[00:10:10](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=610)]
Next is... So, I started to look into all the Vflow 16 supports that we have. And I found a bunch of issues. With those... I created, like, issues for these. But mostly because we decompose the X into X2 and a constant. If we do the whole thing in Vflow 16, that constant would be represented in Vflow 16. The whole thing would end up having a pretty big diff because X is exponentially big. So, for example, if we do this. So, for now, I only fix X. For now, I want the way to write this better. We should at least also fix cosine, which we now currently decompose with sine and the I over 2 shift. And another one is log. I think these three in Vflow 16, we should be, like, no different from Torch.

##### **Geohot** [[00:11:22](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=682)]
Yeah, I saw the pull request for this where the guy wanted to add X. But obviously, this isn't the solution. But so the solution was just to keep precision on the Vflow const?

##### **Chenyu** [[00:11:33](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=693)]
Yeah, so for now, for X, the middle thing is converted into Vflow 32. So, like, your constants in Vflow 32, I think, last little closest.

##### **Geohot** [[00:11:44](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=704)]
Makes sense. Yeah, it's slightly...

##### **Chenyu** [[00:11:49](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=709)]
I don't know. I feel some of these small D type things. I think we also need to prepare ourselves for FP8 anyway. I really want to get these two, like, work together without too many Vflow 16 hack. Another issue is cast. So now, we currently, when we cast into Vflow 16, we don't round correctly. So if you have, like, residual in your mentis, then it's not. Rounded correctly that I can fix. This week, eventually, I want to get Python backend for Vflow 16 support to work. Because for now, there are a lot of diff, which is really bad for, like, const folding or other pre-computed stuff on Python. Because we use Python backend for that. And if the value is slightly a little bit off, it's very annoying to debug. So... That's the goal. And after that, I really want to get FP8. There are so many different ways to get FP8.

##### **Geohot** [[00:12:59](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=779)]
For the small D type stuff. So I was playing with that tiny box. I installed VLLM and I was running GPT-OSS. It's all, like, GPT-OSS was getting 150 tokens per second. Which isn't bad, but you can do 10x better.

##### **Chenyu** [[00:13:21](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=801)]
Oh, 10x better how?

##### **Geohot** [[00:13:23](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=803)]
So GPT-OSS 120 is 5.1 billion parameters per token.

##### **Geohot** [[00:13:31](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=811)]
And the parameters are, like, 4 or 5 bits. So if we could get the 4-bit D type working.

##### **Geohot** [[00:13:41](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=821)]
You only have to read, like, 3 gigabytes of stuff. Which, 2000 tokens per second, like, in theory, should be possible.

##### **Geohot** [[00:13:55](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=835)]
That's the goal. Oh, each 1590 is 1.5? 2. What, 2?

##### **Geohot** [[00:14:01](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=841)]
It's more than 2 actually. The advertised is 1.8, but you actually get 2.3. Great. Yeah.

##### **Chenyu** [[00:14:12](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=852)]
I mean, then you don't even really need that, right? You should be able to hit 500 just by storing these in B4.0. 16, then I wonder why that's not the case.

##### **Geohot** [[00:14:25](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=865)]
Yeah. Well, I wasn't hitting 500. I don't know what the. And I have the driver. I have the P2P driver installed. OK, anyway.

##### **Geohot** [[00:14:34](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=874)]
Maybe it's only for something. I don't know.

##### **Geohot** [[00:14:39](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=879)]
I was definitely using all the GPUs. You need it to fit, though. You need the RAM.

##### **Chenyu** [[00:14:42](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=882)]
I don't know. Maybe it's somewhere it copies everything to the first run or something. I don't know. I don't know. Yeah, I don't know. So anyway, our current small D type support, especially when things are not representable by memory view, is pretty poor and you don't want to fix that. Because we might need FP8 eventually.

##### **Geohot** [[00:15:06](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=906)]
Yeah.

##### **Qazalin** [[00:15:08](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=908)]
Cool.

##### **Chenyu** [[00:15:10](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=910)]
So that's Bflow16. For LLAMA, has been helping running some runs.

##### **Wozeparrot** [[00:15:21](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=921)]
So let's see if we can get some of these things to work. So we're here. So I merged eval last week. I'm up here open for small. My long small run crashed with an MMU fault.

##### **Chenyu** [[00:15:35](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=935)]
Yes. All right. So this might be a separate issue. I also had some MMU fault issue. And I think Hulu also mentioned some MMU fault issue. But I think specifically for LLAMA45B, the problems we have, is it seems more and more likely that the benchmark is just and we can hit that 5.6 something log

##### **Geohot** [[00:16:02](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=962)]
perplexity, which is pretty annoying. So my thinking is

##### **Chenyu** [[00:16:09](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=969)]
Is this for 8B or 405 that is bad? I mean, the problem is we are trending towards a benchmark. And if we say this benchmark is bad, can be hit by a much, much smaller model in a much, much faster time than what really is this benchmark doing.

##### **Geohot** [[00:16:28](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=988)]
Sure. So you're saying you're saying that 405B is broken. The one that people submitted for last time. It's just it's just like too easy and hyper parameters are real bad.

##### **Chenyu** [[00:16:38](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=998)]
I mean, it's totally legit. If what they want to measure is how fast you can run. You can trend like this many steps. That's fine. I then don't use don't check RCP because RCP here is a joke. It's like measures nothing. I just want to get this clarified. Because previously our model has been converging slightly worse than RCP. And we are finding this.

##### **Geohot** [[00:17:04](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1024)]
What's RCP?

##### **Chenyu** [[00:17:07](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1027)]
The reference conversions point. So basically how fast your model converges. And for MLPerf, there is a strict rule. You cannot converge faster than reference. This is assuming the reference is doing the best.

##### **Geohot** [[00:17:30](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1050)]
I mean, that makes sense. You don't want people tweaking stuff.

##### **Chenyu** [[00:17:33](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1053)]
So I mean, our main concern is first, we want to make sure we are not doing something obviously wrong. It might be a bug in our code or something. But we also want to make sure we are measuring or at least get this accurate. So we can just acknowledge that, okay, this is a not so good benchmark. And this number is arbitrary because there's no point to train the model to this number. Kind of.

##### **Geohot** [[00:18:00](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1080)]
Have we tried our test procedure on real llama?

##### **Geohot** [[00:18:06](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1086)]
What do you mean by that? Like, have we used like the real llama weights and tried our test procedure? Oh.

##### **Chenyu** [[00:18:19](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1099)]
So there's no real llama weight because for this benchmark, it's llama. But we can do that now.

##### **Geohot** [[00:18:27](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1107)]
Yeah, I understand the tokenizer.

##### **Geohot** [[00:18:30](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1110)]
I understand the tokenizer is different, but we should do it.

##### **Wozeparrot** [[00:18:35](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1115)]
We can run full llama because the small LLM retrain task uses the same tokenizer.

##### **Qazalin** [[00:18:42](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1122)]
Okay.

##### **Chenyu** [[00:18:43](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1123)]
So we should be able to eval the already trained llama on the eval so that we can make sure the eval script is correct, at least for that.

##### **Geohot** [[00:18:57](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1137)]
I mean, yeah. That number should be published. We should look at the eval and see if it's right. Yeah.

##### **Geohot** [[00:19:05](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1145)]
Is that number published?

##### **Chenyu** [[00:19:08](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1148)]
It should be the same to whatever the number is. I don't know.

##### **Wozeparrot** [[00:19:13](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1153)]
We just assume it's around what the target is? Yeah.

##### **Chenyu** [[00:19:18](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1158)]
So we should at least be close to a reasonable number and not like 10 or higher because now we have bigger . Okay. So we'll do that. Then we will see where we are training HB. Maybe we need to hit AB.

##### **Geohot** [[00:19:43](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1183)]
And we will figure out all MMU faults separately. All right. NimbleJet, any ideas on that? Not really. I haven't looked into that.

##### **Nimlgen** [[00:19:58](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1198)]
But it might be a broken kernel. I think it's that because it's AMD driver, not even AM.

##### **Geohot** [[00:20:10](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1210)]
Got it. So you think the kernel is actually accessing memory out of bounds? I think, yeah.

##### **Nimlgen** [[00:20:17](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1217)]
Because actually, Hooved got a DRAM beam. So I think in his case, it's definitely the bad kernel.

##### **Geohot** [[00:20:28](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1228)]
We got to detect that and save the kernel. And then run SuperZ3 on that.

##### **Chenyu** [[00:20:38](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1238)]
Well, I think general domain. So I think the best directions on LLama and using the MI machine is we have now multiple jobs or training tasks running on it. So we should be able to discover these things better. Then we'll see where we are after we do the eval and training the small LLama AB.

##### **Geohot** [[00:21:07](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1267)]
Oh, and thanks to B1TG.

##### **Chenyu** [[00:21:09](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1269)]
He fixed the . I think we're going to have to do a little bit more of the AMD LLVM compiling issue on LLama. So now we can . Oh, George, you commented about reverting LLVM default to false or something?

##### **Geohot** [[00:21:25](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1285)]
Yeah. I mean, I don't know. Like, which one are we using?

##### **Geohot** [[00:21:28](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1288)]
We use LLVM now. Oh, great. Then city fall. OK.

##### **Chenyu** [[00:21:34](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1294)]
Yeah, I think LLVM is. We eventually want to move that.

##### **Geohot** [[00:21:39](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1299)]
I don't know. I like setting the other one just so I can read debug equals four. But if we're using LLVM, then let's keep it.

##### **Geohot** [[00:21:46](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1306)]
I can't read LLVM.

##### **Qazalin** [[00:21:47](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1307)]
Is it fine on 350?

##### **Geohot** [[00:21:52](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1312)]
Is LLVM fine on 350? Yeah, I don't know. I haven't tried. I don't know.

##### **Wozeparrot** [[00:22:03](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1323)]
I haven't been using LLVM on 350.

##### **Geohot** [[00:22:05](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1325)]
Maybe I'll try.

##### **Chenyu** [[00:22:06](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1326)]
On 300, it runs fine. If we want it on 350, we can. Yeah. If we want it to work, maybe add B1TG to 350, then it will work. I don't know.

##### **Geohot** [[00:22:16](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1336)]
We can definitely add B1TG to 350, but cool.

##### **Qazalin** [[00:22:20](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1340)]
Yeah.

##### **Chenyu** [[00:22:20](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1340)]
OK. So one direction, the driver thing, another direction. There we are. And with that, we can move on to this.

##### **Qazalin** [[00:22:35](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1355)]
I'm here to bikepack here. So we were at 160 bytes per second. We had three events last week. Now we're at 27. Are you happy with that? Yeah, we're kind of going. We're running a little more. It does a little bit of a spec. I'm sharing it with you. Check. Like what the response format is. I moved all the layouts up to the client side. So it just finishes all the raw data. And now I'm moving on to actually fixing the UI and making that the format. So we've got this default canvas, and we've broken it up onto this example here. Double click on it to put it back, and we need a new helper to that dumb. instruction. single kernel use case.

##### **Geohot** [[00:23:27](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1407)]
How does Perfetto deal with the events are small problem?

##### **Qazalin** [[00:23:32](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1412)]
You zoom and rectangles appear magically.

##### **Geohot** [[00:23:36](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1416)]
In Perfetto? Yeah. Does Perfetto do this well or not? I don't like the behavior that

##### **Qazalin** [[00:23:50](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1430)]
it's blank at a high zoom and then when you zoom it shows up.

##### **Geohot** [[00:23:56](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1436)]
Well, it definitely shouldn't have that. Probably what you want to do is set a minimum width on stuff.

##### **Nimlgen** [[00:24:05](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1445)]
Yeah, I did this in my

##### **Sieds Lykles** [[00:24:06](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1446)]
patch set.

##### **Qazalin** [[00:24:08](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1448)]
The width gets smaller when you zoom in. Which is also odd.

##### **Nimlgen** [[00:24:12](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1452)]
I mean, I added this in my patch set so you can just try to merge the kernels. But if the width is really small, you just... Yeah.

##### **Sieds Lykles** [[00:24:24](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1464)]
Cap it.

##### **Nimlgen** [[00:24:28](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1468)]
At least something is visible. Maybe it's not the real width of these kernels, but at least you know that there is something there.

##### **Geohot** [[00:24:37](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1477)]
I mean, to be fair, it should never get smaller as you zoom in. It can only ever get bigger. It just might not get bigger at exactly the right rate. But I think that's okay. Yeah, I would set a minimum width to

##### **Geohot** [[00:24:51](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1491)]
a couple pixels or something. Yeah, like it is. It's kind of... I'm playing with Beautiful Emnist right now and you can kind of... It's hard to see where there are kernels.

##### **Sieds Lykles** [[00:25:14](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1514)]
But yeah, no, I think...

##### **Geohot** [[00:25:18](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1518)]
I think some of it's the color too.

##### **Qazalin** [[00:25:22](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1522)]
I don't know.

##### **Geohot** [[00:25:23](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1523)]
I think it's... That line was probably... I don't know.

##### **Geohot** [[00:25:26](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1526)]
I don't know. I think a minimum width fixes this. Yeah, I mean, I'm scrolling around Beautiful Emnist. It feels extremely performant. But I think Beautiful Emnist was always pretty performant. I don't know. I haven't tried any of the big ones.

##### **Geohot** [[00:25:42](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1542)]
Yeah.

##### **Qazalin** [[00:25:43](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1543)]
Smaller ones.

##### **Geohot** [[00:25:46](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1546)]
What's the big one people were asking about? Kekak? I don't think it even works. Kekak work or no? No. Hmm. Why not?

##### **Qazalin** [[00:26:08](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1568)]
It takes a couple seconds to actually run. I think. Or schedule it.

##### **Geohot** [[00:26:14](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1574)]
I mean, I'm running this external test Kekak and it's very slow.

##### **Qazalin** [[00:26:19](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1579)]
The Lama choice in total is like 25 million events.

##### **Geohot** [[00:26:24](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1584)]
Okay.

##### **Qazalin** [[00:26:26](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1586)]
Most of them are copies. Like half of it is just popping stuff. There's probably another plus we can't drop.

##### **Geohot** [[00:26:38](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1598)]
I mean, I ran Kekak and the profile is very performant.

##### **Chenyu** [[00:26:44](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1604)]
I think because you skipped the very slow one.

##### **Geohot** [[00:26:48](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1608)]
Oh, I skipped the very slow one. Okay. You mean, but you're getting it being slow on the profile or being slow? Because it is really slow on... If I click merge views, the thing is like hung.

##### **Geohot** [[00:26:58](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1618)]
If I click like one of the scheduling events, it like hangs. I don't. It shouldn't hang.

##### **Qazalin** [[00:27:07](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1627)]
It should just not show anything.

##### **Geohot** [[00:27:11](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1631)]
It pretty much hangs.

##### **Qazalin** [[00:27:14](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1634)]
It locks up?

##### **Geohot** [[00:27:17](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1637)]
Yeah. Whenever I click a graph that's too big, I've always just had to exit the page and load the page.

##### **Geohot** [[00:27:24](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1644)]
again. That's a JavaScript problem. Well, a JavaScript problem. I mean, what do you mean by it's a JavaScript problem? Like you can always you can always use threads, right?

##### **Qazalin** [[00:27:43](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1663)]
You can use a library to do the layout.

##### **Geohot** [[00:27:49](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1669)]
Yeah, but can we put that layout in a web worker?

##### **Qazalin** [[00:27:53](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1673)]
Oh, it's already there.

##### **Geohot** [[00:27:55](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1675)]
Oh, then why does it hang?

##### **Qazalin** [[00:27:58](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1678)]
The library uses a max function that has a limit of number of arguments. And when you pass too many arguments, it hangs.

##### **Geohot** [[00:28:10](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1690)]
It hangs the main draw process?

##### **Qazalin** [[00:28:14](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1694)]
No. It hangs the layout worker. And then it should exit.

##### **Geohot** [[00:28:20](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1700)]
Okay, yeah. I mean, it can hang the layout worker. But you can can you still terminate the layout worker from the draw thread?

##### **Qazalin** [[00:28:27](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1707)]
That shouldn't happen. If it doesn't happen, that's...

##### **Geohot** [[00:28:30](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1710)]
I mean, yeah, so I ran I ran test unit test hashing and the profiler is extremely performant. I mean, merge views is... Like I would like this to be better. So if I click something, if I click like something that's really slow, it comes up with rendering new graph. And then I click away from that.

##### **Geohot** [[00:28:55](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1735)]
And oh, actually, it seems okay.

##### **Geohot** [[00:29:01](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1741)]
Sometimes I feel also that like, I eventually get a callback like way later that pulls me to that graph even once I've clicked off of it.

##### **Geohot** [[00:29:13](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1753)]
Yeah, that's really hard to reproduce.

##### **Qazalin** [[00:29:16](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1756)]
Okay, try so many times.

##### **Geohot** [[00:29:19](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1759)]
Yeah, I think I've complained about this before. But I call so what's the direction this week?

##### **Qazalin** [[00:29:25](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1765)]
The profiler isn't responsive in large. Got it. It doesn't scale to 25 million events. Got something like the emergence original PR should fix just merge the rectangles with a cap on them. Yeah.

##### **Geohot** [[00:29:43](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1783)]
Great.

##### **Qazalin** [[00:29:44](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1784)]
Also moving the packed stuff to the other you up. Yeah, I think that's a good idea. Yeah, I think that's a good idea.

##### **Geohot** [[00:29:50](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1790)]
Yeah, I think that's a good idea. the long

##### **Qazalin** [[00:29:58](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1798)]
trace right now. It's one it's about 200 bytes per rewrite event. Thank you.

##### **Geohot** [[00:30:09](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1809)]
But there are too many rewrites and kernels.

##### **Qazalin** [[00:30:21](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1821)]
500 million viz represents 25 million for file viz.

##### **Geohot** [[00:30:24](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1824)]
We shouldn't prematurely optimize anything, right? Because it is a lot easier to just... If JSON's good enough, we should leave it as JSON. It's only like, yeah, I mean, once you have 25 million profiler events, sure, that's just never going to work in JSON. But for the rewrites, if it's fast enough, I don't think we should change it. I think we should, with all of these viz improvements, we should have a very clear, like, here's a real workflow, that I want to improve. And yeah, if you're saying right now that if you have, like, Lama, and it has 25 million, and the profiler is non-responsive, okay, cool. That's like a loop. We know what we have to make faster. But just saying, like, oh, well, you know, it'd be nicer if the rewrite event sent less stuff. Is this a problem?

##### **Geohot** [[00:31:11](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1871)]
Maybe not.

##### **Qazalin** [[00:31:12](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1872)]
Two gigabytes of memory usage within the bounds of Chrome.

##### **Geohot** [[00:31:19](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1879)]
I mean, it seems... I've never seen a problem with the transfer being the bottleneck. I usually see the layout be a bottleneck.

##### **Qazalin** [[00:31:30](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1890)]
Maybe... Just the strong that stuff also takes memory from what you could spend on layout caching. So I was thinking of giving myself some space to maybe have a better layout. More of this. This is just like ideas.

##### **Geohot** [[00:31:51](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1911)]
How are you going to make the layout better?

##### **Qazalin** [[00:31:53](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1913)]
I don't know. Cache stuff?

##### **Geohot** [[00:31:56](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1916)]
Cache stuff? What do you want to cache?

##### **Qazalin** [[00:32:03](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1923)]
So right now, the layout is completely in memory. So you just calculate it once. And then you reach where the canvas will run over, as you saw.

##### **Geohot** [[00:32:18](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1938)]
Uh... Okay. How would you change this? What would it be instead?

##### **Qazalin** [[00:32:24](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1944)]
It would be exactly the same. I just don't want it out of memory when that happens.

##### **Geohot** [[00:32:31](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1951)]
Oh, I see what you're saying. Okay, you're saying that, like, you're spending a lot of memory on rewrite rules. Um... Yeah. I understand. Uh... Yeah, no, I wouldn't... I wouldn't... I wouldn't... I've never seen a problem with this. Like, we should really be focused on... on an exact use case and an exact problem. I think one of the things to revisit that I've always wanted with Viz is a better visualization of what the rewrite rule is doing. So, like, right now we have... in that, uh, rightmost panel, we have the, like, the red and the green on the UOP. I've never seen that be useful.

##### **Geohot** [[00:33:15](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=1995)]
Like this. What do you mean? What's very useful? Oh, you've used this? I read this.

##### **Geohot** [[00:33:28](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2008)]
Yes. Oh, I find it unreadable.

##### **Chenyu** [[00:33:31](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2011)]
I don't know. So, I think the less useful part is the code because the code never changed.

##### **Geohot** [[00:33:37](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2017)]
Code is good. I like the code. Yeah, but it never changed. Oh, the code never changes. Yeah. Um... I mean, we have this, like...

##### **Chenyu** [[00:33:50](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2030)]
I mean, I read this. Maybe it's just because lack of better tools for this kind of stuff. Because usually, for my use case, I want to see how one op might disappear from the big UOP.

##### **Geohot** [[00:34:08](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2048)]
The other thing that I'd really like is if I click on a UOP, could it add... labels to each edge to say which input it's going to?

##### **Geohot** [[00:34:28](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2068)]
Like the paths?

##### **Qazalin** [[00:34:30](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2070)]
I like the...

##### **Chenyu** [[00:34:31](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2071)]
Well, so, like, I have a problem. Some annotation to the edge, especially when your edge becomes very big, some of it might intersect or go, like, under another block or another rectangle.

##### **Geohot** [[00:34:47](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2087)]
I'm just talking about, you know, you could have that. I mean, that'd be cool too if it lit up the parents. But I more mean, like a lot of times, like, especially for, like, a UOP, like, where. It's very important to know which argument is the... which is the third, which is the second and which is the third.

##### **Geohot** [[00:35:04](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2104)]
It's, like, hard to know that from the graph. I mean, let's continue.

##### **Chenyu** [[00:35:17](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2117)]
this feature request in the Viz channel.

##### **Geohot** [[00:35:21](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2121)]
All right, cool. But yeah, I think we should always... I think it's good to continue to optimize the profiler so it works for Lama, but then I think we should stop optimizing unless we have a clear use case where this doesn't work right now, this is a reasonable thing people want, and this approach will make it better.

##### **Geohot** [[00:35:40](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2140)]
Make sense?

##### **Qazalin** [[00:35:46](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2146)]
Cool.

##### **Geohot** [[00:35:46](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2146)]
Cool, okay. Next is drivers. Yeah, so marriage check here this week.

##### **Nimlgen** [[00:35:59](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2159)]
So the Lama runs fine now, the My300. So it's about 100 tokens with BMICOS4. It used to be about 25 or so. So... So yeah. So yeah, this week I'll focus on the CPU threading. So I hope that Viz timeline will emerge pretty soon

##### **Geohot** [[00:36:27](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2187)]
because I'll need it.

##### **Qazalin** [[00:36:32](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2192)]
Cool.

##### **Geohot** [[00:36:40](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2200)]
Do we know why the H machine keeps crashing? Can we do anything about that? Yeah. So basically that's like the only problem with H machine.

##### **Nimlgen** [[00:36:58](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2218)]
It's V and B. And I mean, I can reproduce the issue, like then the GPU doesn't return after several resets. And that's pretty reproducible.

##### **Geohot** [[00:37:13](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2233)]
Well, I remember you said that it was trying to load the NVIDIA. So I'm not sure if it's the NVIDIA driver. Did we blacklist it?

##### **Nimlgen** [[00:37:18](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2238)]
Yeah, I mean, I did.

##### **Geohot** [[00:37:21](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2241)]
Okay, then why is it still causing... Why does it still have issues?

##### **Nimlgen** [[00:37:25](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2245)]
Yeah, I mean, it's still... I don't know for what reason, but it's still doing the resets. Like in the Damask, you can see that it just did the FLR reset on the GPU. Maybe that's our driver, but I still don't understand. Maybe why it's not terminating fine.

##### **Geohot** [[00:37:49](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2269)]
Well, I mean, we really need to get this to the point that it can be in any state. There has to be a way to reset this GPU. Like there can't be a way that like if we control C the process wrong, that it... If we like kill minus nine the process, that the GPU just doesn't come back.

##### **Nimlgen** [[00:38:12](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2292)]
Yeah. I mean, yeah, that's totally strange. But... I see this problem only with 5090s and the Blackwell and Hopper. But yeah, okay, I'll investigate this. But actually, that's the only way how I see to reset the GPU is like to do the function level reset. There is... I mean, that driver does nothing.

##### **Geohot** [[00:38:40](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2320)]
Well, I mean, there's a few different types of resets you can do. You can actually like do a hard... The PCI bus can do a reset.

##### **Nimlgen** [[00:38:50](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2330)]
Yeah, the other one is the bus reset. Does a bus reset get it back or no? I'll test it. But actually, I've seen on the internet people complaining that bus reset had the same problem as FLR. Yeah, I can test that.

##### **Geohot** [[00:39:09](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2349)]
Yeah, I mean, we got to find some way that no matter what we do to the GPU, we can get it back. Right? Like we can't rely on the process with the GPU in it being cleanly exited.

##### **Geohot** [[00:39:24](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2364)]
Yeah, okay, I'll play with this.

##### **Geohot** [[00:39:28](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2368)]
Cool. And then the AQL stuff's all merged?

##### **Nimlgen** [[00:39:34](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2374)]
Yeah, it's merged. It's still on the flag, but they are all merged. It will be default for any GPU with several XCCs.

##### **Geohot** [[00:39:42](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2382)]
Great. Yeah, yeah, good. I see your PR to retire, the old sync stuff. Great. I never want to deal with the old sync stuff again. We just got to use AQL for those things. I don't know. I've tried complaining to AMD about AQL, but they're not going to change it.

##### **Geohot** [[00:39:58](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2398)]
Is there any reason why it's not default on?

##### **Nimlgen** [[00:40:07](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2407)]
Yeah, because I think the queue time on PIM4 can be better. Because there is no indirect pocket to execute AQL comments from the indirect buffer. And because of that, we should just copy all the packets every time to the queue. Because of that, the queue time is larger. Not much on MI300.

##### **Geohot** [[00:40:37](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2437)]
Well, those CPUs are extremely fast. Yeah. I want to start moving more and more stuff to... Like, I want to use basically the CPU backend to build these packets.

##### **Nimlgen** [[00:40:51](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2451)]
Yeah.

##### **Geohot** [[00:40:54](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2454)]
Like, we should move away from Python. We should basically use a tiny grad function to do the update, and then JIT that tiny grad function.

##### **Geohot** [[00:41:03](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2463)]
Then that should be really fast. Yeah, that's probably a solution.

##### **Nimlgen** [[00:41:10](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2470)]
I mean, I don't know. I can benchmark AQL and queue times on BERT or other benchmarks we have right now. And if it's not too bad, maybe we can get rid of the PIM4 exec. But we still need a lot of PIM4 stuff because that's just QTT and syncing.

##### **Geohot** [[00:41:33](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2493)]
So you're talking about getting rid of it for all AMD GPUs?

##### **Nimlgen** [[00:41:36](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2496)]
Yeah. So if the numbers are good and we don't see... Any huge performance issues, I think, yeah, we can just leave AQL as the default type and remove the PIM4 queue creation at all.

##### **Geohot** [[00:41:54](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2514)]
Yeah. If it saves code, let's go with BATHs. Sounds good. Sounds good.

##### **Chenyu** [[00:42:02](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2522)]
Yeah. I was planning to benchmark BERT and see if the training time is faster. But if you are interested to do that and see if we can use that for default, that's better.

##### **Geohot** [[00:42:17](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2537)]
I mean, I do like PIM4 more because you can read the... You can read the... Like, I don't know. Maybe we should... You can read the Mac firmware for PIM4 and it shows you what it's doing on the GPU. You read the Mac firmware for AQL and it's a nightmare.

##### **Chenyu** [[00:42:33](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2553)]
Yeah. So this is less about getting rid of PIM4, but just we want the default to be the default. So the BATH one we recommend people to use.

##### **Geohot** [[00:42:43](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2563)]
That's a good point. Sounds good. Okay. Next is symbolic.

##### **Sieds Lykles** [[00:42:53](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2573)]
Yeah. So I've been working mostly on some rules for nested divs and when you want to nest a div and when you want to unnest it. And I have a lot of PRs for it. I haven't got it exactly how I want it, but I think it's one of the remaining things that's missing from symbolic for divs at least.

##### **Geohot** [[00:43:24](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2604)]
And...

##### **Chenyu** [[00:43:28](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2608)]
Do you have an example to show things that should be simplified but not simplified from this?

##### **Sieds Lykles** [[00:43:36](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2616)]
Yeah, sure. I'll post something.

##### **Qazalin** [[00:43:39](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2619)]
Okay.

##### **Sieds Lykles** [[00:43:39](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2619)]
So I'll post something. So I'll post something. I mean, there's a rule currently that does that sometimes nests a div, but it doesn't always choose the best factor to nest it by. And ideally you want, well, ideally you don't want any nesting because it means you do two divs instead of one. But then there's some stuff with like, well, I don't know, it made when I unnested it made Winograd or Max slower.

##### **Geohot** [[00:44:23](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2663)]
Yeah. So that... And that, I mean, it will. Yeah. Yeah.

##### **Chenyu** [[00:44:31](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2671)]
So I think usually these things, you can start it by like editing. Yeah. And then you can start it by like, oh, I just did examples that is currently not simplified into a test. Then mark it as a to-do or like expected value or. So... Yeah. It's a lot easier for other people to understand like what's not done and what can be made better.

##### **Sieds Lykles** [[00:44:54](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2694)]
Yeah. I'll add some to-do's, some examples.

##### **Chenyu** [[00:45:01](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2701)]
I mean, it's pretty nice that you are cleaning up these like divs and mods stuff. Yeah.

##### **Sieds Lykles** [[00:45:10](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2710)]
I think I have an overview now of all the rules that are missing. Like I had some branch where I was doing the, I don't know, I was just printing a lot of UOPs that should simplify to the same thing. You can see the difference. And then like... I was getting pretty close to them always being the same.

##### **Geohot** [[00:45:42](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2742)]
Yeah.

##### **Chenyu** [[00:45:43](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2743)]
And I think another thing to just keep in mind is to some of these you can benchmark and some of these rules or edge cases can be, can make the code itself pretty complex. So if you feel that's going to be the case, then sometimes it needs your judgment code to say, okay, this is... I'm just getting too complicated. Maybe it's not worth it.

##### **Geohot** [[00:46:12](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2772)]
Yeah.

##### **Chenyu** [[00:46:13](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2773)]
That's kind of what happened before to do some of a valid simplification. There are some to-do's that's in a test that's not simplified, but the solution to simplify loads is pretty complicated and I didn't find that like worse.

##### **Sieds Lykles** [[00:46:32](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2792)]
Yeah. The complexity.

##### **Qazalin** [[00:46:36](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2796)]
Cool. Yeah.

##### **Chenyu** [[00:46:38](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2798)]
Sounds good. Wasp Barrier, do you have anything about Uvn's Cloud stuff? Do we have a script that we can run Bert out to?

##### **Wozeparrot** [[00:46:49](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2809)]
I'm trying to run it again because I kept hitting this Nan thing that somehow he's not hitting. I don't know. The last few times I ran it, I always hit it like about two hours into the run. So I'm trying to run it again. Do we know what the expected step time is? I read.

##### **Chenyu** [[00:47:07](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2827)]
I don't know. You really need to run that on one machine and wait 30 minutes and you will find out.

##### **Geohot** [[00:47:16](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2836)]
Okay. Currently we're at like 800 milliseconds a step.

##### **Wozeparrot** [[00:47:27](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2847)]
I feel like that's slow.

##### **Sieds Lykles** [[00:47:31](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2851)]
I don't know.

##### **Geohot** [[00:47:34](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2854)]
Okay.

##### **Chenyu** [[00:47:35](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2855)]
So other than having a script or a method that people can run on two machines, are there any to-dos in that direction?

##### **Wozeparrot** [[00:47:50](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2870)]
It's mostly good, just speed and whether or not we want the kernel driver.

##### **Geohot** [[00:47:57](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2877)]
We don't want the kernel driver. Which I think is no. Yeah. We don't want the kernel driver. I'm fine with requiring AMD and not AM. That's fine.

##### **Qazalin** [[00:48:05](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2885)]
Yeah.

##### **Geohot** [[00:48:07](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2887)]
Until we can. I mean, the kernel driver is never a solution. The solution is going to be to write our own driver for the network card.

##### **Wozeparrot** [[00:48:18](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2898)]
Supposedly it's a lot faster with the kernel driver because of some NUMA node behavior. I'm not sure how good that is.

##### **Chenyu** [[00:48:30](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2910)]
Yeah, that's starting by having a script. Yeah, I'm starting with a script. So that we can reproduce the multi-machine trend and see what the next should be.

##### **Geohot** [[00:48:41](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2921)]
It's also the NAND thing. I mean, I don't want to harp on the NAND thing if this turns out to be just like... Didn't we used to just have this problem in AMD in general? Yes.

##### **Chenyu** [[00:48:53](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2933)]
And I think that was caused by some driver issue. At least it was fixed by some driver change. Huh. So, I mean, I mean. If we can successfully train BERT on one machine, say for a few times, then it failed on the two machine setup, then more likely there's some problem with the two machine setup.

##### **Geohot** [[00:49:20](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2960)]
That seems reasonable. Yeah. Let's run BERT on one machine. That'll give us both the timing and the NAND issue. And if it works a bunch of times on one machine and doesn't work on two machines, then it's a multi-issue. If it's flaky on one machine, then it's a multi-issue. If it's flaky on two machines, and it's also flaky on two machines, but it sometimes works, then good enough.

##### **Qazalin** [[00:49:39](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2979)]
Okay.

##### **Geohot** [[00:49:40](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=2980)]
Cool. Sounds good. Okay. Waiting for a nut on X. We want two target speedup. HMMMMMMMMMMMMM. Oh, definitely just jitted plus optimize equals 2. Optimize equals true. None of those.

##### **Chenyu** [[00:50:06](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=3006)]
yeah there's one flag for prune and there's another flag for optimize and they sometimes are good I know

##### **Qazalin** [[00:50:19](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=3019)]
so

##### **Geohot** [[00:50:19](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=3019)]
I think optimize you might be able to always do prune has a bunch of foot guns

##### **Geohot** [[00:50:26](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=3026)]
yeah so I would think the onX

##### **Chenyu** [[00:50:36](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=3036)]
cleanup follows so few things one is if you can simplify or rewrite the implementation itself so that it's it's faster if you use like a lot less ops or things like that that's definitely good then for the model speed this is slightly tricky because none of the open pilot model use bin because bin is very slow on device so it really is the speed of the default heuristic optimization so there I would say if the change is in principle like simpler and we expect that to be faster then that's probably good otherwise you really need to look into one specific script and say okay condition on this setting is a faster or not and to that we really only care about the open pilot models

##### **Geohot** [[00:51:39](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=3099)]
did we fix the bug in the open pilot model can we run all the open pilot models now we run all

##### **Geohot** [[00:51:47](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=3107)]
I think if it's

##### **Geohot** [[00:51:49](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=3109)]
not merged yet but this is top priority making sure that we can run all the open pilot models

##### **Chenyu** [[00:51:55](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=3115)]
yeah but we also agree that that thing is slightly weird so so that that model export has an if that has a true branching

##### **Geohot** [[00:52:08](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=3128)]
that you cannot represent with with why not

##### **Chenyu** [[00:52:14](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=3134)]
because your output has different shape and it follows different paths does different stuff then merge back

##### **Geohot** [[00:52:23](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=3143)]
your output has a different shape that's allowed

##### **Chenyu** [[00:52:26](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=3146)]
yes so in onyx the if op is running a different subgraph

##### **Geohot** [[00:52:33](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=3153)]
no I'm aware that it's real control flow but I'm still shocked that a different shape is allowed a different shape is allowed that's right yeah that's what that

##### **Chenyu** [[00:52:41](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=3161)]
oh so that's the problem with that model I don't really know

##### **Geohot** [[00:52:47](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=3167)]
I think that one we just need to write a good error message for and complain to the user and be like uh I don't know why you exported it like this

##### **Chenyu** [[00:52:55](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=3175)]
yeah so I think that's that's reasonable maybe we just do that for now I think the if if all tests looks fine so if it can be represented with where we support it if no then we write a error message saying so

##### **Geohot** [[00:53:15](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=3195)]
let's start from there

##### **Sieds Lykles** [[00:53:17](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=3197)]
yeah sounds good

##### **Geohot** [[00:53:25](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=3205)]
Bertrand Koudel under bounte's so let's start with I think that PR looks fine. I looked at it briefly. I was a little confused by it. But if you think it's good, then cool.

##### **Chenyu** [[00:54:11](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=3251)]
I mean, the idea is we don't allow using reshape to register symbolic.

##### **Geohot** [[00:54:21](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=3261)]
And a bunch of tests needs to be updated.

##### **Geohot** [[00:54:27](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=3267)]
Yeah. I mean, I see this symbolic reshape might lead to out of bounds as a value error. I think we should just ban symbolic reshape. I don't understand why symbolic reshape is ever allowed.

##### **Geohot** [[00:54:40](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=3280)]
Yeah. I think that's the goal for that change.

##### **Geohot** [[00:54:44](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=3284)]
Cool. Oh, shrink prod shape to support empty. OK, that's cool. Yeah, I like that.

##### **Chenyu** [[00:54:55](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=3295)]
Yeah. Since you are in the middle, I think a general comment I would have for writing error message or writing a new comment is think about it from a fresh perspective, not conditional on the old behavior. Because if you write something that only makes sense for the reader who understand the old behavior, that comment or error message. It will be less relevant in the future. So if something's not allowed, just say this is not allowed, not some old behavior.

##### **Geohot** [[00:55:33](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=3333)]
So I'm looking here at this change from test symbolic mean 2D axis 1. This is changing several things. This is changing one of these things has a different range now. It's from 2 to 10 instead of 1 to 10. It's changing the shape of the things. I really want nothing to change except using this new thing. This new format. I'll post the one specifically that I'm talking about. There's way too many changes to this test, it seems.

##### **Geohot** [[00:56:15](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=3375)]
Why is a 1 changing to a 2? Yeah, I don't understand this. And . I think it's because they shouldn't reshape to symbolic.

##### **Geohot** [[00:56:32](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=3392)]
Well, the reshape there is fine. But yeah, I don't understand why it's not just like, you keep the size the same and then you do VV2, VV like that. I think this has to be way more carefully done with like, if you want to make any. I think there's some of these changes that are just exact refactors, and those should be merged in one PR. And then if you want to make any changes to any range of any variable, that's got to be in a separate PR and discussed.

##### **Geohot** [[00:57:09](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=3429)]
Anyway, I will review that after it passes all the tests

##### **Chenyu** [[00:57:12](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=3432)]
and complain about the test. Cool.

##### **Geohot** [[00:57:16](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=3436)]
Yeah, no, yeah, I see. I see a whole bunch of changes like that where like this syntax should totally work. You should be able to double slice and not like multiply and contiguous. Yeah.

##### **Geohot** [[00:57:27](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=3447)]
That's true. First, it's got to pass the tests. Anything else?

##### **Geohot** [[00:57:40](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=3460)]
Oh, oh, oh, oh, I think for the reduce access to be keep dims, B1TG, I think we're not going to merge that. But you did the work. I'll pay you out the bounty for that. Because in range of file, it kind of doesn't matter. In range of file, it's just kind of free. There was some like deep bug and beam. But instead of tracking this down, you've been doing a lot of work on the area of stuff. So I'll just pay you out. I'll pay you out the reduce bounty 250.

##### **Sieds Lykles** [[00:58:19](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=3499)]
OK.

##### **Qazalin** [[00:58:25](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=3505)]
Cool.

##### **Geohot** [[00:58:26](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=3506)]
And we'll also get B1TG access to the 350x we can see about LVM.

##### **Qazalin** [[00:58:34](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=3514)]
Cool.

##### **Geohot** [[00:58:38](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=3518)]
Vata, you want to say something?

##### **Wozeparrot** [[00:58:41](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=3521)]
Not so much. Just still working on the eval script. Just pretty much cleaning up the code now and doing that correctness check. It's just taking me a little bit longer, but it should be on its way.

##### **Qazalin** [[00:58:52](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=3532)]
OK.

##### **Geohot** [[00:58:54](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=3534)]
Ready?

##### **Qazalin** [[00:58:57](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=3537)]
OK. Great.

##### **Chenyu** [[00:58:59](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=3539)]
All right, we need to say. Say something. Was lag No.

##### **Geohot** [[00:59:12](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=3552)]
Cal道

##### **Geohot** [[00:59:14](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=3554)]
I forget. A lot of the subtlety involves, you want store to no longer have DTYPE void. You want store to pass through the pointer to the original buffer that it's storing.

##### **Chenyu** [[00:59:37](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=3577)]
Can you comment on one of the PRs? And figure this out?

##### **Geohot** [[00:59:44](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=3584)]
Yeah, I didn't realize the word PR should be made a review on that. I'll do that today.

##### **Geohot** [[00:59:49](https://www.youtube.com/watch?v=KA0h9zmJtcs&t=3589)]
Okay. Anything else? Okay, looks like there's nothing else. Cool. Thank you, everyone. That's the meeting for this week. See you next week. Thank you. Bye. Bye.


"""

highlights_prompt = """
Please provide for me a markdown of highlights of this transcript in the format of

```md
- **[Company Update](#geohot-000004)**: Tiny box V2 green with four 5090s is available for order, shipping in May, priced at $25,000; orders processed based on wire transfer receipt.
```

be extra careful when getting the timestamps #geohot-000004, The timestamps must align with actual transcript timestamps.
"""
from llm.llm_client import LLMClient
llm_client = LLMClient()

print(llm_client.get_llm_highlights(a, highlights_prompt))