# 2025-09-15 Meeting

### Meeting Agenda

**Time:** 9am Monday San Diego time
- company update
- RANGEIFY! https://x.com/__tinygrad__/status/1967446896081076517
- other bounties

### Audio

[Youtube Link](https://www.youtube.com/watch?v=2kpAMGBbtf8)

### Highlights

Here are the highlights from the meeting transcript:

- **[Company Update](#geohot-000012)**: Tiny boxes are selling well at the new $25,000 price point, which will be maintained before potentially raising to $29,000. The company needs competitive memory usage and runtimes with other frameworks for MLPerf submissions.

- **[Rangeify Implementation](#geohot-000053)**: Rangeify is a critical abstraction that needs to be understandable by the entire team. The most complex part is section 3a (lines 122-196) which defines movement operations. Section 3.5 will contain cost functions for trade-offs between compute duplication and storage.

- **[Memory Improvements](#geohot-000525)**: Rangeify uses about a third less memory and 30% fewer kernels compared to the old scheduler, though currently runs slower due to unfused backward kernels.

- **[Technical Architecture](#geohot-001222)**: Rangeify replaces the shape tracker system by applying movement operations directly to ranges/indexes. Key improvements include better handling of padding operations and eliminating many previous hacks.

- **[Buffer Strategy](#geohot-001439)**: The current strategy overuses buffers early in the graph for easier optimization later. Buffers can always be removed (causing recomputation) but never break correctness.

- **[Kernelization](#geohot-001749)**: Part 5 splits into kernels using similar logic to the old system but with improved debugging through tag numbering instead of graph rewrite maps.

- **[Bug Status](#geohot-003614)**: Several known issues exist including problems with disk tensor, JIT, webGPU (ULONG support), and image dtype compatibility. These need to be addressed by specific team members.

- **[Symbolic Handling](#geohot-004724)**: Need to move reshape/expand/pad/shrink arguments from uops in args to proper graph sources for better symbolic handling and deduplication.

- **[Timeline Goals](#geohot-005355)**: Target to have Rangeify fully working before Hong Kong trip, with state-of-the-art flash attention for MI350X by end of year. Multi-output support will be needed for flash attention backward pass.

- **[Development Challenges](#geohot-010102)**: The most difficult part was moving the entire optimizer from before Rangeify to after Rangeify and removing the kernel.py class that was used throughout the codebase.

### Transcript
##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=0)]
Welcome everyone. And there was this big crowd. Let's start with company update.

##### **Geohot** [[00:00:12](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=12)]
So yeah, normally I just talk here about how many tiny boxes we sold and it's good. There's lots of tiny boxes sold. The new $25,000 price seems to be good. So we will keep it for a bit longer before we raise it again to $29,000.

##### **Geohot** [[00:00:31](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=31)]
But yeah, no longer term like we're in a bad place right now. With not having anything to submit to MLPerf.

##### **Geohot** [[00:00:46](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=46)]
We need to get this this range of high stuff done. And we need to start having

##### **Geohot** [[00:00:53](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=53)]
competitive memory usage and competitive run times with other frameworks.

##### **Qazalin** [[00:01:05](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=65)]
So we're going to start with the

##### **Geohot** [[00:01:05](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=65)]
And I worry about I've written a whole bunch of these abstractions.

##### **Geohot** [[00:01:12](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=72)]
I wrote linearizer. Now range of I wrote the shape tracker. Like I worry that if these abstractions aren't understandable by other people, then I'm not doing a good job, then they're not good abstractions. Because the goal of code is not to be written or to be interpreted by machines to be read. So if people can't read the code and understand what's going on, then they're not going to be able to understand what's going on. Something's wrong. And there's stuff that we have to change everyone here. At least everyone who works at the company should be able to work on every piece of tiny grab. At least to some extent, there shouldn't be any pieces that are like, oh, we can't touch that piece. And that's how I felt the scheduler. That's still how I feel the scheduler is. I don't know how to touch the code and grouper. Like the coding grouper that like, max one reduce option. But it's very useful to do point by point ordering. So that's a good point to play with. I'm going to be going devotionally larger be, some sort ofkn Everyone who works here and all the new people who are here right now can get Ranger Phi merged without me, and I think that's a super important test. Because if that can't happen, then this is a bad abstraction and we have to go back to the drawing board.

##### **Geohot** [[00:03:14](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=194)]
I don't know, I think Ranger Phi is easy to understand, but the implementation is hard to understand.

##### **Geohot** [[00:03:21](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=201)]
The implementation can definitely be worked on. The implementation is not the best code in TinyGrad yet. It was kind of my first pass at the implementation. But hopefully each part of it can be worked on individually too. The only part in Ranger Phi that actually is interesting is part 3a. Um... Part 3a lines 122 down to 196.

##### **Geohot** [[00:03:50](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=230)]
That's the definition of all of the movement docs. Part 3.5 is kind of interesting too. Part 3.5 is where we'll put in the cost functions.

##### **Geohot** [[00:04:07](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=247)]
And even the very simple cost function that I wrote that just checks the cost of the movement docs. So that basically just says duplicate... Okay. So you get a choice many times between... Do you want to duplicate compute? Or do you want to store? So say you have two... Say you have something that's reading from a and a times two. Right? And you have another kernel that's also reading from a times two. Do you want to actually compute a times two? Or do you want both compute... Uh... Uh... Kernels to compute a times two locally? And this makes the trade-off to say that whenever it's an element-wise op, always just do it locally. Whenever it does not make a stand. Um... And that heuristic turns out to be a lot better than the heuristic that we had in the old scheduler. At least by... You can try right now. You can run Ranger Phi, uh... Beautiful MNIST. And it uses a third of the memory and uh... Like 30% less kernels. It uses a lot more memory. It uses a lot more runtime now. But that's mostly just due to... Basically this stuff enforces... Uh... This stuff gets you FuseConf backwards for free. And those kernels are never fast.

##### **Geohot** [[00:05:25](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=325)]
I'm not exactly sure why that is. Uh...

##### **Chenyu** [[00:05:31](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=331)]
Can we briefly go through... Can we briefly go through the Ranger Phi dot py and you can just say it out loud like which part are hack? Like I said, I don't know. I don't know what the DLT should be called.

##### **Qazalin** [[00:05:44](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=344)]
Sure. Sure.

##### **Geohot** [[00:05:45](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=345)]
Uh... Okay. So the first part, part zero, uh... Do some cleanup rewrites. Mostly copy from the old stuff. That's all hacks. Uh... And can all pretty much be deleted. You can see half of it's commented out. Um... That's mostly due to like bugs in the spec. I already fixed the const thing. So like there was that const hack. So then I fixed that in ops. Um... You can see there's actually a different Ranger Phi.

##### **Chenyu** [[00:06:08](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=368)]
Everything... Everything in part zero if can be removed, we should remove it. Is what you're saying?

##### **Geohot** [[00:06:13](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=373)]
Yes. Yes. Okay. Um... Okay. Then part one.

##### **Geohot** [[00:06:20](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=380)]
So I've drawn a distinction between contiguous and realize.

##### **Geohot** [[00:06:31](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=391)]
So it's still called... It's still called...

##### **Geohot** [[00:06:34](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=394)]
The pattern matcher is still called add contiguous, but should be called add realize. So contiguous is a user operation that says the user... Demands this be a buffer. Realize is a system operation that says, hey, I'm going to try to make this a buffer, but you're allowed to change that later if you want. Like you're allowed to optimize this buffer out. Um... But yeah, so part one isn't really a hack. Part one is kind of just saying that like, I mean, it's a hack, but it's a longer term hack. Uh... Saying things like, okay, copy. You have to realize the parents and children have copied.

##### **Geohot** [[00:07:15](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=435)]
Okay.

##### **Sieds Lykles** [[00:07:16](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=436)]
Um...

##### **Geohot** [[00:07:16](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=436)]
Anything that's in the sink, you want to realize.

##### **Chenyu** [[00:07:18](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=438)]
Anything that's a sign related issues, likely this part.

##### **Geohot** [[00:07:26](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=446)]
Uh... Anything that's a sign related.

##### **Chenyu** [[00:07:28](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=448)]
So there are several issues now is rectified a sign.

##### **Geohot** [[00:07:33](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=453)]
Oh, I don't think those are in this part. Uh... I fixed most of them too, I think. At least... So the current assign and master is completely broken.

##### **Geohot** [[00:07:47](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=467)]
Uh... The current assigned and master... I have... There's a test now that has an if rangeify in it because it'll only pass with rangeify. Um... So I think the assign is... Oh, you mean the assign in the diamond problem. Yep. Yeah. So the diamond problem is not caused by this. Uh... The diamond problem... This actually, you might be able to fix the diamond problem here. One solution to the diamond problem is to always make a copy before the assign and then remove the copy if you want to later. So like one way to always... Like the problem with the diamond is when you have a kernel that's going to access both the assigned and unassigned version of a buffer.

##### **Geohot** [[00:08:31](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=511)]
But one way to fix that is just always... Yeah.

##### **Qazalin** [[00:08:37](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=517)]
Okay. Okay. Okay. Okay.

##### **Geohot** [[00:08:41](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=521)]
Okay.

##### **Geohot** [[00:08:42](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=522)]
I'm not sure exactly what the right fix is for that, but I don't think that's because of hacks here. Okay. So then... Uh... Part two is definitely not a hack. Uh... Part two just labels all of the children. Oh well, okay.

##### **Geohot** [[00:09:01](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=541)]
Lines 106 to 108 are a hack.

##### **Geohot** [[00:09:04](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=544)]
I gated it so that not all children show up. Okay. But that can be removed now and can be cleaned up later. But the idea of going through the graph and figuring out where children are is not a hack and is a fundamental thing. Because you want to do things differently depending on...

##### **Chenyu** [[00:09:26](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=566)]
What's the difference between ops-child and ops-children?

##### **Geohot** [[00:09:31](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=571)]
So ops-children is the root node and ops-child has things going off of it.

##### **Geohot** [[00:09:42](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=582)]
So if you have like... let's say I have like a...

##### **Geohot** [[00:09:48](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=588)]
A child is a child of children. A child is a child of children, yes. You kind of don't need the children op. I tried it without it. And just having the child ops on the other op. But there were some annoyances there. It was better to just have them both. So yeah, it is a little bit of a... Maybe add a little wider graph with a children and then as many childs as you want on the op.

##### **Geohot** [[00:10:24](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=624)]
So that's just us children extraction.

##### **Geohot** [[00:10:26](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=626)]
That one's easy to see what it does in Viz. Okay. 3a. Not many hacks in 3a. 3a is the replacement for the shape tracker. So this in a lot of ways is the definition. Of what all of the movement ops are. With a few more little cleanups there, there might be some subtle issues in that reshape function around symbolic. Whereas like symbolic has the stride of the max. But the shape of the thing. So yeah, there might be some subtle things in reshape with that. I think pad has been fixed up nicely to now use all the valid stuff. Hopefully it has. Yeah, I see ups invalid here. So that all should be pretty good. Spanned is pretty straightforward. Tracks these ending ranges that can maybe be deleted.

##### **Geohot** [[00:11:30](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=690)]
And then shrink permute and flip are so simple that. They can be written in line. So these are like the definition of the movement ops now.

##### **Geohot** [[00:11:43](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=703)]
Yeah, it's like an existing minute runs through them. And then there's the other ops. When you're running range of eyes through the other ops. That's what part 3b is. There's a lot of logic to deal with children here. So basically, if you have a node with two children, you look at the ranges in both the children. If the two sets of ranges in the children are identical, then you could ignore the fact that it has children. This will happen in things like relu. Which has like a little a little cycle inside of it where you're doing this where in this max on the same input and then combining them later.

##### **Geohot** [[00:12:25](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=745)]
So.

##### **Geohot** [[00:12:29](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=749)]
Then interesting thing. So if they totally don't match. If they have totally different sets of ranges. Like that's what you'll see in like a long edge and a gradient. Then they. You have to fully buffer eyes. You have to fully insert a buffer there. You have to realize everything at that point. But then with things like flash attention, you'll find that often they only mismatch on like one or two axes. And then you can create a buffer that doesn't take up the whole. That doesn't that's not everything. A buffer that's only around for local context. So that's what that range of I equals two is. You can see online 286. There's an assert range of five is greater than one. So there's also some logic on 266 for that. So with a range of five equals one, it will either not insert a buffer or will insert a full buffer. And I think we don't have to get partial buffer stuff working yet. There's also some logic to handle partial buffer in map partial realize. But if you look at like map realize. Map realize is probably a good function. If you want to understand like the core logic of range of I. It's a four line function that just creates a whole new set of ranges. Index is based on those ranges. And then creates a buffer based on those ranges too. You have like a buffer that's indexed based on a new set of ranges.

##### **Geohot** [[00:13:54](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=834)]
And that's what it realizes. Yeah. So that's the logic in 3B.

##### **Geohot** [[00:14:03](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=843)]
Yeah. I wouldn't say there's so much hacks. But yeah, like once range of I1 is stable and good and we start moving into range of I2, there'll be some changes made there. 3.5 is the cleanups. So 3.5, my strategy has been to overuse buffers earlier in the graph. Like anywhere you might want to buffer, just insert it. They're kind of painful to insert later. You can. But it's a lot easier to just remove them later. So yeah, insert extra buffers where you might want them.

##### **Chenyu** [[00:14:39](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=879)]
Yeah. And that should not affect the correctness anyway, right? It's like the later removal ones are optional.

##### **Geohot** [[00:14:48](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=888)]
Yeah.

##### **Geohot** [[00:14:49](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=889)]
So you could always remove a buffer. However, sometimes when you remove a buffer, you're doing an entire recomputation of that buffer.

##### **Geohot** [[00:15:01](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=901)]
Yeah. Yeah.

##### **Geohot** [[00:15:03](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=903)]
So yeah, it's never wrong. You can actually remove all the buffers. At any point, you can remove every single intermediate buffer. And then you're going to get some horrendously slow kernel, which recomputes everything every time it needs it. Yeah. I think maybe I've shown off some kernels that look like that where you can put an entire model in there.

##### **Chenyu** [[00:15:24](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=924)]
That was before you have some cost function to do some least bufferize. Everything was super slow. Super slow.

##### **Geohot** [[00:15:33](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=933)]
Well, before I had any cost function, what it was doing is it was creating lots and lots of buffers, which lots and lots of buffers can be slow, but it's a fixed overhead slower. You can really see this with two gems. You can really see this with A, like A at B at C. So if you don't do any bufferizations of the intermediate, you end up with...

##### **Geohot** [[00:16:02](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=962)]
Recomputing everything in the first matrix multiply n times. So you can do a full bufferize.

##### **Geohot** [[00:16:14](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=974)]
You can do A, A at B, store that in a buffer, and then do the thing stored at C. And that's a full, normally how you do two sequential gems. But you can also do a partial bufferize. We only store one row. And this is also correct. And there's logic to do that. That's like the range of high equals two stuff, but we don't even need to get any of that stuff working yet.

##### **Geohot** [[00:16:42](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=1002)]
But that's... The whole point of this is to eventually enable things like that. Let's continue with range of high four.

##### **Geohot** [[00:16:52](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=1012)]
Yep. So part four, put in buffers for bufferize. It converts the bufferize uop into super. It stores to actual buffers. It actually creates the buffer at this point. And then there's a bunch of logic for assign. Yeah, there's some hacks in there. Some stuff in there could kind of be changed. But the forced reshapes are there. I don't think we actually need those. And then... Yeah, so we'll get to that later. And then part five splits into kernels. So part five is pretty much the same logic as the old thing, which just says every store to global needs to be in its own kernel. I also added something this morning to renumber the ranges in the kernels, because all these ranges have global numbers. So in each kernel, I renumber them to be a local version of the number. And this allows the deduper to work.

##### **Geohot** [[00:17:49](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=1069)]
This also converts the buffers into defined globals. Yeah. So I'm going to do a little bit of a test here. And then I'm going to do a little bit of a test here. And then the big function at the bottom, get range if I map.

##### **Geohot** [[00:18:09](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=1089)]
So the old kernelize used to use this function called graph rewrite map. Graph rewrite map was a pain to understand. When things would break, you couldn't see it in viz. There wasn't really a way to debug it. So I wrote it in a different style here. The first pass just goes through the kernel. The second pass just goes through the tensor graph and assigns each UOP a number. And then you preserve these numbers all the way through. And then that way we know we have a way to correspond the UOPs in the big graph to the final buffers that are assigned to them. So you can see the logic on line 575 looks for all the buffers that are being created and says, OK, what numbers are the buffers being created on? Those are the ones that I'm going to put back in the big graph. Those are the ones that I'm going to like. Like those are the ones that I've actually realized and can safely put back in the big graph so that they're like the users and have to recompute tons and tons of stuff.

##### **Chenyu** [[00:19:12](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=1152)]
In line 571, it says ranges with length one horizontal handle, right?

##### **Geohot** [[00:19:21](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=1161)]
Yeah. So if you use full symbolic, it converts ranges with length one. Into constant zero. And there's just a bunch of things that don't that expect a range like the stores expect a range that might be a simple fix.

##### **Geohot** [[00:19:39](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=1179)]
Like, yeah, range with length one is equivalent to zero. But there's just some stuff not handling that correctly. And then the fix is.

##### **Geohot** [[00:19:56](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=1196)]
So I'm going to use the sign logic I have not tested. I just copied that verbatim from the old one. I don't know if it's correct. And then in the end, we have this thing becomes map where we look for all tags on the sink. The tags on the sink that were assigned to in 577. And then put them in the becomes map, which is the graph, which is the math that's returned to a tensor up high to actually convert the tensors into the ups. I remember you ups are immutable. So the only way that a buffer can actually become a real buffer is that the tensor, the pointer in the tensor is replaced the point to the buffer instead of to the the U of describing the compute.

##### **Chenyu** [[00:20:42](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=1242)]
So there are three you up you up map here. Colonel underscore assign a sign underscore rep and becomes underscore map.

##### **Geohot** [[00:20:51](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=1251)]
So Colonel underscore sign. And the sign underscore rep. I think Rosalind wrote this stuff. I have no idea what it does. I just copied it verbatim. Well, I understand like what it does. I understand what the problem that this thing is fixing is. We can get into what the problem is. But I don't understand how this this I haven't read this code and understand how it works. Becomes map is I did write that becomes that is the single you up to you up map that says. Here you have this a plus B. And I've created a buffer on the output that actually contains a plus B cool becomes map maps from the A plus B you up into that buffer.

##### **Geohot** [[00:21:41](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=1301)]
Okay. So there should be one you up you up dictionary.

##### **Chenyu** [[00:21:46](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=1306)]
The other ones hopefully we can figure it. So every you up should only be updates once. Like every time you change a value of become maps key. I mean, you shouldn't change the value of the key that's already existing in the map.

##### **Geohot** [[00:22:03](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=1323)]
No, definitely not. Yeah. Those the the key side of that becomes map and we can document this better. The key side of that becomes map are you ups that exist in the original big graph. And then the output you ups are buffers and potentially some movement up.

##### **Geohot** [[00:22:32](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=1352)]
So you can see that the Becomes map was the way we used to do this.

##### **Geohot** [[00:22:35](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=1355)]
Unfortunately with gravity right map. It was really annoying to figure out like what should go in and becomes map. We had some logic to do that, but it had bugs. But now with the tag numbers. At least with the tag numbers. It's super easy to debug. You can just go and visit and you can be like, oh cool. Okay, great. That's tag 87. Also like we don't have to like track this metadata through all this stuff anymore. You can see all the metadata stuff is just handled online 531 in a one liner. That just looks in the in the in the input list of you ops and says cool. You up 27. Great. You work home 2D.

##### **Geohot** [[00:23:16](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=1396)]
Great. I'll put that in the metadata. Yeah. When you computerize the data, does it work automatically. Okay, delicious time when I could try to get constantly sitting. I'd do this корい luciana answer to that. So just go scrolling well.

##### **Geohot** [[00:23:48](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=1428)]
3a is the part that actually applies the movement ops to the ranges. So this was kind of the whole key insight of Rangeify. So Rangeify has two eyes. It has one buffer eyes. Buffer eyes takes in a data and a set of ranges, and then it creates a buffer and stores the data at each one of those ranges. So if you want to create a buffer that's like the result of a plus b, and a plus b are tensors of size 10, you'll have a plus b as the first input to buffer eyes, and then the second input to buffer eyes will be that range 10. And that says create a buffer of size 10 and store all the outputs there. Then you'll also see in map realize that it creates an index with those ranges beforehand. That tells you how to index into that buffer. That tells you where, given the range, you're going to find each thing that corresponds to that range. So when it's created, when it's realized, it's created contiguous in the same way we used to create shape trackers contiguous. But then these indexes work their way up the graph. They move to the left, and you apply the movement ops to the ranges. So like you can think like permute is very trivial, right? If I have something that takes in, you know, range zero and range one, and then I have a permute on there, where I like transpose it, I can transpose the two. Okay, cool. I just switched the position of the two ranges.

##### **Geohot** [[00:25:22](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=1522)]
Shrink, similarly simple.

##### **Geohot** [[00:25:25](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=1525)]
You just need to offset it. If there's an offset, that's really it. Otherwise, it doesn't matter. Flip, take the max subtract it. Reshape is probably the most complicated. Reshape relies heavily on symbolic. It just basically creates the, the sum of all of them times the times the stride. So it creates like a, like a real, just single UOP with all the indices. And then it unpacks that using div and mod. And then hopefully symbolic resolves all of that to something nice, which it usually does. Yeah. So 3A is the, is the, you can see that each one of the things in PM mops on line 182, you can see that each one of the things in PM mops on line 182, has a movement op followed by, that's what the dot F is an index. So there's an index on a movement op, and we're trying to return something that's just the index with the movement op applied to it. And it removes all the movement ops on the graph.

##### **Geohot** [[00:26:32](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=1592)]
That make sense?

##### **Qazalin** [[00:26:39](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=1599)]
Yeah, it's basically moving the movement ops again to the edges.

##### **Geohot** [[00:26:44](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=1604)]
It's not moving the movement op. It's actually there was yes, sure, sure. But they're disappearing. The movement ops aren't moving.

##### **Geohot** [[00:26:52](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=1612)]
They're embedded down and how that indexing works. Yeah, there's stuff changing the index in place.

##### **Geohot** [[00:27:05](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=1625)]
Yes. So if you step through it, you can really see it. The index like eats the movement ops and then update itself based on whatever that movement ops said to do.

##### **Geohot** [[00:27:17](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=1637)]
So you can see that,

##### **Chenyu** [[00:27:18](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=1638)]
previously these movement ops are tracked by like a shape checker or a view that you start with a contiguous ones. Then you ask, okay, after some kind of movement, us, what's the end value of, of, uh, of the shape. Then go from there. You in shape checker, you have the function to map that back to the index. And the problem is sometimes it's very hard to do that. And the changes in gentrify basically crack all the movement ops and resolve it on the index level. And that's kind of a reason why in that is very important here.

##### **Geohot** [[00:27:58](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=1678)]
Yeah. Invalid invalid is definitely,

##### **Chenyu** [[00:28:00](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=1680)]
you push the view. Uh, it doesn't rely on like resolving a very good shape checker. It's probably a similar math. I don't know. It should be,

##### **Geohot** [[00:28:13](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=1693)]
um, it's similar math. Oh, by the way, a cool thing now, remember, we used to have all that logic to handle all of the like pad. Can you push pads through this thing? Like, is this a safe op to push pads through that's all fixed now, wherever the pad op used to be, we just add a, where

##### **Chenyu** [[00:28:32](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=1712)]
it's isn't, the, um, and then zero.

##### **Geohot** [[00:28:36](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=1716)]
No, we had both. So, so if you read that pad, uh, you'll see that both online, one 62, we update the index to be invalid, but online one 64, we create a, uh, aware with zero and that where does it move that where is now in the graph. So if you then upstream of that to the left of that, do a, uh, something that's invalid, something that's would, would doesn't preserve zero wherever zero is not zero. This doesn't matter because that where we'll get rid of that later.

##### **Geohot** [[00:29:15](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=1755)]
And we can do that because we actually have ranges at that point. It also keeps the invalid around. So it doesn't actually ever do the load from the bad part of the memory. Yeah. But invalid always map to zero. No.

##### **Geohot** [[00:29:38](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=1778)]
Well, yeah, but okay. So imagine, say you have something like, uh,

##### **Chenyu** [[00:29:42](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=1782)]
so what happened if I have a tensor, I padded then I, uh, next page.

##### **Geohot** [[00:29:50](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=1790)]
Yeah. So, so the other way around. So, so that's not the bad one. The bad one is when you have a tensor, you, uh, say, take the reciprocal of it and then you pad it, right? If you have a tensor, you pad it and take the expert that that obviously just works. But if you have a tensor where you tensor, and then you take the, the expert or the reciprocal of it, and then you pad it, this is where, the old implementation would break. And the new implementation is correct because it inserts a where after reciprocal is easier for me to think about. It's too late for me to think about what experts. So it loads the zero. It does. It does the reciprocal of zero, which is infinity. But then the, where, uh,

##### **Geohot** [[00:30:42](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=1842)]
puts the pad back in and sets the value back up. So it loads the zero.

##### **Chenyu** [[00:30:49](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=1849)]
I thought we want infinity in this case.

##### **Geohot** [[00:30:52](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=1852)]
No, we don't want infinity.

##### **Geohot** [[00:30:54](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=1854)]
So you want infinity. If you did load pad reciprocal, then you want infinity. But if you did load reciprocal pad, you don't want infinity. You want zero. Yeah. Okay. And it's, yeah, it's correct now because we actually, we insert the where in the two places. Um, so we can find the where in the two places. We can remove all that logic where it's like not safe to push pads gone. Um, and then of course we can remove that second where later on, I think, uh, it's like, he's already wrote the, uh, the thing to do that. Uh, I might've been wrong, but I think maybe it was only in range of five,

##### **Geohot** [[00:31:33](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=1893)]
but, uh, he already fixed it. So that's great.

##### **Qazalin** [[00:31:36](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=1896)]
Okay. Okay. Okay. Okay. Okay. Okay.

##### **Geohot** [[00:31:49](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=1909)]
I think something's still wrong, but other important,

##### **Chenyu** [[00:31:54](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=1914)]
though, safe to save to pad is not left for that case, but it's fine.

##### **Geohot** [[00:32:01](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=1921)]
Oh,

##### **Geohot** [[00:32:02](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=1922)]
I think it is. I think you'll see the way the where is inserted and you're like, Oh, I don't care if things are safe to pad anymore. Okay. Anyway. Yeah.

##### **Qazalin** [[00:32:15](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=1935)]
I think it's, I think it's,

##### **Geohot** [[00:32:28](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=1948)]
um,

##### **Geohot** [[00:32:36](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=1956)]
uh,

##### **Geohot** [[00:32:44](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=1964)]
it's not shiny at all. creating the, when you're looking at the indexes of the children, you have to wait until both children are processed to the point that they have an index. So if you get to the first child and you haven't seen all the other children yet, you raise an exception called rewrite not ready. And rewrite not ready will say, okay, I'm not going to continue this. Path of the graph. I'm going to wait here until I see all the children. So children not making progress means that you've seen the node a ton of times. So basically just moves to the end of the stack. So rewrite not ready says you come back to me after you visited everything else in the stack. Children not making progress means you've come back to me in this case 10,000 times and I'm not seeing any more children.

##### **Geohot** [[00:33:43](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2023)]
So something's probably gone wrong. It's kind of like infinite loop. Yeah.

##### **Geohot** [[00:33:53](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2033)]
So the comment says, wait here until we have seen all the children. But sometimes for some reason, like, so if you have two children, you need to wait for them to both get an index. But sometimes one child doesn't get an index for some reason, like a UOP gets stuck somewhere or something gets rewritten and then it never gets an index.

##### **Geohot** [[00:34:12](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2052)]
And that's when it raises children not making progress. So that's a little bit of a Yeah, we can actually probably make that logic a lot better.

##### **Geohot** [[00:34:42](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2082)]
We could probably make it something like. Like, if you raise rewrite not ready, and you're the only thing on the stack, it just kind of says,

##### **Geohot** [[00:34:54](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2094)]
well, sorry, I don't have anything else to process. And that'll at least get that failure to happen instantly.

##### **Qazalin** [[00:35:11](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2111)]
Yeah, after dot points, you basically don't have any new answers to give. Yeah. That mesh function.

##### **Geohot** [[00:35:17](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2117)]
Yeah.

##### **Chenyu** [[00:35:18](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2118)]
I mean, with all things, with all the . Yeah. You're just reinserting yourself back to until it hits that many times.

##### **Geohot** [[00:35:29](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2129)]
Yeah, yeah. I think also with graph infinite loop, sometimes we can explicitly detect the infinite loop, and it'd be nice to have a better error message when we can. You can't always. I mean, you can if you use, like, there's algorithms to do it, but they're kind of complicated and slow.

##### **Geohot** [[00:35:52](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2152)]
But some of them you can detect right away. And yeah, it'd be nice to have better errors about that. I can kind of go through what I think the bugs are.

##### **Geohot** [[00:36:11](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2171)]
I have the bugs listed in scheduler. I have the bugs under good isolated range of five bugs on master.

##### **Chenyu** [[00:36:21](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2181)]
So is it correct to say range of five overall is slower? Because it has a lot of rewrites. The same tests on CPU range of five compared to the old stuff. It's slightly slower.

##### **Geohot** [[00:36:39](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2199)]
I would think that the kernel time dwarfs everything else there. I bet there's some just dumb patterns that we haven't taken out yet. Some dumb, like, it's like making extra copies or something. I don't think that actually running range of eye,

##### **Geohot** [[00:36:56](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2216)]
running range of eye should be faster than the shape tracker. The graph rewrites themselves should be faster. And I think a lot of chronos are faster.

##### **Chenyu** [[00:37:11](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2231)]
I mean, with range of eye, it's faster.

##### **Geohot** [[00:37:14](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2234)]
Yeah, so what I've seen is your average kernel is faster with range of eye, but there's a few really bad outliers that are 10x lower.

##### **Geohot** [[00:37:36](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2256)]
And I think this is just because no one's really looked at them. I think once we look at them again. Excellent.

##### **Geohot** [[00:37:43](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2263)]
I mean, this is always, we would always say it's a comma, like, a lot of effort has been put into the old stack. So like a lot of just manpower has been put into smoothing all the bugs over in the old stack. If we move to this new stuff, okay, well, there's going to be new bugs.

##### **Geohot** [[00:38:03](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2283)]
And it's going to take that time, but hopefully less time. Yeah. How does range of eye work with image D type? It should happen all before that.

##### **Geohot** [[00:38:18](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2298)]
I haven't tested it, but I would expect that all the range of eye stuff happens before the image D type.

##### **Geohot** [[00:38:28](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2308)]
Like the image D type is there, but it's just kind of ignored. I think it all just works.

##### **Chenyu** [[00:38:33](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2313)]
Yeah. Because you raised a lot of your verification fail on ops PTR cat. Also what is ops dot PTR cat?

##### **Geohot** [[00:38:43](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2323)]
Okay. So PTR cat is pointer cat. It's used in the de vectorizer for basically saying like, okay, so say I want to load a float for. Right. So in order to load a float for on a GPU, the four floats need to be in order in memory, right? They need to have offset zero, one, two, and three. But pointer cat is a way that you can express that when it's not bad.

##### **Geohot** [[00:39:13](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2353)]
Pointer cat says, I want you to load four and I'm going to give you four pointers.

##### **Qazalin** [[00:39:22](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2362)]
.

##### **Geohot** [[00:39:31](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2371)]
So basically M Stack. Yes. Similarish to M Stack. Yeah.

##### **Qazalin** [[00:39:41](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2381)]
It takes a while for M stack to double down sometimes. Yeah. Anyway, so basically this whole, whole dynamic data, I just I don't know it requires orders. Yeah. Yeah. Yeah, it investigated that.

##### **Geohot** [[00:39:45](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2385)]
okay oh gpu equals one doesn't work anymore it's cl equals one

##### **Chenyu** [[00:39:58](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2398)]
yes please now you can see why comma really wants depth equal

##### **Geohot** [[00:40:04](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2404)]
yeah yeah yeah okay yeah it looks oh yeah image is failing with pointer cats yeah

##### **Geohot** [[00:40:14](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2414)]
yeah oh that is

##### **Geohot** [[00:40:16](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2416)]
oh that might be because the store is broken uh that might be because the logic and yeah

##### **Chenyu** [[00:40:23](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2423)]
there are some other tests basically saying your store has completely wrong shape my store is completely what uh the shape it's the shape of the store is wrong or the shape of a copy is wrong something very fundamental not even for compute

##### **Geohot** [[00:40:42](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2442)]
i say uh you know yeah no i think that the i think that in order to fix images uh i think the logic in bufferized to

##### **Geohot** [[00:40:49](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2449)]
store needs to be updated um so also the jet

##### **Geohot** [[00:41:00](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2460)]
so the jet right now uh there's definitely bugs in the jet interacting with range of eye the jet right now is using shape trackers and that's going to have to be fixed like the jet right now is going to be so the jet has this expected stvrsd type device that's checking to make sure the input shape tracker is matching

##### **Geohot** [[00:41:20](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2480)]
and i think that's what's not working okay okay i'm entirely sure

##### **Geohot** [[00:41:30](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2490)]
i mean it might also be just think worth thinking about like how we can rewrite the jet in a more modern way the jets really old code i bet there's some stuff

##### **Geohot** [[00:41:41](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2501)]
that's just like a lot simpler to do now with uops i think most of the kernel count looks

##### **Chenyu** [[00:41:54](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2514)]
good i mean the value is smaller so

##### **Geohot** [[00:41:59](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2519)]
yeah there's a few that are bigger and i'd be curious to look at those ones but

##### **Sieds Lykles** [[00:42:03](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2523)]
most of them are smaller and it's pretty obvious why

##### **Chenyu** [[00:42:10](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2530)]
i think some of it is just the don't realize it's a bit too big for me but i think it's just the time and space is just expanding stuff

##### **Qazalin** [[00:42:15](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2535)]
no there's like some of it is just a dumb is because you're reshaping a buffer and you're putting it contiguous all scheduler would make that the same buffer the new one doesn't it's just a contiguous we need a new buffer always

##### **Geohot** [[00:42:34](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2554)]
oh we can fix that oh we should fix that

##### **Geohot** [[00:42:38](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2558)]
actually that that's a good bug to fix like if it's literally just a reshape

##### **Geohot** [[00:42:43](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2563)]
shape, then contiguous should be ignored. Because a reshape is the same buffer.

##### **Qazalin** [[00:42:57](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2577)]
It is the same buffer.

##### **Geohot** [[00:42:58](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2578)]
If it's permute, you want the contiguous to work. But yeah, the reshape is actually the same memory. So like.

##### **Qazalin** [[00:43:03](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2583)]
Yeah, you have to pass over to tags and merge the tags.

##### **Geohot** [[00:43:10](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2590)]
Yeah, I mean, that's all.

##### **Geohot** [[00:43:13](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2593)]
It should support tuple tags now, which are pretty nice. You can assign multiple ops to one in your graph.

##### **Chenyu** [[00:43:29](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2609)]
What are all the meter render error?

##### **Qazalin** [[00:43:37](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2617)]
Oh. This tensor. This tensor is horrible to understand. I never got it right. You're in the old scheduling.

##### **Geohot** [[00:43:45](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2625)]
Yeah, I think now we can start removing hacks from disk tensor. And I'm thinking that Nimlgen and Wozparret, I'm thinking between the two of you, you guys should figure out who's going to fix disk tensor

##### **Geohot** [[00:44:00](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2640)]
and who's going to fix the JIT. I'll probably work on disk because I need that stuff to work for CloudFile.

##### **Sieds Lykles** [[00:44:12](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2652)]
CloudFile system.

##### **Geohot** [[00:44:15](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2655)]
Great. Yeah, I mean, there's hacks in tensor.py to deal with disk assigns. That can probably be taken out. Yeah, and that actually probably makes sense. Nimlgen, if you want to take a look at the JIT and figure out how to make the JIT good.

##### **Sieds Lykles** [[00:44:32](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2672)]
Yeah, OK.

##### **Geohot** [[00:44:35](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2675)]
And then also with an eye to the JIT being more unified with htqgraph. Yeah. We have this abstraction now.

##### **Geohot** [[00:44:51](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2691)]
The thing that I eventually imagine is that you're going to have kernels in the big graph and it's literally just going to be a bunch of rewrite rules to transform those kernels into the bytes that get shoved into the MAC on the GPU.

##### **Geohot** [[00:45:06](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2706)]
This is like putting the drivers in TinyGrid kind of project. But you know, I think you wrote the memory planner.

##### **Geohot** [[00:45:17](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2717)]
I think the JIT is kind of similar stuff, figuring out how we could not use shape tracker

##### **Geohot** [[00:45:24](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2724)]
in there. Yeah. So the three-file ULONG, it's no longer web GPU complaining about a lot of the ULONG stuff? Oh, is that good or bad?

##### **Chenyu** [[00:45:47](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2747)]
Oh, because web GPU doesn't support ULONG, which is using three-file and previously it was resolved, like some rewrite.

##### **Geohot** [[00:45:55](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2755)]
Yeah, it should be rewritten. That should still kind of work.

##### **Qazalin** [[00:46:00](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2760)]
Okay.

##### **Geohot** [[00:46:02](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2762)]
That's fine. I think let's . Seeds, maybe you want to take this one?

##### **Sieds Lykles** [[00:46:10](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2770)]
So what exactly was it? The problem with web GPU or three-file?

##### **Chenyu** [[00:46:15](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2775)]
Web GPU doesn't support UIN64, but three-file algorithm use UIN64. Previously there's a rewrite kind of split one UIN64 into two UIN32, which supports by a web GPU. But now I think because the either order is different or the old rewrite was not triggered, we just need to add it back. Probably then it will work.

##### **Sieds Lykles** [[00:46:45](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2805)]
Okay. Yeah. I mean, I might have wrote something with the index D type lowering because that changed a lot of long term.

##### **Geohot** [[00:46:53](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2813)]
I doubt you broke it. I doubt you broke it. I mean, I'm sure it still works on not range if I, the rule was kind of fragile to begin with, but yeah, I think it's kind of, you've been working in that space. And then also for symbolic reshape, it's clear to me like reshaping for the web GPU, it's from SIMS to ints and ints to SIMS never made any sense. The reshape, the rule for reshape is that the product of both these like input shape and the new shape need to be equal and you can't have a symbolic in one and not a symbolic in the other.

##### **Qazalin** [[00:47:31](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2851)]
Yeah.

##### **Chenyu** [[00:47:31](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2851)]
That was rely on another hack in shape checker to something along the line with if input is contiguous, then just outputs the shape or something.

##### **Geohot** [[00:47:41](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2861)]
Yeah. Yeah. I'm so glad all those hacks are going away. The new stuff should actually just hopefully all the new stuff should be able to symbolic

##### **Geohot** [[00:47:52](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2872)]
like pre-fail for LLMs and stuff.

##### **Qazalin** [[00:47:57](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2877)]
Okay.

##### **Geohot** [[00:48:02](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2882)]
Yeah. Cool.

##### **Sieds Lykles** [[00:48:11](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2891)]
Yeah, I mean I was working on the open using shrink.

##### **Geohot** [[00:48:19](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2899)]
Great. Yeah. I like what you said. I like what you said about the, you can only shrink afterward to smaller than the bound value. That makes a lot of sense.

##### **Sieds Lykles** [[00:48:28](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2908)]
I mean you can actually like with normal tensors. if you try and well with shrink it doesn't work but if you try and use the um like the dot uh get our item and you you use a larger value it just maximum

##### **Geohot** [[00:48:53](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2933)]
that's how like numpy works as well

##### **Sieds Lykles** [[00:48:57](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2937)]
but it does what so if you if you have a symbolic shape which is bound to four and do like get item with dot dot and then a hundred so you try and slice a hundred elements um it just gives you a tensor that has four elements oh there's four elements oh i see yeah

##### **Geohot** [[00:49:21](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=2961)]
yeah yeah yeah i don't know i think we should explicitly assert if we can but oh so the other thing if you're interested in this project um we should move the arguments and this is a causal this is a bit of a viz thing too because i want to keep it looking nice we should move the arguments of reshape uh expand pad and shrink as sources to the movement of so we have this problem right now where we have if there's symbolic there's uops in the argument and there should never ever be uops in the argument um so yeah we should move those to the uh to the to the egg to the sources uh but i want to like keep it looking nice while we do this i don't want it to start rendering uh you know stuff all over the place um for permute and flip these ones are okay to keep in the arg because the directive to permute is not going to be in the arg because the directive to permute and flip can't be a uop uh they kind of like control what the thing does

##### **Geohot** [[00:50:31](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3031)]
not like uh it's not an actual it doesn't go into shape but yeah this makes sense like the idea of like putting the putting the reshape args shape as as inputs yeah cool that should be doable what's the downside of your

##### **Qazalin** [[00:50:55](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3055)]
in the arc like i think we got away with it

##### **Geohot** [[00:51:00](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3060)]
oh barely okay so there's two big problems with uops in the art uh so one is they're not deduped i mean they're deduped at the global level but they're not deduped to the graph level so like if you have uh like they don't they're not they don't point to the same place they're not children

##### **Geohot** [[00:51:25](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3085)]
they they kind of just don't exist um the it's like the other thing is like

##### **Geohot** [[00:51:43](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3103)]
like the the it shouldn't come from nowhere right if you have a reshape that has the symbolic argument already in it then your symbolic argument is in your argument graph and like all the normal tools will show it your table sort will show it to you s parents will show it to you versus if it's in the arg you have to explicitly look inside of reshapes uh expands pads and shrinks in order to see if they have variables and we have like a bunch of things that actually do this and it just be so much easier to just do a tabasaur

##### **Geohot** [[00:52:18](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3138)]
and look for divine bears yeah that makes sense i mean i think it's the same with like the special arc where it's like

##### **Sieds Lykles** [[00:52:34](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3154)]
yeah it's fine it's sort of nice in some way but when you want to do when you want to simplify

##### **Geohot** [[00:52:46](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3166)]
yeah you can't do any you can't do any processing on it um yeah we definitely don't want those in the arcs um

##### **Qazalin** [[00:52:53](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3173)]
um um

##### **Geohot** [[00:53:15](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3195)]
yeah so those uh i'm not sure i have anything else to say about the bugs i think they're all pretty clear at least how to trigger them them

##### **Qazalin** [[00:53:37](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3217)]
okay

##### **Geohot** [[00:53:47](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3227)]
i gave a bit of a timeline uh back in the scheduler so i think by the end of

##### **Geohot** [[00:53:55](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3235)]
i gave a bit of a timeline uh back in the scheduler so i think by the end of hong kong hong kong maybe even before it if you got if you guys can make great maybe even before it if you got if you guys can make great progress in these two weeks then we can get it done before that we'll get all progress in these two weeks then we can get it done before that we'll get all the old stuff removed and um you know what i consider this whole project kind of being on track is if by the end of the year we have state-of-the-art flash attention for

##### **Geohot** [[00:54:13](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3253)]
mi350x

##### **Qazalin** [[00:54:15](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3255)]
uh

##### **Geohot** [[00:54:22](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3262)]
i remember problems we still we still don't know how to do it but we're still

##### **Chenyu** [[00:54:25](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3265)]
i remember problems we still we still don't know how to do it but we're still i don't know how go do you guys know how to do the online soft Etier thing yes we We don't, yes. Offering thing, I think it's those two. Which thing?

##### **Geohot** [[00:54:38](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3278)]
Double buffering for Gen. Oh, no, no, do double offering. Double buffering is easy. Yeah, I'm not sure, but we don't have it yet.

##### **Geohot** [[00:54:48](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3288)]
No, we don't have it. But the double buffering, the double buffering, I see very clearly what the transformation is using the stuff here. I wrote some demos of it in the AMD UAP MatMall stuff. That one I see. The online softmax, I don't understand enough yet to say. So you're right, we don't have that yet. But we can have a small flash attention that fits in the SMAM without the online. I didn't even know about that.

##### **Geohot** [[00:55:20](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3320)]
The example I was reading, they had a simple flash attention that didn't have that. All right. I don't know. I still think it's doable by the end of the year. Yeah. I mean, even if we don't totally have that,

##### **Geohot** [[00:55:42](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3342)]
we have to have memory under control. We have to be able to train with these big context things. It does seem like range of use a lot less memory, and at least with that stuff in 3.5, we can control.

##### **Qazalin** [[00:56:00](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3360)]
Yeah.

##### **Geohot** [[00:56:01](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3361)]
We can control the heuristic and figure out. I mean, you could write a heuristic in 3.5. That'll effectively do gradient checkpointing.

##### **Geohot** [[00:56:09](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3369)]
If you have gradient checkpointing.

##### **Chenyu** [[00:56:12](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3372)]
Mm-hmm.

##### **Geohot** [[00:56:15](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3375)]
Like, imagine having those things tagged as long edges, and the long edge has a big cost. And yeah, it'll checkpoint kind of automatically. Yeah. I mean, if your explosion are kind of independent, then just do that. I think it's probably good enough. Yeah. But yeah, I mean, it should be easy to play with these things now that are just always correct.

##### **Chenyu** [[00:56:45](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3405)]
Great. Anything else or any questions for the people who are in this meeting? I still don't know why we add everyone, but since we add everyone, you can have questions.

##### **Geohot** [[00:56:59](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3419)]
Yeah.

##### **Qazalin** [[00:57:00](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3420)]
Yeah. Yeah.

##### **Geohot** [[00:57:03](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3423)]
I think it's a good meeting to add everyone for. I think we have to bet the project basically on rangeify. Like, this has to work. It works. I know it works. It just takes time. In fact, it was interesting seeing the criticisms.

##### **Chenyu** [[00:57:29](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3449)]
What criticism?

##### **Geohot** [[00:57:31](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3451)]
Oh, oh.

##### **Geohot** [[00:57:32](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3452)]
One guy wrote, like, this just looks like a Walmart-tier polyhedral compiler. And I'm like, OK, yeah, what's wrong with a polyhedral compiler? And then the complaints about polyhedral compilers are that they're too flexible. And that they are a lot of polyhedral.

##### **Chenyu** [[00:57:53](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3473)]
My understanding, at least for the LLVM one, is they do a lot of things for, like, for loop or anything, like, you can call Turing complete on branches.

##### **Geohot** [[00:58:06](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3486)]
They do.

##### **Geohot** [[00:58:07](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3487)]
Halide shows some, like, good examples where they show, like, how they, like, split compute, how they, like, choose to, like, recompute sub-branges. It's, you kind of need it for the DSP stuff. But for the GPU stuff, for, like, fast gems on GPUs and for flash attention on GPUs, you don't need it. Just normal rectangular.

##### **Geohot** [[00:58:30](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3510)]
Yeah. Tiling works fine. OK. Yeah. Oh, how do you want to implement the backward and flash

##### **Geohot** [[00:58:50](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3530)]
attention? There are some math tricks there.

##### **Geohot** [[00:58:52](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3532)]
That's a question. I've not looked yet. Hopefully they're like the sigmoid math tricks. Let's get the forward first.

##### **Chenyu** [[00:59:03](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3543)]
And hopefully the backward one automatically will be good.

##### **Geohot** [[00:59:07](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3547)]
Yeah, that sounds good.

##### **Geohot** [[00:59:09](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3549)]
Oh, we are going to have to stack the, we either are going to have to, in order to get backwards to D1 kernel, we're either going to have to stack QKV, or we're going to have to support multi-output. I don't think multi-output's that hard, though.

##### **Chenyu** [[00:59:26](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3566)]
We definitely want multi-output.

##### **Geohot** [[00:59:30](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3570)]
Well, so multi-output, yeah, OK.

##### **Geohot** [[00:59:35](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3575)]
Multi-output involves something that we haven't done yet. It's not that it's not doable. But multi-output requires you to share ranges with children.

##### **Geohot** [[00:59:56](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3596)]
Like, you have to merge the ranges downstream. Yeah.

##### **Geohot** [[01:00:05](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3605)]
Or we could have something where you specify, like, three things or like an output group. And then that's really easy.

##### **Geohot** [[01:00:12](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3612)]
Maybe we'll start with something like that. Like, in order for things to be multi-output, they have to have the same shape. Yeah, sure. You can start with that. Yeah. Yeah, yeah, yeah. And then like. Yeah.

##### **Geohot** [[01:00:31](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3631)]
That's kind of hard to discover. I don't know. It's not that hard.

##### **Geohot** [[01:00:35](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3635)]
I mean, it should be pretty easy. It should be pretty easy.

##### **Chenyu** [[01:00:39](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3639)]
Yeah, this is similar.

##### **Geohot** [[01:00:41](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3641)]
OK, not very important now, but doesn't sound very difficult. OK. Yeah.

##### **Chenyu** [[01:00:49](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3649)]
Anything else? What was the part that you struggled the most or wasted most of the time on?

##### **Geohot** [[01:01:02](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3662)]
I mean, I had to get the whole other.

##### **Geohot** [[01:01:06](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3666)]
I got all the post-op stuff in before this stuff at any hope of doing anything. So I had to move the whole optimizer from before Rangeify to after Rangeify. And I don't know. I kind of just like, I had a lot of dread about doing that. Yeah. Yeah. Yeah. I mean, I think I half-assed it a whole bunch of times. And then, I don't know, one time I just said, OK, this is really my only priority. I just have to do this.

##### **Geohot** [[01:01:37](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3697)]
And that's done. It seems to work. Oh, and do the A-Range thing first.

##### **Chenyu** [[01:01:45](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3705)]
It's very good. I was pretty happy.

##### **Geohot** [[01:01:47](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3707)]
Oh, yeah. Yeah. Yeah. Now we can do things like the A-Range thing first. But yeah, it was just like, it was just so annoying to, like kernel.py, getting rid of kernel.py was terrible. We used that class everywhere. The multi-month project of getting rid of kernel.py. But it's gone. And this new stuff that we're getting rid of, like kernelize and stuff, is much more modern code and is much more well-factored than kernel.py ever was. So I think that was the most annoying part. I think the Rangeify stuff is actually a lot better. It's a lot better than the kernel.py removal project. Yeah. Yeah. The old scheduler removal project is a lot better than the kernel.py removal project.

##### **Geohot** [[01:02:37](https://www.youtube.com/watch?v=2kpAMGBbtf8&t=3757)]
OK, great. Cool. See you guys in two weeks. Good luck. We'll see you in Hong Kong. Sounds good. Bye. Thanks, everyone. Next week, we'll have a meeting at the same time. So see you next week.
