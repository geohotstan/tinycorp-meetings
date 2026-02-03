# 2025-10-06 Meeting

### Meeting Agenda

**Time:** 6am Monday San Diego time, 9pm Hong Kong time
- company update
- symbolic stuff
- rangeify, remaining bugs (cat in openpilot)
- speed and cleanup
- pipelining
- other bounties

### Audio

[Youtube Link](https://www.youtube.com/watch?v=-boFPBPcUK8)

### Highlights

- **[Symbolic Improvements](#sieds-lykles-000006)**: Added ad chain sorting, eliminated distinction between symbolic flat and symbolic, improved UOp-Given-Valid and UOp-Blood-Factor methods for expression factoring and substitution, targeting ResonateConf range simplification.
- **[Rangeify Progress](#chenyu-000147)**: Nearing default merge; remaining issues include a contiguous cat bug in OpenPilot models and performance regressions, particularly in Stable Diffusion and OpenPilot scheduling times.
- **[Performance Bottlenecks](#chenyu-000324)**: Z3 checks disabled due to slowness; focus on eliminating float indexing and improving UOp-Given-Valid efficiency in large graphs.
- **[OpenPilot Speed Regression](#chenyu-000624)**: Two models slowed by 3ms each due to large reduce kernels; exploring optimizations like Nemoji's reduce fusion improvements.
- **[Pipelining & Rewrite Optimizations](#chenyu-000852)**: George working on pipelining for faster gens/full attention; new recursive property approach fixes stack overflow and improves rewrite speed in TinyGrad.
- **[Multi-GPU Fixes](#chenyu-001205)**: Resolved correctness issues with N-stacks; benchmarks show slow but correct execution, with ongoing tuning for memory and scheduling speed.
- **[FP8 Tensor Core Development](#b1tg-001339)**: FP8 tensor core functional but slower than FP16; priority on correctness before speed optimizations, aligning with pipelining efforts.
- **[AMD FP8 Training Bounty](#chenyu-001439)**: New bounty for FP8 BERT training on AMD MI300/MI350; complexity noted beyond FP8 support, requiring collaboration.
- **[Eval Backend Review](#flata-001549)**: Nowour backend ready for review; eval performance improved but multi-GPU mass select issues remain; targeting future submission cycles.
- **[Rangeify Merge Timeline](#chenyu-001939)**: Aiming to merge Rangeify as default this week after correctness fixes, despite temporary performance setbacks requiring cleanup.

### Transcript
##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=-boFPBPcUK8&t=0)]
Maybe Cid, so you can start with the symbolic stuff.

##### **Sieds Lykles** [[00:00:06](https://www.youtube.com/watch?v=-boFPBPcUK8&t=6)]
Alright, so good morning. Yeah, so the big symbolic update is that we have ad chain sorting now, finally. And also we can get rid of the distinction between symbolic flat and symbolic. And yeah, I made some improvements to UOp-Given-Valid and to a method called UOp-Blood-Factor, which allows you to factor out multiples of an expression, and then you can substitute them. So that works well. That was all necessary for the Resonate on stuff, which is still not fixed. I know how to fix it. It just made CI quite a bit slower, so it was very close to timing out. So we just have to figure out how to make it a little bit faster. But that's for the range of ResonateConf. That was not simplifying on some reshapes.

##### **Chenyu** [[00:01:24](https://www.youtube.com/watch?v=-boFPBPcUK8&t=84)]
And some of the reshapes had to use UOp-Given-Valid. But yeah, doing that on every..

##### **Sieds Lykles** [[00:01:39](https://www.youtube.com/watch?v=-boFPBPcUK8&t=99)]
In rangeify on the big graph was just slow, but it doesn't need to happen.

##### **Chenyu** [[00:01:47](https://www.youtube.com/watch?v=-boFPBPcUK8&t=107)]
Yeah, I think as part of the rangeify thing, there are two things that we noticed. One is.. Invalid can be slow. I think there's a comment somewhere around it. The benchmark now spends lots of time on the invalid stuff. That's one. Another is we currently disable the Z3 check by default because it's very slow. It can get very slow. I think some of it might just be like some expression that's bad or the kernel is getting too big now. So we need to disable that. For speed for now. But I mean, looking forward to get this back.

##### **Sieds Lykles** [[00:02:30](https://www.youtube.com/watch?v=-boFPBPcUK8&t=150)]
Yeah, I mean, the Z3 also had the float stuff. It needs to be fixed. And that, yeah, I mean, that's just.. I think we just banned pretty much all floats in indexing.

##### **Chenyu** [[00:02:45](https://www.youtube.com/watch?v=-boFPBPcUK8&t=165)]
We shouldn't have any real use case for floating indexing.

##### **Sieds Lykles** [[00:02:53](https://www.youtube.com/watch?v=-boFPBPcUK8&t=173)]
Yeah, I don't think so. I mean, this stuff should just be expressed with ints somehow and like remainders. And yeah, it's not easy. But yeah. Yeah, I mean, I'll work on that this week. Get that back.

##### **Chenyu** [[00:03:11](https://www.youtube.com/watch?v=-boFPBPcUK8&t=191)]
Sounds good. Yeah, we are.. We'll probably get rangeify as default, like Spanish. We will talk about that more. But definitely sometime this week.

##### **Sieds Lykles** [[00:03:29](https://www.youtube.com/watch?v=-boFPBPcUK8&t=209)]
Cool. Yeah. Anything else? No, not really. See you in Hong Kong. Yep. Looking forward to seeing you later. Safe trip. Okay. So we still don't have George.

##### **Chenyu** [[00:03:51](https://www.youtube.com/watch?v=-boFPBPcUK8&t=231)]
I can talk about what's remaining to merge rangeify equals to one default. So I think in terms of a correctness, the only thing that's left is the weird contiguous in cat thing that's triggered in one of the open pilot model and the fast fit model.

##### **Flata** [[00:04:20](https://www.youtube.com/watch?v=-boFPBPcUK8&t=260)]
Okay.

##### **Chenyu** [[00:04:22](https://www.youtube.com/watch?v=-boFPBPcUK8&t=262)]
So you can see the discussion in schedule. It looks like there's a was incorrectly split ACC. So it's like counted twice. And basically that's the reason why it is incorrect. So if it's this one, I think we will fix it soon. Probably tomorrow. Oh, it's slightly sketchy. We probably want to better fuzz this. So we would like to at least run the script that we have like in check the like hunger, like a random on X model. I think that'll be useful as a like high level. Was to make sure everything is correct. Then I think everything else, it's a speed issue. So for now in my PR a one, two, three, seven, four. I can X every assert step time because otherwise some of it just cannot make it and I cannot see the output. I'm pretty sure not every one of these is needed so I can like remove some of it. But see far and stable diffusion can get like three X score and you can see stable diffusion itself scheduling is like 10 minutes, like seven minutes already. So I think that's the main bottleneck we need to fix before like merging this. Another thing is open pilot has two models and each one got three milliseconds slower. And half of last three millisecond is because it has a very big reduce, reduce kernel. I saw Nemoji has something that tried to maybe try a better here. So I think it's a good idea to take something like that. You want to talk about it?

##### **Nimlgen** [[00:06:24](https://www.youtube.com/watch?v=-boFPBPcUK8&t=384)]
Yeah. So basically that was for, let's see for, because so, so yeah, actually range if I fusion a lot better and because of that, we can have several reduces chained and sometimes we need to realize them or wise it's a lot compute inside one kernel. Yeah. I know I haven't talked about this. I've tested it on open pilot.

##### **Chenyu** [[00:06:53](https://www.youtube.com/watch?v=-boFPBPcUK8&t=413)]
So I don't know if it's fixed anything there. Sounds good. Realistically the true blocker is open pilot speed.

##### **Chenyu** [[00:07:12](https://www.youtube.com/watch?v=-boFPBPcUK8&t=432)]
Everything else we can always improve. We merge it. I think, I think the bar to make it default is shouldn't be absurdly slow and we kind of need to understand like, is it something wrong or it's just slow because the way we may trade off now.

##### **Chenyu** [[00:07:41](https://www.youtube.com/watch?v=-boFPBPcUK8&t=461)]
Yeah. What else? Cause I think one, do you want to share something?

##### **Flata** [[00:07:59](https://www.youtube.com/watch?v=-boFPBPcUK8&t=479)]
Yeah.

##### **Chenyu** [[00:08:05](https://www.youtube.com/watch?v=-boFPBPcUK8&t=485)]
Yeah. Yeah.

##### **Flata** [[00:08:14](https://www.youtube.com/watch?v=-boFPBPcUK8&t=494)]
Well.

##### **Chenyu** [[00:08:16](https://www.youtube.com/watch?v=-boFPBPcUK8&t=496)]
Yeah, I want to tell, so, the same thing before and what else.

##### **Flata** [[00:08:20](https://www.youtube.com/watch?v=-boFPBPcUK8&t=500)]
Absolutely.

##### **Chenyu** [[00:08:24](https://www.youtube.com/watch?v=-boFPBPcUK8&t=504)]
Right.

##### **Flata** [[00:08:28](https://www.youtube.com/watch?v=-boFPBPcUK8&t=508)]
Not like nature to me.

##### **Chenyu** [[00:08:51](https://www.youtube.com/watch?v=-boFPBPcUK8&t=531)]
I don't know.

##### **Chenyu** [[00:08:52](https://www.youtube.com/watch?v=-boFPBPcUK8&t=532)]
So George is working on adding pipelining and I guess in general making gens and full attention fast. That would be his main thing and also improving the rewriting algorithm or the rewriting speed itself. Now TinyGrad is pretty slow. Slow because like a lot of rewrite steps. So there are rewrites for index, rewrites for rangeify, rewrites for big graph, all the recursive thing, recursive property. Well that's a new thing he added. Supposedly makes everything faster and fixed one of the old issue that. Because it recurs too much, it surpasses the Python stack limits. Replacement was more like.. So instead of going like stack, go into the stack, it just tried to paint the whole top of the sort with that property so that the next time it's something like that. Anyway. Supposedly it's faster. And it fixed the stack overflow issue.

##### **Chenyu** [[00:10:29](https://www.youtube.com/watch?v=-boFPBPcUK8&t=629)]
Stack recursion too deep issue. Okay. And now our backend is ready for review. Okay. So we'll figure out that one probably tomorrow. Figure out like who is going to review that. Okay.

##### **Chenyu** [[00:11:11](https://www.youtube.com/watch?v=-boFPBPcUK8&t=671)]
Qazalin or Wozeparrot. You have anything else to add? Other parts that you were working on?

##### **Qazalin** [[00:11:19](https://www.youtube.com/watch?v=-boFPBPcUK8&t=679)]
Not really. I think we're good. I think I fixed all the multis though. If there's any other bugs. Everything in multi is fixed? I mean, did the benchmarks pass? So there was an issue with rank? Yeah. Yeah. We now have, I think two out of seven benchmark path. Just by this like. Yeah. Very slow. You mean like it's slow, but it's in anything that's incorrect right now? I haven't seen anyone.

##### **Chenyu** [[00:12:05](https://www.youtube.com/watch?v=-boFPBPcUK8&t=725)]
Which one?

##### **Qazalin** [[00:12:07](https://www.youtube.com/watch?v=-boFPBPcUK8&t=727)]
I haven't seen anyone that's incorrect or doesn't compile. Yeah. Yeah. So far it seems to be correct. So looks good. There were correctness issues with how we were doing. We're dealing with N-stacks. It should be fixed now. Great. Yeah. It looks like.

##### **Chenyu** [[00:12:33](https://www.youtube.com/watch?v=-boFPBPcUK8&t=753)]
Yeah. It's a C4 less slow and stable diffusion. XL is slow. We'll test the ML training later after the meeting. I think now it uses slightly more memory. Yeah. At least on BERT. So that's why earlier when I tried the same script, it went out of memory. I would find a better number.

##### **Chenyu** [[00:13:04](https://www.youtube.com/watch?v=-boFPBPcUK8&t=784)]
It also takes forever to schedule.

##### **Flata** [[00:13:12](https://www.youtube.com/watch?v=-boFPBPcUK8&t=792)]
Okay.

##### **Chenyu** [[00:13:13](https://www.youtube.com/watch?v=-boFPBPcUK8&t=793)]
Oh, we know where it looks like it's slow. We will also quickly go through other bounty. Yeah. So we have a question from the audience. Do you want to share what you have been working on? I was working on the FP8 tensor core.

##### **B1tg** [[00:13:39](https://www.youtube.com/watch?v=-boFPBPcUK8&t=819)]
The one tensor core running better and it's slower than the 016.

##### **Chenyu** [[00:13:53](https://www.youtube.com/watch?v=-boFPBPcUK8&t=833)]
Yeah.

##### **Chenyu** [[00:13:55](https://www.youtube.com/watch?v=-boFPBPcUK8&t=835)]
I think that's a separate. Speed is probably a separate issue. It would be nice if we can get the version that just runs and the output is correct. Because it would probably be in the same direction as what George is working on. I'm pretty sure to make those faster you also need similar tricks.

##### **Flata** [[00:14:17](https://www.youtube.com/watch?v=-boFPBPcUK8&t=857)]
Okay.

##### **Chenyu** [[00:14:18](https://www.youtube.com/watch?v=-boFPBPcUK8&t=858)]
I will.. So let's get the correct version. Merge the ladder. can also try those. That would be nice.

##### **B1tg** [[00:14:28](https://www.youtube.com/watch?v=-boFPBPcUK8&t=868)]
Should we get the AMD ARVM version first? Up to you.

##### **Chenyu** [[00:14:39](https://www.youtube.com/watch?v=-boFPBPcUK8&t=879)]
So the new bounty, there's a new bounty for training FP8 BERT. AMD MI300 or MI350? I don't know how difficult or different these two would be, but up to you to decide which one you want to get in first.

##### **Chenyu** [[00:15:05](https://www.youtube.com/watch?v=-boFPBPcUK8&t=905)]
That make sense? We're getting fast scan.

##### **Chenyu** [[00:15:15](https://www.youtube.com/watch?v=-boFPBPcUK8&t=915)]
And also I think training with FP8 has a lot more issues than might be in addition to the FP8. I don't know too much about that. Warspirit probably knows more. So I think with him if needed.

##### **Flata** [[00:15:34](https://www.youtube.com/watch?v=-boFPBPcUK8&t=934)]
Okay.

##### **Chenyu** [[00:15:37](https://www.youtube.com/watch?v=-boFPBPcUK8&t=937)]
Going through the list. Now our backend will be reviewed tomorrow. FlatTag, do we have any eval that's good?

##### **Flata** [[00:15:49](https://www.youtube.com/watch?v=-boFPBPcUK8&t=949)]
Yeah, I think so. What I mentioned last time, in the updates channel, is that one is the yeah, I think everything looks pretty much good in terms of the value again with I think with the jurisdiction with the JIT. I think I might have to look at another approach on how to kind of maybe I think one of them is going to probably slice the output by outputting the whatever the maximum size of the sensor could be. So I'll see if I can work on something around that. But the eval does look pretty good. It's a bit faster for sure than the non-Py version. But also the other thing is that I have to make multi work with the mass select. So I think I mentioned that in the bug reports channel. So that's probably have to consider a different version of how to approach the mass select so that it supports multi. I think those are like the only two remaining things.

##### **Chenyu** [[00:16:48](https://www.youtube.com/watch?v=-boFPBPcUK8&t=1008)]
Yeah. So multi needs to be multi only works if on each device you have the same compute. Something like mass select definitely won't work. But also not clear to me why this is not similar to training where you copy the models on each device and you just have them eval things separately.

##### **Flata** [[00:17:15](https://www.youtube.com/watch?v=-boFPBPcUK8&t=1035)]
Yeah. I mean I followed what I even followed what the I think the retina runner that was already there on the model model eval script had and yeah, yeah, that was that was the result that I encountered in terms of the mass select not working on multi for some reason.

##### **Chenyu** [[00:17:36](https://www.youtube.com/watch?v=-boFPBPcUK8&t=1056)]
Okay.

##### **Flata** [[00:17:40](https://www.youtube.com/watch?v=-boFPBPcUK8&t=1060)]
But I'll keep working on the eval for sure. Whether I think most likely we're not going to be able to do the submission for this for this cycle. But I think with if 6.0 which as you said, Chinese and you will still be there then then there should be definitely a higher chance to

##### **Chenyu** [[00:17:56](https://www.youtube.com/watch?v=-boFPBPcUK8&t=1076)]
do so. Sure. Sounds good. Okay. Next who you want to share something will merge your bounty and crates.

##### **Flata** [[00:18:15](https://www.youtube.com/watch?v=-boFPBPcUK8&t=1095)]
Cool.

##### **Chenyu** [[00:18:16](https://www.youtube.com/watch?v=-boFPBPcUK8&t=1096)]
Yeah. So I had another bounty for flux and I think this time I really wanted to be the version on MLPerf. So that one is conditional on getting its MLPerf. So see if you are

##### **Chenyu** [[00:18:30](https://www.youtube.com/watch?v=-boFPBPcUK8&t=1110)]
if you are interested. No pressure. Hey. Uh. I really think I have more

##### **Chenyu** [[00:18:54](https://www.youtube.com/watch?v=-boFPBPcUK8&t=1134)]
Yeah. We don't have new bounties. Because everyone is on rankify.

##### **Chenyu** [[00:19:08](https://www.youtube.com/watch?v=-boFPBPcUK8&t=1148)]
Uh. What else? Anyone in this meeting has any question? You can ask now.

##### **Flata** [[00:19:22](https://www.youtube.com/watch?v=-boFPBPcUK8&t=1162)]
I think I have I think I have a question.

##### **Chenyu** [[00:19:23](https://www.youtube.com/watch?v=-boFPBPcUK8&t=1163)]
Otherwise we probably end the meeting in two minutes. So we probably

##### **Chenyu** [[00:19:39](https://www.youtube.com/watch?v=-boFPBPcUK8&t=1179)]
we should be able to merge rankify soon. Not sure if it's tomorrow but definitely this week soon. Uh. It's probably pretty nice that we

##### **Chenyu** [[00:19:54](https://www.youtube.com/watch?v=-boFPBPcUK8&t=1194)]
cover all the correctness issues and the rest is more of tuning. Is using match statement in compiling a pattern manager worth trying? What do you mean? Oh you mean

##### **Chenyu** [[00:20:28](https://www.youtube.com/watch?v=-boFPBPcUK8&t=1228)]
George's meta code version? Probably. I don't know too much about this. Uh. If you can show that it's faster or if it's like simpler with similar performance then sure. This is the principle for every part of a tinygrad. It's like we don't really know and if you want to propose something open a PR we will test it. If it's better we merge it.

##### **Chenyu** [[00:20:59](https://www.youtube.com/watch?v=-boFPBPcUK8&t=1259)]
Cool. Yeah I mean now we have more and more

##### **Chenyu** [[00:21:04](https://www.youtube.com/watch?v=-boFPBPcUK8&t=1264)]
rewrite so anything that has that can improve the rewrite speed or make it less complicated is always welcome.

##### **Chenyu** [[00:21:30](https://www.youtube.com/watch?v=-boFPBPcUK8&t=1290)]
I think we should

##### **Chenyu** [[00:21:31](https://www.youtube.com/watch?v=-boFPBPcUK8&t=1291)]
try to do a lot of cleanups after that. I think in terms of overall performance we'll probably have a short setback but we should be able to clean up and we should be able to hopefully understand the space better. And with that I think that's today's meeting.

##### **Chenyu** [[00:22:01](https://www.youtube.com/watch?v=-boFPBPcUK8&t=1321)]
See you next week.
