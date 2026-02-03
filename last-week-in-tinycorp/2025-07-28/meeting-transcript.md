# 2025-07-28 Meeting

### Meeting Agenda

**Time:** 9am Monday San Diego time
- company updates
- mi fast gemm
- upcast before reduce
- MLPerf
- viz tool
- drivers
- cloud
- onnx
- other bounties

### Audio

[Youtube Link](https://www.youtube.com/watch?v=wZ5Ch0ODRv8)

### Highlights

- **[Company Updates](#geohot-000009)**: TinyBox "green" units are selling as fast as they can be built (four sold last week). The company is working on the AMD contract and needs to establish clear timelines and deliverables.
- **[Compiler/GEMM Optimizations](#geohot-000157)**: `define_reg` has been unified with `define_local` and `define_global`, simplifying UOps. Work is progressing on generating advanced GEMM kernels ("kernel 3") for AMD GPUs, with a long-term goal of unifying the scheduler and optimizer to support techniques like double buffering and "mega-kernels".
- **[UOp Refactoring (Expand/Reduce)](#geohot-000952)**: Geohot proposed refactoring the `expand` UOp to be a proper inverse of `reduce` by adding new dimensions with stride zero at the end. This change aims to simplify the graph representation and eliminate dimensions of size one.
- **[MLPerf LLaMA](#wozeparrot-001851)**: A data loader for the validation set is ready, but the NVIDIA Nemo reference implementation is complex and difficult to follow. The team will need to reverse-engineer its data processing behavior to ensure a compliant submission.
- **[Viz Tool](#qazalin-002226)**: A new disassembly view has been merged. Work is underway to add RDNA3 instruction timings. Metal performance counter support is available in a branch but has an undesirable dependency on a full Xcode installation. The primary focus is on robust AMD profiling tools.
- **[AMD Drivers & HCQ](#nimlgen-003411)**: CPU-to-GPU copies are now faster by being integrated into the HCQ graph using pinned memory. Fixing BEAM search issues on the MI350 is a high priority, and there are plans to add these machines to the CI pipeline for driver testing.
- **[Disk I/O Performance](#geohot-004141)**: Benchmarking shows disk-to-GPU copy speeds are around 9.8 GB/s. This is below the hardware's potential, likely due to single-threaded limitations; achieving full speed will require a multi-threaded approach.
- **[Cloud & InfiniBand](#wozeparrot-004956)**: The InfiniBand peer-to-peer (P2P) implementation has been merged. While it shows some overhead on small models, a large-scale training run will be conducted to validate its performance before the associated bounty is paid.
- **[ONNX Support](#chenyu-005123)**: Integration of ONNX support is nearing completion, with ongoing cleanups to the parser. The goal is to merge the feature this week after resolving minor test issues and ensuring Python 3.10 compatibility.
- **[Bounties](#geohot-005500)**: A new $200 bounty is being added for implementing the Muon optimizer. Existing bounties for HVIC decode and RKNN NPU support are highlighted as good, accessible opportunities for contributors.

### Transcript
##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=0)]
Okay, can we get started? Sounds good. Let's start with company updates. I see a bunch of folders for TinyBox.

##### **Geohot** [[00:00:09](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=9)]
Yeah, the green boxes are really moving. We sold four last week. We have three outstanding orders right now that we're just waiting on wires for. So yeah, they're moving as fast as we can build them right now. We're working on expanding build capacity. We have all the cases built. They're all sitting there. We got like 40 cases sitting there that we just need to put the stuff in. But, you know, it's shared resources with commas production. But yeah, we're definitely keeping up with orders. And I'd like to get ahead to the point that we send the mailing list. But if we're selling, if we're selling for a week, we're making so much money.

##### **Chenyu** [[00:00:50](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=50)]
Great. Do we have any red thing in the tree?

##### **Geohot** [[00:00:54](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=54)]
We have one. We have one. We read an inventory and I'll vaguely mention it here. This is not the many people in here right now. Once that red sells, there might be a new red.

##### **Geohot** [[00:01:11](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=71)]
Yeah, no, yeah. But we already to come in with that with the new with new cards.

##### **Geohot** [[00:01:20](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=80)]
Cool.

##### **Geohot** [[00:01:24](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=84)]
Yeah, that and, you know, just.

##### **Geohot** [[00:01:28](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=88)]
Just continue to work on the AMD contract. I think when you get here, we really need to. Start coming up with with with timelines and thinking about like, yeah, like breaking everything down into into what tasks need to be done.

##### **Chenyu** [[00:01:45](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=105)]
Sounds good. Cool. You also want to talk about the things that have been working on. We do. And through.

##### **Geohot** [[00:01:57](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=117)]
Yeah. So. The main thing that I did last week, the main thing that actually finished that I'm pretty happy with is define reg now behaves the same as defining local and define global. So we used to call it define ACC, which had different semantics, but there's no reason for this at all. So it's now defined reg. But you could also like there's no reason that your accumulator has to be in registers. You could also put your accumulator in locals or your accumulator in global. So now that it's all unified, that's pretty nice. The. Other advantage to doing this is we used to have defined reg also used to have this initializer semantics that was always kind of actually, I can probably delete. There's probably a whole bunch of rules I can just delete now to that specify the placement of define reg at the top of a block that's all fixed. It now is just the natural the natural top of sort now works. And you can just define reg where it should be inside the loop nest. And actually define reg. Reg is now always at the top. And instead of having this special initializer semantic, it just uses a store. So it uses a normal store to store the zero and then it accumulates in the register and that stores. So some big cleanups there. And then the other thing that I've been working on really for the last month is so I also got I can now output kernel three at the UOp layer. So like by writing the. UOps out manually, I can output kernel three from SEBs fast map mills on. Seven nine hundred and this is using locals.

##### **Chenyu** [[00:03:37](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=217)]
You put a link somewhere.

##### **Geohot** [[00:03:41](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=221)]
Yeah. So this is from the like said blog post the deep dive into matrix optimizations. So I now have effectively the same thing as kernel three being outputted by. A manual UOp. And I'm almost there with like high level UOps outputting it. The only thing that so the. The key insight. The key thing that it's still missing is when you have a barrier instruction, you can reorder the locals however you want. So you can rebind the locals to different to different groups. And we used to have.

##### **Chenyu** [[00:04:27](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=267)]
The local. There are like multiple kernels in the link you gave.

##### **Geohot** [[00:04:33](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=273)]
Because one and two we can already do. One and two are kind of trivial. Kernel three is the first one that the only there's two main tricks missing from kernel three. One to go from kernel three to kernel five is the double buffering. And I have to work to make sure that we can support the double buffering. And then to go from kernel five to kernel eight, they're diving down into the assembly. But I don't actually think you have to. I think that if you just did a BEAM search on kernel five, you'd get kernel eight levels of proof of events.

##### **Geohot** [[00:05:05](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=305)]
That makes sense.

##### **Geohot** [[00:05:07](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=307)]
Yeah. So I think that the only other like missing trick is the double buffering. So to figure out how to support that. I have to clean up this high level UOp semantic thing. And then figure out how to get automated rules to generate them. But like it's. It's looking very similar now to it's looking more and more similar to how like Halide's doing it and how TVM is doing it. We can create these range variables and then put these range variables in. I'm just trying to work out what the cleanest way to do it is. Like one way to think about it is so I'm really trying to also unify whatever we do for the like overworld ranges. There shouldn't be anything special really about kernel boundaries. There shouldn't really be any distinction between like the scheduler and the. Optimizer. Because they're really the same thing. Like we have this thing called opt which has like kernel. Pie and heuristic and all that stuff. And then we have this thing called scheduler which groups things into kernels. But you're effectively doing the same thing. You're assigning buffers to different places. And yeah, we need to like unify them. You could imagine, for example, if you have like an entire model, you could pull the batch dimension out. Like you can pull the batch dimension out. Of the entire model, putting the range all the way at the beginning and then having the final store be the only one that actually outputs on the batch dimension. And then whenever you have a long range like that, you can also reinsert that range at any place locally. Depending on how you want to trade off memory and like computer order. So, yeah, I mean, I also want to like. I want to make sure that when I do this, I capture all of these things even like like because I don't want to. I don't want to design another thing that only goes up to like 2018 levels of optimization, which is kind of what we did the first time. So what people are playing with now are these like mega kernels, these single kernels that can run LLMs. And they're using like this fancy dispatcher logic to do it in their thing. But I don't think you need any of this. I think if we do it right, we could actually like. So you have like barrier and barrier will synchronize. All the locals across all your groups. But you can also make a global barrier. You can just use atomics and do this. So, yeah, I want to be like I want to unify that. I want to unify the idea of a barrier, a global barrier, and then registers obviously have no barrier. But yeah, and I yeah, I know I've been spending a long time on this, but this I want to make sure that whatever I write for this. It can output everything. In the fastest 2025 kernels.

##### **Geohot** [[00:08:02](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=482)]
And then we have a complete. Yeah, that makes sense.

##### **Geohot** [[00:08:07](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=487)]
Yeah, I've been looking a lot more into how TVM does this. And then there's this thing Thailand, which is just like built on top of TVM. You do end up reinventing most of TVM concepts, which is kind of upsetting. But.

##### **Chenyu** [[00:08:22](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=502)]
I mean, that kind of makes sense. It's like how many primitives can you have?

##### **Geohot** [[00:08:29](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=509)]
It's not that many. Yeah, there's the primitives. And then there's this whole concept of like, like binding. So like we were just implicitly bind things to globals and locals. But there's a lot of different ways you can do that, especially with locals. So the way that I want to do it instead, the way that I was thinking about it last night after I wrote this stuff up is like what you want to do is you want to pull the global out. Out of the whole graph, like you can remove the globals from each of the shape. And then the whole graph is just this this inner thing which doesn't have the globals in it anymore. And then you can work on locals and pull those out of the graph or maybe out of different chunks of the graph.

##### **Geohot** [[00:09:11](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=551)]
And then you're left with registers. And that's it. Yeah. So progress.

##### **Geohot** [[00:09:22](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=562)]
I don't know. I mean, I think that this is my main contribution. This is going to be my main contribution. To the AMD contract, which is going to be I'm going to make the flash attention kernel and the GEMM faster than anything else on that on that card.

##### **Geohot** [[00:09:40](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=580)]
Right.

##### **Chenyu** [[00:09:43](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=583)]
Okay. Are you introducing any new UOps or removing any UOps?

##### **Geohot** [[00:09:52](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=592)]
I think overall UOps have been removed. Well, so I've removed them. I've removed assign. There's no more assign on. There's still a sign in the overworld. And I think we actually want to keep it there. But there is no more assign in graphs anymore. So like, like in kernels, kernels used to have both assign and store. There's no more assign. So I've removed that. I've simplified define reg and unified it with the others. So I think overall, this has been UOp reduction. Oh, and then I'm playing with how to we may want to change expand. So if you think about reduce, if you think about reduce as it takes dimensions off of the end and reduces on them, you can think of expand as the inverse of that. And like our current expand isn't that our current expand looks a lot more like our old reduce. So we may want to switch expand to something that just inserts copies at the end. And then we can remove ones from the graph entirely.

##### **Geohot** [[00:11:00](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=660)]
From the shapes. Yeah.

##### **Chenyu** [[00:11:05](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=665)]
I think even for the tensor frontend, we really want the method to add one length expand. This pattern has occurred many times in tensor.py.

##### **Geohot** [[00:11:14](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=674)]
And it's usually pretty awkward. Yes. So think about this in this. Instead, think about the primitive being. So you have something that's like 10 comma 10. And then the new expand you put in a shape like 10 comma 10 comma 10. And the last 10 on the end has strides zero. And then if you want to put that in a different place, you permute it afterward.

##### **Chenyu** [[00:11:39](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=699)]
Why not just put the access you want to insert strides zero and how big you want that to be?

##### **Geohot** [[00:11:45](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=705)]
Because why put it in an access when you can do a permute afterward?

##### **Geohot** [[00:11:55](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=715)]
Because I can. I don't understand. Well, I mean, it just makes.

##### **Geohot** [[00:12:00](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=720)]
Why force them into the ender? I mean, we force the reduce access to the end. It's the same thing. Not in tensor.py. Yes, in tensor.py. Tensor.py under the hood, when you call dot r, it does permutes to force the reduce to the end.

##### **Chenyu** [[00:12:20](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=740)]
Oh, no, but not when you are still operating on the tensor level.

##### **Geohot** [[00:12:26](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=746)]
Well, under the hood, yes. So when you are constructing the reduce uop at the tensor level, it's actually moving. Yeah, I mean, we can keep whatever syntactic sugar you want at the tensor level. I'm not saying we're going to change what the expand function does. The expand function under the hood will just insert this like. I don't know, like whatever. Copy. Not copy, but what is that called? Like aliased copy and then permute. I think it's much cleaner than having to specify axes as well as a shape.

##### **Chenyu** [[00:13:08](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=788)]
Yeah, sure.

##### **Geohot** [[00:13:08](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=788)]
I mean, I'll send the internal message to whatever it is. Yeah. I'm just saying like what the internal, like what the movement uops are going to be. Yeah. So the movement uop is going to be something that inserts expanded dimensions at the end

##### **Geohot** [[00:13:24](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=804)]
and then permutes them to put them wherever you want them. And then this functions as the inverse of reduce. And then it also makes. To have an actual reduce.

##### **Chenyu** [[00:13:44](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=824)]
You think refactoring?

##### **Geohot** [[00:13:46](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=826)]
Yeah. So might be making up to a new problem if this is fit. So sayiltan? Sophie like do you want.

##### **Chenyu** [[00:13:57](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=837)]
Maybe not use the, Elina. illustration? All right. I'm just, this is obviously going to be a spoil test. Yeah, sure. Yeah, sure. That's how this should look. We also want the diamond shelf here for reference science. So, they've probably also been built on comment our growing masculine streak in only

##### **Geohot** [[00:14:10](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=850)]
have w misery. Oh my god. So good Growth Tolerance. dimensions are compact. Because we have all the normal dimensions followed by all the reduced dimensions, instead of having a special get contraction with reduce, we could just have basically two get contractions.

##### **Geohot** [[00:14:33](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=873)]
Yeah.

##### **Geohot** [[00:14:35](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=875)]
There's a lot of things that are just a lot simpler to specify once you realize that these reduced dimensions are at the end and added. Well, the dimensions are removed by the reduce. And then, yeah, I want to make this ShapeTracker inverse, which adds the dimensions on the other end. And then also, I want to write some ShapeTracker. I want to write some UOp algebra to maybe clean things up at the movement op level instead of going straight to views. Because the movement ops have a lot of information that we throw away when we go to views.

##### **Chenyu** [[00:15:05](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=905)]
What?

##### **Geohot** [[00:15:07](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=907)]
Well, so if you have a view, how expanded is the view?

##### **Geohot** [[00:15:13](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=913)]
What? Like, given a view, can you figure out how much of the original tensor is accessed?

##### **Wozeparrot** [[00:15:25](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=925)]
Isn't that the Smax on your index?

##### **Geohot** [[00:15:29](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=929)]
Well, yeah, but that's only going to give you a max. That doesn't tell you about how many elements are accessed.

##### **Geohot** [[00:15:43](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=943)]
Oh, excuse me.

##### **Geohot** [[00:15:45](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=945)]
See what I mean?

##### **Geohot** [[00:15:47](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=947)]
No. So it can definitely tell you the max index. But what if that thing is like stride 10 or something, right? Like, the max index could be 100, but you could actually only be accessing 0, 10, 20, 30, 40, so on.

##### **Geohot** [[00:16:05](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=965)]
Oh, OK, I don't know.

##### **Chenyu** [[00:16:06](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=966)]
Maybe I need an example.

##### **Geohot** [[00:16:08](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=968)]
It's just a lot easier. I mean, with all of these things, like when we do gradients, or when we do multi, it's a lot easier to read. It's a lot easier to reason about the movement UOps than it is to reason about views. Because we can reason about each movement UOp. Like, the movement UOps are simple. It's really easy to reason about, oh, this is a shrink. This is a pad. Yeah, I think I might do some more focus there when I change. These around to be, I think I got to think the right name for it, the name of it, like insert more dimensions at the end that are copies. Pretty good.

##### **Chenyu** [[00:17:02](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1022)]
Yeah.

##### **Geohot** [[00:17:03](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1023)]
Yeah, I'll ask you about this, but if we switch if we switch the expand to this and we switch the reduce to remove the ones, These graphs will also just be easier to read, like just a whole lot easier to understand where the changes will come. understand it's like, oh, cool, I'm sticking those there. And then we can push permutes around a bit. Yeah, and end up with some very simple.

##### **Geohot** [[00:17:27](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1047)]
Oh, I understand what the movement patterns are here instead of this arbitrary view, which is like, oh, that's cool. But I mean, going to view strictly destroys information.

##### **Chenyu** [[00:17:45](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1065)]
Yeah, because that's the minimal information you need. That's why you want view to be merged.

##### **Geohot** [[00:17:53](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1073)]
Yeah, yeah. And then once you go to view, it's like, again, what's the gradient of a view? I don't know. Maybe there are magic methods to get to this.

##### **Geohot** [[00:18:06](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1086)]
That's too far digressed. Yeah, yeah. I mean, yeah, again, if there's magic. I don't know. No, I don't know. I mean, you keep a map between moving up to view, right? No, no.

##### **Geohot** [[00:18:23](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1103)]
I don't do that. And there's also a problem.

##### **Geohot** [[00:18:29](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1109)]
Like, yeah, we have our function to invert it. But I don't know. I think that those transformations are like NP. And you can do them, but yeah. Yeah. OK.

##### **Chenyu** [[00:18:41](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1121)]
Anyway. Cool. OK, sounds good. LLaMA. I don't know. What do you have? Any update?

##### **Wozeparrot** [[00:18:51](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1131)]
I have a bin IDX loader, so we can load those.

##### **Geohot** [[00:18:56](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1136)]
Yeah.

##### **Wozeparrot** [[00:18:57](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1137)]
I mean, we can load all the sequences from the Val set. They are all different lengths, which is annoying. Yes.

##### **Geohot** [[00:19:06](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1146)]
I understand.

##### **Wozeparrot** [[00:19:08](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1148)]
Yeah. The Nemo code is still really hard to read. So it's not really a problem. So it turns out that they have GPT data set in the Nemo code base. But that's not actually the one that they use, because there's one in Megatron core that's split out. And then they import it dynamically. So you can't really follow where it goes.

##### **Geohot** [[00:19:34](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1174)]
I would just run it and then write a test to make sure I'm getting this right.

##### **Chenyu** [[00:19:38](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1178)]
So the problem to run that is you need to mark all the actual codes to there. So I'm going to do a test on the device and setup. And I mark all those to get something. It's very ugly.

##### **Wozeparrot** [[00:19:50](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1190)]
No, I just trace the code. And I think I have a pretty good understanding of how Nemo is doing the data loading now. Anyway, we will figure this out after me flying there. And before you are gone, we will figure something out.

##### **Geohot** [[00:20:04](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1204)]
Yeah. I think this is the problem with this benchmark. It really is not a very good reference implementation.

##### **Chenyu** [[00:20:12](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1212)]
Here, quote on implementation.

##### **Geohot** [[00:20:15](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1215)]
Yeah.

##### **Geohot** [[00:20:19](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1219)]
Very less information. Does Google have a better one?

##### **Geohot** [[00:20:23](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1223)]
No. Supposedly, Google didn't submit. Google didn't correct either.

##### **Chenyu** [[00:20:28](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1228)]
So Google's submission is lack of the actual implementation and after a while. So everyone in the current round of submission is just calling that group.

##### **Geohot** [[00:20:46](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1246)]
I see. And then did they mock all that? I mean, Google's using TPUs, right? Did they mock all the Nvidia stuff?

##### **Chenyu** [[00:20:51](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1251)]
So Google submission, their oldest submission, the first step is we convert all the examples to TF records stored in this internal place without telling you how they convert. Isn't that against the rules? So they didn't submit. They withdrew all the submission. Yeah.

##### **Geohot** [[00:21:11](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1271)]
Oh, I see. So they didn't open source the code?

##### **Chenyu** [[00:21:14](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1274)]
No.

##### **Chenyu** [[00:21:16](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1276)]
And even if you look into their original submission, the private repo, there's nothing.

##### **Geohot** [[00:21:26](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1286)]
Well, it sounds like you have something that works. Yeah.

##### **Chenyu** [[00:21:29](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1289)]
So I think our best bet is trying to, as what I did before, understand what's, like try to call their thing on whatever they're doing.

##### **Chenyu** [[00:21:41](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1301)]
And then try to do the same thing on whatever GPU, as long as it runs and see what's the behavior and try to do that behavior.

##### **Wozeparrot** [[00:21:48](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1308)]
The other thing is there's like, at least the data set has a bunch of extra data that isn't used. Far as I can tell.

##### **Chenyu** [[00:21:59](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1319)]
Okay.

##### **Geohot** [[00:21:59](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1319)]
I don't know.

##### **Geohot** [[00:22:00](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1320)]
We will figure this out. It's not very useful to discuss like this meeting. Yeah. I mean, we got to get a timeline for when we're training.

##### **Geohot** [[00:22:09](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1329)]
We got to get AP training. Yeah. Yeah. Yeah.

##### **Geohot** [[00:22:14](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1334)]
Yeah. I think we're just starting to figure that out.

##### **Geohot** [[00:22:19](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1339)]
So then you may just plug in of these capabilities. I think it's LAMA. We can move on to this.

##### **Geohot** [[00:22:22](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1342)]
Okay.

##### **Qazalin** [[00:22:26](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1346)]
I merged a new view disassembly into this yesterday. I think this week I'm going to add the RDNA3 instruction timings.

##### **Geohot** [[00:22:40](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1360)]
Cool. Is the metal one working now? Do I see metal performance counters?

##### **Qazalin** [[00:22:49](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1369)]
It is in a branch. It's in a branch, right. Xcode? Yeah, you have to install the Xcode from the App Store. No!

##### **Geohot** [[00:22:57](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1377)]
Why do I need Xcode?

##### **Qazalin** [[00:22:59](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1379)]
I'm sorry. There's absolutely no way. They don't ship the binary as a standalone. You have to install.

##### **Geohot** [[00:23:06](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1386)]
Do I really need this binary? What's it doing?

##### **Qazalin** [[00:23:11](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1391)]
It's recording GPU counters, I guess. AMD documents this stuff and open source system, but metal is.. Yeah.

##### **Geohot** [[00:23:21](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1401)]
For AMD, I mean, we're just setting the registers to do the sqgt logging, but yeah, we should figure out what this is and avoid Xcode.

##### **Geohot** [[00:23:32](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1412)]
I do have Xcode.

##### **Geohot** [[00:23:37](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1417)]
So what's this branch called?

##### **Qazalin** [[00:23:40](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1420)]
Metal traces on my work.

##### **Geohot** [[00:23:43](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1423)]
It's a Y in general.

##### **Qazalin** [[00:23:46](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1426)]
Yeah.

##### **Geohot** [[00:23:48](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1428)]
Got it.

##### **Geohot** [[00:23:50](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1430)]
Yeah. Yeah.

##### **Geohot** [[00:23:51](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1431)]
Yeah. Oh, it's on your..

##### **Qazalin** [[00:23:53](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1433)]
You can fetch this hash. It will go there.

##### **Geohot** [[00:23:56](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1436)]
Got it.

##### **Geohot** [[00:23:57](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1437)]
Yeah.

##### **Wozeparrot** [[00:23:59](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1439)]
Okay.

##### **Qazalin** [[00:24:01](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1441)]
I will test on the AMD Europe.

##### **Geohot** [[00:24:05](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1445)]
The big one.

##### **Qazalin** [[00:24:07](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1447)]
Small ones just build with zeros.

##### **Geohot** [[00:24:11](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1451)]
All right. So I'm on the branch. Do I have to put anything beside this equals one?

##### **Qazalin** [[00:24:16](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1456)]
Profile equals two.

##### **Geohot** [[00:24:18](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1458)]
Oh, profile equals two. Oh, I see. All right. There we go.

##### **Geohot** [[00:24:24](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1464)]
I paste it. And then I say forget it and unkk. It's called..

##### **Geohot** [[00:24:29](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1469)]
All right.

##### **Geohot** [[00:24:38](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1478)]
I've done withPS into our list.

##### **Qazalin** [[00:24:43](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1483)]
Got the I just, I just Hey, same in the vanity, similar to big.

##### **Geohot** [[00:24:50](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1490)]
Yeah. GPU I don't have instruments oh you're on like

##### **Geohot** [[00:25:05](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1505)]
I'm on Sonoma 1473 do you have instruments like the app I do oh it doesn't make the directory

##### **Geohot** [[00:25:28](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1528)]
yeah you know we need to we need to figure out how to make this stuff more robust ideally we need to figure out what that maybe you and maybe you have some ideas about how how apples actually doing this

##### **Qazalin** [[00:25:45](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1545)]
no you really want to do it just make that directory that templates directory and that's it all right

##### **Geohot** [[00:25:50](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1550)]
all right all right so I make this directory it's do I need sudo to make that directory and I didn't look like it all right all right profile equals to viz I'd start recording with the okay okay parsing time info parsing GPU counter info parsing GPU counter value okay took a while but whoa all right we got some stuff

##### **Geohot** [[00:26:17](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1577)]
this is box tiny when I click on it OMG I can't figure out what happens when I click on this kernel when I click on this I check the run I did I'm only at 1%,

##### **Qazalin** [[00:26:44](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1604)]
yes, I got it I'm done I see that right now I can finally let it run my because I have aält camera you can see the you can actually set up AOL tables you can test it if you need to.

##### **Geohot** [[00:26:49](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1609)]
world one run here. If I put the test name twice, does it run it twice? I cool it ran the test

##### **Geohot** [[00:26:57](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1617)]
twice. Oh, this is mad slow, too.

##### **Qazalin** [[00:27:05](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1625)]
It is mad slow, I agree.

##### **Geohot** [[00:27:06](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1626)]
Oh, I see. Yeah, okay. Run one of two, run two of two. Okay, I see. I can scroll down here.

##### **Chenyu** [[00:27:12](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1632)]
Do you want to do a screenshot?

##### **Geohot** [[00:27:15](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1635)]
Yeah, I'll post a screenshot. Yeah, okay, cool. I don't know, maybe we shouldn't spend too much time on Metal. And we should just make sure this works for AMD. AMD is the real place we need this. And yeah, I think the instruction level profiling stuff would be cool, too.

##### **Qazalin** [[00:27:45](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1665)]
I think I'm gonna do that on the fly. Like, the way I generate the disassembly on the fly, it just makes me keep the kernels and sample it.

##### **Geohot** [[00:27:54](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1674)]
Yeah, I mean, it would just be it would just be great, it would make the workflow so much better if we could just, you know, we're gonna be probably in about a week or two, I'm going to be ready to start really just optimizing the GEMM. And to see where all the all the hotspots are. are we great.

##### **Qazalin** [[00:28:15](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1695)]
Right, yeah. So pretty.

##### **Geohot** [[00:28:18](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1698)]
I mean, yeah, eventually we'll be able to put this. We'll be able to guide. I want to be able to guide the search with this stuff. I think that that's a huge advantage. I mean, so this is a way that we can beat TVM search. None of these searches are profiler guided, aside from just measuring the time. But if we could look and we could figure out, like, even asking little questions, there's a maximum number of memory accesses that you can have in flight. And eventually you're going to hit that, and it's going to stall when you try to add one more. So then that's, well, like, whatever optimizer we have should be able to look at that and be like, OK, well, I should stick some ALU operations in there because they're free. But I think that's eventually where we'll get to with this stuff.

##### **Geohot** [[00:29:20](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1760)]
Oh, cool.

##### **Geohot** [[00:29:21](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1761)]
Yeah, I think focusing on AMD and hopefully making it so we can, I guess you're always going to need some kind of extra flag.

##### **Qazalin** [[00:29:33](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1773)]
For metal, because it's sampling and requires Xcode install, I'm putting it black. But for SQTT, because I'm generating on the flag, I'll just put it in this one.

##### **Geohot** [[00:29:45](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1785)]
I don't think that's going to work. I think SQTT uses a ton of GPU RAM.

##### **Qazalin** [[00:29:54](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1794)]
I mean, like, not enabling SQTT during the run, sampling it later, asking for the sample later.

##### **Geohot** [[00:30:07](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1807)]
Oh, like rerunning the kernel. Oh, interesting.

##### **Qazalin** [[00:30:14](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1814)]
Yeah. So you just want instruction level type, right? You don't want full GPU state. Yeah, I guess. You want the entire state.

##### **Geohot** [[00:30:28](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1828)]
Yeah, I mean, the only problem with that is, if you recreate the buffers, everything's not going to be in the same L2 position. Right? Like, you don't know which buffers are going to be hot in your L2. Because if you got a VostegRO Salut cémmm Either way, I think there's a lot to do here. Getting to the point where we can view, just the infrastructure that view an annotated disassembly. Oh, well, yeah. OK, yeah. I think there's probably some light weight stuff we can get. Anything we can get that's light weight should work that way. could be invisible one, like, yeah, if we can just read performance counters. But if we need actual tracing, that's probably going to have to be behind the flag.

##### **Qazalin** [[00:31:27](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1887)]
The instruction level tracing is pretty heavy. Yeah. Yeah, cool. I can merge metal. I've merged all the general stuff to master already. The diff is just standalone.

##### **Geohot** [[00:31:46](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1906)]
Yeah, as long as it's not going to interfere with anything behind a, let me read the diff and see how crazy it is. What is, I see start, exit, trace. Oh, I see. Oh, yeah, I wouldn't put. Why do you have that if statement inside start, exit, trace?

##### **Qazalin** [[00:32:18](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1938)]
So there's one exit trace process per mental GPU.

##### **Geohot** [[00:32:25](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1945)]
No, I get it. But you have a call to a function called start. Yeah, host your ifs. You have a call to a function called start exit trace. Yeah, that if should always be outside, right? Like, the function shouldn't gate it. The gate should be. Yeah, I see. OK, so a bunch of terrible OS systems. RMRF? Don't do that. Don't do that. Use PathLab.

##### **Geohot** [[00:33:04](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=1984)]
And then what's here? This is biz stuff.

##### **Geohot** [[00:33:21](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2001)]
Yeah.

##### **Geohot** [[00:33:24](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2004)]
Yeah, a few comments on that, but it looks good. Yeah, something will reverse this one. Yeah. Yeah, no, I think no rush on the method. I think the metal one, the AMD one is the most important. But it's always good to support two. OK, anything else? No, that's what I'm saying.

##### **Geohot** [[00:34:03](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2043)]
Oh.

##### **Geohot** [[00:34:05](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2045)]
OK, let's move on to the drivers.

##### **Geohot** [[00:34:10](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2050)]
OK.

##### **Nimlgen** [[00:34:11](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2051)]
Yeah, so I merged the CPU copies. So they are now part of the HCQ graph. That's like the pin memory, and they're fast. Yeah, so I'm going to finish CPU uploading this week. Profile it. So to see that everything is fine. I'm not over 11.

##### **Geohot** [[00:34:45](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2085)]
OK.

##### **Geohot** [[00:34:49](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2089)]
So is there any CPU threading support on the roadmap?

##### **Nimlgen** [[00:34:57](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2097)]
Yeah, I thought about that. I mean, I have a branch, but currently it's not merged, basically because of the overhead. Like, I don't know.

##### **Geohot** [[00:35:11](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2111)]
I don't know.

##### **Nimlgen** [[00:35:11](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2111)]
But I think it's going to be a little bit more. Yeah, it's like 11 microseconds compared to the master.

##### **Geohot** [[00:35:19](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2119)]
It's a low-chain kernels. Yeah.

##### **Geohot** [[00:35:25](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2125)]
So I haven't kept up to date. I haven't read your changes to HCQ. But the more I look at HCQ, I think that eventually everything's going to become HCQ.

##### **Geohot** [[00:35:40](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2140)]
Like, what can't be HCQ? Hold on. Yeah, I think.

##### **Nimlgen** [[00:35:54](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2154)]
Yeah, yeah. I also thought about that, that currently we have like HCQs, like a lot of obsessions already and maybe it would be a good idea to unify them like with device.

##### **Geohot** [[00:36:06](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2166)]
Yeah. I think I've. But I don't know. I don't know. There's a lot. I don't know anything.

##### **Geohot** [[00:36:15](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2175)]
I feel there's a lot of stuff that can be refactored there. I feel that this is like a big place where we're spending a lot of lines on these almost replicated abstractions. Like we have like device and HCQ device. We have buffer and HCQ buffer. Yeah. Like what would it take to unify these into, you know, to very carefully unify these into one very clean one? Also, did we fix the issues with on the MI350?

##### **Geohot** [[00:36:47](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2207)]
Do we fix the BEAM issues? I think no.

##### **Nimlgen** [[00:36:55](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2215)]
So I haven't looked into that. I think it was kernel problems.

##### **Geohot** [[00:37:00](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2220)]
I think we've got to make sure that gets fixed. And that's that's that's high priority. I mean, you mean just it's generating bad kernels or it's like. Not setting like the shared memory something, right?

##### **Nimlgen** [[00:37:13](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2233)]
No, I think it's bad kernels. I think we discussed this previous time. Or maybe I misunderstood that.

##### **Geohot** [[00:37:20](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2240)]
Oh, you mean like it's accessing out of bounds memory?

##### **Nimlgen** [[00:37:25](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2245)]
Yeah, I need to check. I think false parrot mentioned that that.

##### **Wozeparrot** [[00:37:30](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2250)]
Don't the page addresses maybe don't seem like that.

##### **Wozeparrot** [[00:37:34](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2254)]
I'm not sure.

##### **Geohot** [[00:37:36](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2256)]
I think fixing I think fixing this is tough. It's hard to pronounce if it's Violet priority and then Hola gelir.

##### **Nimlgen** [[00:37:49](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2269)]
Just trying to pick up the head 123. That's kind of massive that query. But then you know, in the end the key there is University, buradan Glenn why they wouldn't tab in corresponds with you So that's the So, but then we have reduction and four. yeah. If you don't get you don't start at 11 o'clock. because I think sometimes it's still possible to reproduce this SIG fault, and I'm not sure why.

##### **Geohot** [[00:38:17](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2297)]
What we should do is we should get two of the H machines on CI, if you want to do that. Yeah. I suppose we'll get two of the H machines on CI, and then we can start. I mean, even if they fail sometimes, I think we just got to get something stood up with these 1590 drivers. And yeah, it should check. So we should test both on those machines. We should test. Think of them as driver test CI. We should test the 1590, and we should test the, they all have 9070 XTs in them as well. So we should just have some basic stuff, which tests the drivers. There should be no drivers installed on those computers, or at least never inserted. Yeah, we got to get that stuff into CI.

##### **Chenyu** [[00:39:02](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2342)]
We already don't insert on thread.

##### **Geohot** [[00:39:04](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2344)]
Yeah. Yeah, we can leave it inserted on the greens with the 4090s, but with the 5090s, let's get this stuff on our drivers.

##### **Nimlgen** [[00:39:18](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2358)]
Yes, we can. Yeah, once machines are packing, it's ready.

##### **Geohot** [[00:39:23](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2363)]
Cool. Want to do that too? Yeah. Great.

##### **Geohot** [[00:39:29](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2369)]
Yeah, and then I think, yeah, your main project is just going to be benchmarking the optimizer, the offloaded optimizer on the MI350 machines. And yeah, figuring out what it's going to take to make it faster. If the copies are fast now, that's good. And then seeing, we're probably going to have to do some multi-threaded stuff on CPU. Because I don't think the CPU, from a single thread, there's no way the CPU gets all of its RAM bandwidth. There's no way to run Atom from a single thread and get anywhere near the copy out performance. Yeah.

##### **Wozeparrot** [[00:40:06](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2406)]
Yeah.

##### **Geohot** [[00:40:07](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2407)]
I guess you don't need all the RAM bandwidth. You just need the, but it's actually the copy out of all the GPUs. Yeah, so you need like an Atom kernel on the CPU, which is capable of processing 400 gigabytes per second.

##### **Geohot** [[00:40:24](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2424)]
Which? Closer.

##### **Geohot** [[00:40:28](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2428)]
The CPUs in those new machines are incredible. We're also going to get, I think, a new CPU. Any progress on that? I think we have a bunch of those cards coming. We're going to put some 16 terabyte ray arrays in both of those machines. We should figure out how to buy those drives in bulk.

##### **Wozeparrot** [[00:40:51](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2451)]
Yeah, just ordering them. Oh, and I don't think the card is here.

##### **Geohot** [[00:40:57](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2457)]
Yeah, there's some thread about that. I don't know if this will get pulled out, but. Yeah, let's figure out what the purchase order. And yeah. Yeah, so we're going to put some massive ray arrays in those computers. And then the other thing that I want to benchmark is copying from. So the ray arrays should be able to get about 100 gigabytes per second. And we should be able to copy to the GPUs at that full speed. So the load of the 405B. So 405B at FP16 is going to be 900 gigabytes.

##### **Geohot** [[00:41:30](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2490)]
So yeah, I want to be able to load that in like 10 seconds. And then I'm going to have to do a little bit of testing. Actually, yeah, how are we doing right now?

##### **Geohot** [[00:41:41](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2501)]
What's our copy speed from the rate array on a TinyBox?

##### **Geohot** [[00:41:49](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2509)]
To the GPU? On the TinyBox, I think it's about like 10 gigs a second.

##### **Nimlgen** [[00:42:00](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2520)]
Why isn't it 20? Yeah, I mean, for the disk, we're still limited. But the disk is still limited. So we're going to have to do it on the CPU. Oh.

##### **Geohot** [[00:42:10](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2530)]
What do you mean by the CPU?

##### **Nimlgen** [[00:42:15](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2535)]
Basically, because we do two copies, we just. But actually, no, I need to check that. Maybe it's better now. But yeah, actually, because if we go through the system memory, it's still. No, we don't do any mem copies on CPU, but yeah.

##### **Geohot** [[00:42:35](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2555)]
Yeah. All right. So I'm running. I'm on tiny R9, and I'm running Python 3 examples, LLaMA 3.

##### **Geohot** [[00:42:46](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2566)]
Let's see what our time is.

##### **Geohot** [[00:42:51](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2571)]
Oh, well, actually, that one's a little unfair, because it's the 1B, right? Let's see, size 8B.

##### **Geohot** [[00:42:59](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2579)]
So I'm running this. How fast should that load the thing?

##### **Geohot** [[00:43:08](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2588)]
Yeah, it's going to load in the second.

##### **Geohot** [[00:43:08](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2588)]
I'm getting 2.19 gigabytes per second.

##### **Nimlgen** [[00:43:19](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2599)]
Yeah, but I can measure the real speed. Actually, that's because of the Python as well.

##### **Geohot** [[00:43:30](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2610)]
What's a good way to measure the speed, then? I mean, but that's the one we really care about, right? I would love to see that loaded in under a second.

##### **Geohot** [[00:43:54](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2634)]
Yeah, I think some of it is that we're realizing them individually.

##### **Geohot** [[00:44:03](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2643)]
My.. Yeah. I think that's a good way to measure the speed. I think it's a little better.

##### **Wozeparrot** [[00:44:12](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2652)]
That's going to take forever.

##### **Geohot** [[00:44:15](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2655)]
But yeah, no, we should make that fast, make the whole LLaMA 3 thing fast. There's a flag to the loader to not have things realized individually if you're saying that that's what's slow.

##### **Geohot** [[00:44:30](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2670)]
OK, OK, I see.

##### **Nimlgen** [[00:44:31](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2671)]
We have, actually, external benchmark. I should..

##### **Chenyu** [[00:44:36](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2676)]
I'm not sure if there was speech.

##### **Geohot** [[00:44:39](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2679)]
What was this one with some permuted stuff? Which community stuff?

##### **Chenyu** [[00:44:49](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2689)]
I think. I don't know if it's this example, but some LLaMA code, some LLaMA model has permuted answer on the disk.

##### **Geohot** [[00:44:56](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2696)]
So it's calling, like, permute as part of a loading process.

##### **Geohot** [[00:45:05](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2705)]
I ran external benchmark disk raw and it's segfaulted. And now it's running and it's very slow.

##### **Geohot** [[00:45:14](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2714)]
OK, let's get these fixed.

##### **Geohot** [[00:45:16](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2716)]
Yeah. Oh, this is brutally slow. Post the comments. So this is what we're doing. This is what I got from external benchmark disk raw.

##### **Geohot** [[00:45:39](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2739)]
I first got a segfault. And then I got a copy at 0.5 gigabytes per second. And then I ran it again and I got one at 1.4 gigabytes per second.

##### **Geohot** [[00:45:58](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2758)]
Yeah, I know. Do you have any idea why these are so slow?

##### **Nimlgen** [[00:46:01](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2761)]
Yeah, because CPU doesn't.. I mean, just copy to GPU. Like, CPU doesn't support that. I mean, CPU doesn't support fast copies from disk.

##### **Geohot** [[00:46:11](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2771)]
Why is it not.. oh, I see. Why is it not copying to GPU? Oh, failed to take.. oh, is someone on this machine?

##### **Geohot** [[00:46:23](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2783)]
No. Oh, I see. This process has a lock. Somebody.

##### **Geohot** [[00:46:33](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2793)]
OK.

##### **Geohot** [[00:46:40](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2800)]
OK, so this is better. Now I'm getting 9.7. 9.8. All right, so why is it not 20? I don't know.

##### **Geohot** [[00:47:04](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2824)]
I'm going to try to copy to CPU.

##### **Geohot** [[00:47:11](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2831)]
Yeah, OK, we'll take a look into this. I'm trying it with DD right now and seeing what I can get. Yeah, DD only gives me 9.9 also.

##### **Wozeparrot** [[00:47:28](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2848)]
Yeah, I find that it's actually very hard to saturate this without multiple threads copying.

##### **Geohot** [[00:47:35](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2855)]
Without multiple threads copying.

##### **Wozeparrot** [[00:47:37](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2857)]
Yeah. Like, on this array, I had to use 16 to actually get..

##### **Geohot** [[00:47:44](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2864)]
Oh, you had to use 16 threads to get the full.. OK, cool.

##### **Geohot** [[00:47:47](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2867)]
So we're going to have to support multi-threaded. I mean, so this is going through system RAM still? Yeah. There's no way to tell the disk, the DMA to the GPU? I mean, with IORink, I don't think so.

##### **Nimlgen** [[00:48:12](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2892)]
Or maybe.. I know. Maybe we can use this DMA.. Yeah, I think we can use the buffer thing, but not for AM for now, at least. Not for AM.

##### **Geohot** [[00:48:22](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2902)]
Yeah, no, we talked about this. We'll have to write our own NVMe driver if we want to do that.

##### **Geohot** [[00:48:28](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2908)]
But.. OK, cool.

##### **Geohot** [[00:48:34](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2914)]
I mean, at least, like, yeah, 9 point something is not terrible. Yeah, well, that one was 12, but that's good some RAM.

##### **Geohot** [[00:48:41](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2921)]
Yeah.

##### **Geohot** [[00:48:45](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2925)]
OK, cool. Yeah. Cool.

##### **Geohot** [[00:48:50](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2930)]
That's good.

##### **Chenyu** [[00:48:54](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2934)]
Let's move on to cloud and hash. Oh, I did a bunch of hash filling up and stuff by inserting some kernelize and going through all the const in C tensor. So now at least you're hashing one MB. Wrong.

##### **Geohot** [[00:49:18](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2958)]
I think what's happening is you cannot have an internal representation that grows in the size of your data. That simply won't work.

##### **Chenyu** [[00:49:27](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2967)]
You could argue that one MB is a const, but it's too big of a const for our UOp and device rewrite. So for now, FDC runs, and its value is correct compared to the.. That's good.

##### **Geohot** [[00:49:54](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2994)]
You have thoughts on.

##### **Wozeparrot** [[00:49:56](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=2996)]
I mean, I merged the InfiniBand P2P one. That's fine. I was messaging you, Vien, and he said that something regressed. Or it might be slower. At least for beautiful MNIST, but that's pretty small. The overhead is, like, 3x. It's a little bit more than 3x, but it's not that bad.

##### **Geohot** [[00:50:15](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3015)]
It's not that bad. It's.. I see. I mean, we should just test this and pay out the bounty if it's good. Yeah. Yeah. I mean, if we're training on..

##### **Wozeparrot** [[00:50:28](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3028)]
I'll start a run today, and then if it's good.

##### **Geohot** [[00:50:32](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3032)]
Cool. Yeah, sounds good. I mean, we should also.. on next MLPerf, I want to get a.. I mean, I think our real goal for next MLPerf is going to be if we can get a 405B on a single machine, and we can get a multi-machine anything else. Okay. That's pretty good.

##### **Wozeparrot** [[00:50:50](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3050)]
Is Burt still in the next one?

##### **Geohot** [[00:50:52](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3052)]
Yes. Okay. Sweet. Oh, I think so. What about the ResNet part?

##### **Geohot** [[00:51:02](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3062)]
Uh.. Yeah, Burt is fine. Just Burt is fine. Just Burt is fine. If it's some weird.. Just Burt is fine. Yeah, yeah, yeah. We're cool paying out the bounty for just Burt, but I do want to figure out what this regression was. Okay.

##### **Chenyu** [[00:51:23](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3083)]
Yeah, so let's.. for ONNX, I will just summarize a bunch of stuff for comma. I think the script issue was fixed. I also added the div equals support for the flag, their favorite flag, so hopefully we are happy now.

##### **Geohot** [[00:51:46](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3106)]
Oh, we have dev? We can set the device with dev?

##### **Wozeparrot** [[00:51:49](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3109)]
Yes. I support that. They reverted the pangagrad bump for dev. I don't know if they reapplied it.

##### **Chenyu** [[00:51:56](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3116)]
Hmm. Okay. Anyway, it's there. I don't know.

##### **Chenyu** [[00:52:01](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3121)]
I closed that issue and say if anything is wrong, let me know. For ONNX specifically, cleaning up some parser stuff and the old parse buffer code cleanup,

##### **Chenyu** [[00:52:15](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3135)]
and I think working on more cleanup, you get this eventually merged, also clean up some type stuff.

##### **Geohot** [[00:52:26](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3146)]
Generally, just need more cleanups. Cool.

##### **Geohot** [[00:52:34](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3154)]
Yeah.

##### **Geohot** [[00:52:35](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3155)]
Yeah. How close do you think we are to that? I mean, depends on.. This week?.. quality.

##### **Chenyu** [[00:52:45](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3165)]
If you just want to merge it. You want it to be clean up then merged.

##### **Geohot** [[00:52:52](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3172)]
It's different. Yeah. I mean.. I definitely don't want to change the API after we merge it. It depends what you mean by cleanups.

##### **Chenyu** [[00:53:05](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3185)]
API is fine. I mean, if you say this week, then this week it is. Did we ever figure out what... ##### **Geohot** [[00:53:15](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3195)]
Did we ever figure out what the seg faults were? I feel like there's some race condition in disk or something.

##### **Chenyu** [[00:53:30](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3210)]
Yeah.

##### **Geohot** [[00:53:34](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3214)]
Maybe like something's getting closed and it's trying to read... I can also sense a bug in the environment as well. I don't know. It's not a blocker, that's an independent bug anyway. Got it. Yeah. I mean, it's moving. We move.

##### **Chenyu** [[00:54:01](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3241)]
I think it's very close. It's just like there are some.. There are some weird and.. test case that's always there.

##### **Chenyu** [[00:54:10](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3250)]
Oh, I also remove a strenum thing that was only introduced in 3.11 or 12. So it's not compatible with 3.10. So I remove that. And I think two training tests have some issue. I just skip that because it's fairly minor. But we also want to fix that. And I also add this to the CI. So it should be linked by 3.10.

##### **Chenyu** [[00:54:41](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3281)]
So this won't happen again. Cool. In general, more stuff that can make emerging on that.

##### **Chenyu** [[00:54:57](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3297)]
Other bounties.

##### **Geohot** [[00:55:00](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3300)]
I'm adding a $200 bounty now for Muon Optimizer. Muon is a new one. Muon.

##### **Chenyu** [[00:55:09](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3309)]
The Facebook one got merged. Which Facebook one? So Torch. Torch is going to merge that as in their official repo. There's a PR for that.

##### **Geohot** [[00:55:22](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3322)]
Oh, Torch is going to merge Muon? Yeah. Oh, and that reminds me. I still haven't looked at the beautiful on this Torch. Every week.

##### **Wozeparrot** [[00:55:31](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3331)]
HLB C4 one.

##### **Geohot** [[00:55:34](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3334)]
HLB C4. I can't believe still that fusee range isn't equal to one yet.

##### **Chenyu** [[00:55:40](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3340)]
I don't know when it's working on that. I mean, it's kind of related to the reduced refactor.

##### **Geohot** [[00:55:48](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3348)]
It's so simple when you get down to what it is. I don't know. Scheduler and code gen almost both entirely need to be thrown away and replaced by a new thing. Oh, what's this?

##### **Chenyu** [[00:56:03](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3363)]
They just forward. We still have the merge. And store thing. That's the other thing.

##### **Geohot** [[00:56:08](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3368)]
Not really. I kind of did it. You would figure out that one. Yeah. I don't know.

##### **Geohot** [[00:56:20](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3380)]
I'd pick what is like half the bounty. I think I did. I think I did half of it. I think it's kind of. I mean, I did the whole like define reg thing, which was really the hard part. But the overworld, it actually does mean something different. A sign returns the buffer, whereas store doesn't. And this makes the overworld cleaner. Yeah. I think those are mostly done. The const refactor can still be done. I was staring at that.

##### **Geohot** [[00:57:02](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3422)]
I did something small on that. So now it's less scope. Cool. Try something with removing ops LLVM.

##### **Geohot** [[00:57:17](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3437)]
You remove ops LLVM?

##### **Wozeparrot** [[00:57:19](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3439)]
Just to unify it with CPU.

##### **Geohot** [[00:57:22](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3442)]
Oh, yeah. We should do that. The device and compiler separation. Oh, yeah. That's a good project. Not quite that.

##### **Wozeparrot** [[00:57:31](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3451)]
Just removing ops LLVM and making it like a flag. Yeah. To turn on LLVM compiler.

##### **Geohot** [[00:57:38](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3458)]
Yeah. I mean, what we want is like a device can specify multiple compilers. We have a whole bunch of these now. Like AMD has LLVM and HIP. CPU has Clang and LLVM. Yeah, so everybody has PPX and CUDA.

##### **Geohot** [[00:57:56](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3476)]
So yeah, that should all be. That's like a big refactor that needs to be done. It shouldn't be hard. And we should have three Condule types ensemble,

##### **Geohot** [[00:58:18](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3498)]
just NUPCE and Simpleate. And so we have our offerings on both bundles and vibros. That's pretty good. And that's it. All all right. So let's just get on with the lizugs cloud and get some, get bluebellies that I already have. Now is going to be interesting to me because YouTube, this thing Is enabling us to get which is talking. So punch in there. Now, Yeah.

##### **Chenyu** [[00:58:37](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3517)]
Anyway, I was writing muon, and I was hoping that I could wait until the torch one got merged so I have a reference. That's how I'd like to test it anyway.

##### **Geohot** [[00:58:52](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3532)]
Yeah, yeah.

##### **Wozeparrot** [[00:58:54](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3534)]
I think the implementation is not that bad. It's really clean. And there's a lot of clean implementations of muon as well.

##### **Chenyu** [[00:59:03](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3543)]
Yeah, but I mean, it's like, it is way too maintain. Yeah.

##### **Geohot** [[00:59:08](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3548)]
And if we have to install something, we have to install something. And we still have to install something for it. We still install TensorFlow to test Lion or whatever.

##### **Chenyu** [[00:59:18](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3558)]
Yeah. Yes, and it's pinned to a much older version because.

##### **Geohot** [[00:59:26](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3566)]
Yeah.

##### **Chenyu** [[00:59:28](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3568)]
If someone can find a better way to remove that, that would be nice.

##### **Geohot** [[00:59:36](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3576)]
Yeah. How's the Whisper bounty?

##### **Geohot** [[00:59:42](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3582)]
Tough on that. Didn't have much time to work on it. Oh, that's from last week. We don't really have that many bounties.

##### **Chenyu** [[01:00:00](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3600)]
That's like, am I workable?

##### **Chenyu** [[01:00:02](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3602)]
I don't know if that's an issue.

##### **Chenyu** [[01:00:04](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3604)]
No.

##### **Geohot** [[01:00:07](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3607)]
I mean, it's kind of hard. All of this refactor stuff is really hard to make bounties. No, no, it's easy to make bounty. It's very clear what the end state look like. It's just very hard for people to do it.

##### **Geohot** [[01:00:24](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3624)]
Yeah.

##### **Geohot** [[01:00:32](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3632)]
Maybe, I mean, I've been working on, maybe we'll be able to have a bunch of bounties once I have this intermediate UOp syntax. We could just, I don't know. But no one ever does those bounties either, the ones where it's like, get the GEMM to be fast. LAMMIT kind of does them. But yeah.

##### **Geohot** [[01:00:54](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3654)]
Anyway.

##### **Geohot** [[01:00:58](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3658)]
HVIC decode is a very doable bounty, $500 for that one. That one's doable. RKNN NPU, $500. $500 is very doable. I'll move those ones to the top, because they're very doable.

##### **Wozeparrot** [[01:01:10](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3670)]
Have you seen the new chip?

##### **Geohot** [[01:01:13](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3673)]
What new chip?

##### **Geohot** [[01:01:14](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3674)]
The Rockchip's new, the announced one. No, is it good? What nanometer? I believe it's 3. Really?

##### **Geohot** [[01:01:27](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3687)]
37.

##### **Geohot** [[01:01:35](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3695)]
Wait, there's no way they let China buy a three nanometer chip? I don't know.

##### **Geohot** [[01:01:39](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3699)]
Off topic for the meeting.

##### **Chenyu** [[01:01:42](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3702)]
OK. Great. Oh, my flight got delayed again.

##### **Geohot** [[01:01:46](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3706)]
Oh, great. OK.

##### **Chenyu** [[01:01:49](https://www.youtube.com/watch?v=wZ5Ch0ODRv8&t=3709)]
Hopefully, I'll see you later today. Cool. I think that's it for this meeting. Thank you all. See you next week.
