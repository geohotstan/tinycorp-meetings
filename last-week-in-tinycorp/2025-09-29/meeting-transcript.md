# 2025-09-29 Meeting

### Meeting Agenda

**Time:** 6am Monday San Diego time, 9pm Hong Kong time
- company update
- RANGEIFY! SPEC=1
- remaining bugs (rand in jit, gpt2 weight, multi assign, const reduce folding, openpilot big rewrite stack, hashing, linalg, buf limits, cifar memory, bert)
- tuning for default
- other bounties

### Audio

[Youtube Link](https://www.youtube.com/watch?v=AX6o0lK6RZA)

### Highlights

- **[Company Update: Team in Hong Kong](#chenyu-000000)**: Most of the core team is working together from a new, large office in Hong Kong and invites contributors to visit.
- **[Company Update: TinyBox Sales](#geohot-000113)**: TinyBox Pros with eight 5090s will be sold for $50,000 as "rack mountable workstations," and a TinyBox Red V2 is also planned.
- **[Rangeify: Top Priority](#chenyu-000304)**: The company's top priority is upgrading the infrastructure with Rangeify to support more advanced features, which involves fixing numerous regressions and bugs.
- **[Rangeify: SPEC=1](#chenyu-000457)**: A new `SPEC=1` check has been added to enforce that every created UOp follows a strict specification, which will help simplify the IR after the old stack is deleted.
- **[Rangeify: Bug Fixes](#chenyu-000646)**: The team has fixed several bugs exposed by Rangeify, including `rand` in JIT affecting MNIST accuracy and a silent transpose error in GPT-2 weights.
- **[Rangeify: Multi Assign](#qazalin-000905)**: Reordering `multi` has fixed sharding bugs. A remaining issue with cyclic dependencies will be solved by making a copy rather than asserting.
- **[Rangeify: Openpilot Stack Performance](#geohot-001214)**: Geohot advises against the current approach for the "big rewrite stack," suggesting a separate stack for rewrites to avoid potential quadratic performance issues.
- **[Rangeify: Memory Usage](#geohot-001617)**: CIFAR and other models are allocating excessively large buffers. The proposed fix is to re-implement the `remove_dead_axes` function to optimize memory usage.
- **[Rangeify: Post-Merge Cleanup](#geohot-001803)**: After Rangeify is merged, the plan is to delete a significant amount of old code, including the `ShapeTracker`, `view` ops, and other UOps, to clean up the codebase.
- **[Rangeify: User-Facing API](#geohot-002309)**: There is user interest in an "outer world rangeify" (user-facing API). The team discussed its potential for use cases like data loading and plans to explore it after the current refactor is complete.
- **[Other Bounties: NIR Backend](#geohot-002740)**: Progress is being made on an NIR backend, which will enable running on NVIDIA hardware without CUDA by leveraging Mesa.
- **[Hardware: AMD Machines & eGPUs](#geohot-002846)**: Comma plans to sell its own external GPU enclosures. Issues with the AMD MI300/350 machines are being addressed.
- **[MLPerf Submission](#flata-003234)**: Flata is working on an MLPerf submission on the MI350 machines, with a deadline of next Friday, October 11th.

### Transcript
##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=0)]
We have a fairly small group, but I think we can get started. So let's start with company update. So most of us are in Hong Kong. Most of us spent the day in an office together.

##### **Geohot** [[00:00:17](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=17)]
Yeah, so if people listen to this and they've been a contributor and they want to come out here at all, we have a big office.

##### **Chenyu** [[00:00:35](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=35)]
Yeah, no, and I think, I mean, the other thing we discussed today was we can't keep, these abstractions have to work for other people.

##### **Geohot** [[00:00:45](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=45)]
They can't just be my weird shit. I think we're going to have to spend a long time after we delete the old stack, just cleaning things up and making this stuff accessible to other people.

##### **Chenyu** [[00:01:03](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=63)]
So, yeah, I think we can get started. There's still, yeah, I'll get to this next part.

##### **Chenyu** [[00:01:09](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=69)]
Great. Anything to say about TinyBox?

##### **Geohot** [[00:01:13](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=73)]
They're moving. Yeah, you're right. We only sold one last week. We only shipped one last week. We shipped three the week before.

##### **Chenyu** [[00:01:23](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=83)]
We're doing update version for Red? Yeah. Yeah. Yeah, something like that. We haven't announced anything yet. But yeah, I think there'll be a Red V2.

##### **Chenyu** [[00:01:39](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=99)]
Great. Yeah, I think someone asked the pitcher.

##### **Geohot** [[00:01:43](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=103)]
Oh, will the Reds be back in stock anytime soon? Yeah, we need to focus on TinyGrad. I don't care about this. We got someone who wants to buy TinyBox Pros too. We also have TinyBox Pros. They're eight 5090s. We're going to sell them for $50,000. Five-year rack mountable. Rack mountable workstation. Yeah, rack mountable workstation. That's the term we should use.

##### **Chenyu** [[00:02:11](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=131)]
Is it data center certified?

##### **Geohot** [[00:02:14](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=134)]
Oh, definitely not. Not at all. And if you're going to use it in the data center, you better pay attention to your license agreements. Because I'm not the one violating them. Hmm. But if you're using it for cryptocurrency mining, I believe that's okay. Yes, if you use it, it's licensed for data center deployment if you use it for cryptocurrency mining.

##### **Chenyu** [[00:02:37](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=157)]
Very important. We'll put a checkbox saying I will be okay with cryptocurrency mining. Yeah. Great. Okay, so let's go to the meeting. Let's rangeify.

##### **Chenyu** [[00:02:54](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=174)]
So, yeah, I fixed the.. RandomJet thing.

##### **Geohot** [[00:02:59](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=179)]
I fixed the GPT-2 thing.

##### **Chenyu** [[00:03:04](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=184)]
For the people in this meeting who didn't participate in our last meeting, this is the focus of the company and the top priority now. We are upgrading the infra so that this new abstraction can support more advanced stuff that is impossible now. So in the meantime, we need to fix a lot of regressions and tests. So here we discussed a lot in the office today for how to make progress. And here I think we have some ideas for focusing on making the spec, tightening the spec to make everything.. Make the possible states smaller. And here I list some reminders. I think we have a lot of bugs that are in the PR to make rangeify default. And I believe there are probably more. It's just this is the frontier of things that's failing.

##### **Geohot** [[00:04:07](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=247)]
Yeah, I did some stuff on performance today, too. I fixed the efficient NAT. Like, it mostly just emulates the old scheduler. But it seems.. I mean, it seems strictly better in all the things that work. Like, they all seem to.. The only annoying thing is we no longer have reduced splitting. So we can decide if we want to add that back or if we want to improve the kernels.

##### **Chenyu** [[00:04:38](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=278)]
I think that falls into the tuning for default part. We can quickly go through these, making sure everyone is working on some of this. Hopefully we can get this.. End of this week.

##### **Chenyu** [[00:04:56](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=296)]
Yeah, it sounds good.

##### **Chenyu** [[00:04:57](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=297)]
So spec equals to one is.. So previously.. So tinygrad is pretty much all UOp. And it's very important to limit the spec for every UOp. UOp has like source and arguments for different ops. And previously we have kind of a step check. And then we have a little bit of a step check. tinygrad has multiple passes and lower things from tensor to the intermediate ones, then lower to the linearized ones, then finally render into streams. And we have a step check to making sure when you pass this stage, what's the possible set of the UOp. But we didn't really check all the intermediate ones. We didn't have a spec for that. So George just added a spec. So we can see that the spec equals to one today. So that is kind of checking every created UOp needs to follow these specs.

##### **Geohot** [[00:06:02](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=362)]
Yeah, I think especially once we switch only to Ranger 5, we can delete a whole bunch of UOps. We can delete a whole bunch of op types. We can delete view and stop. And then we should have a relatively small spec. We can also get rid of.. We can merge assign and store. Yeah, then I think the spec overall will be pretty small. And we can check every UOp on creation. So it's important that every intermediate state preserve the spec. I fixed a few things in the de-vectorizer that didn't. Maybe there's a few things in the index stuff that don't also.

##### **Chenyu** [[00:06:41](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=401)]
Great. Okay.

##### **Chenyu** [[00:06:46](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=406)]
We can quickly go through the remaining bugs. We found a few. We found the random counter increment thing in JIT. That was the issue for Beautiful MNIST. So Beautiful MNIST, we find a few things about Beautiful MNIST. But one of it is because the random doesn't work properly with JIT. It's like creating.. It's like if you overfit one batch, you got 95%. Our current master has like 98%. And this behavior is kind of trend on a smaller batch, like gives you 97%. And things like these are very hard to debug because it just.. In this case, we got lucky because it's kind of easy to tell. It's like 98 versus 97. But just imagine in a much bigger model, it's very hard to say, okay, now our model regressed by slightly. Is it a bug or numerical or something else? So it's good that we kind of fixed.. We at least through costless. Okay. And GPT-2 weight is transposed on disk is wrong or silently wrong?

##### **Geohot** [[00:08:18](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=498)]
Yeah. It's not a range of high related bug. Range of high just exposed it because it didn't push the transpose after the copy.

##### **Chenyu** [[00:08:29](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=509)]
So what's the current behavior? It doesn't transpose?

##### **Geohot** [[00:08:34](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=514)]
The current behavior is it doesn't transpose and it's just silently wrong.

##### **Chenyu** [[00:08:39](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=519)]
Oh, but there's no like access issue or anything. Now the shape is different.

##### **Geohot** [[00:08:47](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=527)]
The shape changes, but it just doesn't actually transpose.

##### **Chenyu** [[00:08:51](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=531)]
Anyway, this is was buried. Next is multi assign. I saw the change to move multi earlier before the range of our stuff. Does it fix?

##### **Qazalin** [[00:09:05](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=545)]
Yes, it does fix the sharding stuff, which are the main bugs. There are a few remaining bugs in assign and multi. I think if I fix that, all the other tests in multi should pass. And they have eight more failing tests. I also fixed permuted assign today. So that should be good. And right now, the only failing test in assign is if you have a die that would create a cycle, the old scheduler would assert. The new one just gives a wrong answer. The path forward is to either fix diamonds by just making a copy. If that doesn't work, I'll just assert it to like to take that pattern.

##### **Chenyu** [[00:09:59](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=599)]
Well, that's the test that expect 4444 but gives you 7777.

##### **Qazalin** [[00:10:04](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=604)]
Yes, the correct the old behavior was to assert and say you can't do this. I don't know if there are thoughts about.

##### **Geohot** [[00:10:15](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=615)]
I think getting the copy is probably better. That's easy.

##### **Qazalin** [[00:10:20](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=620)]
Great. Yeah. Currently range of fight does actually realize the input to the assign. It's just that sometimes it gets optimized away when it shouldn't.

##### **Geohot** [[00:10:33](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=633)]
Yeah, if you detect the cycle there, you can just not optimize it away.

##### **Qazalin** [[00:10:37](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=637)]
Yeah, we'll just. Okay. So it's probably enough to not do anything for that.

##### **Chenyu** [[00:10:43](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=643)]
Great. That's the plan.

##### **Chenyu** [[00:10:46](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=646)]
Next is cons reduce folding. I have a PR that does this. The issue is in some other I think unrelated part. It has some index because I just reuse some of the later patterns and I think there are patterns left cast index into something else. I will revisit this after C's fixed the indexing issue and see that make this easier.

##### **Geohot** [[00:11:18](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=678)]
Yeah, I think if we're careful about always making sure the types are right on index.

##### **Chenyu** [[00:11:23](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=683)]
Yeah, because this this idea, the idea of doing this is easy. It's just not so clear to me. It was not clear to me what the output you have should be looking like and like why sometimes look at the types are right.

##### **Geohot** [[00:11:37](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=697)]
Yeah, you should never invalid should only exist on index. So what you do is you create one where with an index at the end of people's into this meeting. I made it already. So the cons that is invalid is never changed from index type, but you want to not change the last where also.

##### **Chenyu** [[00:11:55](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=715)]
Okay. Yeah.

##### **Chenyu** [[00:11:58](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=718)]
So this will revisit later. There are some discussions for I think the open pilot. Yeah. Big rewrite stack. I saw a seed has a tent and there are yours or comment on.

##### **Geohot** [[00:12:14](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=734)]
Yeah, I really wouldn't do it. I really wouldn't do it like that again. This is just throwing shit at the wall. Like don't do that. I think what you have to do. Well, first off instrument it like you can instrument how many rewrites are happening. And yeah, don't do. See if there's any square behavior. I think what you want to do is if we write spot ready, you don't just want to put it on the end of the stack. You want to put on a separate stack.

##### **Chenyu** [[00:12:44](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=764)]
And then that stack will only be visited. The main stacks empty. Then so that's equivalent to every time you insert something that is.

##### **Geohot** [[00:13:02](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=782)]
Okay. Anyway, yeah, that's just over the king. Yeah. Yeah. So now we're going to change that only touches the rewrite not ready part and not everything.

##### **Chenyu** [[00:13:12](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=792)]
Okay.

##### **Chenyu** [[00:13:16](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=796)]
Sounds good. Next is hashing. What's very fine. Anything hashing. Is it incorrect or slow or something else? Yeah, there's some real that fails currently. What do you mean by fail? Like the error is out. Like it doesn't. Okay.

##### **Chenyu** [[00:13:53](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=833)]
Okay.

##### **Chenyu** [[00:13:57](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=837)]
So that's hashing.

##### **Chenyu** [[00:14:01](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=841)]
It's not hat Linear algebra you R and SVD, I think it's related to a sign, but I can it's really cool. double check. And that tells me how the looks like. I think we've done all the IQs and system dentist sites so far. I think it's related to a sign. But I don't know if it's just that and not clear how to fix it yet. This I will look later. Next is the thing is kind of an optimization, but kind of important is the buff limits for metal and for web GPU. I saw Nimmo, do you have a temp on that? I don't know if you have update on that.

##### **Nimlgen** [[00:14:59](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=899)]
Yeah. I fixed metal on non-rangeify because it was broken and didn't account for variables. And we have tests now. And because of that, actually, I used to implement buffer limit before rangeify, so it was as simple as realize. But because we need variables, it should be after rangeify because they happen at this stage.

##### **Chenyu** [[00:15:29](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=929)]
So yeah. And you like to take the variables from the Thank you. I wouldn't do that. I would do it at the last minute. After the first bufferize pass. Yeah.

##### **Geohot** [[00:16:00](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=960)], because the buffer is going to be optimized out also. Also, Nimmojin, you want to look at memory usage, just memory

##### **Chenyu** [[00:16:09](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=969)]
usage in general? Yeah.

##### **Geohot** [[00:16:17](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=977)]
So there's a function that's commented out now called remove dead axes. I think you're going to want to fix that and make that work. So what that does is sometimes there's a, you know, you're going to have to fix that. Like, if you have a P ask, that is an access going into a bufferize, that's just a range. That's not actually.. The range is actually used anywhere. And this happens with

##### **Chenyu** [[00:16:40](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1000)]
Can you post the link?

##### **Chenyu** [[00:16:44](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1004)]
Yeah.

##### **Chenyu** [[00:16:46](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1006)]
Yeah, to be commented.

##### **Geohot** [[00:16:48](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1008)]
Yeah, if you just search for remove dead axes, and it's in range of five. Okay. I'm going to bring it out now. But yeah, so I think you're going to want to make that work and then just in general look at memory usage for things.

##### **Chenyu** [[00:17:04](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1024)]
It's related to the next one. I think CIFAR now tries to allocate a very big buffer.

##### **Chenyu** [[00:17:16](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1036)]
That's a common thing.

##### **Geohot** [[00:17:17](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1037)]
But yeah, so if a range isn't used, if a range was only used in bufferize and it's not using any of its parents, then you can just remove that range.

##### **Chenyu** [[00:17:26](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1046)]
And make the buffer that much smaller. Right? Because that's just like an expanded access.

##### **Chenyu** [[00:17:35](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1055)]
Mm hmm.

##### **Chenyu** [[00:17:36](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1056)]
Okay.

##### **Geohot** [[00:17:38](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1058)]
Yeah, I would I would guess that's a lot of memory usage. Yeah, just make sure all this stuff's correct with memory planner.

##### **Chenyu** [[00:17:46](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1066)]
But uh, yeah, how have you been finding reading range of five? Um, It's fine. I think Yeah, it's it's not really polished.

##### **Nimlgen** [[00:17:58](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1078)]
But yeah, it's readable. Cool.

##### **Geohot** [[00:18:03](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1083)]
Yeah, no, I mean, there's a lot of there's a lot of polished work to do. And when you get here, and like, I think that'll be most of this month will be two basic things just getting range of five merged deletion of tons of stuff, we're going to delete the st method. We're going to delete. Well, the ShapeTracker entirely every reference to the ShapeTracker, a whole list of you ops, a whole list of ops, like opt out view. All that can go any reference to view can go. And then yeah, so those cleanups, and then better abstracting where the decisions are. So there's a bunch of decisions made in range of five. Right now, there's like range of five, one and range of five to range of five, two, and two is more aggressive about like partial buffer fusion. But yeah, we're gonna have to like expand the notion of the memory planner to see what we can fit in locals and what we can fit in globals and stuff.

##### **Chenyu** [[00:19:10](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1150)]
That's good. Leading stuff is nice. I also just pushed into my library.

##### **Chenyu** [[00:19:23](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1163)]
So my library and, and yeah, like Noel or separate your own libraries here as well. And like, and they're saying like 30 50 or so in the mainstream or like like 15,000 or something like that. But yeah, just, just adding this to the script. So I don't know what's happening. We will take a look.

##### **Chenyu** [[00:20:04](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1204)]
I see. OK.

##### **Geohot** [[00:20:07](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1207)]
Yeah, that has to be the remove data access thing. They cannot allocate 76 petabytes or something.

##### **Chenyu** [[00:20:19](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1219)]
And they didn't really check, but maybe stable diffusion and BERTs. We have a smaller version of that in test reward. So probably also shows there.

##### **Chenyu** [[00:20:32](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1232)]
Yeah, some slight regression to comma speed. Yeah. Yeah, we don't want to regress that. Yeah, I think that's part of the tuning.

##### **Chenyu** [[00:20:57](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1257)]
I think after we fix the correctness issue, then we can think more about tuning. Some of the do we like splay reduce, or what's the default optimization? Is there anything else that we need to look at? I think at least we can revisit after we fix the correctness issue. But I don't know. So far, it feels not too bad compared to a few days ago.

##### **Chenyu** [[00:21:26](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1286)]
Yeah, no, I think there's definitely been progress.

##### **Chenyu** [[00:21:32](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1292)]
OK.

##### **Chenyu** [[00:21:37](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1297)]
Anything else on rangeify? Not really.

##### **Qazalin** [[00:21:46](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1306)]
We talked about this at night. We want to also make it better in the tooling to follow the rangeify graph. Currently, the indexes are very hard to read compared to the movement hops graph before PM rangeify. That's going to be another project. Right now, I can't read that graph. It's all scattered. Yeah.

##### **Geohot** [[00:22:14](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1334)]
I think that what you might be able to do is literally just render index, like do dot render on it. And we can add a little thing which uses c style array. I think that'll look pretty good.

##### **Qazalin** [[00:22:28](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1348)]
Yeah, just not render the sources as nodes, right?

##### **Geohot** [[00:22:35](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1355)]
I mean, you're going to want to keep them as nodes too, but I would just add a separate thing to index, which just has a special render.

##### **Qazalin** [[00:22:44](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1364)]
Is there a value to these sources?

##### **Geohot** [[00:22:49](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1369)]
Yeah, you don't want to start deleting the actual ranges. Well, we can play with this tomorrow. But yeah, I don't think I actually want to delete the sources.

##### **Qazalin** [[00:23:00](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1380)]
That's right.

##### **Chenyu** [[00:23:02](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1382)]
And we have a user that is interested to know if there is a plan for outer world rangeify.

##### **Geohot** [[00:23:09](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1389)]
Yeah, we discussed this a bit today. Good, good. Yeah, see? The users want to have a world rangeify. Yeah, world rangeify.

##### **Chenyu** [[00:23:15](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1395)]
So we had a heated discussion in the office today about, should we do outer world rangeify, and if people will find it useful.

##### **Chenyu** [[00:23:26](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1406)]
I think if we can find a use case that makes sense for a user to specify things, we discussed about the inference stack. You want to abstract your data loading. You apply a function to that. Yeah. And maybe there are some other cases that this will be useful. So I think definitely after we finish the correctness and delete a bunch of stuff, making a cleaner place, we will think about what to expose. And similar to Beautiful MNIST, if we really write this and have a more beautiful version of Lake St. Louis that we offer, we definitely. We'll make it like a user-specable feature.

##### **Chenyu** [[00:24:28](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1468)]
Yeah, there's no reason that the range graph can totally

##### **Geohot** [[00:24:32](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1472)]
exist within the tensor graph. The tensor graph can't really exist. You have to get rid of the tensor graph to render things. But you can totally add a few ranges, and it should just work fine.

##### **Chenyu** [[00:24:44](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1484)]
Yeah.

##### **Geohot** [[00:24:47](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1487)]
So in theory, you can think about rangeify going one range at a time. You could take the first axis and just rangeify that, and take the second axis and rangeify that, and slowly remove things from the shape one at a time.

##### **Chenyu** [[00:25:03](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1503)]
We are going to need to view up end range, which puts things back in the shape. Yes.

##### **Chenyu** [[00:25:13](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1513)]
And?

##### **Chenyu** [[00:25:14](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1514)]
I think that's a reason why it's not a priority now, but we will think it later when we are done with the current rangeify. Yeah, there is interest. And another similar thing is the rewrite of multi. I think now if we change the order of multi, it works now. So that's great. But we definitely will want to make multi just part

##### **Chenyu** [[00:25:38](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1538)]
of the rangeify as well. Yeah. So finally, finally the right abstraction for this stuff. PyTorch is still on multi-LazyBuffer.

##### **Geohot** [[00:25:56](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1556)]
We used to have a class called multi-LazyBuffer, and I thought it was clever. It was like, oh, look, it can make a list of lazy buffers. You don't want anything like this. So PyTorch has a class called detensor, which is basically this.

##### **Chenyu** [[00:26:09](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1569)]
Yeah. And later we can use the range. Rangeify multi should naturally give us like multi-short, multi-tensor, or whatever that is. Because now you just have to.

##### **Geohot** [[00:26:24](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1584)]
Yeah, and I think with our driver, we can do something pretty incredible where we just view the same memory layout on all the GPUs and stuff.

##### **Chenyu** [[00:26:37](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1597)]
Great. OK. So let's rangeify. And with that, we can move on to other boundaries.

##### **Geohot** [[00:26:52](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1612)]
There's a bunch available if people are interested. $800 if someone can figure out how to make Winograd a generic rewrite world. Should be doable. $300 for the metal compiler actually going in the BEAM process. I think UVM's got that locked, and he's going to get it for free once the next version of Mac OS

##### **Chenyu** [[00:27:21](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1641)]
comes out, just for updating the API. If somebody can get GPT-OSS to run fast.

##### **Geohot** [[00:27:35](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1655)]
Oh, ooh, OK, the NIR backend, cool.

##### **Chenyu** [[00:27:39](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1659)]
Cool.

##### **Geohot** [[00:27:40](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1660)]
Here we have some progress there. So the NIR backend is going to give us a full path to running NVIDIA without CUDA. Mesa has a replacement for SASS. But for the, yeah, so yeah, we just render to NIR. It's pretty cool. And then we can do all the Mesa stuff too. Mesa has a Qualcomm backend. And yeah, I mean, we've made some progress in this direction, with the CPU and CPU LLVM thing. Another thing that we could search across is just which compiler to use. I bet we'll be able to make some OpenPilot kernels faster by using the Mesa compiler.

##### **Chenyu** [[00:28:26](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1706)]
Mm, mm. Yeah, OpenPilot speed. Talking about non-contiguous for search. Nice. Yeah.

##### **Chenyu** [[00:28:44](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1724)]
OK.

##### **Geohot** [[00:28:46](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1726)]
I don't know what ever happened to the person who was working on Thunderbolt GPUs, but that would be cool. We should like to, I want to test that soon too. Comma's making, Comma's going to start selling an external GPU. Because all the ones on Amazon are rip off.

##### **Chenyu** [[00:29:06](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1746)]
We made our own. All right. Yeah, going to start selling them. And they don't just work with OpenPilot devices. They work with computers too.

##### **Chenyu** [[00:29:19](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1759)]
OK.

##### **Chenyu** [[00:29:22](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1762)]
You want to share something you're working on? The AMD machine. It didn't work last week. So I didn't expect to be able to come. GPU, I was done. I cannot really hear you. Can you hear me now? Yes, go on. Last week, the AMD machine was done. It's. My GPU was done. So I didn't. My machine is done. The MI300 and the MI350 were done. They're all down? The GPU down.

##### **Chenyu** [[00:30:29](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1829)]
Now it works.

##### **Geohot** [[00:30:31](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1831)]
Oh, machine is up, but GPU dropped.

##### **Chenyu** [[00:30:35](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1835)]
Yeah. So I don't know. It's probably.

##### **Geohot** [[00:30:48](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1848)]
Well, it looks like tinyAMD3 needs

##### **Chenyu** [[00:30:52](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1852)]
to insert the AMD GPU module.

##### **Chenyu** [[00:31:00](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1860)]
OK.

##### **Chenyu** [[00:31:01](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1861)]
Nimble gen, any progress there with doing it without AMD GPU? No, I haven't done that. The only thing that still to implement

##### **Nimlgen** [[00:31:16](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1876)]
is the GMC9, I mean, like the page tables format and all these things. I mean, it's slightly different.

##### **Chenyu** [[00:31:27](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1887)]
Yeah. I see all the GPUs up in the MI300 boxes. I don't know what happened. Oh, wow. AMD4 just has six GPUs, though. I don't know what happened.

##### **Chenyu** [[00:31:47](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1907)]
OK.

##### **Chenyu** [[00:31:50](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1910)]
I think for people who are using this machine, if you find the machine is down or the GPU disappeared, just post somewhere so that people know the machine has issues. I just rebooted AMD4.

##### **Geohot** [[00:32:06](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1926)]
It only had six GPUs.

##### **Chenyu** [[00:32:08](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1928)]
Yeah. The idea is you shouldn't be blocked if the machine is bad. It won't fix it by itself.

##### **Chenyu** [[00:32:17](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1937)]
Someone needs to reboot the machine or do something. OK. What else? We have here.

##### **Chenyu** [[00:32:30](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1950)]
You have anything to say about writing on it?

##### **Flata** [[00:32:34](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1954)]
Not that much yet. I think I was talking to. I think I was talking to a copy about that JIT issue that I was experiencing with the mass select. I tried with optimize equals true. But I think the last time when I tried it last week, what happened was that it hung. So I think seeds restarted the machine. So that was OK. So I'll have to take a look into that and see if that fixes that issue. Because he also had problems with, I think, related to the on exchanges that he made. So I'll take a look into that. And hopefully, that helps with my case.

##### **Geohot** [[00:33:07](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1987)]
OK. Thanks. It'll be cool to get. We should try to get something submitted on the 350 machines.

##### **Chenyu** [[00:33:16](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=1996)]
We can. That'd be great. OK, sounds good. Do you have access to the 350s? No, not yet. We should get your access.

##### **Chenyu** [[00:33:36](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=2016)]
OK.

##### **Flata** [[00:33:39](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=2019)]
So what's the deadline again?

##### **Chenyu** [[00:33:42](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=2022)]
I think the deadline is next Friday.

##### **Chenyu** [[00:33:45](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=2025)]
I think two weeks, right? October 11.

##### **Chenyu** [[00:33:50](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=2030)]
Yeah, I think it's next Friday, 1 PM California time

##### **Chenyu** [[00:33:56](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=2036)]
or something like that. Directing on that email has data dependent shape. Great. Good and symbolic. It just work. OK. Anyway, if you are blocked by a machine, we will find your machine.

##### **Chenyu** [[00:34:20](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=2060)]
And if you have some smaller repo for things that you believe should work in user space, but it's not working, feel free to just post it, create an issue somewhere.

##### **Chenyu** [[00:34:33](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=2073)]
OK, sounds good.

##### **Chenyu** [[00:34:35](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=2075)]
Cool.

##### **Chenyu** [[00:34:38](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=2078)]
We also have Hoov here. I commented on your PR. You have anything else to share?

##### **Geohot** [[00:34:48](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=2088)]
No, not really. I addressed the LR scheduler PR, so that's ready again. And the clip one will be ready very soon.

##### **Chenyu** [[00:34:59](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=2099)]
Yeah, I think those looks fine.

##### **Chenyu** [[00:35:04](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=2104)]
I just want to make sure. I think the principle is anything that touches me, I'm going to have to fix it. The first work will come right away, depending on where I use the UI, there's winners and losers. So I kind of keep it to the very end. if you haven't��'t hit it, I have indic heleomuch would be kind of the ESYPro does more oh enter çalıştings than when you perform

##### **Chenyu** [[00:35:37](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=2137)]
everything.

##### **Chenyu** [[00:35:42](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=2142)]
what else I think we can have a short meeting today

##### **Geohot** [[00:35:53](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=2153)]
we spent most of the time in the office great

##### **Chenyu** [[00:35:57](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=2157)]
okay that's it for today thank you everyone

##### **Chenyu** [[00:36:01](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=2161)]
see you next week

##### **Geohot** [[00:36:03](https://www.youtube.com/watch?v=AX6o0lK6RZA&t=2163)]
bye bye bye
