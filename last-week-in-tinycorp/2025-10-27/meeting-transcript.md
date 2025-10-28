# 2025-10-27 Meeting

### Meeting Agenda

**Time:** 6am Monday San Diego time, 9pm Hong Kong time
- company update
- new linearizer, SPEC, flash attention
- openpilot regression
- FUSE_OPTIM, assign?
- viz
- driver
- tiny kitten
- more symbolic?
- other bounties, fp8, clang2py

### Audio

[Youtube Link](https://www.youtube.com/watch?v=z_FDsZ1ms2s)

### Highlights

- **[Company Update](#geohot-000000)**: The company sold two tiny boxes this week, with payment received for both. A reminder was issued that orders without payment will not be fulfilled.
- **[New Linearizer, SPEC, Flash Attention](#geohot-000055)**: The new linearizer has caused some regressions but is now cleaner, functioning as an opinionated toposort. The specification for tensors and kernels has been tightened, and PyRender has been improved for better readability. Work on flash attention is blocked by the need to improve the expander and unify shape definitions.
- **[Openpilot Regression](#chenyu-001014)**: There are two major regressions in the visual model. One is a 10% regression after rangeify, and the other is a 6-millisecond slowdown after the new linearizer, which also made the policy model 2 milliseconds faster.
- **[VIZ](#qazalin-001536)**: Work is underway to visualize cache counters, with a functional UI that can pull data from CUDA counters. This will help in understanding cache utilization.
- **[Driver](#nimlgen-002207)**: Refactoring has been done on the PCIe components, which might resolve reset issues on Macs with 50-series GPUs. Progress on the 580 is awaiting the new Client2Pi as updates to the GSP require runtime updates.
- **[Tiny Kitten](#geohot-002507)**: To improve performance, it was suggested to use Warp Group, which utilizes four warps (128 threads) to better overlap loads and MMAs, potentially doubling the performance.
- **[More Symbolic?](#sieds-lykles-002815)**: A-range folding was merged, and a bug in cat splitting was fixed. Work is also being done to merge adjacent reshapes and permuted ranges to optimize operations like summing a transposed matrix.
- **[Other Bounties, FP8, Clang2py](#b1tg-003801)**: The FP8 tensor core bounty is complete. An issue with MMU faults on the MI350 during multi-GPU training was reported. For clang2py, good progress is being made, though parsing macros and the slowness of libclang present challenges.

### Transcript
##### **Geohot** [[00:00:00](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=0)]
Anyway, welcome everyone to our Monday meeting. I think I started with a company update. We sold a bunch of tiny boxes this week. Money came through for two of them.

##### **Geohot** [[00:00:24](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=24)]
Email, if you order a tiny box and you didn't send the money, you don't get a tiny box. Yeah, we sold two tiny boxes this week. We've regressed. Well, I guess we'll talk about that soon. But yeah, we have to get back in the good graces of our only customer.

##### **Geohot** [[00:00:47](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=47)]
Yes. We can move on to next slide.

##### **Geohot** [[00:00:55](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=55)]
So it seems like the new linearizer causes a lot of trouble. We've sold a bunch of regressions.

##### **Chenyu** [[00:01:03](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=63)]
It's not just that. Rentify also caused a bunch of regression, but we'll talk about that later. We can talk about a good thing about a new linearizer.

##### **Geohot** [[00:01:11](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=71)]
Yeah, so it even cleans up a little bit more. It's even cleaner now. It's a linearizer is just a toposort that has some priorities. So it's just an opinionated toposort, which is nice. I also factored if and end if out of the graph. If and end if are over, they were always kind of confusing. So the only place they're inserted at the very end just for renderers, so that we can do gated stores. So you know, the dream is finally happening with the deletion of a whole bunch of UOPs or at least some places and I've tightened the spec up a whole lot. So the spec is now pretty low.

##### **Nimlgen** [[00:01:57](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=117)]
So the spec is now pretty low.

##### **Geohot** [[00:01:57](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=117)]
Like we have three specs. We have the tensor spec and the tensor graph. We have the kernel spec for what's inside each kernel before code gen. And then we have the program spec, which is what's inside the kernel after code gen. I also work today on PyRender. So you'll see that in Viz, the rendered stuff looks a whole lot nicer.

##### **Geohot** [[00:02:22](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=142)]
It's actually kind of readable.

##### **Nimlgen** [[00:02:23](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=143)]
So. Okay.

##### **Geohot** [[00:02:27](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=147)]
Why is it called control flow? It should be renamed linearizer, I think.

##### **Nimlgen** [[00:02:33](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=153)]
Okay.

##### **Geohot** [[00:02:34](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=154)]
That's just what Thompson called it.

##### **Geohot** [[00:02:39](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=159)]
But yeah, so now spec equals two checks, both that the UOPs match the full UOP spec and that all of the three points PyRender, PyRender, exec PyRender returns the same UOP. So.

##### **Nimlgen** [[00:02:54](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=174)]
Mm-hmm.

##### **Geohot** [[00:02:56](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=176)]
Yeah, I'll get that. And I'll get that in CI. It's a little bit slow right now, but I'll just disable some tests. Yeah. Figure something out about that. I'm for flash attention. I mean, what kind of got me started doing this was that the de vectorizer, another expander doesn't work for flash attention. So, yeah, I mean, I don't know what, what does that mean? The expander. Uh. If you have. Intermediate buffers. Okay. So there's two ways you could have an intermediate buffer interact with like upcasts in one way. The upcast terminates at the bufferize and in the other way, the upcast flows through the bufferize. But when the upcast flows through the bufferize, you have to make the buffer bigger. And this is easy to do when it's a bufferize, but hard to do after you've lowered it to stores. So there's some you can do in one. Abstraction and some you can do in the other abstraction. But in reality, I think that like we have a problem right now where shape is in two places. So we have shape in like dot shape and then we have shapes in the D types. And I think we should unify all of that to one.

##### **Geohot** [[00:04:16](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=256)]
And then the expander will basically be free. I also am starting to like really understand semantically with each one of these UOPs means.

##### **Geohot** [[00:04:27](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=267)]
So like index selects a region and then load. What load does is moves that region from whatever memory system it's in to a different memory system. So maybe D types will start including an address space. We'll start including a shape and then we can like work on this stuff better.

##### **Geohot** [[00:04:52](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=292)]
We can work on like. Like all of these these intermediate buffers will be better understood what they what they are.

##### **Geohot** [[00:05:05](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=305)]
But like I'm starting to see how it comes together where all these graphs are basically the same thing. Like we have this lowering of the bufferize to a store and a buffer and it's the same for defined globals and defined locals. And soon I'll rename define global and define local like we're getting to the point now where this can all kind of be unified. So yeah, that's kind of the blocker on on flash attention getting the vectorizer and the expander to work. I could hack it but I shouldn't hack it. I think I just waste time doing that. So get the expander to work then once the expander works, I mean it does kind of work but there's some sets of opt-ops that it doesn't work for. So I just want to like rewrite it to not even think about these problems. So I just want to like rewrite it to not even think about these problems. So I just want to like rewrite it to not even think about these problems. Then it's easier to think about what the what the online max trick is.

##### **Nimlgen** [[00:06:07](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=367)]
Then it's easier to think about what the what the online max trick is.

##### **Geohot** [[00:06:08](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=368)]
Basically, the D type has a shape and the shape is one dimensional. And there's no reason for this. They should be the same shapes and it should be arbitrarily dimensional. And you can just have like a flattener pass which puts everything in one dimension for one.

##### **Nimlgen** [[00:06:33](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=393)]
And you can just have like a flattener pass which puts everything in one dimension for one.

##### **Geohot** [[00:06:33](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=393)]
We can also unify. We can also unify Japan index. Japan index are pretty much the same thing. Oh, that would be nice. Yes. Yeah. We can kind of get rid of job. Just index. So next. Just index.

##### **Geohot** [[00:07:02](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=422)]
So next. I also made a. So now when you look at the colonels in the pie render, it like draws out the colonels, so you can check out what I posted in general, you can see how it's like split into all the colonels and that's the beautiful, eminence trainer in like uop format, you can actually evaluate that and then schedule that and run it.

##### **Chenyu** [[00:07:29](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=449)]
Can I print this for Python backend instead of whatever thing?

##### **Geohot** [[00:07:35](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=455)]
So I looked at that, and yeah, I could. We could definitely do something else with the Python backend, but the problem with the Python backend is it's not really this, because this is for single uops that does the top of sort. The Python backend needs a list of uops. Oh. Because it's after cogen. Yeah, yeah, yeah. Yeah, so that's how I was originally doing it, but yeah. I mean, we should unify a bunch of these things. Now with these spec checks, we should be able to delete the old uop pretty printer. I think this one's a lot better.

##### **Geohot** [[00:08:19](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=499)]
Yeah. That's nice. Sounds good. One last thing.

##### **Chenyu** [[00:08:29](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=509)]
You say something about nan and dedupe?

##### **Geohot** [[00:08:33](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=513)]
Oh, yeah. I fixed a bug today. So float, so nan is not equal to nan, and we know that. But I thought that nan is nan, but nan is not nan. If you generate the nans with float quote nan, float quote nan. So here, I'll post a funny picture, because I think I can do it with a dictionary. So if I make like a, yeah.

##### **Geohot** [[00:09:09](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=549)]
Check that out. Post a screenshot in general.

##### **Nimlgen** [[00:09:14](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=554)]
Mm-hmm.

##### **Geohot** [[00:09:17](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=557)]
See? Yep. So if you canonicalize that, if you do math.nan instead, it doesn't have a problem.

##### **Geohot** [[00:09:39](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=579)]
So since I just changed them into 2.0,

##### **Geohot** [[00:09:51](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=591)]
it's gonna give you the same truth. Yeah. That wouldn't be doing Viola lga.

##### **Chenyu** [[00:09:59](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=599)]
I think for NAND, it's better to just use the math.version anyway. We probably want to do that.

##### **Geohot** [[00:10:07](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=607)]
Yeah, we should always use the math.version.

##### **Chenyu** [[00:10:14](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=614)]
Great. Let's move on to the next one. Next is open pilot regression. So I think there are two major big regressions for the visual model. One is immediately after rangeify. I think there's like a 10% regress, which is pretty much just the last big kernel. We have a very big kernel at the end that gets a bunch of stuff. So that was slow. That one, we can just hack by adding contiguous to the kernel. Or do something with that very big kernel that feels at the end. Then there's the other one that's after the new linearizer. So that has a mixed effect. It made vision model, I think, six milliseconds slower. But to make other policy model like two milliseconds faster. So I think that one is mostly just from the effect of the vision model. And then the other one is removing the reorder, block reorder, which I think is just because the load, the order is different than something like out of the for loop or something like that. I would take more look today.

##### **Geohot** [[00:11:40](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=700)]
Well, it does do something concretely pretty stupid. And I remember this bug in the old linearizer. And it's hard to even think about how we want to beat it. But like the biases. So the biases are loaded before the ranges and then added after the ranges. So you just have you just waste your registers, basically.

##### **Chenyu** [[00:11:59](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=719)]
Yeah, I think it's something like that. Because previously, I tried to remove block reorder. And that caused some other issue. Onyx model won't compile. I think for now it's fine just because we removed that model from benchmark. I don't know if we currently run that model. That they're wrong or not. Yeah. Yeah. So I will see. So the good thing is this time is not image value pack. So all the image stuff looks fine. So something else. Great. Yeah. Yeah. Because Karma really wants to upgrade. So they can use they can benefit from all the USB stuff.

##### **Nimlgen** [[00:12:47](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=767)]
Yeah.

##### **Chenyu** [[00:12:50](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=770)]
So yeah, hopefully you get this. I'll see if we can fix this this week so they can prepare for their CommaCon stuff. Okay. Cool. Next is fuse opting. Oh, this is the same item as last week. I spent probably 30 minutes on it. And I don't know what to do with this one. So it's not it's not unique. Because I have a hack that fix unique. I didn't fix this one. Something else.

##### **Geohot** [[00:13:18](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=798)]
I haven't had a chance to look at it.

##### **Chenyu** [[00:13:19](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=799)]
Yeah. So I have to comment. We will produce this one in in I think dev channel. But it currently works for so it only fails for one of the next test and works for everything we put. So I added that to the test. But it's still not default. As we discussed earlier, it probably shouldn't be default. But it's still not default for every optimizer. Just for the ones that I support.

##### **Geohot** [[00:13:51](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=831)]
Yeah.

##### **Chenyu** [[00:13:53](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=833)]
Cool. This is for I don't know if we have any plan to change assign or anything like that. Always feels confusing to me.

##### **Geohot** [[00:14:04](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=844)]
I mean, yeah, there's problems with it. But it's not gonna it's not causing an issue with like the main there's two. Major things we need for the contract. One is like a fixed lower that supports the like flash attention optimizations and the other is like a fast back end like tiny kittens.

##### **Chenyu** [[00:14:29](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=869)]
Yeah, I think I think this is less of the contract for contract. It can be more like specific focus on the model of the contract.

##### **Geohot** [[00:14:39](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=879)]
Yeah, we can also like I mean, there's a lot of stuff we can do for the contract to like we don't even have to figure out. How to find the optimizations automatically. We can just have contiguous pass at an ARG which is just Python that'll do an ASC transform.

##### **Chenyu** [[00:14:54](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=894)]
Yeah, it's just like the DSP contract.

##### **Geohot** [[00:14:57](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=897)]
Yeah. But we need like two things are super important to tiny kittens and like the high level lowering stuff.

##### **Geohot** [[00:15:09](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=909)]
Yes. Like the stuff that's gonna fix the memory usage. Yes. Okay, the next one is for this.

##### **Qazalin** [[00:15:36](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=936)]
So for this I'm working through getting the cash counters visualized. And this. And Lydia has something in there to link but it doesn't really have anything that we can look at. So I'm trying to get these graphs in this currently I have a UI that works and also I can pull the counters from the CUDA counters. So they said it's just looking those up. Oh, that's the picture of that. In general.

##### **Geohot** [[00:16:16](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=976)]
This is how

##### **Qazalin** [[00:16:20](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=980)]
this is the graph that we're talking about is basically concerned about how you're utilizing your cash is going to help with our memory stuff too.

##### **Geohot** [[00:16:35](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=995)]
You got a screenshot of our replica.

##### **Qazalin** [[00:16:40](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1000)]
Oh, this is this MVDS thing. I can share that too. Yeah, our replica is very close. Almost there.

##### **Geohot** [[00:16:54](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1014)]
Is our replica. Yeah, pretty much. Yeah. Then behave like all these graphs. Yeah. We got to like light up those hours if it's big, but. Yes.

##### **Nimlgen** [[00:17:26](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1046)]
Cool.

##### **Geohot** [[00:17:41](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1061)]
Yes. Yeah.

##### **Geohot** [[00:17:41](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1061)]
So I think this segues into a no Jen, your top priority this week is to get these counters exposed to get this UI actually wired out.

##### **Nimlgen** [[00:17:53](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1073)]
Yeah. Yeah. Actually, that was my question. If we want this because this cutity is merged. Yeah. Okay.

##### **Geohot** [[00:18:03](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1083)]
Oh, we definitely want the counters. So the reason we want the counters is sqtt can never be free. Sqtt will always have to be behind a flag. But I think these counters can be free.

##### **Geohot** [[00:18:24](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1104)]
True. Yeah.

##### **Nimlgen** [[00:18:26](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1106)]
Yeah. Almost free. We need just some overhead to copy these. I mean, I think we. Yeah. We just need some pockets to copy these data. After you. Each kind of execution. But, yeah, I think it's it's almost free.

##### **Geohot** [[00:18:46](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1126)]
Yeah. I'm I'm I'm okay with this taking like a 10 or 20% hit, but there's no way we could ever enable sqtt by this equals one. But I think we should be able to enable these counters with this equals one.

##### **Nimlgen** [[00:19:00](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1140)]
Yeah. Also for sqtt currently like the design of sqtt initially was that we flush the buffers from the device only once. When we. So destruction of python. So maybe we can do this manage this a bit better and flush buffers after each kernel. So maybe this will require less VRM.

##### **Geohot** [[00:19:30](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1170)]
That'd be cool.

##### **Nimlgen** [[00:19:31](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1171)]
Yeah. Well, okay. So, yeah, I can look into that as well. Yeah.

##### **Geohot** [[00:19:38](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1178)]
Yeah. Let's start. Let's start getting this stuff wired up. Yeah. Let's start getting this stuff in the UI. Yeah.

##### **Geohot** [[00:19:51](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1191)]
And then just an update on the I requested that other privilege from Apple. I think we'll give them another week to give it to us and if they don't we'll have to use a user shim app.

##### **Geohot** [[00:20:05](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1205)]
Yeah.

##### **Nimlgen** [[00:20:06](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1206)]
Yeah. Yeah.

##### **Geohot** [[00:20:09](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1209)]
It's probably not the end of the world if we use a shim app.

##### **Geohot** [[00:20:12](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1212)]
I wonder if we could just even like open the mock port and a shim app and then forward it

##### **Geohot** [[00:20:16](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1216)]
to python. Probably yes.

##### **Geohot** [[00:20:27](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1227)]
But yeah, I mean, the basic thing is that we need an app signed with our certificate in order to access in order to use the IO service open.

##### **Geohot** [[00:20:37](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1237)]
Yeah.

##### **Geohot** [[00:20:39](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1239)]
But it does work. I did confirm that what they gave us actually does work. And did you check you have signing access to it as well?

##### **Nimlgen** [[00:20:46](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1246)]
Yeah, I also tested this. Yeah, it works.

##### **Geohot** [[00:20:49](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1249)]
Great. You know, I mean, it'll be great. It'll be great to have all this. This profiling stuff working with with USB and our MacBooks and we can all debug it easy.

##### **Geohot** [[00:21:00](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1260)]
And yeah. Oh, fun project for someone who's just starting to work with us.

##### **Geohot** [[00:21:07](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1267)]
Oh, we got a question from someone else who's who's who's listening to this. If you want to get CUDA the CUDA compiler running on Mac in like a Docker container, that'd be

##### **Geohot** [[00:21:16](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1276)]
good. Just so like, like if you see like we have like MVCC compiler now if you get that working on Mac.

##### **Geohot** [[00:21:26](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1286)]
It'd be cool.

##### **Geohot** [[00:21:28](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1288)]
I'm going to use CUDA equals one for Mac. Not CUDA equals one, but not have to use a NAC.

##### **Nimlgen** [[00:21:43](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1303)]
Okay.

##### **Geohot** [[00:21:47](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1307)]
Anything else for this. So, that's what I think. Nexus driver.

##### **Nimlgen** [[00:22:07](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1327)]
Yeah, so, for the USB GPU, I think we're waiting for Apple. I did some refactors in the PCIe stuff. I think that, I don't know, I don't have the 50 series GPU, so maybe if you can test this. So, actually, I think the reset problem on Mac. Because the address has changed and we basically should have remapped after reset. So, maybe it should be better now. Cool.

##### **Geohot** [[00:22:49](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1369)]
I can test it tomorrow. I'll try with that 5060 or whatever.

##### **Geohot** [[00:22:55](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1375)]
But also, what about NV being, I guess, yeah, we're still waiting on the new thing for the 580 so we can test it.

##### **Nimlgen** [[00:23:05](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1385)]
Yeah. Basically, yeah, and currently 580 is blocked on the new Client2Pi. Basically because we even cannot update our runtime because it will break. Because they changed some structs. And actually, these structs go directly to the GSP. So if they update GSP, our runtime should be updated as well. So just to fix this once. And for good, it's just, yeah, to generate these online for each version. So, yeah. I think the cleaner solution will be just to use the new after-gen stuff instead of EVEs. Great. Cool.

##### **Geohot** [[00:24:02](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1442)]
Anything else? Yeah.

##### **Nimlgen** [[00:24:04](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1444)]
Yeah.

##### **Geohot** [[00:24:40](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1480)]
um. Yeah, any last tips for this game? Round of four. Somewhere in that bullet column. There is a synth in there.

##### **Geohot** [[00:25:01](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1501)]
We will bring you one later. while I could write basically.

##### **Geohot** [[00:25:07](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1507)]
So I double-double-double-double. And it still only gets like 60, 70-ish? So there's also Warp Group that might help you. Is that on the 4090s?

##### **Geohot** [[00:25:24](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1524)]
Yeah, so Warp Group is not anything special about the 4090s. Warp Group just means that you use a that you use 128. 128. So you basically use right now, this is only using a local size of 32, which is only using one Warp. But if you use Warp Group, that'll use basically four Warps. The Thundercat writes it pretty simply. So it'll use four Warps so it'll be able to overlap loads and MMAs in the single in the same CU. Like right now, even though it's double-buffered, you're not being able to keep the tensor cores constantly fed because you only have one Warp occupancy in the CU. But with Warp Group, you'll get four Warps of occupancy. And I think that'll... I think that and double-buffering alone should get you pretty good numbers.

##### **Geohot** [[00:26:17](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1577)]
Okay, yeah. I'll try that. And I should also be able to get the Flash Attention example running.

##### **Nimlgen** [[00:26:26](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1586)]
Cool.

##### **Geohot** [[00:26:26](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1586)]
I think the thing to do here is to first achieve some... first get their fast examples running, and then figure out how to implement these in TinyGrad.

##### **Nimlgen** [[00:26:38](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1598)]
Yeah.

##### **Geohot** [[00:26:39](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1599)]
In the low-level UOP stuff. Also, even with their stuff, we should be able to still get it working with our run times. We should be able to see all these counters and stuff. This is why we're getting all the counters working. It's time to really push on performance. But cool. I'm glad the map all got merged today. Yeah, check out Warp Group. I actually really like how they do it with the warp colon colon thing, which is like it's clear that that thing... is running on the whole warp. And then Warp Group is like, yeah, it's like the four. So I wonder if you literally just change

##### **Geohot** [[00:27:11](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1631)]
that, if that would fix. That probably doubled the perf. Well, now we also have the FP8 memo that you can test. Wait, how is this example double buffered? Not the one that I merged. I have a...

##### **Geohot** [[00:27:33](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1653)]
Oh, you have another one. It didn't get faster. Okay.

##### **Nimlgen** [[00:27:37](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1657)]
Cool.

##### **Geohot** [[00:27:40](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1660)]
But yeah, I think we can also get really minimal stuff just to read the PTX and make sure we're doing the same

##### **Geohot** [[00:27:50](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1670)]
layouts. Anything else? No. I think that's all. Next one is for Seitz. Hello.

##### **Sieds Lykles** [[00:28:15](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1695)]
Yeah, so I got A-range folding in the big graph merged last week. It's nice. I found another A-range that I wasn't folding. It should be actually pretty simple to get that one. Because you just have to, like, we only do A-range folding when there's a single A-range. And it's just, you just have to do it in two stages. And then I found the bug with cat splitting today, so I can get that merged for CPU now.

##### **Nimlgen** [[00:28:51](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1731)]
Cool.

##### **Sieds Lykles** [[00:28:51](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1731)]
And then, you know, we'll figure out how to render that for GPU DIMMs as well. And then... Yeah, once it's merged for CPU, we can go over that tomorrow. Yeah. Yeah. So, yeah, I think that's all. And I've also been trying to move the merge adjacent to the big graph. But I realized that the merge adjacent is like, it's only merging, like, reshapes, but it's not merging permuted ranges. Because you have to try to merge the ranges also in permuted order. Yeah. Yeah. So I was just wondering how much, I was just playing around, see how much was to be gained by that. Because if you remember the example of, like, a transposed matrix and then summing the whole matrix, like, that one still doesn't work.

##### **Geohot** [[00:29:59](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1799)]
I see.

##### **Geohot** [[00:30:01](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1801)]
But yeah, that's... Yeah. Yeah. So you want to, I saw your thing about that should, that's because that's on a reduce, right? You can try the reduces in any order.

##### **Sieds Lykles** [[00:30:07](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1807)]
Yeah. Yeah. But, well, yeah, the reduces, yeah, you can...

##### **Geohot** [[00:30:13](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1813)]
Well, the transpose matrix summing the whole thing would be a reduce, right?

##### **Sieds Lykles** [[00:30:17](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1817)]
Yeah.

##### **Nimlgen** [[00:30:20](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1820)]
Yeah.

##### **Geohot** [[00:30:21](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1821)]
Yeah. The stores you can only do adjacent.

##### **Geohot** [[00:30:26](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1826)]
Yeah. I mean, the stores, like, it's easier for me to think about this stuff while it's still in buffer. Yeah. It's like enjoy your level of error, right? Yeah. So it gives you a little bit of a Spider you can it yani. Absolutely. If it does come to this, it doesn't need a small spot there. But it gives it full alignment with the Educom looks like that. Fee design around that. Yeah. Yeah. I think one of the things I wanted was the web site and後 Do not take advantage of it. Done. why you can merge adjacent ones.

##### **Geohot** [[00:31:05](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1865)]
And yeah, not adjacent ones. Yeah, and I mean, I think also

##### **Sieds Lykles** [[00:31:15](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1875)]
you want to try the split-reduce-opt after merging all the reduce ranges. I think Chan-Yu posted something at some point about inconsistent split-reduce-opt.

##### **Geohot** [[00:31:32](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1892)]
Yeah, we definitely want to first merge the ranges

##### **Geohot** [[00:31:35](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1895)]
before we do that. Yeah. I mean, the split-reduce-opt is... Sorry?

##### **Geohot** [[00:31:47](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1907)]
The split-reduce-opt is like a really basic thing. The code's kind of confusing to me, but the only time you want to do that, what that basically means is it's the same thing as group-reduce, but on globals. So we can think about how, like, to...

##### **Geohot** [[00:32:02](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1922)]
Yeah. Use the same logic.

##### **Nimlgen** [[00:32:09](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1929)]
Yeah.

##### **Geohot** [[00:32:13](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1933)]
Oh, and also, I saw Chan-Yu's trying to get rid of the correct div mode folding. This one...

##### **Sieds Lykles** [[00:32:26](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1946)]
I think it might be easier to change div and mode into full. So it's more diff than to...

##### **Chenyu** [[00:32:36](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1956)]
Oh, I don't think that's the issue, though. So I thought the regression was causing by... So the div mode is only correct if it's, like, numerators positive or something like that. It has a limit. But the thing that regress...

##### **Sieds Lykles** [[00:32:57](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=1977)]
So the reason that it's... Basically... Basically... The way that the image... Like, when you do the image index, it takes an index and does, like, a single div and a mode, and you can remove them if... Right? If... When your index is negative,

##### **Geohot** [[00:33:24](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2004)]
you can fold the... Like... If the... If the... You can get rid of the... Valid. If...

##### **Sieds Lykles** [[00:33:37](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2017)]
If the thing is negative, the valid is... True, but... So... We do truncating div. When your index is minus one, the div of that is zero. So your index is not actually out of bound. But when you do floor div, like, if your index is negative, one, then it's actually out of bound.

##### **Chenyu** [[00:34:08](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2048)]
Yeah. So my impression is the expression that was not folded correctly, it's because there's an alter date that was not considered when that expression is... So that expression itself cannot be simplified with the correct div mod. But if it's combined with the alter condition, that should be fine. That's my take for left lag. And why we cannot take it out because our current rules, it's only look at the index,

##### **Geohot** [[00:34:43](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2083)]
but not the alter valid.

##### **Nimlgen** [[00:34:49](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2089)]
Yeah.

##### **Chenyu** [[00:34:50](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2090)]
So this is only given some conditions, right? It's either... I think the solution is probably either combined the condition of, and the actual expression as a whole, and a fold let using the correct rules.

##### **Geohot** [[00:35:13](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2113)]
But it's also not the... Yeah.

##### **Sieds Lykles** [[00:35:16](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2116)]
There's another thing you have to be careful with, which is we rewrite mod by a power of two as an and,

##### **Geohot** [[00:35:26](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2126)]
but that's only correct if your numerator is positive. I wasn't aware of this.

##### **Sieds Lykles** [[00:35:40](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2140)]
It's like there's these two or three different things, and they're interacting with each other. And if you all leave them on, turn on, they will work. But if you turn one of them off, then you have to turn all of them off.

##### **Geohot** [[00:35:57](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2157)]
And it's... I don't know. Yeah, it's hard. It's hard to get it.

##### **Chenyu** [[00:36:03](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2163)]
There are certain things about the... I think we should separate the correctness fix, like what's correct for every input versus what's correct for image and other stuff in general. So we certainly don't have this concept of... I mean, we have the concept of a rewrite context, but we don't quite have the concept for... Given these constraints, we can simplify this expression. I think there's like uop given valid, that's kind of like this. So you simplify uop given other uops. But there are certain... It's not just image folding. There are other uop expression or kernels that can be simplified if we have a clear version of this concept. Because for now, if you have something like a valid inside, a valid inside a kernel, a branch of another valid, it doesn't necessarily consider the outer gate. Although if you consider that, obviously you can simplify it further.

##### **Geohot** [[00:37:12](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2232)]
So that's something I'm more interested in. Okay. Anything else? Not really. Okay. Next we can move on to other bounties.

##### **Chenyu** [[00:37:40](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2260)]
B1tg got FP8 tensor core. I think that completes the original bounty. I already commented on the final PR itself.

##### **Geohot** [[00:37:55](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2275)]
B1tg, do you have something else to add? Hello?

##### **B1tg** [[00:38:01](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2281)]
I started doing some experiments on the MI350 and the dev run script fails with MMU. And it can train single GPU with PS 128.

##### **Geohot** [[00:38:34](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2314)]
So I think it's a good idea to add a kernel.

##### **Chenyu** [[00:38:35](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2315)]
I think for this, it's more useful if you can find those smaller examples and say, OK, if running this script fails, then people can take a look.

##### **B1tg** [[00:38:47](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2327)]
You mean I need to find the broken kernel?

##### **Chenyu** [[00:38:51](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2331)]
Yeah. So let's start with finding which kernel, which optimization gives the MMU fault and is consistent, or is this MMU fault. Yeah. So I think it's a good idea to add something else. Maybe it's independent of the kernel because there are hidden states somewhere. I don't know. So for now, it's very far for people to help you other than running the whole thing and maybe wait until it faults.

##### **B1tg** [[00:39:20](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2360)]
OK, I think I just working using a single GPU. Yeah.

##### **Chenyu** [[00:39:29](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2369)]
Usually, if it's tied to a single kernel, then it should be able to find which kernel faults consistently. If you suspect it's due to multi-GPU, then reduce the GPU count so that you can still reproduce the issue and just be aware of certain behaviors that's different between two GPUs and four GPU. Notably, the ring already used will be different. So also test that. Other than that, if you still don't have GPU, you still cannot specify, find a specific thing, let me know. I can help. I can take a look.

##### **Geohot** [[00:40:08](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2408)]
OK.

##### **Chenyu** [[00:40:09](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2409)]
Yeah, but usually just reduce the GPU count, reduce the batch size, try to find a specific kernel, see if it's consistent. Little things will help.

##### **Geohot** [[00:40:24](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2424)]
Also, do you know why is FP8 tensor core not fast?

##### **B1tg** [[00:40:34](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2434)]
I have implemented all the shape documents described.

##### **Nimlgen** [[00:40:46](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2446)]
OK.

##### **Geohot** [[00:40:47](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2447)]
All slower than half and Bflow 16. OK. I just remembered.

##### **Chenyu** [[00:40:58](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2458)]
You said the FP8 tensor core example in your simple memo

##### **Geohot** [[00:41:03](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2463)]
is not fast. I was wondering why. Yeah. I still have some. I see the double speed half ones in there now. Is that working?

##### **Nimlgen** [[00:41:29](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2489)]
Yeah.

##### **Geohot** [[00:41:31](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2491)]
So I see there is the half tensor cores have been added that have the double size. Do those work? And are they twice as fast?

##### **B1tg** [[00:41:41](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2501)]
No, not fast.

##### **Geohot** [[00:41:43](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2503)]
Not fast. Not fast. Why not? Yeah. OK. And another general.

##### **B1tg** [[00:41:57](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2517)]
Seems like an instruction with the FP8 scale. It may be needed to be faster with the FP8 scale support.

##### **Geohot** [[00:42:19](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2539)]
I just run the instruction with scale one. OK. So main. Maybe not use the instruction right.

##### **Nimlgen** [[00:42:41](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2561)]
OK.

##### **Geohot** [[00:42:48](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2568)]
I don't know.

##### **Chenyu** [[00:42:51](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2571)]
One last comment on FP8. I think generally for small nodes, you can use the FP8. But for small D type, we try to match JAX. I think JAX has also a lot of these small D type cases. So we're already discussing one of the PR. And in general, when thinking about small D types and what rules we put, always think in a group for like FP8, FP16, Bflow16. All these like soft flow D types should ideally have a similar rules. And if you have a small D type, you can use the least D type or least float use list to make sure anything you change applies to all small D types. I think that's much better than one of. Because we are very likely to have other random small D type like MX, FP4, or FP4O, whichever FP4. All these things would be impossible to manage if we start to adding one of rules for all.

##### **Geohot** [[00:43:53](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2633)]
One of those. OK. Oops. Yeah, do we have like a group called small D types? No. You know what I mean?

##### **Geohot** [[00:44:09](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2649)]
Like, the way that we have like floats? We can make like small floats.

##### **Chenyu** [[00:44:15](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2655)]
So for now, we have like a Flow 16, Bflow 16, and FP8S, I think?

##### **Geohot** [[00:44:22](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2662)]
Oh, FP8S. Yeah, yeah, yeah. Yeah.

##### **Chenyu** [[00:44:24](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2664)]
So let's go. That's what we have for now. I think only if we start to worry about MX types, basically a type with a scale vector and a shape, we worry more.

##### **Geohot** [[00:44:38](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2678)]
For now, we just .

##### **Nimlgen** [[00:44:44](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2684)]
OK.

##### **Geohot** [[00:44:47](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2687)]
Next.

##### **Chenyu** [[00:44:48](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2688)]
So I don't know if we have any update for Client 2.0 Py.

##### **Chrism** [[00:44:52](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2692)]
Yeah. I mean, it's going well. It should be making pretty good progress on that. There's like one or two things that are left to fix. But it should work. Yeah. Libclang is kind of frustrating. But it works. Yeah. I also haven't started the Objective-C stuff at all. But I'm assuming that's just auto-generated stuff in Ops Metal.

##### **Geohot** [[00:45:18](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2718)]
Yeah. I think it should just. It should just work. I mean, Clang can definitely parse it. There was just stuff in the old one that couldn't deal with it. But yeah, the idea would be to generate the types for the Ops Metal and not have it all be. Yeah.

##### **Chrism** [[00:45:36](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2736)]
Yeah. Yeah. I think there's a cursor type for the Objective-C stuff. So that should not be a problem. Yeah. I also heard earlier that you were talking about running the auto-gen like every time you're running a new object. Every time the code runs. Or I guess maybe every time you install it. Because there's some special thing for Envy. So it's a little slow. So that's the only thing. How slow? Right now, I think it takes like 15 seconds to generate all of the files. Or I haven't set up all of them. Oh, that's fine. So you should think about. Yeah.

##### **Geohot** [[00:46:11](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2771)]
Yeah. It's not like we'd run it on everything. It would just be like, it would be like cached. We'd have like a decorator. Yeah.

##### **Chrism** [[00:46:15](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2775)]
Well, Envy is the slowest one. Yeah. The problem. The problem is parsing macros is really tricky. So the way I've been doing it is just like attempting to parse them and then exacting the file. And if it fails, then you delete the macro that failed. So that's obviously not very fast. And then also Libclang is not very fast.

##### **Geohot** [[00:46:35](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2795)]
How do you get test data for it?

##### **Chrism** [[00:46:39](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2799)]
No, just to see if there's syntax errors. Because there's not. Libclang doesn't parse the macros very well, or really at all. So it just gives you the token stream. So I just copy the. Yeah. I just copy the code. I just copy the code into the Python file and then run some transformations on it. And then if that's not valid syntax, then I delete the macro.

##### **Geohot** [[00:47:00](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2820)]
Is there an exploit?

##### **Chrism** [[00:47:03](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2823)]
What do you mean?

##### **Geohot** [[00:47:05](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2825)]
I mean, like, could someone write malicious C code that then gets executed?

##### **Chrism** [[00:47:11](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2831)]
Oh, I mean, probably. I don't know. I mean, we'll also download a tarball and extract it for the NP stuff. So if that got pointed to something bad, then. Like, that would clobber your. That would not be good.

##### **Geohot** [[00:47:24](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2844)]
Fair point.

##### **Nimlgen** [[00:47:25](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2845)]
Yeah.

##### **Geohot** [[00:47:26](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2846)]
Cool. Yeah, good progress. I'll add another bounty also for, if we don't have one, for the Qualcomm. Oh, yeah. We already have one. A Mesa backend for Qualcomm.

##### **Chrism** [[00:47:40](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2860)]
Yeah. Yeah. Those were both blocked. I don't even know how the Mesa thing was working, because the structs are actually not the right size. I looked at that.

##### **Geohot** [[00:47:47](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2867)]
Oh. Yeah. I was playing with Mesa a little bit. I was using Samsung DeX on my phone. And I was playing with trying to get Mesa to build. I hope that that compiler is better than the Qualcomm one.

##### **Geohot** [[00:48:00](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2880)]
But cool. OK. So I'll block on the Clank API. Yeah. Sweet. OK. So, yeah. I think that's it. Do we have anything on the bounty? A bunch of items that have been there forever. Oh, I think the shrink and pad is tricky for Moti. Because Moti, you always do that. I see. OK. We can just delete that one. I don't know. Yeah, that one's not that great. Yeah.

##### **Chenyu** [[00:48:47](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2927)]
I mean, you can leave it. It's fine.

##### **Geohot** [[00:48:53](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2933)]
Deleted. There's some progress on the Winograd. I'll pay out half the linearizer bounty. I think T. Thompson and I split it. I think we did an interesting about. There's definitely good stuff there. But to bring it all the way home was basically what I did with the ends and stuff.

##### **Geohot** [[00:49:14](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2954)]
But, yeah.

##### **Nimlgen** [[00:49:17](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2957)]
OK.

##### **Sieds Lykles** [[00:49:19](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2959)]
I double one for the removing pool implementation.

##### **Geohot** [[00:49:26](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2966)]
I don't know. 200 sounds good. Yeah, we can double that. Yeah.

##### **Nimlgen** [[00:49:33](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2973)]
OK.

##### **Chenyu** [[00:49:36](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2976)]
So, if people are interested in fix. I don't know what's left to fix the torch tiny back end. Is it just fixing the S-axis? I don't know. I think it's just a little bit. I don't know if I've tried it or if there's more. No idea. But since we are mentioned in torch comb, probably a good idea to fix it. I don't know.

##### **Geohot** [[00:49:57](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=2997)]
Yeah. There's a bunch of stuff.

##### **Nimlgen** [[00:50:03](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=3003)]
OK.

##### **Geohot** [[00:50:10](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=3010)]
OK. Let's see. Let's see.

##### **Chenyu** [[00:50:17](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=3017)]
There's a bunch of, oh, that is those being equals to three test speed versus torch and solve a jam something.

##### **Geohot** [[00:50:29](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=3029)]
Some people were working on it. I don't know. I mean, they're just really hard to do without massively rethinking things. Or change the input size to be much bigger. I'll delete the NV one. There's no way that one's going to happen. The LVM ones, maybe. Update with the Whisper Web GPU. There seems to be some progress. Yeah.

##### **Chenyu** [[00:51:29](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=3089)]
So generally for these ones, it's use your best judgment. And we will only evaluate the code and the output quality.

##### **Geohot** [[00:51:39](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=3099)]
So make a decision yourself. I just merged the spec equals to check tests.

##### **Nimlgen** [[00:52:01](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=3121)]
Great.

##### **Geohot** [[00:52:12](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=3132)]
I think the other thing I kind of want to talk about is the fact that we're kind of

##### **Geohot** [[00:52:14](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=3134)]
talking about is, do you think, OK, should shape and device be in the D type?

##### **Geohot** [[00:52:26](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=3146)]
I'll say that again.

##### **Geohot** [[00:52:29](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=3149)]
So I was thinking more about what D type really means.

##### **Geohot** [[00:52:33](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=3153)]
And let's start with, is device part of the D type? Why should device part of the D type?

##### **Geohot** [[00:52:44](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=3164)]
Because if you have two buffers and you want to do a mull on them, the D types need to match. But why have the D type just be float? Why not also include the shape and the device?

##### **Geohot** [[00:53:07](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=3187)]
Sure.

##### **Chenyu** [[00:53:08](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=3188)]
So this is not just D type, right? You are basically creating a new metadata that you want to match this up.

##### **Geohot** [[00:53:14](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=3194)]
Yeah. I mean, it's not necessarily, it's one piece of metadata. And like type is the right name for it. But it really is like the type of the UOP.

##### **Geohot** [[00:53:29](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=3209)]
It's not clear, right? We don't have such a concept for tensor. What do you mean we don't have a concept for tensor?

##### **Chenyu** [[00:53:41](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=3221)]
It's like when I have a tensor and I code tensor dot dot. D type. Do you expect it to also return you the shape of such tensor?

##### **Geohot** [[00:53:48](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=3228)]
No, but that's, I mean, that's like a separate thing. It's like we have these three things that are like properties on tensor, the tensor, the shape and the device. Yeah. I mean, maybe. Okay. You're right. Maybe they don't actually have to be the same thing on the UOP. They could just be like different properties just like that.

##### **Chenyu** [[00:54:07](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=3247)]
Yeah. So I think that's fine. And because we have the same concept in tensor, if you want to create a new field and say, that such field needs to match, that's why you can find a good name for that. But I don't think it should be like expanding the current D type.

##### **Geohot** [[00:54:21](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=3261)]
You don't think it should be? Okay. I mean, the problem with doing it so you don't expand the current D type is that like the more of these things you add to UOP, the slower it's going to get.

##### **Chenyu** [[00:54:36](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=3276)]
Yeah. But then that comes with the drawback to make D type very convoluted, right? D type starts with very simple idea and very simple. And now it has a lot more to that.

##### **Geohot** [[00:54:49](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=3289)]
Yeah. Yeah. Yeah. Okay. I see. I see what you're saying. So you just want to add new parameters to the class.

##### **Chenyu** [[00:54:57](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=3297)]
Yeah. Because I understand that there are many places that we check all three things, the shape, the D type and the device are the same before we do stuff. And if you think that always writing all that three is bad, we can have another thing that just comes up. So I think that's why I don't want it to reclam into key type and kind of make it different from the one in that search. Okay.

##### **Geohot** [[00:55:26](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=3326)]
Yeah. I mean, it's just like we can start to do some really nice things with like reduce access could just modify the shape and not have like some like parameter thing for the access, right?

##### **Geohot** [[00:55:42](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=3342)]
Reshape and expand are just the same thing. So we can just erase the shape. Maybe. I mean, maybe, maybe it can be something that expands the D type, like the PTRD type

##### **Chenyu** [[00:56:00](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=3360)]
or something. I don't know.

##### **Geohot** [[00:56:03](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=3363)]
I mean, I want to delete, I want to delete the idea of the vec on the D type.

##### **Chenyu** [[00:56:08](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=3368)]
Oh yeah. So that would be really nice because always you need to consider about the base of that D type.

##### **Geohot** [[00:56:14](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=3374)]
Yeah. Yeah. Yeah. I mean, maybe I can just delete the vec and just like reuse shape for that. Yeah. Just reuse the existing stuff we have for shape. Right. Cause like, like there's no, the D type shouldn't. Yeah. That should be a shape.

##### **Chenyu** [[00:56:28](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=3388)]
No, that I'm really supportive. I was really supportive of that. That's very nice.

##### **Geohot** [[00:56:33](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=3393)]
I mean, but the, the problem then is like, like the reason I like it to be the actual D type is because like you have something like a, like a, like a, like a, like a, like a load, right? How do you know if you're loading or you have like a, like an index, how do you know if you're indexing, I guess you should have shape. I don't know. I'll have to think about it, but okay. I see what you're saying.

##### **Chenyu** [[00:56:55](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=3415)]
Yeah. So I think, I think because this concepts are, it is self like similar to device, right? Device by itself can be very simple. Type by itself should be also simple.

##### **Geohot** [[00:57:07](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=3427)]
Yeah.

##### **Chenyu** [[00:57:08](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=3428)]
Shape by itself should also be simple. So if there's a case that we can just separate them. And keep them separated. That seems nice. It's similar to like the struggle we always have with image because image has like one D type, one shape inside of shape inside of D type and other shape of the tensor stuff like that. It's hard to, hard to reason.

##### **Geohot** [[00:57:33](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=3453)]
Yeah. I mean that there's a different fix for that, but yeah.

##### **Geohot** [[00:57:39](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=3459)]
Yeah. Okay.

##### **Geohot** [[00:57:42](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=3462)]
I'll try, I'll try to see if I can use shape. Instead of using a back. Yeah. That would be nice. Yeah. Cool.

##### **Geohot** [[00:57:52](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=3472)]
Okay.

##### **Chenyu** [[00:57:53](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=3473)]
It's about time. That's about it for this meeting. Thanks everyone. And see you next week.

##### **Geohot** [[00:57:58](https://www.youtube.com/watch?v=z_FDsZ1ms2s&t=3478)]
Bye.
