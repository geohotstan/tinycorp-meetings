# 2025-08-18 Meeting

### Meeting Agenda

**Time:** 9am Monday San Diego time
- company updates
- release!
- rangeify
- MLPerf LLaMA (eval / MP / grad_acc mem, fp8)
- viz tool
- drivers
- cloud
- symbolic
- onnx
- other bounties


### Audio

[Youtube Link](https://www.youtube.com/watch?v=6EDbdI_m73o)

### Highlights

- **[Company Update](#geohot-000011)**: Tinyboxes are back in stock and shipping after receiving a new supply of CPUs.

- **[Release](#geohot-000022)**: A new release, version 0.11, is planned for after the meeting. The main feature is the integration of ONNX, removing the need for extra imports. A key focus is ensuring the wheel file size is around 1MB.

- **[Rangeify](#geohot-000234)**: Geohot is hoping to merge Rangeify this week. This major refactor will replace the grouper, kernelize, ShapeTracker, and lower, with the goal of improving kernel splitting and view handling. It will initially be available via an environment variable flag.

- **[MLPerf LLaMA](#chenyu-000923)**: Work on model parallel is waiting on evaluation correctness and resolving compiler errors on LLVM and HIP. For the 8B model, the new dataset was just uploaded, and they plan to start trying it, though it may require more drive space. Work is also being done on supporting smaller data types like BFLOAT16 and FP8.

- **[Viz Tool](#qazalin-001438)**: The tool is struggling with large LLaMA traces (~2GB, 100k events), causing browser memory issues. Instead of moving processing to the server, the proposed solution is to reduce the size of each event by creating a more compact data format, aiming to handle up to a million events within about 100MB.

- **[Drivers](#nimlgen-003325)**: There's a draft PR for AQL support which should provide a "free speed up" for kernel time. Progress is also being made on MI400 support.

- **[Cloud](#wozeparrot-004007)**: The multi-host training bounty requires BEAM to be working. Currently, it's not functioning correctly because runtime errors are not being propagated from the cloud node.

- **[Symbolic](#sieds-lykles-004248)**: Work is underway to ensure that symbolic simplification rules are robust enough to handle the patterns that will be generated after the ShapeTracker is removed by Rangeify.

- **[ONNX](#chenyu-004723)**: The immediate priority is to get the new release out. Following that, there are plans to improve ONNX support, including tools to debug differences between TinyGrad's implementation and ONNX runtime.

- **[Other Bounties](#speaker_01-005003)**: Progress is being made on the Stable Diffusion training bounty, with plans to scale up training on an MI300X machine. The OLLMOE bounty has been unlocked to encourage more participation.

### Transcript
##### **Geohot** [[00:00:00](https://www.youtube.com/watch?v=6EDbdI_m73o&t=0)]
Welcome to our Monday meeting. Shall we start with company updates?

##### **Geohot** [[00:00:11](https://www.youtube.com/watch?v=6EDbdI_m73o&t=11)]
Uh, not in particular. Shipped a bunch more Tinyboxes, we finally have them in stock. The limiting factor was the CPUs, we got a whole lot more of them last week.

##### **Geohot** [[00:00:22](https://www.youtube.com/watch?v=6EDbdI_m73o&t=22)]
More of the project for Comma. Mostly that. Great. Okay. So next is release. So let's do a release this week or after this meeting. I don't know.

##### **Chenyu** [[00:00:46](https://www.youtube.com/watch?v=6EDbdI_m73o&t=46)]
So I think the big thing we want to include in release is ONNX. So you don't need to import from extra to use ONNX. That's pretty nice. I think we can do a release. Maybe just after this meeting. I said I want to include some fix for Comma's new model, but we can do that after. We can do a minor release once that is figured out. Comma hasn't released that model anyway.

##### **Geohot** [[00:01:19](https://www.youtube.com/watch?v=6EDbdI_m73o&t=79)]
The other thing I want to make sure about the release, I want to check the size of the wheel file.

##### **Geohot** [[00:01:26](https://www.youtube.com/watch?v=6EDbdI_m73o&t=86)]
Like it should be around like a megabyte. Because the last one went up to 10 megs. Last time includes all the include AM stuff.

##### **Geohot** [[00:01:37](https://www.youtube.com/watch?v=6EDbdI_m73o&t=97)]
Yeah. So I think we fixed that. We never did a release after. Alright, cool. So who's handling this?

##### **Wozeparrot** [[00:01:43](https://www.youtube.com/watch?v=6EDbdI_m73o&t=103)]
I'll tag today. Great.

##### **Chenyu** [[00:01:47](https://www.youtube.com/watch?v=6EDbdI_m73o&t=107)]
Can you also just put somewhere for the release size?

##### **Hooved** [[00:01:51](https://www.youtube.com/watch?v=6EDbdI_m73o&t=111)]
Yeah. Cool.

##### **Chenyu** [[00:01:54](https://www.youtube.com/watch?v=6EDbdI_m73o&t=114)]
Yeah, we shouldn't have anything else.

##### **Chenyu** [[00:01:57](https://www.youtube.com/watch?v=6EDbdI_m73o&t=117)]
Yeah, let's just do one release and we can do a subsequent one. There are like some other ONNX toolings I want to include. We can discuss later.

##### **Chenyu** [[00:02:07](https://www.youtube.com/watch?v=6EDbdI_m73o&t=127)]
Should this be 0.11?

##### **Geohot** [[00:02:11](https://www.youtube.com/watch?v=6EDbdI_m73o&t=131)]
That's right. Yeah, we include ONNX.

##### **Hooved** [[00:02:13](https://www.youtube.com/watch?v=6EDbdI_m73o&t=133)]
Great.

##### **Chenyu** [[00:02:15](https://www.youtube.com/watch?v=6EDbdI_m73o&t=135)]
One step ahead of Comma. I think there are releases 0.11.

##### **Geohot** [[00:02:21](https://www.youtube.com/watch?v=6EDbdI_m73o&t=141)]
I think we'll get to 1.0 first, maybe.

##### **Hooved** [[00:02:24](https://www.youtube.com/watch?v=6EDbdI_m73o&t=144)]
Great.

##### **Chenyu** [[00:02:27](https://www.youtube.com/watch?v=6EDbdI_m73o&t=147)]
Okay. So let's release. Let's move on to Rangeify.

##### **Geohot** [[00:02:34](https://www.youtube.com/watch?v=6EDbdI_m73o&t=154)]
Yeah, so, you know, progress is slow, but it's there. I'm hoping this week to merge it and have it training Beautiful MNest. So first for anyone, an update on what Rangeify is. So, Rangeify replaces like four different things right now. So we have the grouper, which determines where kernels are split. This is what's currently there. We have kernelize, which actually does that splitting. We have the ShapeTracker, which builds these view UOps. And we have the lower, which is what currently adds ranges to stuff. And Rangeify is going to replace all four of those things with hopefully a much better version. So right now we have this separate logic called the grouper that makes decisions beforehand about which tensors are going to be realized. But this is not that easy. And it relies on a bunch of heuristics, which are not always true and I think are actually causing some major issues. I think that's what's causing like these long strings of contiguouses. Like we do that thing and it like has all the kernels. And it's because the current grouper is always making the decision to redo element wise operations. And you kind of need this to lower kernel counts, but this should not be the right. You shouldn't say arbitrarily redo element wise operations. You have to have a cost function here. So what Rangeify does is, oh, it also replaces all of the logic for view left and view right. So we have a big thing. I forget what it's in, but it's in code gen.

##### **Geohot** [[00:04:27](https://www.youtube.com/watch?v=6EDbdI_m73o&t=267)]
There's a big thing in code gen. Where did I put this? Did I put it in uopt?

##### **Geohot** [[00:04:40](https://www.youtube.com/watch?v=6EDbdI_m73o&t=280)]
View left and view right. So what view left and view right do is they push these. Oh, it's in swizzler, code gen opt. Oh, it also replaces kernel.py. It replaces really the entire op folder, but I don't have that stuff yet. But it's what view left and view right do is they push views. So instead of pushing views, we move indices through the graph. So Rangeify is just basically saying where all the loops should be. And by determining where all the loops should be, you're also determining what should have a tensor. Right? Because anytime you have a basically anytime you have a store, the store ends loops. Right? Well, that's not always true. You can have a store to just one that doesn't end loops. But stores usually end loops. And like you can think of the end of a kernel in a store to globals as loops. Yeah. So, you know, it's a huge refactor. I hope to get it merged by the end of the week, not by deleting the other stuff. You know, I'm going to make an environment variable flag. You run it with Rangeify equals one. And then you can. And then you can start. Start playing with it.

##### **Chenyu** [[00:05:53](https://www.youtube.com/watch?v=6EDbdI_m73o&t=353)]
That makes sense. Otherwise, we also need other optimization.

##### **Geohot** [[00:05:58](https://www.youtube.com/watch?v=6EDbdI_m73o&t=358)]
Yeah. Yeah. So the main thing that I'm not going to get done this week is I hope everything's correct in Rangeify. And I want to get all of the functionality tests working. But I'm not going to get tensor cores or optimizations. These are these are hard. Not that hard. But these require like it's kind of a separate project. We could be doing a lot of this stuff now. So currently we do run kernel dot pi before the lower, which adds the ranges right now. But we have to move to something that looks like kernel dot pi after the lower. This is advantageous for a whole bunch of reasons, too, because I think we can make BEAM search a lot faster. Right now, we are basically redoing the we're at the kernel dot pi level when you redo BEAM search. But you shouldn't have to. You should just be able to make a quick change. Rerender. That's Rangeify. But I've been working on for almost two months now.

##### **Geohot** [[00:06:56](https://www.youtube.com/watch?v=6EDbdI_m73o&t=416)]
But it does work. And it almost trains MNIST. It does train MNIST. It's just slow. Okay.

##### **Geohot** [[00:07:05](https://www.youtube.com/watch?v=6EDbdI_m73o&t=425)]
Yeah, I broke the. Yeah, it's correct. But I broke the indexing. The fast indexing.

##### **Geohot** [[00:07:12](https://www.youtube.com/watch?v=6EDbdI_m73o&t=432)]
And if you don't do fast indexing, it's really, really slow. Is it the wrong lemma?

##### **Hooved** [[00:07:16](https://www.youtube.com/watch?v=6EDbdI_m73o&t=436)]
I don't know. I don't know.

##### **Geohot** [[00:07:19](https://www.youtube.com/watch?v=6EDbdI_m73o&t=439)]
I should. I'll try that. Okay. Anyway.

##### **Chenyu** [[00:07:23](https://www.youtube.com/watch?v=6EDbdI_m73o&t=443)]
Okay, great.

##### **Chenyu** [[00:07:25](https://www.youtube.com/watch?v=6EDbdI_m73o&t=445)]
It should also replace the current fuse logic.

##### **Geohot** [[00:07:31](https://www.youtube.com/watch?v=6EDbdI_m73o&t=451)]
Oh, yeah. Yeah. So the current fuse logic, I mean, there shouldn't be.

##### **Geohot** [[00:07:43](https://www.youtube.com/watch?v=6EDbdI_m73o&t=463)]
There's no reason for that anymore. There's no reason right now. Like what we call for. There's no reason for a full fuse there. That would all be automatic. If you want to redo compute, we'll have to have some new way to specify that.

##### **Geohot** [[00:07:59](https://www.youtube.com/watch?v=6EDbdI_m73o&t=479)]
But I think that's a lot more rare. Yeah.

##### **Geohot** [[00:08:04](https://www.youtube.com/watch?v=6EDbdI_m73o&t=484)]
Like Rangeify should just flash attention as an obvious pattern. Rangeify should just absolutely generate flash attention. And then if you want what we currently have, contiguous still works. You can also do partial contiguous. You can also say contiguous. You can give it an arg. And those args are axes.

##### **Geohot** [[00:08:18](https://www.youtube.com/watch?v=6EDbdI_m73o&t=498)]
And the axes are, they will only contiguous on those axes.

##### **Chenyu** [[00:08:26](https://www.youtube.com/watch?v=6EDbdI_m73o&t=506)]
I think Lo's and other people can experiment once that is merged. Cool. Hopefully this week.

##### **Hooved** [[00:08:34](https://www.youtube.com/watch?v=6EDbdI_m73o&t=514)]
Yeah.

##### **Chenyu** [[00:08:36](https://www.youtube.com/watch?v=6EDbdI_m73o&t=516)]
I think one thing to add is we both agree that the render stuff and the cogen is pretty robust. I think so far it rendered pretty much. Oh. Correctly everything.

##### **Geohot** [[00:08:48](https://www.youtube.com/watch?v=6EDbdI_m73o&t=528)]
Oh yeah. Yeah. The render and the linearizer are great.

##### **Chenyu** [[00:08:54](https://www.youtube.com/watch?v=6EDbdI_m73o&t=534)]
And I. It's like seven back to back loops and like some splits and merge thing seems to be pretty correct.

##### **Geohot** [[00:09:02](https://www.youtube.com/watch?v=6EDbdI_m73o&t=542)]
Yeah. I mean this is the third linearizer I wrote. And this one I think is good. Great. Yeah. It's faster. So I'm happy with that.

##### **Chenyu** [[00:09:15](https://www.youtube.com/watch?v=6EDbdI_m73o&t=555)]
Okay. Yeah. Looking forward to the next one. Looking forward to that. So moving on. Next is LLaMA.

##### **Chenyu** [[00:09:23](https://www.youtube.com/watch?v=6EDbdI_m73o&t=563)]
So I don't have a new picture for the whiteboard. It's the same as last week. I think we are at LNB model parallel. For that one. Basically I'm waiting for eval. That's one thing I really want to see if the eval is correct. And there are compiler arrows, both on LLVM and HIP that I hope would disappear after we upgrade the compiler versions. We will follow up on that. My hope is we can like run 7B with split, like split the model on eight GPUs.

##### **Wozeparrot** [[00:10:05](https://www.youtube.com/watch?v=6EDbdI_m73o&t=605)]
Oh, as far as I can tell, both MI300 boxes have LLVM 20 already. Okay.

##### **Geohot** [[00:10:13](https://www.youtube.com/watch?v=6EDbdI_m73o&t=613)]
Is that the version that's being used?

##### **Wozeparrot** [[00:10:17](https://www.youtube.com/watch?v=6EDbdI_m73o&t=617)]
Well, it's the whatever latest LLVM version is. Okay.

##### **Chenyu** [[00:10:20](https://www.youtube.com/watch?v=6EDbdI_m73o&t=620)]
Anyway, yeah, I will confirm this and see if it's like our bug or whatever bug it is. It's just weird.

##### **Chenyu** [[00:10:31](https://www.youtube.com/watch?v=6EDbdI_m73o&t=631)]
And I don't have update on gradient accumulation. I still don't know what's happening.

##### **Chenyu** [[00:10:40](https://www.youtube.com/watch?v=6EDbdI_m73o&t=640)]
Okay. But I started to look into what's, oh, sorry. What's the paragraph?

##### **Wozeparrot** [[00:10:45](https://www.youtube.com/watch?v=6EDbdI_m73o&t=645)]
Is there an update on 8B?

##### **Geohot** [[00:10:49](https://www.youtube.com/watch?v=6EDbdI_m73o&t=649)]
Oh, you mean their PR? Yes.

##### **Chenyu** [[00:10:57](https://www.youtube.com/watch?v=6EDbdI_m73o&t=657)]
As I check, not really. So, I mean, even if they merge that PR, they haven't released a new data set. They say they will. Oh, it is merged. So it's okay. Then it's either, I think it's either we follow their setup. To generate the data or we'll wait until the update.

##### **Wozeparrot** [[00:11:14](https://www.youtube.com/watch?v=6EDbdI_m73o&t=674)]
Well, the data was uploaded an hour ago. Okay, great.

##### **Geohot** [[00:11:18](https://www.youtube.com/watch?v=6EDbdI_m73o&t=678)]
Okay. Then we can try that and try an 8B model.

##### **Hooved** [[00:11:28](https://www.youtube.com/watch?v=6EDbdI_m73o&t=688)]
Good.

##### **Geohot** [[00:11:32](https://www.youtube.com/watch?v=6EDbdI_m73o&t=692)]
What was the PR? I don't think we can fit this on the 350 boxes.

##### **Chenyu** [[00:11:40](https://www.youtube.com/watch?v=6EDbdI_m73o&t=700)]
Oh, because the context is too big?

##### **Wozeparrot** [[00:11:44](https://www.youtube.com/watch?v=6EDbdI_m73o&t=704)]
No, like on the drive in the 350 box.

##### **Geohot** [[00:11:48](https://www.youtube.com/watch?v=6EDbdI_m73o&t=708)]
Oh, yeah. Yeah, I can order. I'll order more drives. We're going to put in, I tested the new ASRock cards. They're good. I just didn't get around to ordering them. But I'll order, send me the model number of those drives. I'll order 16 of them. Okay. I'll put, yeah.

##### **Geohot** [[00:12:09](https://www.youtube.com/watch?v=6EDbdI_m73o&t=729)]
Okay. We'll put McPherson.

##### **Chenyu** [[00:12:12](https://www.youtube.com/watch?v=6EDbdI_m73o&t=732)]
How big is the data set?

##### **Wozeparrot** [[00:12:15](https://www.youtube.com/watch?v=6EDbdI_m73o&t=735)]
I'm assuming it's the same size as the last one.

##### **Chenyu** [[00:12:18](https://www.youtube.com/watch?v=6EDbdI_m73o&t=738)]
Yeah, we can delete the one for BERT. We don't really need the BERT one if we are low on storage. We can check, yeah. Yeah, so because light is one terabytes, right? And this new one is like 1.1 presumably?

##### **Qazalin** [[00:12:35](https://www.youtube.com/watch?v=6EDbdI_m73o&t=755)]
Yeah. Okay.

##### **Chenyu** [[00:12:38](https://www.youtube.com/watch?v=6EDbdI_m73o&t=758)]
Looking into smaller D type. And I just realized for the AMD renderer, we still have a bunch of craps for B416. And when I try to remove that, some other compiler issue happen. So I was looking to what's happening there. I think we just want to support. B416 would definitely support. FP8, I would imagine if it's trainable, we'll support it. It's just a nice to have option to save even more memory.

##### **Geohot** [[00:13:11](https://www.youtube.com/watch?v=6EDbdI_m73o&t=791)]
Because we can just use that for wait.

##### **Sieds Lykles** [[00:13:20](https://www.youtube.com/watch?v=6EDbdI_m73o&t=800)]
I just opened a PR to fix the F16. You can check it out later.

##### **Chenyu** [[00:13:28](https://www.youtube.com/watch?v=6EDbdI_m73o&t=808)]
OK, great.

##### **Chenyu** [[00:13:30](https://www.youtube.com/watch?v=6EDbdI_m73o&t=810)]
Yeah, so a bunch of your fix, what George mentioned as well.

##### **Hooved** [[00:13:38](https://www.youtube.com/watch?v=6EDbdI_m73o&t=818)]
Yeah.

##### **Chenyu** [[00:13:39](https://www.youtube.com/watch?v=6EDbdI_m73o&t=819)]
George, do you want to quickly check the C style one and the cast one, both you requested before?

##### **Geohot** [[00:13:48](https://www.youtube.com/watch?v=6EDbdI_m73o&t=828)]
Sure.

##### **Chenyu** [[00:13:50](https://www.youtube.com/watch?v=6EDbdI_m73o&t=830)]
Yeah, so hopefully this week we will have LLaMA eval. And around the 70B, maybe smaller context windows. Then we'll see. Some AB going on. Hopefully we can start to trend those as well.

##### **Geohot** [[00:14:13](https://www.youtube.com/watch?v=6EDbdI_m73o&t=853)]
Oh, sweet. You fixed the cast. Nice.

##### **Chenyu** [[00:14:18](https://www.youtube.com/watch?v=6EDbdI_m73o&t=858)]
Yeah, just review those. And we can move on to make more stuff. And we will discuss other MLPerf stuff in other bounties. So I have four LLaMA.

##### **Geohot** [[00:14:32](https://www.youtube.com/watch?v=6EDbdI_m73o&t=872)]
So with that, we can move to this.

##### **Qazalin** [[00:14:38](https://www.youtube.com/watch?v=6EDbdI_m73o&t=878)]
So I realized that the problem with Wiz is that we can't the entire LLaMA trace to the browser. When you forward with SSH, it's extremely slow over the internet. And it's just 100K events. So it's out of memories. I have it here.

##### **Geohot** [[00:14:59](https://www.youtube.com/watch?v=6EDbdI_m73o&t=899)]
Wait, how big is the trace?

##### **Qazalin** [[00:15:02](https://www.youtube.com/watch?v=6EDbdI_m73o&t=902)]
It's like 100,000 events.

##### **Geohot** [[00:15:09](https://www.youtube.com/watch?v=6EDbdI_m73o&t=909)]
Okay. That sounds like a very small number.

##### **Qazalin** [[00:15:14](https://www.youtube.com/watch?v=6EDbdI_m73o&t=914)]
Still, like it takes, I don't know, a couple seconds.

##### **Geohot** [[00:15:18](https://www.youtube.com/watch?v=6EDbdI_m73o&t=918)]
I don't generally like this trend of saying, okay, like the browser is slow, so we're going to offload it to the server. Like, why is the browser slow? The browser is running on a fast computer. JavaScript is faster than Python.

##### **Hooved** [[00:15:34](https://www.youtube.com/watch?v=6EDbdI_m73o&t=934)]
Yeah.

##### **Qazalin** [[00:15:41](https://www.youtube.com/watch?v=6EDbdI_m73o&t=941)]
I think that's the problem with that. It's out of memory. It is out of memory. So basically, like.

##### **Geohot** [[00:15:45](https://www.youtube.com/watch?v=6EDbdI_m73o&t=945)]
Okay. So you're telling me that my computer with 48 gigs of RAM can't handle 100,000 things.

##### **Qazalin** [[00:15:52](https://www.youtube.com/watch?v=6EDbdI_m73o&t=952)]
The browser limits how much RAM the tab can use.

##### **Qazalin** [[00:15:57](https://www.youtube.com/watch?v=6EDbdI_m73o&t=957)]
How about you?

##### **Qazalin** [[00:15:59](https://www.youtube.com/watch?v=6EDbdI_m73o&t=959)]
I think it's different per browser. Some things work better on Firefox. box. Chrome is a couple gigabytes.

##### **Geohot** [[00:16:08](https://www.youtube.com/watch?v=6EDbdI_m73o&t=968)]
Okay, so I have 100,000. How much? How much kilobytes do I have per event?

##### **Qazalin** [[00:16:16](https://www.youtube.com/watch?v=6EDbdI_m73o&t=976)]
In total, the LLaMA trees was around two gigs.

##### **Geohot** [[00:16:23](https://www.youtube.com/watch?v=6EDbdI_m73o&t=983)]
Two gigs. So you're telling me it's two e nine divided by Okay, okay, that seems plausible. And that's too big for a browser.

##### **Qazalin** [[00:16:41](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1001)]
I think so. When I tested on brave, it crashed. Another problem is that when I forward the SSH from the 300x machine, I have to enable compression. And it's not

##### **Hooved** [[00:16:58](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1018)]
working. So I have to do a little bit of compression.

##### **Qazalin** [[00:16:58](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1018)]
The default passive path is too slow for my downloads. I'm in Europe. So maybe like pasture when you're

##### **Geohot** [[00:17:07](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1027)]
you have to enable what kind of compression?

##### **Qazalin** [[00:17:11](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1031)]
So there's like this flag for SSH for work wording, I don't know it, but you can enable compression. When you're forwarding the port and it will

##### **Geohot** [[00:17:23](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1043)]
Okay, so how much how is this lower if you pre process stuff on the on the server?

##### **Qazalin** [[00:17:32](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1052)]
You would basically calculate the layout on the server and get like a higher level. So not send like the 400k trace events, but send like the shape of the timeline in unit vectors and then the browser just rescales those two pixels and draws it on the screen. It would look at the zoom. Yeah. and cloth level when you looking at a couple minutes. So the that the anti level things

##### **Geohot** [[00:18:07](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1087)]
when you zoom in automatic and make a request on the server.

##### **Qazalin** [[00:18:12](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1092)]
Yes

##### **Geohot** [[00:18:14](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1094)]
Yeah, Mauricio Crespo This is LLaMA. So who kicked? I mean, which LLaMA you are talking about.

##### **Qazalin** [[00:18:32](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1112)]
Oh, it's the, I think, let's see, 70B.

##### **Chenyu** [[00:18:44](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1124)]
Yeah, so even if this barely fits when it goes to 4 or 5B, there's at least double the size again.

##### **Geohot** [[00:18:57](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1137)]
I mean, yeah, it adds a lot of complexity if you have to start zooming in and re-requesting regions.

##### **Chenyu** [[00:19:05](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1145)]
Yeah, I think maybe instead of doing the, like, I don't know. I don't know how complicated it is, but it sounds complicated. Even if we really do, like, pass all the hundreds of thousands of events to a browser, it's just hard to believe humans would read them one by one. There's no way. So maybe start by, like, dropping stuff. So that we end up and see what's there now.

##### **Hooved** [[00:19:42](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1182)]
Yeah.

##### **Geohot** [[00:19:43](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1183)]
What are the 100,000? What can we just drop? The kernel that you want.

##### **Qazalin** [[00:19:54](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1194)]
Which of the events represent the kernel? What it could represent. I don't know. A buffer allocation, the allocation, if it's a memory.

##### **Chenyu** [[00:20:04](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1204)]
Yeah, so I think a better design for this might be just started from the user's point of view. Say, for example, I'm training a model. What do I want to see? Maybe I want to see the buffer allocation. I want to see how memory is used. I want to see certain time stuff. Maybe I care less about individual kernels or rewrites. Is there a way for me to either turn that off or not showing

##### **Geohot** [[00:20:31](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1231)]
that by default or something? I definitely want to show everything by default. But I want to see everything by default.

##### **Chenyu** [[00:20:49](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1249)]
When you turn it on, the use case is very different from looking to single rewrite, I think.

##### **Geohot** [[00:20:59](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1259)]
I'm still not quite understanding why 100,000 is too many. That would be 20 kilobytes each. So the per tab memory limit is 4 gigs in Chrome.

##### **Geohot** [[00:21:16](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1276)]
Again, that might be handy.

##### **Geohot** [[00:21:17](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1277)]
The thing that I'd really love to see be the solution here is like, oh, oh, each one of these things

##### **Geohot** [[00:21:22](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1282)]
is 10x larger than it should be.

##### **Qazalin** [[00:21:29](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1289)]
I mean json.dumps is a little, yeah. Yeah.

##### **Geohot** [[00:21:36](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1296)]
Can we find it?

##### **Qazalin** [[00:21:37](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1297)]
It's picking up stuff. You have to put things up. Like the only thing that's available at serialization is JSON. JSON is layout. Those strings are too much. The same thing would be much smaller.

##### **Geohot** [[00:21:53](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1313)]
Yeah, I mean, we might want some. So you can make some byte pack format.

##### **Geohot** [[00:22:00](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1320)]
Like how many things do you have per thing? The pickle is much smaller than the actual JSON. How much more? A couple megs. Wait.

##### **Geohot** [[00:22:17](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1337)]
How is a pickle of 100,000 things a couple megs? This seems wrong the other way.

##### **Qazalin** [[00:22:23](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1343)]
A couple hundred megs.

##### **Geohot** [[00:22:25](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1345)]
A couple hundred megs. Yeah, I mean, what I would do here is, well, first we should figure out a number that we want to target. Because fundamentally it's just a target.

##### **Geohot** [[00:22:38](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1358)]
Like it's never going to work for 10 million. And then, yeah, having some command line flags to turn things off is fine, but not on. Because off people will figure out, on they'll never figure out. But yeah, I think that might be the idea. So how much stuff do you have to store per event? They don't have to save people. Don't mess things up. Apart from what they're sure they're going to take but don't you fear that they're going to be stopping you though? Yeah.

##### **Geohot** [[00:23:31](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1411)]
So they're probably going to be realizat.. Cool, how much do they need in Excel.. Or on the Word console? So there are user passwords, educational purposes, if they have to live somehow, and I don't know like what it's called, but I'm not so sure. Like what because you're just like a centimeter, so. Okay, I see. Yes, this is effective today. It's a little bigger purpose.

##### **Geohot** [[00:23:37](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1417)]
This is getting a charged time. problem. Just store the bytes. Think about it, JSON's printing these numbers. Putting strings everywhere. Yeah, yeah, it is slow. Just have Python

##### **Geohot** [[00:24:01](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1441)]
put the bytes. Okay, the other question here is, yeah, and I guess and then I guess Chen Yu's suggestion if it's still not enough when we get to 405B, have some command have some environment variable which can turn off certain trace events. But off not on. See? Yeah, the solution here is definitely not to move things to the server. I think the solution here is because this is complexity. That nobody can maintain. The solution here is to say, wait 100,000. Okay, even if there are 100 bytes each, that's 10 megs. Right, like to ask like, like, this just doesn't

##### **Geohot** [[00:24:44](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1484)]
add up. These files shouldn't be that big. I guess that's Yeah, the metric here is bytes per event. What constitutes an event? If I run the kernel, how many events roughly that is?

##### **Qazalin** [[00:25:09](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1509)]
One event per kernel.

##### **Chenyu** [[00:25:13](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1513)]
Also, each kernel is one event. And all the rewriting information of that kernel is part of that event.

##### **Qazalin** [[00:25:23](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1523)]
No, rewrites are separate events in the tiny device.

##### **Geohot** [[00:25:27](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1527)]
Okay. I mean, rewrites are also pretty rare. Compared to kernel runs anyway.

##### **Qazalin** [[00:25:35](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1535)]
Yeah, they're cached.

##### **Geohot** [[00:25:37](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1537)]
Okay. Cool. Sounds good.

##### **Geohot** [[00:25:42](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1542)]
But yeah, the main thing I would focus on here is just reducing the size of each event.

##### **Chenyu** [[00:25:49](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1549)]
Another use case I'm interested for this is I was trying to use this to debug or to work on the MOE. The OLL. The OLL MOE model because we have a bounty. And my use case was I was trying to use this to run the thing and see if I can find what's slow and turn out to be not very useful compared to if I just get equals to two and like, about

##### **Geohot** [[00:26:22](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1582)]
like imprinted by two and read the kernels. So. Not entirely sure, like, what's the solution here?

##### **Chenyu** [[00:26:37](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1597)]
But that's the use case I think people will want to use. Basically run OLL MOE or run stable diffusion or any of the inference tasks and try to and they want to use this to understand where the bottleneck is and how potentially they can make it faster. For example, we discussed the idea about like kernels. That is hitting the kernel. And then the other compute bound or memory bound or cache bound. Things like that to understand what's the limiting factor. And stuff like that.

##### **Geohot** [[00:27:10](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1630)]
I think currently we don't have enough tooling to show those.

##### **Qazalin** [[00:27:17](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1637)]
What was your experience when you opened Viz?

##### **Chenyu** [[00:27:21](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1641)]
So first, OLL MOE spent a lot of time loading and big as the weights. So my Viz timeline is dominated by stable.

##### **Hooved** [[00:27:31](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1651)]
And the OLL MOE is the same as the OLL MOE.

##### **Chenyu** [[00:27:32](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1652)]
So if I have a lot of time loading, it's very hard to find the actual steps that runs the OLL MOE steps to one. And it's just not that easy to figure out after I figure out which chunk of the timeline is the 10 steps to figure out what's the bottleneck.

##### **Hooved** [[00:27:59](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1679)]
You can actually do that. You can just go to the OLL MOE. And then you can just go to the OLL MOE.

##### **Chenyu** [[00:28:00](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1680)]
You should be able to try that and just run the OLL MOE. Imagine your task is to make it fast. And this is the profiling tools that you have. Does that help you?

##### **Geohot** [[00:28:12](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1692)]
I think it's a good practice. I don't have concrete suggestion here.

##### **Chenyu** [[00:28:22](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1702)]
I try to use that for improving the inference speed. It turns out not very helpful.

##### **Hooved** [[00:28:29](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1709)]
Well.

##### **Geohot** [[00:28:30](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1710)]
So I mean, how much of the problem is that you need the memory planner in this?

##### **Chenyu** [[00:28:36](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1716)]
So OLL MOE, I don't think it's a memory issue. More of are we, are some of the kernel too slow for no reason? Because similar to LAMA, LAMA, we already hit the limit. And I think one interesting thing I observed by reading debug, debug two is the same kernel sometimes can hit. Sometimes it hits the limit and sometimes cannot. I don't know if it's data dependent. Depends on which experts being picked. If so, that would be interesting. But that's only if I read the debug equals to two per kernel numbers and compare that

##### **Geohot** [[00:29:17](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1757)]
to the theoretical limits that I know. I wouldn't think it's data dependent, but it could be dependent on like whether something's hot in the cache or not. Yeah, or that. Because if you think about it, when it beams, maybe the patterns matters or something.

##### **Chenyu** [[00:29:44](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1784)]
Anyway. So I surely hope this experience can also, like whatever I learn by reading the debug two or like per kernel information can be like shown or easier to understand. And I think it's worth to observe the LVS as well.

##### **Nimlgen** [[00:30:05](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1805)]
Yeah, I can add there is a feature in Perfetta where you can actually select any range with your mouse and it will sort all the kernels and all the events inside this range. So you can actually see like the timings, the average time each kernel takes, like the total time, like the average time multiplied by the count each kernel run. So yeah, it's pretty useful for for this. So if we want to debug in this, maybe we need such kind of table in this as well. And it's not like only visual on the like on the timeline, but you also have a table with timings. Like we can also add like the average time, the minimum and maximum time. For each kernel. Yeah.

##### **Chenyu** [[00:30:51](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1851)]
So I mean, yeah, I don't I don't know what would be best here. But this is the use case that I imagine. Like other people will use a lot.

##### **Geohot** [[00:31:00](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1860)]
As well as having a tool to understand where the bottleneck is. I'm looking into that.

##### **Qazalin** [[00:31:19](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1879)]
I think the Perfetta one table is kind of raw, but maybe we can find another tool. I don't think that one.

##### **Chenyu** [[00:31:30](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1890)]
Yeah, I think I think just try to run try to run OLLMOE with maybe JITBIM equals to two and like this and see what you are seeing and see if that's helpful.

##### **Qazalin** [[00:31:44](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1904)]
It gets into the counter, the performance counter stuff with the bottlenecks. Like you should be able to see it very clearly.

##### **Qazalin** [[00:31:54](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1914)]
Okay. That's good.

##### **Chenyu** [[00:31:59](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1919)]
Okay, let's move on. Let's move on to drivers.

##### **Geohot** [[00:32:02](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1922)]
I want to say one more thing about this. If you do want to change the format to something. If you want to change the format to something custom, write a spec of what you want to change the format to and look it over. And then before we code this, we should have an estimate like we are designing the new

##### **Geohot** [[00:32:22](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1942)]
viz to be able to handle I think a million events is reasonable. Yeah, so put us back together about your data format that's going to store a million events in some hundred megs. Maybe that's 100 megs. I think it's 100 megs. I can't imagine an event being more than 100 bytes. We'll see. Yeah.

##### **Hooved** [[00:33:14](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1994)]
Cool.

##### **Geohot** [[00:33:18](https://www.youtube.com/watch?v=6EDbdI_m73o&t=1998)]
Okay, driver.

##### **Nimlgen** [[00:33:25](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2005)]
Yeah, so yeah, I've seen a couple of things. I've seen a couple of complaints about NV driver. I'll look in details this week. So basically, there is something that still ensures the NVIDIA driver. So in these machines, and I'm not sure exactly what's doing that.

##### **Geohot** [[00:33:52](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2032)]
If that's the issue, you just blacklist on the machines. You're added to like mod probe and blacklist it.

##### **Geohot** [[00:33:59](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2039)]
Yeah, I'll check that. Let's try that.

##### **Nimlgen** [[00:34:04](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2044)]
So yeah, so for AQL stuff, I have a draft PR. So with AQL, so basically that's like the AQL queue and we can execute the PM4 pockets in the AQL. So that's less like the first approach. And the second approach, I think, is that we can just execute the NVIDIA. So we can execute AQL from PM4 queues. Like the difference is like what the base type of queue of compute queue. So the second one, I mean, where we have like PM4 queue and execute pocket three AQL pocket. So it should be better because we can use bind. But I so there is no documentation for this pocket. And yeah, we need to. To reverse it. Or maybe we can ask AMD for the semantics for this pocket. But it should be better for us because.

##### **Geohot** [[00:35:09](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2109)]
AMD has never been useful at this.

##### **Nimlgen** [[00:35:13](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2113)]
Yeah, but yeah, they've never used them like in tests. I don't know if it's even like implemented like modern machines. Yeah. But there is some headers.

##### **Geohot** [[00:35:27](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2127)]
Yeah, I think it's. Yeah, I think it's 99. PM4 99 runs AQL. Why do I know that? I mean, the advantage to actually like making the base type of the queue be AQL is that it just copies what the existing driver is sending. I don't know. I would briefly. I understand why it's easier if we can leave the base type as PM4. I would maybe briefly try it, but I think we're just going to have to make the base type be AQL. So we can make it match. And these AMD's implementation.

##### **Nimlgen** [[00:36:04](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2164)]
Yeah, but yeah, I've done that. But actually, there is some problem with AMD LLVM because it's like the kernel is not compatible. I think maybe I need to. Okay, I'll look into it. There is. I mean, it can find the AQL header. So it can't execute.

##### **Geohot** [[00:36:22](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2182)]
Oh, it's not generating the AQL header. Yeah. I don't know. I don't know where those come from, but I'm sure we can figure that out. I'm sure that's some fun. I think it's going to flag somewhere.

##### **Nimlgen** [[00:36:28](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2188)]
Yeah, yeah, yeah. But basically, like with AQL queue, we just steal all the signals and all the like all the signals are in PM4 and only kernel execution is in AQL.

##### **Geohot** [[00:36:44](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2204)]
That should be fine.

##### **Nimlgen** [[00:36:46](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2206)]
Yeah. If the base type is. Yeah, because it's like HSA signals are quite annoying and quite limited what they can handle. So it's will be really hard too much to use them like in each queue. So yeah, yeah. That's fine. Yeah. Stick to.

##### **Geohot** [[00:37:06](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2226)]
I'm pretty sure that path is used in AMD stuff too. I'm pretty sure the path where you call into PM4 from an AQL queue is used in their tests.

##### **Nimlgen** [[00:37:16](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2236)]
Oh, it's used even in their like runtime.

##### **Geohot** [[00:37:20](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2240)]
Oh, great. Yeah, yeah, yeah. Let's do it this way. I feel much better about that. And we can do all we can keep all the signals in PM4. Yeah.

##### **Nimlgen** [[00:37:27](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2247)]
Okay. Yeah. Yeah. I think I'm going to merge it and maybe after that I can clean up all the. Yeah, I think I'll merge it under flag and maybe after that we can clean up all the XCC stuff from PM4 we have right now. And just leave in AQL. Yeah. So.

##### **Geohot** [[00:37:49](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2269)]
Yeah, I'm okay with only supporting. Yeah. I'm okay with only supporting AQL for the MIs. Yeah.

##### **Nimlgen** [[00:37:58](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2278)]
Okay.

##### **Geohot** [[00:38:01](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2281)]
So, yeah. And timings actually look good already. I need to fix some things. But yeah.

##### **Hooved** [[00:38:09](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2289)]
Sweet.

##### **Nimlgen** [[00:38:13](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2293)]
So, yeah. So, 4AM MI400, there's some progress, but I spent a lot of time figuring out some.. I mean, actually, because of these GPU support, XGMI, they have different aperture mappings. And basically, yeah, like it was quite strange to debug because it worked on one GPU, not another because like the window is floating based on which peer ID each GPU is. So, yeah. But I also fixed that and it should be pretty close to merging it. I've already merged some parts from it.

##### **Geohot** [[00:38:58](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2338)]
So, yeah. Cool. Yeah.

##### **Nimlgen** [[00:39:04](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2344)]
So, yeah. And also maybe AQL support for AM as well. I'll do it this week. So, not much there.

##### **Geohot** [[00:39:13](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2353)]
It's just several flags. Yeah. I'm happy that kernel time is going to be fast. This will just be free speed up. Yeah.

##### **Hooved** [[00:39:24](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2364)]
So, yeah. So, yeah. So, yeah. So, yeah. So, yeah.

##### **Nimlgen** [[00:39:28](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2368)]
Yeah. It's not a buffer, so basically damaged because of manufacturing things or something been And yet, it works. Yeah. Yeah. This was Hey. So, yeah.

##### **Geohot** [[00:39:41](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2381)]
So, how, how, how do we get to the right consistency to make the leaduen as price effective?

##### **Qazalin** [[00:39:48](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2388)]
Yeah.

##### **Geohot** [[00:39:49](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2389)]
So this is my first derivatives, you guys try to get paid as much

##### **Chenyu** [[00:39:56](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2396)]
Next is anything for Cloud? I think there are several open PR from UUVN as well.

##### **Wozeparrot** [[00:40:07](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2407)]
Yes. So I tested the thing. Do we want, does the bounty include beaming the model?

##### **Geohot** [[00:40:16](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2416)]
Which bounty? The host time within a multi-host one. It should, right? I don't know. George? Let me read the text of the bounty.

##### **Wozeparrot** [[00:40:37](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2437)]
This training, well, we dropped Resonance. So training on three GPUs across two machines, getting 80% of the same machine speed.

##### **Geohot** [[00:40:45](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2445)]
Yeah, of course you have to do that with BEAM.

##### **Wozeparrot** [[00:40:47](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2447)]
OK. So it doesn't work with BEAM because we don't propagate runtime errors from Cloud node. UUVN says he's trying to reproduce it. So that's fine.

##### **Geohot** [[00:40:59](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2459)]
Yeah, I mean, it has to be our best speed, right? You can't say, oh, it's the unbeamed speed. Yeah.

##### **Chenyu** [[00:41:07](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2467)]
Because only when you BEAM, you would see other things. Because now the ratio between kernel launch time and other stuff versus kernel runtime can be that close.

##### **Qazalin** [[00:41:20](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2480)]
Yeah.

##### **Hooved** [[00:41:23](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2483)]
OK.

##### **Geohot** [[00:41:25](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2485)]
OK. Yeah.

##### **Nimlgen** [[00:41:35](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2495)]
And so I'm going to start sweetware one. Does anyone remember him saying as reference to his test

##### **Hooved** [[00:41:42](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2502)]
that we meat it later?

##### **Nimlgen** [[00:41:42](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2502)]
I'm sorry.

##### **Geohot** [[00:41:43](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2503)]
I was totally trying to figure out how to act if saying that the kernel of R is properly issued. So we're now going to look at that. I couldn't remember it being a code thing.

##### **Nimlgen** [[00:41:57](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2517)]
I've done a propagation from the, yeah. I know it's strange it doesn't work for BEAM.

##### **Wozeparrot** [[00:42:06](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2526)]
Yeah, I don't know. I was testing it, and it still failed on the remote.

##### **Geohot** [[00:42:11](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2531)]
OK. Anyway, so that's the definition of LabBounty. Anything else? That's mostly all. OK. Symbolic. Yeah, all right. Symbolic.

##### **Sieds Lykles** [[00:42:48](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2568)]
So most of what I've been working on is, like, last week, you talked about the ShapeTracker tests and making sure that those simplify well. So I've just been, I mean, I guess basically what you want is to index uops, like the function in the lower,

##### **Geohot** [[00:43:12](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2592)]
that that generates nice, nice expressions without having simplified the ShapeTracker.

##### **Sieds Lykles** [[00:43:25](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2605)]
So I'm just trying to see what rules are missing for, yeah, some of the symbolic simplification so that that gets done,

##### **Geohot** [[00:43:35](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2615)]
so that symbolic can find those simplifications.

##### **Chenyu** [[00:43:43](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2623)]
So in general, I think it's good to make sure that you make the simplification rules more complete. But also, I heard ShapeTracker is going to be removed soon.

##### **Geohot** [[00:43:54](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2634)]
No, but I requested this. So the task is not to improve ShapeTracker. The task is to make sure that, so when we remove ShapeTracker, you're basically going to get the same patterns, and symbolic's going to have to do them, because we're not going to have merge views anymore. Yeah, that's fine. Yeah, and that's the project key. Yeah, I think you captured it correctly.

##### **Sieds Lykles** [[00:44:18](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2658)]
Yeah. So I mean, what I'm doing now is just one ShapeTracker that's simplified and the other one that's not. And then when you do, when you generate the indexing from the unsimplified one, you want to make sure that it simplifies with symbolic. This is right.

##### **Geohot** [[00:44:39](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2679)]
And it's good to do this before ShapeTracker goes away. So that we've, yeah.

##### **Chenyu** [[00:44:43](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2683)]
So my experience. Doing the first version of this, when we initially remove symbolic and use the rewriting rules for symbolic, is to make sure you have a script that generates the diff between the one you two just mentioned, the width and the old method with ShapeTracker math, and the new method with only symbolic rules, and have a matrix to track. Having an easier way to see what's left not done, help you to figure out what was missing a lot easier. Yeah. I remember there was some like.

##### **Sieds Lykles** [[00:45:24](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2724)]
I mean, I think the hardest part is going to be the valid actually. But I think there's not that much missing to get the sort of diffs

##### **Geohot** [[00:45:36](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2736)]
or like division to get that to simplify completely.

##### **Geohot** [[00:45:44](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2744)]
So. When you get here next week. When you get here next week, I think that's going to be your in-person project. We want to figure out how to basically mix index and valid.

##### **Geohot** [[00:46:00](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2760)]
So like what invalid really is,

##### **Geohot** [[00:46:03](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2763)]
is imagine like a where that has like a poison value or an invalid value inside the indexing. But I think this will help us like with the simplification of indexing and valid as well. But yeah, we'll work this out when you get to the office.

##### **Sieds Lykles** [[00:46:20](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2780)]
Yeah. I mean, there's some simplifications you can only make if the valid is true or false.

##### **Geohot** [[00:46:26](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2786)]
Yeah. Yeah. But no, I want to like combine the indexing and the valid. I don't know. I'll explain it. We'll explain it when you get here. But you know, I think otherwise this is a good project. And yeah, I definitely agree with Chin-Yu's suggestion

##### **Geohot** [[00:46:35](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2795)]
of making an automated thing for this. Yeah. For generating shape trackers. Check it.

##### **Hooved** [[00:46:44](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2804)]
Cool.

##### **Sieds Lykles** [[00:46:45](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2805)]
I mean, yeah, I'm just using the Fuzz shape tracking math. I mean, I don't have a metric set up for it. But it's just generating like hundreds of expressions.

##### **Geohot** [[00:46:56](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2816)]
And I can see if they're equal or not. That sounds good. Cool. OK. Uh, on X. There's a number important dropout.

##### **Chenyu** [[00:47:23](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2843)]
So I won't worry too much about this for now. Let's make a release first. We can have a cleanup release after. I don't see the point of blocking this release.

##### **Geohot** [[00:47:36](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2856)]
And yeah, I'm definitely interested in those shape.

##### **Chenyu** [[00:47:44](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2864)]
Not being cached properly. And basically, at this point, you are the ONNX expert. So you know much more about what's not done. And we definitely want to support those. The ones I can think of is the symbolic shape. And the if op to support the commas new big model. So I think you are on the progress now. So let's make a release. And we will have a follow up once we fix more issue. And speaking of ONNX specifically, so when I was in San Diego, I was promoting TinyGrad to commas new people to have them try. We use TinyGrad more. And I also ask them to open issues. So the ones I tag you into is one of the issue that they start to use ONNX. Then see there is a difference between. Any grass implementation and ONNX runtime. In terms of output. So I think having a workflow. Or a tool slash like and like show where. Any greatest making. Is generating different output be very useful. Now we want more people to use our ONNX. I would. I can probably sponsor a bounty. If you get the tools in and we can use. That tools to fix less specific. Issue that running an ONNX model on CUDA. Like produce different results than GPU.

##### **Geohot** [[00:49:23](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2963)]
I think that would be a nice tool and workflow to have. Otherwise good job on ONNX. Yeah. I will post more in the ONNX channel after the meeting.

##### **Chenyu** [[00:49:48](https://www.youtube.com/watch?v=6EDbdI_m73o&t=2988)]
With that said. Move on to other bounties. I see who you want to say something about. Training stable diffusion.

##### **SPEAKER_01** [[00:50:03](https://www.youtube.com/watch?v=6EDbdI_m73o&t=3003)]
Hey sir. So I mean I wrote up.

##### **Hooved** [[00:50:07](https://www.youtube.com/watch?v=6EDbdI_m73o&t=3007)]
Most of the recent progress. And one of the other discord channels. I'm setting up on tiny MD one to do training there. Scanning batch sizes right now to see what will fit in memory. Seems like at least. 248. Which is it's like, it's going to be a lot faster. This is really good. So. Once I'm done setting this up, I'd expect to be able to train within. You know, less than half a day, hopefully. Including eval fingers crossed. If everything. Speeds up with BEAM, et cetera. So. I'm going to be able to do training. In the next couple of weeks. I'll post updates in that channel. But yeah, the main issue was it's basically the same issue. We discussed a couple of weeks ago, which is. I think, you know, the learning rate was really mismatched with the batch size. And, you know, we didn't want to do gradient accumulation because that's a little bit different than the official. Per reference. So we're trying not to do gradient accumulation.

##### **Geohot** [[00:51:12](https://www.youtube.com/watch?v=6EDbdI_m73o&t=3072)]
And we're trying to do it in a more. I mean,

##### **Chenyu** [[00:51:14](https://www.youtube.com/watch?v=6EDbdI_m73o&t=3074)]
the only thing I would say is if you expect to run something for extended period of time, just post in the. In the. The TinyBox access channel. So we can sync. Because we only have like two MI 300 X machine. It's fine. If it's fine. If you have calculated everything and just need some time to run, but just. Post later for estimated time. So everyone else knows like not to break your job first. Then know when, when that will be free.

##### **Hooved** [[00:51:43](https://www.youtube.com/watch?v=6EDbdI_m73o&t=3103)]
For sure. I'll do that right now. I'm just running a couple minutes at a time, but I'll,

##### **SPEAKER_01** [[00:51:47](https://www.youtube.com/watch?v=6EDbdI_m73o&t=3107)]
I'll post that when I have it ready.

##### **Geohot** [[00:51:52](https://www.youtube.com/watch?v=6EDbdI_m73o&t=3112)]
Sounds good. Oh, That was B1TG. You want to add something?

##### **Hooved** [[00:52:07](https://www.youtube.com/watch?v=6EDbdI_m73o&t=3127)]
Oh, Yeah.

##### **Geohot** [[00:52:09](https://www.youtube.com/watch?v=6EDbdI_m73o&t=3129)]
so I can look at that.

##### **Sieds Lykles** [[00:52:09](https://www.youtube.com/watch?v=6EDbdI_m73o&t=3129)]
The reduced access PR is still review.

##### **Geohot** [[00:52:15](https://www.youtube.com/watch?v=6EDbdI_m73o&t=3135)]
Yes. Um, so I can look that over again. There were a few things. Commented out that I'm not totally sure they had to be. Um, I merged your cast and your other thing.

##### **Geohot** [[00:52:45](https://www.youtube.com/watch?v=6EDbdI_m73o&t=3165)]
I don't know. I'll look this over more today.

##### **Geohot** [[00:52:47](https://www.youtube.com/watch?v=6EDbdI_m73o&t=3167)]
I think it's probably good to merge. If all the tests pass, it's probably not wrong. Cool. Yeah, I'll revisit your master.

##### **Geohot** [[00:52:57](https://www.youtube.com/watch?v=6EDbdI_m73o&t=3177)]
And if the test pass, I will merge that. And the bounty is yours.

##### **Chenyu** [[00:53:03](https://www.youtube.com/watch?v=6EDbdI_m73o&t=3183)]
I also unlock all MOE bounty.

##### **Chenyu** [[00:53:07](https://www.youtube.com/watch?v=6EDbdI_m73o&t=3187)]
Because I want more people to try that. And also, I'm poaching my friend. So I want something for them to do.

##### **Chenyu** [[00:53:16](https://www.youtube.com/watch?v=6EDbdI_m73o&t=3196)]
We need more bounties, apparently. Great.

##### **Geohot** [[00:53:22](https://www.youtube.com/watch?v=6EDbdI_m73o&t=3202)]
Yeah, I think that's.

##### **Chenyu** [[00:53:24](https://www.youtube.com/watch?v=6EDbdI_m73o&t=3204)]
And I think some of the old bounties, maybe, is either a complaint. It's either done, or we probably need to do something. There are some of the really old ones.

##### **Geohot** [[00:53:39](https://www.youtube.com/watch?v=6EDbdI_m73o&t=3219)]
I hope with like, we already sort of have it

##### **Geohot** [[00:53:42](https://www.youtube.com/watch?v=6EDbdI_m73o&t=3222)]
with the rangeify language. I have that one where I make the kernel fast. We need to figure out how to get bounties for people to just do performance. We need to figure out some system to do this.

##### **Chenyu** [[00:53:58](https://www.youtube.com/watch?v=6EDbdI_m73o&t=3238)]
Yes, I think for now, we are in a limbo, because a lot of these performance bounty will directly or indirectly solve by rangeify. So once we have it, maybe we can revisit these. OK. Yeah, so I think having people to do performance, and we should be able to provide a set of tools that help them improve. That should be the default tools we recommend people

##### **Geohot** [[00:54:28](https://www.youtube.com/watch?v=6EDbdI_m73o&t=3268)]
to improve the performance. And then we can do some stuff. I see Harold, do you like the TinyGrad? Are you a happy TinyGrad user?

##### **Chenyu** [[00:54:43](https://www.youtube.com/watch?v=6EDbdI_m73o&t=3283)]
Yeah, I've had no issues recently. I guess AMD GPU is the only thing we're working on now.

##### **Geohot** [[00:54:55](https://www.youtube.com/watch?v=6EDbdI_m73o&t=3295)]
We will fix your big model. I'm sorry. I mean, fix the performance.

##### **Chenyu** [[00:55:03](https://www.youtube.com/watch?v=6EDbdI_m73o&t=3303)]
We will first get it to run, then we will think about performance.

##### **Chenyu** [[00:55:07](https://www.youtube.com/watch?v=6EDbdI_m73o&t=3307)]
Oh, I see. Yeah, it doesn't run on master yet. Yeah.

##### **Chenyu** [[00:55:10](https://www.youtube.com/watch?v=6EDbdI_m73o&t=3310)]
Let's start from there.

##### **Chenyu** [[00:55:12](https://www.youtube.com/watch?v=6EDbdI_m73o&t=3312)]
Yeah, because if not, we can look for different architectures that already compile well. But if you guys want to fix it anyway, that's fine.

##### **Chenyu** [[00:55:18](https://www.youtube.com/watch?v=6EDbdI_m73o&t=3318)]
So we definitely want to fix it anyway, because that's the point. We don't want you as a researcher to pick architecture just because the compiler supports it or not. Right. So yeah.

##### **Chenyu** [[00:55:30](https://www.youtube.com/watch?v=6EDbdI_m73o&t=3330)]
OK, yeah. That's fun.

##### **Geohot** [[00:55:32](https://www.youtube.com/watch?v=6EDbdI_m73o&t=3332)]
And we'll wait until TinyGrad's fast. Wait. OK. No, what happened to a Whisper bounty? There's update. We can test. Yeah, I'm waiting for the Whisper bounty.

##### **Geohot** [[00:56:03](https://www.youtube.com/watch?v=6EDbdI_m73o&t=3363)]
Post a link and say, copy and paste the MP3 file of the last TinyGrad talk in there,

##### **Geohot** [[00:56:09](https://www.youtube.com/watch?v=6EDbdI_m73o&t=3369)]
and it just works. That's great. Yeah, no. Just, yeah, tell me when you're ready to claim it. Give me a link. I'll test it a bit. OK. I think that's it for this. Thank you for this meeting. Thank you, everyone. See you next week.

##### **Qazalin** [[00:56:34](https://www.youtube.com/watch?v=6EDbdI_m73o&t=3394)]
Thank you.

##### **Geohot** [[00:56:34](https://www.youtube.com/watch?v=6EDbdI_m73o&t=3394)]
Bye.
