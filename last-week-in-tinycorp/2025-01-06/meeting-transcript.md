# 2025-01-06 Meeting

## Meeting Agenda

**Time:** 9:30 AM San Diego time (PST)
- company update, CES Booth #6475 in the LVCC West Hall https://x.com/__tinygrad__/status/1875204954295881868
- quantize DSP contract
- AM, HW interface
- scheduler cleanups, VIZ
- llm.c and MLPerf bert
- bounties: onnx, tinygrad whisper, int64, tensor cores, graph rewrite 2.0

## Audio

[Youtube](https://www.youtube.com/watch?v=_zNqg1U1vdI)  
_there is an auto-generated transcript on youtube, but obviously our's here is superior in every way:)_  
_also chapters will be in the youtube description_

## Transcript

**Chenyu** [[00:00:00](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=0)]  
I think this will be a fairly short meeting.  
We don't have George today.  
George said he's on the flight to CES.  
Uh, I will also be flying later today.  
So we are going to see as I have post the [tweet](https://x.com/__tinygrad__/status/1875204954295881868) for which, so we, we, uh, we are going with comma and so we use commas both.  
Uh, we have one TinyBox repair there for people to, um, take a look.  

**Chenyu** [[00:00:41](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=41)]  
Okay.  
Uh,  

**Chenyu** [[00:00:45](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=45)]  
TinyCorp got another contract running quantized model on DSP.  
That's why the conversation about running these ONNX model want to support for the quantized layers and making sure DSP is faster.  
Nimlgen, I'll leave these two to you.  
Anything DSP and AM you want to talk about?  

**Nimlgen** [[00:01:15](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=75)]  
So I have nothing to talk about DSP.  
So AM.  
So it's merged.  
We still have several things to do.  
So the main one is the startup speed.  
I made some progress during the last week, but it's still a bit slow.  
And the main reason is just because they do the whole GPU reset each run.  
I think we can, yeah, I had a dropped pull request.  
I think we can just not do the GPU reset and reload firmware if we know that it's already loaded.  
So I'll play with this more this week and merge if it's, yeah, if everything is fine.  

**Chenyu** [[00:02:09](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=129)]  
How would it take to use AM in CI, I mean a benchmark?  

**Nimlgen** [[00:02:17](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=137)]  
Yeah, I mean, we can do that.  
But I think it's better to fix this speed.  
I mean, like this startup time.  

**Chenyu** [[00:02:27](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=147)]  
Oh, sure.  
I mean, you don't need to change everything at once.  
I think it's a good idea to start by running maybe test tiny or something in AM and making sure there's always something wrong in the CI.  
Then once you fix the speed, we can change everything else to that.  

**Nimlgen** [[00:02:51](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=171)]  
Oh, OK.  
OK, yeah.  

**Chenyu** [[00:02:53](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=173)]  
Yeah, just I think similarly to other less used backend, start with something small.  
Making sure I can run.  
So that would be nice also for, at least for me, if I want to test, I can follow how the CI is set up, then I can at least run it.  
Oh, by the way, are you using Tiny13?  

**Nimlgen** [[00:03:22](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=202)]  
Yeah, yeah.  

**Chenyu** [[00:03:24](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=204)]  
OK, I just want to make sure, because some.. 

**Nimlgen** [[00:03:22](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=202)]  
So I think, yeah, just because I think BERT dataset is broken on Tiny10.  

**Chenyu** [[00:03:34](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=214)]  
I see, I see.  

**Nimlgen** [[00:03:35](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=215)]  
Maybe we should re-copy it, yeah.  

**Chenyu** [[00:03:39](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=219)]  
Oh, you can make a copy if you want.  
Okay, sounds good.  
I also see you are working with a person that is working on our interface PR.  

**Nimlgen** [[00:03:55](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=235)]  
Yeah.  
I know it's still some failures in CI.  
But yeah, so I know but still there is some progress there.  
Maybe.  

**Chenyu** [[00:04:12](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=252)]  
I don't know.  
If it's something that can be incentivized by throwing a bounty, you feel free to throw a bounty and ask for more concrete progress.  
I think that's fine.  
I think the goal is it's always nice to involve more contributors, to make this project, to incentivize more people to contribute, we provide what we can?  

**Nimlgen** [[00:04:48](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=288)]  
Yeah, sure.  

**Chenyu** [[00:04:49](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=289)]  
OK, sounds good.  
Next, I have a scheduler in ops for Qazalin.  

**Qazalin** [[00:05:05](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=305)]  
Yeah, so I'm actually  
I kind of realized that there's a lot in the scheduler that exists that shouldn't exist.  
And all of them are sort of like interconnected.  
I feel like a throwback to the linearizer, lowercase.  
Sorry, is my voice okay?  
Yes.  
Okay.  
So I am doing a refactor of the scheduler based on the tracking graph rewrite that we now have.  
So the problem and the reason why I love this flexibility in the scheduler is because it's very annoying to keep track of the UOps while also doing rewrites on them.  
So you can imagine if I do a tensor plus 0, and then I simplify that to the same tensor,  
If I do that, I lose the previous representation of that UOp that existed on the tensor.  
So then I can't actually backtrack to the tensor, and I can't free the buffer.  
So yeah, that's the main challenge with this diff.  
I have it in, let's see, it's in the 8495 pull request, still working on it.  
But hopefully, once it's done, it should be a much more readable scheduler and have all the CastBeforeView stuff that is blocking Gradient right now.  

**Chenyu** [[00:06:45](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=405)]  
Yeah, I will share.  
So I was debugging BERT yesterday for a while.  
BERT somehow used more memory in the past two weeks.  
Uh, so we previously can fit batch size 72.  
Now we can only do 66 and there's like, I don't know, more than 10% slower.  
Uh, I made a PR to clean up something, the UOp.st.  
I hope I think that's correct, but I was trying to read scheduler and a lot of functions or it's just, as you said, it's like a lot of interconnect and not really separated.  
I think a lot, I think maybe some of it is because we copy the old, we copy things from linearizer.  
We copy things from old lazy.  
So, uh, I think it can be cooling up further.  

**Qazalin** [[00:07:48](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=468)]  
Agree.  
Yeah.  
I was thinking about adding like a, so that ShapeTracker thing, yeah, the PR is correct, honestly, but it's like that ShapeTracker thing kind of acts like a spec too, because I have the PR and I don't know how to fix this 8499.  
I'm trying to delete the entire ShapeTracker stuff being asserts and move all that to pattern matchers.  
For some reason, optimizations break.  
If you look at the process replay diff, the kernels that are generated are different.  
And it's indexing it.  
I don't know if this is a bug.  

**Chenyu & Qazalin** [[00:08:32](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=518)]  
Is this correct?  
I'm reading the process replay diff.  
It seems to do.. I mean, the output is correct.  
It's just.. It's just indexing it different.  
Like something is permuted or something.  
Like something is swapped or permuted.  
Yeah, so it's basically changing like a..  
changing to a contiguous shape track or from shape for the reduced axis.  
I'm not sure if this is correct.  
OK, I think this is too much detail.  
I will take a look.  
We can discuss this offline.  
If we can get this merged, that would be awesome.  
So I really want to get rid of.  
We're wasting lines doing that.  
And I also want to have a shared spec.  
So right now, we have Tensor UOp spec.  
I want to add shape spec and shares with kernel, schedule, everything.  
Yeah, and I think some functions in scheduler are currently doing multiple stuff.  
And we probably want to separate them, if possible, or rethink about some fundamentals.  
I talk about the two functions, one is verify and one is can_pad.  
I think maybe it's used to actually do some cache or repeat your stuff.  
But it's just very weird that you have the functions doesn't make sense by reading the function signature was my point.  
It makes things much harder to reason about.  
Yeah, it's not functional, it's not clear, it's not local.  
Yeah, talking about local.  
I think we have a lot of these functions that, due to the recursive natures, that carries some kind of a cache or a state.  
I saw there was a graph rewrite 2.0 maybe that can fix some of it, hopefully.  
Yeah.  
We also dedupe copy now.  
So I merged that.  
Does that fix memory?  
I don't know if that fixes memory.  
I would think about more to add tests like this.  
I don't think we have enough tests for memory usage and things.  
And BERT is a special case because it's very tight on memory.  
Can we add BERT to CI?  
Look, I need the feedback loop, though.  
If you don't want me to merge..
That's another problem.  
For now, just to start and do the scheduling, it takes five minutes.  
So that's the short reason for why it's not in CI.  
I mean, benchmarks already takes 20 minutes.  
So I'm not super.  
Benchmark is 15 minutes?  
No, it's about you cannot start to have single tasks that takes five minutes, right?  
I will think about this.  
Yeah.  
No worries.  
I think this is different from the last time.  
Last time, the BERT doesn't even start because there was a wrong cache or something.  

**Qazalin** [[00:12:18](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=738)]  
Yeah.  

**Chenyu** [[00:12:19](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=739)]  
So this is just we were on the fence, and now it used slightly more.  
Hopefully, it's fixed by copy.  
I'll test later.  

**Qazalin** [[00:12:29](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=749)]  
Yeah, I think this made the device a little faster, but I didn't see anything weird in the benchmarks.  

**Chenyu** [[00:12:39](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=759)]  
Yeah.  
Speaking of BERT, so I posted a new issue is for MLPerf BERT.  
I think this is probably the important, one of the important things for me for next three months is we want to get this to be fast.  
The training BERT resembles a lot of like  
any things that involves transformer, or basically if we can turn BERT fast, we can turn other models fast.  
And this involves two.  
So if you run this on master on a green TinyBox, I think it takes around 9 to 10 hours.  
Our previous submission was 6 hours.  
There are like two hours more due to Python speed.  
Because we need to reset, and reset is very slow.  
So there are probably more fundamental issues with BERT that I don't fully understand yet.  
Because if you look at LLM.c, LLM.c is very comparable with torch speed.  
There is one kernel that's very slow.  
And I think that is a search problem.  
Because I have isolated a kernel, and if I manually  
So it was a big reduced kernel.  
It's just a matmul, a linear.  
And if I manually put group, if I manually do this local and group thing, it's a lot faster and comparable to others.  
So I think that is just a search issue at this point.  
So I'm not worrying too much for llm.c speed.  
But that being said, BERT is even not considered  
Multiple GPU not considered Python speed.  
BERT is still 2x slower than our target.  
So I think there's more issue in the BERT that I'd like to know why.  
Yeah.  
So the goal is to submit with a comparable time.  
I think we target April, so we have like three months.  
Let's move on to bounties.  
We have ONNX.  
I think ONNX is making progress.  
I see the script for fetching top 100 models and subsequent comparing that with ONNX runtime.  
adding different ops that is required for the context, context, DSP model.  
And I think, I think it's, it's fine.  
I have a working PR or the same bounty.  

**Chenyu** [[00:16:10](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=970)]  
uh okay for working prs for the bounty i leave that to george because he he he gave he gave the the person the permission okay so i think ONNX fine i also posted for how i think it can be uh made it can be like split into several ones i think we want  
Basically smaller independent thing that we can merge and add value.  
We can edit instead of like one big thing that do three different things.  
Okay.  
So Tinygrad whisper, I saw a comment that it's almost ready.  
If the repeated thing is fixed, I will leave that to you to decide if it's ready or if I should lock it.  
Okay.  
Okay.  
So which PR is in this?  
I can lock it.  
I think he has another bounty.  
That's lock low.  
I don't know.  
It's probably fine.  
I will leave it to you to decide if it's functional already, then I will probably have a quick review for some of the coding stuff.  
Similar things for int64.  
I also put some high-level comments on that for the basic stuff.  
I see a reply to that, but I haven't reviewed that yet.  
I will do that later today.  
TensorCores.  

**Ignaciosica** [[00:18:04](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=1084)]  
Hi, hello.  
I'm just getting back to work today.  
So this week, I'm going to finish up the bounties, the open bounties, and tackle the H100, start working on it.  

**Chenyu** [[00:18:23](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=1103)]  
Great.  
Sounds good.  
Is there anything you need that can make your job easier?  
We don't have H100.  

**Ignaciosica** [[00:18:34](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=1114)]  
Yeah, I know.  
I've been looking to rent it to test.  
No, that's it.  
Once I start working, maybe I hit Europe.  
But for now, it's OK.  

**Chenyu** [[00:18:50](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=1130)]  
OK, sounds good.  
Yeah, I really like the refactor and clean ups for the TensorFlow query you have done.  
I think George also said nice thing about the work.  
So good job there.  

**Ignaciosica** [[00:19:06](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=1146)]  
Sure, thank you.  

**Chenyu** [[00:19:09](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=1149)]  
Graph rewrite 2.0.  

**Tomsa** [[00:19:25](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=1165)]  
Yes?  

**Chenyu** [[00:19:26](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=1166)]  
Hello?  
Oh, OK, you have permission to speak.  
Great.  
Something you want to add?  

**Tomsa** [[00:19:33](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=1173)]  
And I just joined, so I'm supposed to speak?  

**Tomsa** [[00:19:43](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=1183)]  
No, it's just if you want to say something or have a quick discussion, feel free.  
If no, that's fine.  
Wait, so we're talking about the bounties then, is it?  

**Chenyu** [[00:19:56](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=1196)]  
Yes.  

**Tomsa** [[00:19:58](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=1198)]  
OK, so I think that's the right way to do the graph rewrite.  
Because Graph Rewrite wants to, Graph Rewrite rewrites the sources before it rewrites itself for each UOp.  
You want the matching to, I guess, follow the same flow.  
So if you do from leaf node, from leafs to root, then you can reuse all the computation.  

**Chenyu** [[00:20:32](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=1232)]  
Yeah, that makes a lot of sense.  

**Tomsa** [[00:20:36](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=1236)]  
There's one issue, which is while that's for a graph rewrite, the issue is that for the pattern matcher rewrite, you do want from root to leaf node.  
Because if you think about it, for example, for the renderer, the renderer is just trying to find  
the anytime, essentially, the pattern match or rewrite is used, you want to do from root to leaf.  
So that's a little bit annoying.  
You'd have to have two implementations, I guess, one for the graph rewrite, another one for the uop rewrite.  
That's something I realized after posting the PR.  

**Chenyu** [[00:21:28](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=1288)]  
I see.  
I think since the bounty is concerning about the algorithm change and see how fast the rewrite can be made, I think it's fine for you to focus on making a graph rewrite fast with the new algorithm first.  
If you just want to test having two separate implementations, fine.  
Just for the sake of bounty.  
And we will think about how to clean those up and what will end up being merged.  

**Tomsa** [[00:21:56](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=1316)]  
I didn't work on the x86 bounty, but I did the benchmarks just now.  

**Chenyu** [[00:22:06](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=1326)]  
Sorry, can you repeat?  

**Tomsa** [[00:22:09](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=1329)]  
So George asked me to do the execution time benchmark for the x86, yeah.  
And I did it just now.  
And it's twice as slow as O0, essentially.  
Okay.  
I only tested for the transformer.  
So I just ran the transformer test.  
And I did it just now.  
I need to do more tests.  
But for the O2, it's 0.4 seconds.  
The O1, it's 0.8.  
O0 is 3.3.  
Then LLVM is 1.3.  
So it's slower than O1.  
And x86 is 6.7.  
So I need to figure that out.  
I actually expected it to be faster, but I'll see why.  

**Chenyu** [[00:22:52](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=1372)]  
Okay.  
No, sounds good.  
Yeah, so if you have questions that you need to clarify or discuss, feel free to post.  
We usually recommend focusing on one bounty and get it done before working on another.  
But since we are making good progress, it's up to you to decide.  

**Chenyu** [[00:23:20](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=1400)]  
OK.  
That's bounty.  
Did I miss anything?  
Okay.  
For the people in this channel, if you have questions or comments about TinyGrad or TinyCorp, feel free to post in general or in the VC of this talk.  

**Chenyu** [[00:23:45](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=1425)]  
Otherwise, we'll probably end the meeting soon.  
What is the plan in general for distributed?  
What do you mean by that?  

**Chenyu** [[00:24:11](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=1451)]  
There's a bounty for implementing FSDP.  
There's nothing fundamentally not supported.  
It just needs to be implemented.  
You still have a bounty for that, right?  
And there was an attempt that was, I would say, maybe 70% there.  
Just need to be finished.  
Yeah, the bounty is still there.  
FSDP in tinygrad.  
Demo by training and LLM larger than that fits on 1GPU.  
Yeah, the distributed or multi-GPUs primitives are supported by TinyGrad.  
Or specific like auralism or how you separate a model like FSDP, it just needs to be implemented.  
There might be some nuance on how do you want to swap axes for multi-GPU tensor, but that's the core issue for that bounty.  
So I tried this yesterday, and it just doesn't do anything.  
The tiny chat on WebGPU, I don't know.  
I can test it later.  

**Chenyu** [[00:25:51](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=1551)]  
I don't have anything.  
I'll also let George test that.  

**Chenyu** [[00:26:00](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=1560)]  
I see it takes a minute to decompress.  
Great.  

**Chenyu** [[00:26:08](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=1568)]  
I think it needs a lot of refactor to multi, but in terms of line, do you plan to spend on it?  
I mean, this is similar to what we spent on the lines.  
As long as, so this is clearly a feature that we want to support and  
If it needs lines, it's fine, but it needs to, but you need to justify that it's a good use of line.  
Like if it's 10 lines of complexity, then sure to spend 10 lines on it.  
But if you end up like need like 200 lines, then no, it shouldn't be more complicated than what it needs to be.  
OK, I'll test the web GPU one later.  
So at least we want a good demo.  
So opening a tab and do nothing for one minute is not a very good demo.  
But I will test and let you know now.  
It's not just that.  
It's more of a, imagine you are trying to sell TinyGrad to your friends and families, and this is a demo you want them to see.  
So think about how that makes a good user experience.  

**Chenyu** [[00:27:45](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=1665)]  
Cool.  
Any more stuff?  

**Chenyu** [[00:28:01](https://www.youtube.com/watch?v=_zNqg1U1vdI&t=1681)]  
Okay.  
I think that's everything we have for today.  
We'll probably post more about CES.  
We want to figure out what are the new chips that is coming and like, what do we do for the future TinyBox and stuff like that.  
So stay tuned and that's it for this meeting.  
Thanks everyone.  
See you next week.  
