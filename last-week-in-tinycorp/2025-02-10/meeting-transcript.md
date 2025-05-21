# 2025-02-10 Meeting

### Meeting Agenda

**Time:** 6am Monday San Diego time (10pm HK time)
- company update
- ci speed, llvm speed, dsp speed
- Ops.POW, gated load/store to where, resnet
- scheduler
- drivers
- tensor cores
- onnx
- bounties (webgpu fp16, tinychat, retinanet, graph rewrite 2.0, flatten add chain, hevc decoder)

### Audio

[Youtube Link](https://www.youtube.com/watch?v=sMxM41tpijc)

### Transcript

##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=sMxM41tpijc&t=0)]
We can get started.
Any company update from you?

##### **Geohot** [[00:00:06](https://www.youtube.com/watch?v=sMxM41tpijc&t=6)]
Not really.
No updates yet on, well, apparently next week we're going to get some 5090s, but I'll believe it when I see them.

##### **Chenyu** [[00:00:17](https://www.youtube.com/watch?v=sMxM41tpijc&t=17)]
Great.
I think I would be giving a talk or there's a study group that they are adding kernel stuff in person in New York.
I can give a talk and the organizer is sure, so I'll probably prepare something for that.
Mostly, I think, just to show, since they are interested in reading kernel code, I'll probably just show some examples from
similar to abstraction, like top-down, and maybe show some tools like VIZ and support in different kinds of backend and go from there.

##### **Geohot** [[00:01:04](https://www.youtube.com/watch?v=sMxM41tpijc&t=64)]
Yeah, I think one of the most interesting things about kernels is the opt-ops and what they do, like an unroll and an upcast and what these things look like.

##### **Chenyu** [[00:01:16](https://www.youtube.com/watch?v=sMxM41tpijc&t=76)]
Yeah, probably I have some examples, maybe just the simple ones.
And I just want to provide it in a way so that if people are interested, they can hear some examples for them to try Tinygrad to start with.

##### **Geohot** [[00:01:34](https://www.youtube.com/watch?v=sMxM41tpijc&t=94)]
Yeah.
No, I mean, Viz is a great way to teach this stuff too.
We need like a tutorial for speed.

##### **Chenyu** [[00:01:41](https://www.youtube.com/watch?v=sMxM41tpijc&t=101)]
Yeah, and I also saw your other speed doc.
I think similar to abstraction, I think these things attract people.

##### **Geohot** [[00:01:50](https://www.youtube.com/watch?v=sMxM41tpijc&t=110)]
Yeah, yeah, I hope so.
Yeah, I'm going to put some effort into that.

##### **Chenyu** [[00:01:55](https://www.youtube.com/watch?v=sMxM41tpijc&t=115)]
Cool.
Yeah, I will share whatever I come up with later.
OK, let's move on.
Oh, so for speed, there's George, this is all for you.

##### **Geohot** [[00:02:11](https://www.youtube.com/watch?v=sMxM41tpijc&t=131)]
Yeah, no, I worked I did a lot of stuff on CI last week, I upgraded us for $100 a month to the GitHub organizations.
Enterprise or whatever it's called.
But it gives us 500 runners.
So we can use a lot more runners now.
We still can't use more macs.
We can only use five macs.
But we can use more Linux runners to pretty much do whatever.
So it hasn't really made CI that much faster.
But now a lot of CI completes faster.
It's pretty much just like NV that's still slow.
And I think there's...

##### **Chenyu** [[00:02:47](https://www.youtube.com/watch?v=sMxM41tpijc&t=167)]
The Linux NV=1 is probably still bottleneck.
It takes 12 minutes.

##### **Geohot** [[00:02:55](https://www.youtube.com/watch?v=sMxM41tpijc&t=175)]
Yeah, and I don't really know why Linux NV is so much slower than Linux PTX.
Is it compile time?
Is it?
I don't know.
But yeah, no, so we can use more CI runners.
I also refactored.
The CI code looks good now.
I refactored those YAML files to actually look decent.
I made some subactions for process replay and for environment setup.
So it's really easy to add another runner, read test.yaml if you haven't.
But yeah, there's just like, check our code, set up environment, run your tests, and then add process replay action at the bottom if you want.
Yeah, so I did two streams this weekend for LLVM speed.
LLVM is really nice.
So the only things it seems like we're really missing are just a bunch of OptOps.
I did a stream on Sunday that shows how to fix the reduce thing.
So just adding a few more OptOps to BEAM should do that.
There's this concept also of adding horizontally.
that maybe doesn't exist in the OptOps.
I haven't totally thought it through yet.
But it's up there.
It's a bounty.
And I want to get other people excited about working on speed.
This is definitely doable now.
It's doable to get LLVM speed that exceeds Torch's speed with not that much work.
I've also been working on de-vectorize equals zero.
So de-vectorize equals zero doesn't do the de-vectorization before it renders it to the IR.
It keeps it vectorized.
It's really annoying in the DSP.
So I wrote this, like, re-vectorization thing, and then I was like, this is stupid and super slow, because it, like, de-vectorizes to 128, and then it re-vectorizes.
I think we'll try to keep it de-vectorized, so that'll be fast for the DSP.
The trick to making the DSP good is that you have to do things... It's an 124-bit... vector machine.
So you have to do things in 128-byte chunks.
And that's an upcast of 128.
So that's a lot bigger than the other ones we've been seeing.
So that's why de-vectorize is really nice.
Yeah, we have some things getting like 30 gigaflops now on the real DSP too.
I got 35 on the actual DSP hardware.

##### **Chenyu** [[00:05:45](https://www.youtube.com/watch?v=sMxM41tpijc&t=345)]
What's that's a limit for that.

##### **Geohot** [[00:05:50](https://www.youtube.com/watch?v=sMxM41tpijc&t=350)]
The theoretical limit supposedly is three terafops.
But it seems like... It seems like SMPE gets about 80 gigaflops.
So that might pretty much just be what we've been doing plus two cores.

##### **Chenyu** [[00:06:09](https://www.youtube.com/watch?v=sMxM41tpijc&t=369)]
Oh, I see.
75 times two, okay.
35 times two.

##### **Geohot** [[00:06:14](https://www.youtube.com/watch?v=sMxM41tpijc&t=374)]
35 times 2, yeah, yeah.
There's two cores you can use.
But that's the last thing I'll do.
There's a lot of lower hanging fruit than that.
Also, this morning, I wrote a nice QMU will tell you the cycle counts.
And if you just take how many cycles the thing runs, and if you just take that and divide it up by 1E9, it gives you a pretty good idea of the time for 10 gigahertz, and that's it.

##### **Chenyu** [[00:06:38](https://www.youtube.com/watch?v=sMxM41tpijc&t=398)]
I see.
Great.
So contract, on track?

##### **Geohot** [[00:06:46](https://www.youtube.com/watch?v=sMxM41tpijc&t=406)]
Yep.
That's going to be what I'm working on for the rest of probably this week and next.

##### **Chenyu** [[00:06:54](https://www.youtube.com/watch?v=sMxM41tpijc&t=414)]
OK.
Sounds good.
Before we move on to the next one, so you changed the commutative to be integer only?

##### **Geohot** [[00:07:07](https://www.youtube.com/watch?v=sMxM41tpijc&t=427)]
Yes.
Is that bad for some reason?

##### **Chenyu** [[00:07:10](https://www.youtube.com/watch?v=sMxM41tpijc&t=430)]
Yes, because there's a bounty to flip and sort things in a chain.
And that basically needs commutative.

##### **Geohot** [[00:07:21](https://www.youtube.com/watch?v=sMxM41tpijc&t=441)]
Yeah.
So the problem with commutative is sometimes, and I'm not exactly sure why it happens,
I guess this is less of a problem with de-vectorize.
But sometimes, for some reason, one or two of the vector items will flip.
And then if one or two of the vector items flips, I can't re-vectorize it.
So yeah, if I'm using de-vectorize, you could put it back if you really want it.

##### **Chenyu** [[00:07:55](https://www.youtube.com/watch?v=sMxM41tpijc&t=475)]
Judging from how you change the code and no test really was broken, I think if we want to add it back, we probably need to add more tests around that too.

##### **Geohot** [[00:08:04](https://www.youtube.com/watch?v=sMxM41tpijc&t=484)]
Yeah, no, definitely.
There are tests that will break if you remove the integer, because it's how it does the constant.

##### **Chenyu** [[00:08:12](https://www.youtube.com/watch?v=sMxM41tpijc&t=492)]
Yeah, because the current test probably only build on variable of integers.
But OK.
OK, no problem.
I will figure it out with the person working on the bounty.
OK, moving on to the things I did.
So I moved the POW to be an ops.
So it's no longer in and most of the logics are moved to one of the two graph rewrites.
So I also, I also remove another place in the getitem that try to extract the const from tensor.
So we don't have that behaviors anywhere in tensor now, but we don't have that to const of our thing.
Small issue to bring back the behavior for getitem and similarly to fix a lot of the cat and pad in the kernel is because currently, for gated load and store, we only rewrite it as a where in the renderer.
And that's too late if you want to.
So there's a lot like.

##### **Geohot** [[00:09:28](https://www.youtube.com/watch?v=sMxM41tpijc&t=568)]
Well, you can't really write it as a where.
I've been thinking about this too.

##### **Chenyu** [[00:09:35](https://www.youtube.com/watch?v=sMxM41tpijc&t=575)]
OK.
Why not?

##### **Geohot** [[00:09:38](https://www.youtube.com/watch?v=sMxM41tpijc&t=578)]
OK.
So let's just talk about a gated load.
So if you want to write a gated load as a where, you're imagining the where being after the load, right?

##### **Chenyu** [[00:09:46](https://www.youtube.com/watch?v=sMxM41tpijc&t=586)]
You mean in UOP representation?

##### **Geohot** [[00:09:54](https://www.youtube.com/watch?v=sMxM41tpijc&t=594)]
Yeah.

##### **Chenyu** [[00:09:56](https://www.youtube.com/watch?v=sMxM41tpijc&t=596)]
So the load will be a source to a where.

##### **Geohot** [[00:09:59](https://www.youtube.com/watch?v=sMxM41tpijc&t=599)]
The load will be a source to the where.
So the problem with that is if the index is something out of bounds in memory, it could crash the GPU.

##### **Chenyu** [[00:10:08](https://www.youtube.com/watch?v=sMxM41tpijc&t=608)]
Yeah, but shouldn't it be tied to the load?

##### **Geohot & Chenyu** [[00:10:12](https://www.youtube.com/watch?v=sMxM41tpijc&t=612)]
No.
After lower.
After lower, yes.
After lower, if you have a gated load, some of the things where the gate is false, where it should be returning zero, are out-of-bounds memory access.
So the load actually has to not happen.
And if that's an input to the where, that means that the load happened.
is not short circuit?
No.
I mean, there's no work.
Yeah, the current behavior in the renderer is short circuit, yes.
But there's no guarantee if you just put an arbitrary where afterward that it'll be short circuit.
And then think about how would you do a gated store using that?

##### **Chenyu** [[00:11:21](https://www.youtube.com/watch?v=sMxM41tpijc&t=681)]
We probably don't need a gated store.
We can focus on gated load.
I'm still not too following if we guarantee that your where.
So basically, conditional on valid or the where condition is true.
That load is always safe.
Yeah, condition on the wear being true, yeah.
Yeah, but I don't see in what condition we will remove that where condition for that load.

##### **Geohot** [[00:11:51](https://www.youtube.com/watch?v=sMxM41tpijc&t=711)]
Again, you're making an assumption that a where is a short circuit, and that's true in C style, but it's not true in LLVM, for example.

##### **Chenyu** [[00:12:02](https://www.youtube.com/watch?v=sMxM41tpijc&t=722)]
Is there a way to make it true?

##### **Geohot** [[00:12:07](https://www.youtube.com/watch?v=sMxM41tpijc&t=727)]
No, no, it can't be, right?
Like by design of the uops, it can't be true.
It's also not true in PTX.
It's not true in assembly language.
It just happens to be true in C. You can look at the implementation in PTX of like gated load and you can see how it differs from the implementation of where.
You actually need that load not to happen.
So I have another proposal.
My proposal is that you put the where in front of the index.
And then like, so it's like load from an index, and then the index has the buffer as the first one, and then it has a where as the second one.
And that where sets it to a poison value if the valid is false.

##### **Chenyu** [[00:13:02](https://www.youtube.com/watch?v=sMxM41tpijc&t=782)]
Yeah, I think that is similar to the current gated load in the sense that I was just not sure if I want to rewrite this where merge.
So we have the where merging rules saying if the condition's on the same, we can merge it.
If we want to separate these, so now we have cases for gated load to gated load, gated load to a where, and where to a where.

##### **Geohot** [[00:13:27](https://www.youtube.com/watch?v=sMxM41tpijc&t=807)]
Well, I think you also want the where.
So the poison thing doesn't get you out of the where.
So you'd put the where basically in two places.
You'd put the where on the index, and you'd put the where on the output.

##### **Chenyu** [[00:13:41](https://www.youtube.com/watch?v=sMxM41tpijc&t=821)]
Yeah, my point is just now the same where merging rules, I need to repeat it three times.
Like for cats, it's like, yeah, yeah.
So that's a main issue.
I was trying to see if there's a way to get around this.

##### **Geohot** [[00:14:01](https://www.youtube.com/watch?v=sMxM41tpijc&t=841)]
All I can say about this, for 100% certain, is that you can't just have a where on the output of the load, because...
But if you also put a where on the index to give it a poison value, this kind of fixes it.
Also, the thing I like about that where with the poison value is it kind of specifies how to do those, like, you know those index folds you do?
The index folds where it's, like, based on the gate, you can not compute some things?
Like, that becomes a just purely mathematical rewrite based on that where.

##### **Chenyu** [[00:14:37](https://www.youtube.com/watch?v=sMxM41tpijc&t=877)]
I see, I see.
Okay, I would think about it.
OK, one last thing.
So for ResNet I was trying AM driver.
I don't know.
I saw Nimlgen has a lot of fix on that.
So maybe some of it is that.
Sometimes I get very weird values and weird results.
But if I pull to master, sometimes it works.
So maybe we can discuss about the status of AM later.
But for AMD, ResNet crashes always.
But for AM, it seems to run fine.
So not very useful to debug AMD, but good job for AM.

##### **Geohot** [[00:15:22](https://www.youtube.com/watch?v=sMxM41tpijc&t=922)]
Well, when it runs fine, does it get good values?

##### **Chenyu** [[00:15:25](https://www.youtube.com/watch?v=sMxM41tpijc&t=925)]
Yeah.
So the most recent one I get, they get similar values to NV.
So we still don't know a lot of convergence issue.
But it's similar to NV, so I don't think it's specific to AM.

##### **Geohot** [[00:15:41](https://www.youtube.com/watch?v=sMxM41tpijc&t=941)]
Great.
We made a better driver than AMD.

##### **Chenyu** [[00:15:44](https://www.youtube.com/watch?v=sMxM41tpijc&t=944)]
Great.
Let's move on to scheduler.

##### **Qazalin** [[00:15:48](https://www.youtube.com/watch?v=sMxM41tpijc&t=948)]
All right.
I have the kernel refactor ready.
I'll post the benchmarks preview in the scheduler channel.
As you can see, the Python time just increases substantially for a bunch of stuff.
So I'm working on just optimizing Python speed last, but it's correct.
And what you can really do is like assigns can depend on other assigns and preload is gone.
So yeah, I'm planning to get that.

##### **Geohot** [[00:16:20](https://www.youtube.com/watch?v=sMxM41tpijc&t=980)]
That's speed diff doesn't look too bad.

##### **Qazalin & Geohot & Chenyu** [[00:16:27](https://www.youtube.com/watch?v=sMxM41tpijc&t=987)]
I'll leave it to you.
I mean, you can click on which is the which is which which which PRS is this one?
8925.
Alright, so sorry to pay off.
It looks like 10% lower.
Yeah.
Do you want to explain it for everyone here?

##### **Qazalin** [[00:17:06](https://www.youtube.com/watch?v=sMxM41tpijc&t=1026)]
Sure.
So this is
about resolving how to topo sort the different kernels.
So what the scheduler does really is take a really big graph of tensors and break it into kernels.
But once you've broken it into kernels, you also have to topo sort them in a way that the output is correct.
this is easy for most of the time but it's hard when you have assigns because assign means that a buffer can have multiple values depending on which kernel ran first so what we have right now is a hack called preload this hack is very limiting and it's also fragile 
This hack basically says okay if you have a preload of a buffer, do this first before doing the assign, otherwise do the assign first.
This limits us in two ways.
One is that there's extra rewrites in there, there's extra complexity, but the biggest thing is that you can't have multiple assigns scheduled in one kernel, one schedule.
So, what we have here is like a refactor of exactly what exists in the linearizer for the UOPs, but expressed in the tensor kernel style.
So far, I have gotten to a point where you can have multiple assigns depend on each other and the existing test work as expected.
Realization happens before breaking it into blocks.
So it looks up the realizes map to see, OK, does this tensor end up getting realized?
Otherwise, it just appends it to a kernel.
So if you visit, you can actually see things being gobbled up into block kernels and getting connected together.
That's the basic idea.

##### **Geohot** [[00:19:12](https://www.youtube.com/watch?v=sMxM41tpijc&t=1152)]
I got to look this over with Viz.
But OK, so it's basically that same assigned app thing, but you removed all the DFS code.

##### **Qazalin** [[00:19:23](https://www.youtube.com/watch?v=sMxM41tpijc&t=1163)]
I did not remove DFS.
I put DFS back because ResNet seems to have memory issues when I do DFS.
So DFS is correct, but we have to understand why DFS is required to make ResNet work.

##### **Geohot** [[00:19:41](https://www.youtube.com/watch?v=sMxM41tpijc&t=1181)]
I see.
Can we, I mean, I'll give this a try tomorrow or you're welcome to merge it if you think it's good.
Can we separate the idea of like grouping and scheduling?
Like, can we rewrite the tensors with the kernels in their history, in their parents?

##### **Qazalin** [[00:20:18](https://www.youtube.com/watch?v=sMxM41tpijc&t=1218)]
The way I imagine it is that realization, the grouping should happen before the kernel is run.
The kernel grouper, the append to kernel, the append to block, whatever it's called, should have a reference of which ones to append and which ones to not.
It's a separate concept.

##### **Geohot** [[00:20:42](https://www.youtube.com/watch?v=sMxM41tpijc&t=1242)]
Yeah, the grouper should definitely happen before anything runs.
So what I'm saying is the scheduler could actually put things back in the tensor, like put UOPs in the tensors that point to kernels.

##### **Qazalin** [[00:21:00](https://www.youtube.com/watch?v=sMxM41tpijc&t=1260)]
I don't understand.
Can you explain?
You said about the Super Mario thing.

##### **Geohot** [[00:21:08](https://www.youtube.com/watch?v=sMxM41tpijc&t=1268)]
Yeah, well, yeah, the Super Mario thing, it's kind of like, you can think of the kernel graph, like the sced sync, as the overworld.
And then you can zoom in on each one of those kernels, and those kernels are like the levels.
Um, but no, what I'm saying is like, so right now the scheduler still returns this list of schedule items, right?
Instead of returning a list of schedule items, what you could do is update the graph to have the kernels in it.
Or have we thrown that information away by now?

##### **Qazalin** [[00:21:42](https://www.youtube.com/watch?v=sMxM41tpijc&t=1302)]
You can literally like return sketch thing from the scheduler and put that BFS or topo short, whatever it is in realize.

##### **Geohot** [[00:21:52](https://www.youtube.com/watch?v=sMxM41tpijc&t=1312)]
Uh, yes.
But we'll talk about this in a while.
But yeah, I think this is a good direction.
And we can separate the sced sync from the other stuff.
We can think about how we want to do that.

##### **Qazalin** [[00:22:07](https://www.youtube.com/watch?v=sMxM41tpijc&t=1327)]
I want to move on with this because it's like preload has to go.
I completely understand preload has to go.
I'll work on making this fast.
If you don't want to click merge right now, you can give me feedback on.

##### **Geohot** [[00:22:23](https://www.youtube.com/watch?v=sMxM41tpijc&t=1343)]
No, let's just click merge.
Let's just merge it.
If you think it's good, go ahead.

##### **Chenyu** [[00:22:29](https://www.youtube.com/watch?v=sMxM41tpijc&t=1349)]
10% is fine.
And there are other more systematic way to make that fast.
It's still pretty slow, but not for this specific PR.

##### **Geohot** [[00:22:42](https://www.youtube.com/watch?v=sMxM41tpijc&t=1362)]
Okay, merged.

##### **Chenyu** [[00:22:42](https://www.youtube.com/watch?v=sMxM41tpijc&t=1364)]
Probably want to test with benchmark or was it test on benchmark?

##### **Qazalin** [[00:22:52](https://www.youtube.com/watch?v=sMxM41tpijc&t=1372)]
It was.
I ran a benchmark like that.

##### **Chenyu** [[00:22:57](https://www.youtube.com/watch?v=sMxM41tpijc&t=1377)]
Great.

##### **Qazalin** [[00:22:58](https://www.youtube.com/watch?v=sMxM41tpijc&t=1378)]
I'm going to work on your don't realize expands and make that generic.
I don't know what you want from that.

##### **Geohot** [[00:23:06](https://www.youtube.com/watch?v=sMxM41tpijc&t=1386)]
Oh, from don't realize expands?
What do you mean by generic?

##### **Qazalin** [[00:23:14](https://www.youtube.com/watch?v=sMxM41tpijc&t=1394)]
I mean, can it be made generic?
Is that the thing we should focus on?

##### **Chenyu** [[00:23:20](https://www.youtube.com/watch?v=sMxM41tpijc&t=1400)]
It's an important thing that we want to focus on in the next month or two, because that has a big impact on training Bert.
But unless you already have a good idea for when do you want to expand or when not to expand, because I don't.
I don't know if George does.
We can only do that once we know what to do with the expand.

##### **Geohot** [[00:23:43](https://www.youtube.com/watch?v=sMxM41tpijc&t=1423)]
Yeah, when you say make it generic, so you don't want do realize expand.
You don't want don't realize expand.
You want sometimes realize expand.
But figuring out an answer to that sometime is not that obvious to me.

##### **Chenyu** [[00:24:01](https://www.youtube.com/watch?v=sMxM41tpijc&t=1441)]
Yeah, so that should be probably want to run over a bunch of kernels and either having other heuristic to make a decision or find a set of rules that is good enough.
But for now, we don't really know.
So that's why our current rule and with that special flag try the two things.
And you can observe that for individual kernels.
That's where we are now.

##### **Geohot** [[00:24:37](https://www.youtube.com/watch?v=sMxM41tpijc&t=1477)]
I think there's a lot more cleanup to still do here too.
There's still a lot of stuff in the schedule context.
Do we need all these things?

##### **Qazalin** [[00:24:49](https://www.youtube.com/watch?v=sMxM41tpijc&t=1489)]
As long as there's custom stuff that I'm maintaining for the reduces.
That's the oldest part of the scheduler right now.

##### **Geohot** [[00:25:00](https://www.youtube.com/watch?v=sMxM41tpijc&t=1500)]
What do you mean?
Did you bring back multi?

##### **Qazalin** [[00:25:08](https://www.youtube.com/watch?v=sMxM41tpijc&t=1508)]
I'll bring it back.

##### **Geohot** [[00:25:10](https://www.youtube.com/watch?v=sMxM41tpijc&t=1510)]
Yeah, that's a good thing to do.

##### **Qazalin** [[00:25:16](https://www.youtube.com/watch?v=sMxM41tpijc&t=1516)]
But like multi, if I can bring it back, it's again custom stuff.
So we have a custom DFS.
It's groups the reduce ops with the children.
I did a bunch of refactors last week to just, like, sectionize the scheduler.
We only need the context for that.
The context lifetime is that place.
It starts and ends with the custom stuff.
So we don't need the context for the other stuff.

##### **Geohot** [[00:25:44](https://www.youtube.com/watch?v=sMxM41tpijc&t=1544)]
Yeah, taking it out of there would be good.

##### **Qazalin** [[00:25:48](https://www.youtube.com/watch?v=sMxM41tpijc&t=1548)]
Like, the only way is, like, rewrite that into rewrite rules.
I'm not sure how.
I don't want to keep me doing it.

##### **Geohot** [[00:25:57](https://www.youtube.com/watch?v=sMxM41tpijc&t=1557)]
But messing with the expand thing is actually, if you want to play with that for a BERT, is actually very easy now.
You can just write where it says, don't realize expand.
You can just do whatever you want with it.

##### **Chenyu** [[00:26:17](https://www.youtube.com/watch?v=sMxM41tpijc&t=1577)]
Yeah, I try that.
And sometimes it got faster, or sometimes it got slower.

##### **Geohot** [[00:26:22](https://www.youtube.com/watch?v=sMxM41tpijc&t=1582)]
Yeah, yeah.
Well, sometimes you realize expand.

##### **Chenyu** [[00:26:27](https://www.youtube.com/watch?v=sMxM41tpijc&t=1587)]
OK, let's move on.
Or anything else to add?

##### **Geohot** [[00:26:36](https://www.youtube.com/watch?v=sMxM41tpijc&t=1596)]
I'll write up tomorrow the stuff about separating the grouping and putting the grouping into the overworld and see if this is feasible.
I'm basically saying maintain tensor map for as long as possible.
Oh, are the views gone too?
Is it now always movement ops?

##### **Qazalin** [[00:27:06](https://www.youtube.com/watch?v=sMxM41tpijc&t=1626)]
Oh, yeah, yeah, yeah, yeah.
Yes, yes.
I merged that.
So like, it's sort of like realizations.
We're getting to this point where things are, diffs are like five lines, less than five lines, but it's like, okay, this insight we missed and it broke a bunch of stuff.
Like the most correct way to represent a realized tensor base is a root shape on a buffer.
Then you can do all the fancy stuff with the cast before views or whatever you want to do where you actually make tensors become views of other tensors.
And that view can be anything, right?
Because it's movements all chained together.
And that view thing, I don't need that anymore.
I fixed that with a nice property of substitute.
It just worked.

##### **Chenyu** [[00:27:58](https://www.youtube.com/watch?v=sMxM41tpijc&t=1678)]
That's good.
Okay, let's move on to drivers.

##### **Nimlgen** [[00:28:08](https://www.youtube.com/watch?v=sMxM41tpijc&t=1688)]
Yeah, so this week, so we added support for 7600 to AM.
Basically, it's like AM is now more generic, so it can just treat versions directly from GPU and load the correct firmware and register subsets and yeah.
so yeah also fix the power consumption and this gfx utilization which at 100 

##### **Geohot** [[00:28:40](https://www.youtube.com/watch?v=sMxM41tpijc&t=1630)]
What are we down to now?

##### **Nimlgen** [[00:28:42](https://www.youtube.com/watch?v=sMxM41tpijc&t=1632)]
so yeah it's um it's 18 watts for 7900 and 3 watts for 6 7600 um yeah so
Yeah, so this week I'm just going to continue working on the USP GPU.
I've been reading firmware.
So yeah, but not much progress there.

##### **Geohot** [[00:29:13](https://www.youtube.com/watch?v=sMxM41tpijc&t=1753)]
You've been reading the firmware for the 24?

##### **Nimlgen** [[00:29:14](https://www.youtube.com/watch?v=sMxM41tpijc&t=1754)]
Yeah, I mean, both of them.
I'm just comparing them.

##### **Geohot** [[00:29:22](https://www.youtube.com/watch?v=sMxM41tpijc&t=1762)]
Yeah, I mean, it'd be cool as a first step to get the 24 working like we have the 23 working.

##### **Nimlgen** [[00:29:35](https://www.youtube.com/watch?v=sMxM41tpijc&t=1775)]
Yeah.  OK, yeah.
I think, yeah.
I mean, yeah, just trying to get the full picture of what's happening because, yeah, some parts of difference between them and just doing it straightforward on 24, it just doesn't work for some reason.

##### **Geohot** [[00:29:54](https://www.youtube.com/watch?v=sMxM41tpijc&t=1794)]
Yeah, we don't actually need to support 23s.
I don't care about 23s.
If all we support is 24s, that's great.
Just there's a chance that the 24s are going to do the fast DMA thing differently.

##### **Nimlgen & Geohot** [[00:30:30](https://www.youtube.com/watch?v=sMxM41tpijc&t=1830)]
How's the move to AM for everything going?
I didn't get the question.
Can you repeat it?
Oh, how's the move for the benchmarks, the AM?

##### **Nimlgen** [[00:30:39](https://www.youtube.com/watch?v=sMxM41tpijc&t=1839)]
Oh, yeah.
So actually, I just did it and then just rewrote it because during this week and just some fuzzers, I found a strange behavior on the RESNet.
So yeah, I'm just going to look into this also this week and also into the page fault, uh, you caught NCI.
So like, yeah, I've just been investigating this, like the address is correct.
I mean, maybe it's something kind of the race.
So yeah, I just started, uh, added some barriers to our Python code.
So yeah, I'll just fuzz this more.

##### **Geohot** [[00:31:21](https://www.youtube.com/watch?v=sMxM41tpijc&t=1881)]
Yeah, I saw the Atomics.
I think, yeah, fuzz it.
But let's also stop inserting AMD GPU.
I have no idea what that thing's doing.
I'd like to just keep it out for the benchmarks.
Maybe we can have one small section where we just do a regression test just to make sure that that behavior is still supported, where we insert it, do the regression test, remove it, and then we never insert the AMD GPU module again.

##### **Nimlgen** [[00:31:54](https://www.youtube.com/watch?v=sMxM41tpijc&t=1914)]
Yeah, okay.
I mean, actually, this problem, when we get some style pits, I mean, I think
I think it's happened when we just cancel workflow or just it's timeout.
So I think it's more related to how we stop these speeds.
GitHub CI stop these speeds.
So maybe we can change that so we do not have problems with this memory usage.

##### **Geohot** [[00:32:26](https://www.youtube.com/watch?v=sMxM41tpijc&t=1946)]
So those are happening with AMD GPU or with AM?

##### **Nimlgen** [[00:32:33](https://www.youtube.com/watch?v=sMxM41tpijc&t=1953)]
Um, so actually I think both of them, so it's actually, I mean with AMD GPU, uh, like, yeah, AMD GPU just resolved this memory for the speed because these speeds kind of steal life.
And for AM, I think Qazalin also saw when, yeah, also like the log files.
So to access the GPU also were taken.
So I think, yeah, we're just not properly killing some bits.

##### **Geohot** [[00:33:02](https://www.youtube.com/watch?v=sMxM41tpijc&t=1982)]
Yeah, maybe we just need an exit handler or something.
We need to figure out what signal GitHub Actions sends to make sure we handle the shutdown.

##### **Chenyu** [[00:33:19](https://www.youtube.com/watch?v=sMxM41tpijc&t=1999)]
Cool.
Yeah, I think for now, if you got weird behavior on CI,
What I did is you log into the machine, find the stall process, and kill it.
And that's pretty much a fix.

##### **Geohot** [[00:33:36](https://www.youtube.com/watch?v=sMxM41tpijc&t=2016)]
Yeah, I was doing that too.
But I like the idea of just moving to our driver.
And then we know that all the bugs are our bugs.
And then we just got to fix them.

##### **Chenyu** [[00:33:46](https://www.youtube.com/watch?v=sMxM41tpijc&t=2026)]
Yeah, yeah.
That's the goal.
I think for now the issue is there are some bugs still in AM that if we use AM for everything.
It has issues sometimes.
But looking forward to that.

##### **Geohot & Chenyu** [[00:34:04](https://www.youtube.com/watch?v=sMxM41tpijc&t=2044)]
Yeah, we got to figure out how to get fuzzers on there, finding those things.
I mean, we can also put, we got six more red boxes I can plug in if we want more red boxes to do fuzz farms and stuff.
OK, great.
Lots of red box.
lots of red box.
So yeah, no, any, any, uh, there was any, you think the like father will keep finding things if we run it for a long time?
let's try to write the best fuzzer we can and then just run it for, run it for a week.

##### **Nimlgen** [[00:34:46](https://www.youtube.com/watch?v=sMxM41tpijc&t=2086)]
So yeah, I just did some overnight runs on some machines, like for there is that.
So yeah, I think we have more machines that would like to keep doing this.

##### **Geohot & Chenyu** [[00:35:02](https://www.youtube.com/watch?v=sMxM41tpijc&t=2102)]
Yeah, I mean, we have a whole bunch now we can use.
I don't know.
I'll have to get those new machines plugged in.
That's going to take time.
But actually, we're out of power right now.
All the tiny rooms?
Yeah.
All the tiny rooms are out of power.
The compute cluster has more power.
But feel free to use 32 and 15 and just run fuzzing on them constantly.
I'll just coordinate in the access channel.

##### **Chenyu** [[00:35:44](https://www.youtube.com/watch?v=sMxM41tpijc&t=2144)]
Let's move on to TensorCores.

##### **Ignaciosica** [[00:35:48](https://www.youtube.com/watch?v=sMxM41tpijc&t=2148)]
Hi.
Hello.
For me, it's AMX, basic AMX support for all LLVM is now ready for you.
As I said, it's not, it's like the same support as for Clang.
Like it's almost matches LLVM's output with a level of optimization one, but it's working.
And that's it for me.

##### **Geohot** [[00:36:24](https://www.youtube.com/watch?v=sMxM41tpijc&t=2184)]
Cool.
You know, it looks simple and straightforward.
I think I will.
Yeah, can I just merge this?

##### **Ignaciosica** [[00:36:40](https://www.youtube.com/watch?v=sMxM41tpijc&t=2200)]
Yes.
I mean, maybe.
I ran the tests locally, but a benchmark run, and if it passes, it could be merged.

##### **Geohot** [[00:36:49](https://www.youtube.com/watch?v=sMxM41tpijc&t=2209)]
Cool, yeah, I'll do a few tests tonight.
But yeah, I think it looks good.
And that bounty is yours.

##### **Ignaciosica** [[00:36:58](https://www.youtube.com/watch?v=sMxM41tpijc&t=2218)]
OK, cool.

##### **Geohot** [[00:37:00](https://www.youtube.com/watch?v=sMxM41tpijc&t=2220)]
You want a big bounty for making it?
You know how to make it fast?

##### **Ignaciosica** [[00:37:05](https://www.youtube.com/watch?v=sMxM41tpijc&t=2225)]
It's working in kernel.py.

##### **Geohot** [[00:37:18](https://www.youtube.com/watch?v=sMxM41tpijc&t=2238)]
I'm not sure.
I'm not sure it's just kernel.py.
You know what?
I'll throw $1,000 on that.
And do you want me to lock it to you?

##### **Ignaciosica** [[00:37:30](https://www.youtube.com/watch?v=sMxM41tpijc&t=2250)]
I'm working on the other, on the Dtype stuff.
I'm not going to be able to multitask in many things.

##### **Geohot** [[00:37:47](https://www.youtube.com/watch?v=sMxM41tpijc&t=2267)]
I'm more interested in the speed.
I'm more interested in the speed.
There's a $500 bounty.
I'll double it for you if you think you can do it.

##### **Ignaciosica** [[00:37:58](https://www.youtube.com/watch?v=sMxM41tpijc&t=2278)]
Well, I try this week on focusing solely on that.

##### **Geohot** [[00:38:04](https://www.youtube.com/watch?v=sMxM41tpijc&t=2284)]
Great.
Yeah.
$1,000.
We need...
Like, TinyGrad's a combination of stuff that's all breadth first and depth first.
Let's go depth first, and let's make that AMX fast.
Do you see sort of how to do it?
It's not kernel.py.

##### **Ignaciosica** [[00:38:26](https://www.youtube.com/watch?v=sMxM41tpijc&t=2306)]
Yes, I mean, hand coding the kernel, it's... I have an idea.

##### **Geohot** [[00:38:36](https://www.youtube.com/watch?v=sMxM41tpijc&t=2316)]
Cool.
Yeah, it's fun.
It's fun, and it'll show that you can work on a different part of TinyGrad.
And I think that's a good path.
Yeah, you've got to kind of create.
It's kind of like right now we have, so define ACC.
We have define ACC, define local, and define global.
I think this is more than just the AMX thing.
This is kind of more generic.
You want to add another UOp.
Like define ACC.
ACC is the wrong name for that.
That's actually a register.
Define ACC as a register.
And then define local as like the local memory.
So there's like a third kind of, there's a fourth kind of thing, which is like special register.
So you can add something like define special register and then add loads and stores to that special register and then have them cancel out when you do the accumulate.

##### **Ignaciosica** [[00:39:35](https://www.youtube.com/watch?v=sMxM41tpijc&t=2365)]
Cool.
I think I know what you mean.
Yes.
Great.
I tried to make a good work.

##### **Chenyu** [[00:39:48](https://www.youtube.com/watch?v=sMxM41tpijc&t=2388)]
Cool.
Let's also add a channel somewhere for the CPU program or LLVM or CLANG speed.
I don't think we have that.

##### **Geohot** [[00:40:01](https://www.youtube.com/watch?v=sMxM41tpijc&t=2401)]
OK.
Yeah, we'll just call it CPU speed.
Yeah.
I was thinking, I bought a notebook this weekend.
I was writing in the notebook and I'm like, assign, what are we assigned to a defined ACC?
That's not really the right thing.
What we really want to do is store in a defined ACC.
It's like a store to a register.
Yeah.
And then I was thinking about how like loops, our range is kind of the wrong abstraction for loops because range itself is the induction variable, but we could take the range and rewrite it as a defined ACC add one compare kind of thing.
And I'm thinking of other ways.
I was trying to get ChatGPT to tell me how compilers represent loops in DAGs, and they don't.
They only have DAGs for basic blocks, basically.
They have a separate algorithm which does basic blocks.
So yeah, we're pushing the frontier of data flow programming languages.
in compiler tech, unless there's papers that ChatGPT doesn't know of.
Great.

##### **Chenyu** [[00:41:38](https://www.youtube.com/watch?v=sMxM41tpijc&t=2498)]
Any update for ONNX?
I think I need to review one huggingface script PR.
Anything you want to add, you can type.
OK, and while we wait, let's move on to other bounties, starting with WebGPU float16.

##### **Geohot** [[00:42:17](https://www.youtube.com/watch?v=sMxM41tpijc&t=2537)]
You have speaker rights if you'd like to talk about it.
I clicked the link on my phone, but then I got impatient.
I wonder if it's good.
Yeah, there's a link in the WebGPU thing.

##### **Chenyu** [[00:42:45](https://www.youtube.com/watch?v=sMxM41tpijc&t=2565)]
No, this is for the WebGPU float16 support.

##### **Geohot** [[00:42:50](https://www.youtube.com/watch?v=sMxM41tpijc&t=2570)]
Oh, not float16.
Oh, OK.
This is tiny chat.
Sorry.
WPMED.
Oh, you don't have speaker?
Oh, now you have speaker.
Sorry.

##### **Chenyu** [[00:43:00](https://www.youtube.com/watch?v=sMxM41tpijc&t=2580)]
It's 8653.
Looks all green.

##### **Wpmed** [[00:43:13](https://www.youtube.com/watch?v=sMxM41tpijc&t=2583)]
Sorry for the background noise.
So the first part of the bounty was auto-generating the Dawn engine, and that's been merged.
And the second part is also ready for review, which is actually adding their F16 support.

##### **Chenyu** [[00:43:36](https://www.youtube.com/watch?v=sMxM41tpijc&t=2616)]
I see now it's D-type supported, support half, and...

##### **Wpmed** [[00:43:45](https://www.youtube.com/watch?v=sMxM41tpijc&t=2625)]
Yeah.
Yeah.
And I added a bitcast a string rewrite?
Because so there's no short and ushort, in a webGPU.
We only have u32 and that made this special handling.
So it's six line overall in core.

##### **Chenyu** [[00:44:06](https://www.youtube.com/watch?v=sMxM41tpijc&t=2646)]
That's probably fine.
Do you have a, uh, do you have a link to stable diffusion that you previously deployed by float16?

##### **Wpmed** [[00:44:15](https://www.youtube.com/watch?v=sMxM41tpijc&t=2655)]
Yeah, it's in the webGPU channel.

##### **Chenyu** [[00:44:15](https://www.youtube.com/watch?v=sMxM41tpijc&t=2655)]
Oh, OK.

##### **Geohot** [[00:44:27](https://www.youtube.com/watch?v=sMxM41tpijc&t=2667)]
Here looks good.
I will test.
OK.
On my list to test tomorrow is this one.
And the AMX one.
And I think they both look good.
And I will test them tomorrow and get you guys the bounties.
Do you have other suggestions for new webGPU bounties?

##### **Wpmed** [[00:45:00](https://www.youtube.com/watch?v=sMxM41tpijc&t=2700)]
Can you repeat the question?
Sorry.

##### **Geohot** [[00:45:14](https://www.youtube.com/watch?v=sMxM41tpijc&t=2714)]
Oh, do you have suggestions for other WebGPU bounties?

##### **Wpmed** [[00:45:24](https://www.youtube.com/watch?v=sMxM41tpijc&t=2724)]
I think it's mostly for WebGPU, but I think it would be really good to have export model in core because I had for a client, they wanted to port their stuff, TinyGrad stuff to WebGPU.
And if you just pip install TinyGrad, you don't have export model.
But I think it would be really nice if you just had that when you pip install.
So you have to actually clone the repo and stuff because it's in extra currently.
So I think it's a bigger bounty, but maybe that would be nice that you can use that.
Yeah, I think that would be nice.

##### **Geohot** [[00:46:06](https://www.youtube.com/watch?v=sMxM41tpijc&t=2766)]
So you're saying bring export model logic into main TinyGrad?
Cool.
I'll put $1,000 on that.
Export model in main TinyGrad.
It is a refactor bounty, so I will lock it to you No pressure to do it or not do it the problem with
uh, refactor bounties that I don't lock to somebody who has contributed before is you get the absolute, you know, I'm going to get somebody who just is like, Oh, I just need to copy and paste this file.
ChatGPT told me, I just drag it into this folder and now it's in main tinygrad, please pay me bounty, sir.
And that's just not how it works.
Um, but yeah, so, uh, I'll put a thousand bucks on that.
Um, I know you're doing, uh, contract work using, uh, using web GPU stuff.
Uh, so, you know, if it, uh,
If it helps you out, if it kind of isn't already on your path already, I'll put a thousand bucks on making it clean.
Cool.

##### **Chenyu** [[00:47:20](https://www.youtube.com/watch?v=sMxM41tpijc&t=2840)]
Sounds good.
Move on to TinyChat.
I tested it on my Pixel phone, and it seems to work fine.
Similar speed to, I think, five tokens per second.

##### **Hooved** [[00:47:31](https://www.youtube.com/watch?v=sMxM41tpijc&t=2851)]
Cool.
Glad to hear that.
Yeah, so I'm pretty happy with some progress I made in the past few days where I was able to get webGPU to work, at least on my phone.
And I think on maybe hopefully on newer phones, or at least on my phone, that seems to work very smoothly.
Rarely crashes on load.
I only ever get crashes on load.
But the webGPU load seems to be very stable.
Loading the WASM version.
It's less stable.
I'm still figuring it out.
I think I've narrowed down where it's failing, where it's crashing on my phone when I load Wasm.
And it seems to be copying data from the main JavaScript space to Wasm module space.
That seems to be unstable when you do a lot of those copies using the typed array dot set method from the JavaScript byte array to the Wasm instances memory.
So I have AB tests where if I just don't do that and just let the arrays sit, I don't crash.
But if I try to copy them into Wasm, I crash.
So not consistently, but that just seems to be the root cause right now.
So I'm trying to work around that, trying different ways to get the data into Wasm.
This is just like the icing on the cake.
It sort of still works if I just refresh the page after it crashes, but I want it to just be really smooth.
And then that sort of gets it to where I want to be.
And after that, it's just potentially some minor things like increasing context window, because right now it's only like 1024 tokens.
And then, of course, once you go over that, the model just spits out gibberish because memory access is probably just undefined behavior or reading into other parts of memory at that point.
So if we can just increase the context window a little bit and then some other minor things maybe if they're quick.
But once that's done, I would then just try to get my code cleaned up
I was pretty interested at what you guys just discussed about the export model, moving that into main TinyGrad.
I think that's a great idea.
I think, you know, a lot of the value even of the TinyChat bounty is just
it's not even really the app itself.
It's just showing people, Hey, like you can build this kind of thing with tinygrad.
Right.
And so people might want to, yeah.
So, so I think that's a great bounty.
Um, that would, I was almost going to do, try to do not move it into main tinygrad, but try to make my compile stuff cleaner and i still will try to make it cleaner but now i have to just take that into keep that in mind um that you know maybe i shouldn't try to do too much if it's going to be covered by the other bounty so so yeah just just trying to clean it up and and then that's it 

##### **Geohot** [[00:50:47](https://www.youtube.com/watch?v=sMxM41tpijc&t=3047)]
if you're interested in it if you're interested in it too i am happy to uh
I'm definitely happy to split the bounty or you guys, you guys figure it out, uh, how you want to like, like I see this being kind of a big effort.
Um, and I think it's really valuable and I'm down to, I'm down to incentivize it more.
Like I'm down to pay a thousand dollars for that bounty, a thousand dollars for export model.
if there's like another thousand dollar bounty here, like webGPU is worth several thousand dollars to us, probably not 10,000, but something like 5,000 total is, is probably, uh, like for like a really clean way to export things to web GPU.
Um, so, I mean, yeah, we run into the, we run into sort of the, the issues with the, with the exactly what's a clear bounty here.
Uh, you know, especially anything that's a refactor.
Uh, but, uh,
Yeah, I'll lock the bounty to both of you, and I'll double it to 2,000.
But I want it to be really nice.

##### **Chenyu** [[00:52:07](https://www.youtube.com/watch?v=sMxM41tpijc&t=3127)]
So specifically for TinyChat, do you know our current speed of loading a model is
It's already close to a limit.
I think there's definitely you need to wait.
Even if you have downloaded the model, loading the model to memory time is still pretty long.
And I don't know if it's close to a limit now.

##### **Hooved** [[00:52:36](https://www.youtube.com/watch?v=sMxM41tpijc&t=3156)]
If I understand the question correctly, you're just trying to understand what's taking time in the entire launch process, is it?

##### **Chenyu** [[00:52:44](https://www.youtube.com/watch?v=sMxM41tpijc&t=3164)]
Yeah, can we be faster?
Because George is going to say he got impatient.

##### **Hooved** [[00:52:49](https://www.youtube.com/watch?v=sMxM41tpijc&t=3169)]
Yeah, so I intentionally had to throttle the, I'm not sure I'm actually throttling it, but I had to limit the concurrent downloads on phone to two, because
or it seemed about the same as five.
I'm not sure that it even makes a difference to add more.
But let me break down real.
I'll try to be concise here.

##### **Chenyu** [[00:53:14](https://www.youtube.com/watch?v=sMxM41tpijc&t=3194)]
I have already downloaded the model, I'm pretty sure.

##### **Hooved** [[00:53:18](https://www.youtube.com/watch?v=sMxM41tpijc&t=3198)]
OK, so from cache you mean.

##### **Chenyu** [[00:53:20](https://www.youtube.com/watch?v=sMxM41tpijc&t=3200)]
Yeah, so I'm just curious.
Now every time I refresh the page, it still says loading the model and the load.

##### **Hooved** [[00:53:27](https://www.youtube.com/watch?v=sMxM41tpijc&t=3207)]
Right, right, yeah.
I think, yeah, I think it's just, I think the main bottleneck there, and I could be wrong, but I think it's just the time it takes to read from IndexedDB into memory.
I need to go and actually benchmark to understand, like to profile it.
I don't have a good answer for you right now, but I think it's some split between reading from IndexedDB and then, you know, either writing to a GPU buffer or loading into WASM memory.
I need to profile it.

##### **Geohot** [[00:54:02](https://www.youtube.com/watch?v=sMxM41tpijc&t=3242)]
Are you doing the ggml unpack there?
Are you unpacking six bits into?

##### **Hooved** [[00:54:12](https://www.youtube.com/watch?v=sMxM41tpijc&t=3252)]
Right, right, right.
So there's two separate things there.
So one, I've actually completely got rid of the ggml stuff.
It's all quantized from float16 in tinygrad from the float16.

##### **Geohot** [[00:54:28](https://www.youtube.com/watch?v=sMxM41tpijc&t=3268)]
But if you're doing float16, aren't you downloading double the size?

##### **Hooved** [[00:54:35](https://www.youtube.com/watch?v=sMxM41tpijc&t=3275)]
No.
So here's what I do.
When I compile, before anything ever goes to Hugging Face or the browser or anything, just when I'm compiling and preparing everything, I take the float16 weights into TinyGrad, I quantize them, and then I save them to disk, the quantized weights to disk.
it like split up into chunks and then i host those so the only thing that's going to... 

##### **Geohot** [[00:55:02](https://www.youtube.com/watch?v=sMxM41tpijc&t=3302)]
quantized to float16 but it is still double the size of the...

##### **Hooved** [[00:55:06](https://www.youtube.com/watch?v=sMxM41tpijc&t=3306)]
no no no i uh one thing i don't think i mentioned it but i i used the the the quantization of the linear layers that was already implemented and i implemented my own um int8 embedding quantization and tinygrad and so
So everything is being quantized to int8 with float32 scales before it ever gets hosted.
So this is different than it was a week ago, I think.
But basically, you're not doing any decompression after you download.
It's just loading from IndexedDB, for instance, directly to model with no decompression.
So the whole download size is the same as what sits in memory either in WebGPU or in host memory if you're using Wasm, which is 1.2 gigabytes.
That's what you download.
That's what gets loaded to the model.

##### **Geohot** [[00:56:09](https://www.youtube.com/watch?v=sMxM41tpijc&t=3369)]
Yeah, so I doubled the export model bounty, $1,000 each if you both work on it.
very clean and documented code.
But if we could really get this in main TinyGrad, meeting the quality requirement of main TinyGrad, I think that's very valuable.

##### **Geohot** [[00:56:33](https://www.youtube.com/watch?v=sMxM41tpijc&t=3390)]
Sounds good.
Let's move on.
Retinanet?

##### **Flata** [[00:56:41](https://www.youtube.com/watch?v=sMxM41tpijc&t=3401)]
Hello.
So for mine, I think I guess I just have a few little small updates.
My end.
So the first one I've tried to play around with the model inference for the I think the model eval script using the new data loader implementation.
So
I think on the multiple GPU, because the main issue right now is that if I use multiple GPUs versus single GPUs on inference, it's slightly faster on single GPU versus the multiple GPUs.
But with the data loader implementation, I was able to save one second, but I think it can possibly be better than that.
So I'll take a look at that after I do more on the correctness runs.
So I'll kind of put that in the back burner just for a bit.
And then I did a few benchmark runs on both TinyBox Green and Reds.
And I think on the TinyBox, if I remember correctly, I posted it, I got roughly around 22 hours.
So there's that run right there.
And I think the AM GPU is actually pretty stable.
I'm able to do continuous benchmark runs a few days ago.
So I don't think I have any problems with that so far.
And then I also started my first run as well, first correctness run rather.
And I just found out that after the first epoch, I needed more memory for eval.
So I'm going to add some sort of a JIT reset, I think, which is what we do in ResNet and BERT as well, which we have it turned on, I think, optional.
So I'll do that as well.
And then also notice that the loss function right now is kind of declining pretty slowly.
And I think I probably went pretty small on the learning rate.
So I'll have to adjust that as well and do a smaller run as well just to see if it actually goes down that much faster than expected.

##### **Chenyu** [[00:58:33](https://www.youtube.com/watch?v=sMxM41tpijc&t=3513)]
So I think what was useful before was for learning rates, you can check other people's submissions, see what their global batch size and learning rates are.
And I think it's also useful for you if you can find a workflow to find the issues like you just mentioned, like you are out of memory, because these things you don't need to wait for the whole thing to setup and the whole first epoch or whatever to figure it out.

##### **Flata** [[00:59:05](https://www.youtube.com/watch?v=sMxM41tpijc&t=3545)]
Okay.
Sounds good.

##### **Chenyu** [[00:59:07](https://www.youtube.com/watch?v=sMxM41tpijc&t=3547)]
Yeah.
Basically see what, what you can copy or learn from other people's submission.
And you should definitely get a dedicated red machine if you want to run back to backgrounds.
But, uh, I think it's still valuable for you to find a workflow that you can iterate faster.

##### **Flata** [[00:59:24](https://www.youtube.com/watch?v=sMxM41tpijc&t=3564)]
Oh, I had a question about the, uh, the examples.
Are you referring to like the other submissions from other, uh, from other teams, right?

##### **Chenyu** [[00:59:32](https://www.youtube.com/watch?v=sMxM41tpijc&t=3572)]
Yeah.
From other teams.

##### **Flata** [[00:59:34](https://www.youtube.com/watch?v=sMxM41tpijc&t=3574)]
Okay, because I was using... Go ahead.

##### **Chenyu** [[00:59:38](https://www.youtube.com/watch?v=sMxM41tpijc&t=3578)]
I think there are a lot of people that use very big batch size and maybe very aggressive schedule, like learning rate and stuff.
But usually for BERT and ResNet, if you go back a few rounds, it doesn't need to be the most recent round, but you can see the previous ones and find the one that has similar batch size.
And that should be a good reference point for how you want to schedule your learning rate and stuff and other hyperparameters.

##### **Flata** [[01:00:07](https://www.youtube.com/watch?v=sMxM41tpijc&t=3607)]
OK, sounds good.

##### **Chenyu** [[01:00:11](https://www.youtube.com/watch?v=sMxM41tpijc&t=3611)]
OK, it's an hour already.
So let's speed up.
I don't see ttomsa up here for graph rewrite 2.0.
George, if you have any comment on that, I don't know what's happening to that.

##### **Geohot** [[01:00:28](https://www.youtube.com/watch?v=sMxM41tpijc&t=3628)]
I haven't seen updates on it in a while.

##### **Chenyu** [[01:00:31](https://www.youtube.com/watch?v=sMxM41tpijc&t=3631)]
Okay.
We'll figure it out.
So for the flatten add-chain thing, I would take a look for the commutative flipping thing.
I think that also fix a bug, so we definitely want to understand what's happening there before bringing it back.
But let's leave it.
Definitely leave it for that.

##### **Geohot** [[01:01:00](https://www.youtube.com/watch?v=sMxM41tpijc&t=3660)]
It fixed two linearizer failures on Metal.
I don't know why.

##### **Chenyu** [[01:01:04](https://www.youtube.com/watch?v=sMxM41tpijc&t=3664)]
I would check that.
And...
Finally, the decoder for NV driver.
I think you already commented on that.

##### **Geohot** [[01:01:21](https://www.youtube.com/watch?v=sMxM41tpijc&t=3681)]
Yeah, so they wrote one in using the Cuvid API, using NV Cuvid.
They'll have to rewrite it in the NV driver, but NV cuvid is the first step anyway.
Just look at the I.O. controls, figure out how to send the I.O. controls.
It's overall very simple.
If they see this in the replay, no need to worry about...
Raw bitstreams are fine.
The user can do demultiplexing of the bitstream.
That's all pretty easy.
I mean, these things are so small relative to the pictures they blow up to.
But yeah, no, it'd be awesome to have support for that in NV.
And then that's our first kind of tensor that comes from a magical source.
Uh, like it's a tensor that's sourced from, from something else, which eventually gets to like how to put data, really fast data load of pipelines into tinygrad.
Uh, they can automatically do that, like HVEC stuff.
Um, I think I'll have, if that bounty works out, I'll add more bounties for, uh, things like adding JPEG decoders and anything we can use accelerated on the GPU.

##### **Chenyu** [[01:02:37](https://www.youtube.com/watch?v=sMxM41tpijc&t=3757)]
Great.
OK, that's it for the agenda.
Any last words?

##### **Geohot** [[01:02:45](https://www.youtube.com/watch?v=sMxM41tpijc&t=3765)]
Yeah, so I just wanted to talk about the, there's a whole lot of one, two, I'm going to move the AMX one down.
The AMX one's kind of special.
There's one, two, three, four, five, six, seven, eight bounties for speed.
Some of these speed bounties, some of these $300 speed bounties are solvable with like two or three lines of code.
So they're easy ways for new people to get into TinyGrad.
I posted the exact command there.
You have to run, just figure out how to make that command fast.
And yeah, I think there's what I really like about those bounties and why they're good for new people is because there's no real way to like not know that you did it.
Like with a refactor, you have no idea if you did a good job or not.
You're just going to have to, you know, maybe submit, maybe this is, but this is the kind of thing where you can get in a loop and you can be like, okay, I made this change and it got 10% faster.
Okay.
I'm still 2X off of torch.
How do I make it faster?
Right?
Like that's a loop that you can work in by yourself and improve, improve, improve, improve.
Hopefully it's addictive.
Hopefully it'll come work on speed and tinygrad.
This is who we want to hire full-time.
I will definitely like our next full-time hire really has to be somebody who can, sit with these kernels and improve the speed of them.


##### **Chenyu** [[01:04:12](https://www.youtube.com/watch?v=sMxM41tpijc&t=3852)]
Great.
I will probably also promote those bounties.

##### **Geohot** [[01:04:18](https://www.youtube.com/watch?v=sMxM41tpijc&t=3858)]
Cool.
Yeah, no, I mean, they're good.
A lot of people are thinking about this stuff with kernels.

##### **Chenyu** [[01:04:21](https://www.youtube.com/watch?v=sMxM41tpijc&t=3861)]
I think, yeah, it's also good because it's kind of standalone-ish.

##### **Geohot** [[01:04:30](https://www.youtube.com/watch?v=sMxM41tpijc&t=3870)]
Yeah, most of them are probably just going to be added.

##### **Chenyu** [[01:04:33](https://www.youtube.com/watch?v=sMxM41tpijc&t=3873)]
And the value is also clear.
You made this thing fast.
OK, that's nice.
OK, that's it for this week.
Thank you, everyone, and see you next week.

