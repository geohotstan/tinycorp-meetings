# 2025-07-21 Meeting

### Meeting Agenda

**Time:** 9am Monday San Diego time
- company updates
- mi fast gemm
- upcast before reduce
- mlperf
- viz tool
- drivers
- cloud
- onnx
- other bounties

### Audio

[Youtube Link](https://www.youtube.com/watch?v=ZH1wOuAvl3k)

### Highlights

- **[Company Updates](#geohot-000012)**: Geohot shares the difficulty of finding small commercial buildings with high power capacity (a 5MW target) for a data center. On a positive note, tinybox sales are increasing, and they have 5090s in stock.
- **[MI Fast GEMM](#geohot-000438)**: After reviewing TVM and TileLang, Geohot proposes a new abstraction for fast GEMM in tinygrad. This involves a `contiguous define local` operator to explicitly manage memory hierarchies (DRAM, SRAM, registers), which will simplify kernel writing and may replace the `block_reorder` logic.
- **[Upcast Before Reduce](#chenyu-001134)**: Chenyu has refactored `kernel.py` to place upcast operations before reduce operations. This change makes the code more readable, simplifies hand-coded optimizations, and is a key step towards removing `ones` from the graph.
- **[MLPerf](#chenyu-002009)**: A Llama 4.5B data loader has been created. The stable diffusion bounty will be tied to the new MLPerf v5.1 "flux" model. Hooved is getting tinybox access to run training for the stable diffusion work.
- **[Viz Tool](#qazalin-002254)**: Qazalin presented progress on the visualization tool for performance counters. Geohot emphasized the tool should focus on surfacing key metrics like DRAM, SRAM, and ALU utilization to help developers quickly understand kernel performance bottlenecks.
- **[Drivers and CPU Backend](#nimlgen-003407)**: Nimlgen's refactor to support multi-device graphs (e.g., CPU+GPU) is almost complete, with copy speeds reaching 53 GB/s on the MI300. The next focus is offloading the optimizer to the CPU and implementing an efficient multi-threaded CPU backend.
- **[Cloud](#wozeparrot-004207)**: The remote scheduler has been merged. Cloud work is currently blocked by a recursion error in the `cac` hashing function on inputs larger than 4KB. Drive benchmarking is complete, and Western Digital drives will be used.
- **[ONNX](#geohot-004316)**: A large PR adding an ONNX importer is under review. The team discusses merging this functionality into the main tinygrad repository soon.
- **[Other Bounties and PRs](#geohot-004519)**: The `const` folding bounty is available again. The large C backend PR needs to be split into smaller parts. For the Whisper WebGPU bounty, the focus is on getting a functional version merged. A new, clearer device selection syntax (`DEV=...`) will be implemented to replace confusing flags.

### Transcript
##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=0)]
Let's start with company updates. So I met with several realters. Realters drive me crazy.

##### **Geohot** [[00:00:12](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=12)]
They basically, okay, so first off, one of the things before they want to show you buildings, they want you to sign a representation agreement, which pretty much says that if you buy a building, if they show you a building, it has to be bought through them. Okay, which I thought was kind of ridiculous. And then it was so hard to get across the point that what I wanted to buy was small buildings with lots of power. The listings don't include how much power the things have. Most of the time the only way to figure out how much power the building has is just go into the into the room and take a look. And the most of any of the buildings we went to, well, okay, well, so the one big building had more, but the reasonable buildings, 1200 amps, so literally less power than we have a comma. It's not viable. Like there's no way to buy a small building with a lot of power. You'll never get more power hooked up to it and dealing with realters is the worst.

##### **Chenyu** [[00:01:15](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=75)]
If we just post where you are looking for in terms of size and power on Twitter.

##### **Geohot** [[00:01:20](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=80)]
Oh, Twitter. Oh, I mean, I've tried Twitter. I tried. I'm still going back and forth with another again. They just have you up about the representation agreement.

##### **Chenyu** [[00:01:29](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=89)]
I don't know what realtor is. But I mean, I mean, if it's very clear for how big you want or you want.

##### **Geohot** [[00:01:36](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=96)]
Well, the problem is the realtor's don't know how much power buildings have. Someone must know, right? No. As far as I can tell, the it's probably deep in some inaccessible city plan somewhere. But as far as I can tell, the best they can do is take you to the building and then you can go in the closet and you can like, look. Great. So yeah, I mean, I don't know. It seems less viable that we can like, there's all these things are like not much bigger than comma.

##### **Chenyu** [[00:02:11](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=131)]
If you consider just same same stuff multiplied by four.

##### **Geohot** [[00:02:17](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=137)]
Oh, just by four. Yeah. You can definitely find more buildings. Yeah, you could definitely do that. You could probably also with a long enough lead time get more power hooked up. We're trying that here. So like we'll see if that pans out. But no, I mean, it just really gets me thinking that you just really have to just do this stuff at scale. Like there's no way to do anything close to five megawatt by buying like a small building.

##### **Geohot** [[00:02:52](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=172)]
I see much bigger in the clinic. Well, five, five megawatt is 10X comma. And that would be plenty. I mean, it's a lot five megawatts, but it's only like 50 racks. It's not like. It's not like, I guess I did, but I've been around 60 racks, 70 racks, but still it's like not like huge. Much too neat. It depends for what.

##### **Geohot** [[00:03:26](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=206)]
And another company, we just got an email from someone who wants to buy four tiny box screens. So they really, they're really starting to move now. Oh, should we raise the price? Someone serious. Should we raise the price? Yeah, maybe. Now I'm pretty happy with the price. I'm having enough GPU. Sorry. Oh, we have no shortage of GPUs. We have 5090s. So yeah, tiny box screens are moving. Yeah, the other project is coming along well for come.

##### **Geohot** [[00:04:00](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=240)]
Great. Sounds good. Sounds good. Hey. Oh, you really pose on Twitter or something? Yes. Okay, but it didn't get much reach for some reason.

##### **Chenyu** [[00:04:21](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=261)]
It's Monday morning here. Okay. Anyway, let's move on to a cool, tiny, great stuff. I don't know what you were up to, but you want to talk about your fast jamming, like some other abstraction.

##### **Geohot** [[00:04:38](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=278)]
Yeah, so mainly what I did this week was I built like I built TVM, I built tile, I went through it just saw what all of these existing abstractions were. And it's pretty clear, I think. It's what I described. I just need to implement that this week. Like instead of putting a load in the store with the defined local, you can really just say contiguous define local and this works. Because we have the axes labeled like like like so when you think of what contiguous is contiguous is just like creative to create a buffer and DRAM. But there's no reason that contiguous can't also be create a buffer in locals or create a buffer registers. Tile Lang has these abstractions pretty good. I posted, I posted Tile Lang and I actually like played with it a whole bunch. It's just yeah, like the front example basically explains how to write a fast jam. We just need to support that in in tiny grad.

##### **Chenyu** [[00:05:49](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=349)]
I also just post the new cutlass and their new tree in I think I'm via channel.

##### **Geohot** [[00:06:03](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=363)]
I didn't try cutlass at all.

##### **Chenyu** [[00:06:06](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=366)]
Yeah, let's tell us their new version that apparently to be unifying, unifying a lot of stuff over their old version.

##### **Geohot** [[00:06:17](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=377)]
Well, yeah, I mean, so all of this stuff that I'm thinking about isn't going to like like the things change in the B200. So maybe that's why Nvidia needs a new stuff.

##### **Chenyu** [[00:06:29](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=389)]
I just want to follow YouTube. They just realized they can represent stuff much simpler.

##### **Geohot** [[00:06:36](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=396)]
Interesting. Okay, I should spend some time reading this. But yeah, I mean, Tile Lang is a Tile Lang clearly represents a Tile Lang also is built on top of TVM. So it just compiles to a set of TVM transformations. So like I see how to like write that layer in in tiny grad by saying basically like yeah, contiguous local is the operator. And then you can also put after any contiguous you can put a view. So if you want to like if you want to swizzle the store, you can put a permute before they can take you as if you want to swizzle load, you can put a permute after they can take you as. Okay. But then it's only two shape trackers is not three right because we used to have the load store the load and that was three shape trackers and it was unclear exactly like what you could change to keep the thing correct. But with the contiguous you can put any shape trackers and it's always days correct. This also gets into the block reorder thing. So block reorder primarily exists to group all the loads and stores together. But there's another way to group the loads and the stores together, which is to talk about it being a copy to registers. So like right now we have this idea of like load and then what are we loading to loads to this implicit register, but we could also just like say I want to do this load to a defined reg.

##### **Geohot** [[00:08:12](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=492)]
And if yeah, and then that would then we could remove block reorder basically.

##### **Geohot** [[00:08:26](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=506)]
Well, the order would just be the only thing the block reorder really does the only thing that it makes things faster on is that it puts the loads before the math.

##### **Chenyu** [[00:08:38](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=518)]
But that's not always faster. Well, yeah, I mean then some some some algorithm somewhere and still need to figure out what's the last.

##### **Geohot** [[00:08:51](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=531)]
Yeah, so but then what it would become is a lot more like like you can do to define regs that are each half the size. Right, it's it defines this in the graph instead of in the implicit afterward. You still always a question fundamentally of what you want the top of sort to be right there can be there can be many top of sorts, but you can say that's part of graph and just.

##### **Chenyu** [[00:09:26](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=566)]
I saw I saw a block has some other nice property that's. It was split stuff such that the top of sort is individually. Directly met her hard.

##### **Geohot** [[00:09:40](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=580)]
Well, yeah, no, so the blocks are still good. I'm not going to remove block is just the whole idea like block reorder can be anything with a valid top of sort. So so blocks are already broken up into basic blocks so that every top of sort is valid for block reorder, but. Now what I'm saying is that like. It's that that's mostly a hack to deal with the fact that. So that's why we have to look at why that's happening and the reason it used to be if you just do like the normal like DFS top of sort it puts the loads it does like load mat, load mat, load mat, load mat, load mat, but you really want to do all loads put them in the load queue there's probably a limit to the size of the load queue and that's why maybe it's not always faster. And then you want to do with math. But yeah, then this can also so what I need to write is the thing also then like right now we are very explicit about when you do put things into registers it has to be upcasted, but these are actually different operations. There's nothing that says like you actually have to write out eight loads you could still use a for loop but loaded into a registers.

##### **Chenyu** [[00:10:52](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=652)]
Yeah, how you really loaded it and be separate from. No, upcast.

##### **Geohot** [[00:11:00](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=660)]
Yeah, exactly. So like like we almost I haven't found a counter example. Yeah, and this is what I've been looking for to basically just saying that like global means D RAM local means S RAM and upcast means register. Okay. Yeah, so I'm just going to work on implementing that this week and then we should start seeing some fast jams. I still haven't worked out exactly how to do the pipeline thing, but I think I can think about that later.

##### **Geohot** [[00:11:32](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=692)]
Sounds good.

##### **Chenyu** [[00:11:34](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=694)]
Okay, and I guess semi related. Oh, I did ask me was a bunch of refactors in current hot up high. Oh, now. The most significant differences now upcast is before reduce or see all those yellows before all green red. Apple. And I think hand club hand club optimization in here is to get much more readable now. We I get rid of all the first underscore produce works on the score upcast and I think pretty much everything is read from the axi type. So I test bunch of random insertion. Here's some other. Your stuff is less relevant to heuristic that if you always insert into globals and break up globals something else is breaking. But other than that. Mostly you can insert into like any place so you can see the final PR to let us just changing the insert upcast previously was inserting to the last game and now it's like inserting into the end of basically the head of. Reduce.

##### **Geohot** [[00:13:01](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=781)]
Yeah. Yeah, you can insert that max self dot axis.

##### **Chenyu** [[00:13:07](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=787)]
Yeah, so so so now it's very easy to write least you can just say okay, I want these types and I pick them mean or max or max plus one something like that.

##### **Geohot** [[00:13:16](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=796)]
Awesome. Yeah, no, I mean it's so it's so great that we have that now and hopefully now we can start figuring out how to remove the ones like hopefully what you're working.

##### **Chenyu** [[00:13:25](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=805)]
So once I think once would be easier after we figure out how you want to do with tensor core. So if you just do once now I have a draft the only thing that breaks is tensor core and it's because. There's also some mass in tensor course to add and subtract to account for the game that would disappear or reappear or something like that. Oh, maybe we should fix the repeat that so I think that first then I can finish removing once let's like very straightforward after the tensor course fix.

##### **Geohot** [[00:14:01](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=841)]
Great yeah, okay, I'll look at exactly what the what the problem is if you're if you're. Sure, I'll go draft yeah. But yeah, no, I mean hopefully this logic makes sense why all the upcasts had to go before the reduces like the reduces just like go away as you move down the graph.

##### **Chenyu** [[00:14:20](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=860)]
Yeah, but is impart of the group produce local.

##### **Geohot** [[00:14:24](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=864)]
Ah, okay, so yeah, we were thinking about it wrong. The group for reduced just because group for reduce happens to be assigned to the local access doesn't mean that it should go before the upcast.

##### **Chenyu** [[00:14:37](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=877)]
Right like you and yeah, so I understand because now that's the current behavior now it goes after the upcast and the reason for that. I still have a I don't know something like a hack or something that permutes something so that your upcast is still loaded as flow for because let's. I would currently low flow for.

##### **Geohot** [[00:15:02](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=902)]
Yeah, we can think about what that that that hack is, but my point is there's no reason that like when you end the group for reduce you end the locals that's what the if statement does. Yeah, you're end ranging on the locals basically. Yeah, so it really does belong after the upcast because you haven't closed the range of the upcast yet, but you have closed the range of that reduce just because it happens to be a local that doesn't really mean anything.

##### **Chenyu** [[00:15:35](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=935)]
I think for now we have a logic that let's for loop load is also in maybe that's a hack for how we store the local to be float for. But currently in the low store for the middle local is in like upcast if one.

##### **Geohot** [[00:15:58](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=958)]
I see the middle local is oh I see so it's.

##### **Chenyu** [[00:16:04](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=964)]
So for now to achieve that I temporarily permit when we fix a st and premier the back.

##### **Geohot** [[00:16:12](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=972)]
I see because that dimension actually exists in the.

##### **Chenyu** [[00:16:15](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=975)]
So let's let's let's let's why I initially thought maybe some of it should be before some of every after.

##### **Geohot** [[00:16:24](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=984)]
Interesting.

##### **Chenyu** [[00:16:25](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=985)]
Yeah, that thing is very easy to work with now so yeah, I think I'll think about what it is you're right it exists in the shape from the perspective of the yeah. Yeah, because you have to add them up later so yeah it's also in the in my last PR like move the actually you can see the fix st there's like a permute. But I should be like straightforward to work with now.

##### **Geohot** [[00:16:49](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1009)]
I mean that four thing isn't really an upcast it's an unroll right. Yes, I mean I know yeah we know cast and under also the same thing really but yeah yes.

##### **Chenyu** [[00:17:03](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1023)]
Okay anyway so hopefully that thing should be I think that part at least for me is very readable. I think somewhere somewhere something in the lower and something can be pulling up more. There's still some questionable logic that was reading it and was like wild.

##### **Geohot** [[00:17:24](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1044)]
Yeah, I mean hopefully we can change and clean up the like the constant and we can clean up I mean Colonel Pi technically doesn't have to track all the shape trackers which is kind of slow.

##### **Chenyu** [[00:17:37](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1057)]
Yeah, and we also have a little full shape is still there. I don't know how we want to deal with that.

##### **Geohot** [[00:17:43](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1063)]
Oh yeah, we got it. We got to get rid of full shape.

##### **Chenyu** [[00:17:47](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1067)]
Yeah, we need to also need to define like certain stuff.

##### **Geohot** [[00:17:52](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1072)]
What uses full shape still? So it's mostly... I think it's mostly just tracking like what's the max shape of stuff.

##### **Chenyu** [[00:18:07](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1087)]
So like you know the most outer thing. Yeah. And that's kind of stupid because most of the time that's only used to determine which axis are like reduce actually.

##### **Geohot** [[00:18:23](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1103)]
Yeah.

##### **Geohot** [[00:18:25](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1105)]
I mean I'm sure I'm sure a lot of it can be it can be. Yeah, I mean you have to think about it just from the perspective of there are multiple reduces. There are multiple reduces.

##### **Chenyu** [[00:18:34](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1114)]
The problem now is even there will be multiple reduces and like what ultimately is the property that we want to. For example, we might want to keep the GCD of the game because that's how you can do certain stuff.

##### **Geohot** [[00:18:52](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1132)]
What's GCD? GCD? Oh.

##### **Geohot** [[00:18:59](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1139)]
Yeah, but no like you don't need the GCD or the DEM. The problem is the optimization space is wrong, right? Like right now when you do an unroll that unroll applies to all.

##### **Geohot** [[00:19:12](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1152)]
Yeah, that's the real.

##### **Geohot** [[00:19:15](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1155)]
We need to assign the optimization to the reduce. Not to the graph in general and then this fixes all of that.

##### **Chenyu** [[00:19:23](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1163)]
Yeah, so I think I think this can be fixed once we have the lead from work to work with. Because this logic needs to move somewhere. It's not just completely removed because we still need it.

##### **Geohot** [[00:19:34](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1174)]
Yeah, I mean we need the only the only way that this really needs to be expressed is like you can put the optimizations on different parts of the graph. Like right now we just have opt-offs for the entire AST but really it should be opt-offs for the sync opt-offs for the produce. Maybe even opt-offs for loads that's what the locals and stuff are. So like different parts of the graph can be optimized.

##### **Chenyu** [[00:19:55](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1195)]
I think we will start with the reduce and see like how this work with like use air and jet letter stuff.

##### **Geohot** [[00:20:02](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1202)]
Cool. Next is ML Perth.

##### **Chenyu** [[00:20:09](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1209)]
I create a llama for a vibe data loader with was parrots. I will work on his a cack and well to use the caloder. Yeah, I think we talk about ML Perth. I saw a PR for stable diffusion. I know stable diffusion is going to change to flux in I.1. So I think it's fair to say who if you can get this down and like. Urge before the deadline for 5.1. You should still think printing you the bank is mine. But if you want the double bounty to be on the ML Perth results that needs to be what it is.

##### **Geohot** [[00:20:57](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1257)]
Yeah, I found that.

##### **Hooved** [[00:21:00](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1260)]
Okay, so it would just help to know like the value even if I just do stable diffusion. And it doesn't get on ML Perth. Like it's just is the value just having another example of training in tiny grad. Just so I understand like the motivation.

##### **Chenyu** [[00:21:17](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1277)]
I mean, I would imagine whatever you put in changing to flux. It's fairly straightforward. So it's more of a first example to train a diffusion model. And given given that ML Perth is the best. We have in terms of the rule and like the vigorous of the like how fast you can train. I think that's reasonable.

##### **Hooved** [[00:21:42](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1302)]
Okay, and then I think I'm pretty close to being ready to run training runs. Like what I'd be able to get on a tiny box, you know, assuming that's the case.

##### **Chenyu** [[00:21:53](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1313)]
I'm sure. I don't know how long you would take. Maybe if you can give some estimation. I mean, Grinting rule about is the least of a problem. But you also need to figure out the data in like time.

##### **Hooved** [[00:22:07](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1327)]
Yeah, I mean, I could try to calculate that from running it on my single GPU. But you know, I think I'd be able to give you a better much better idea by just adding some quick.

##### **Geohot** [[00:22:18](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1338)]
If you're cool red, yeah, we can get you boxes right away.

##### **Hooved** [[00:22:21](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1341)]
Yeah, I'm cool with red. I mean, like I'm a little worried about like full runs. But for now, just giving you an estimate and getting it up and running on a multi GPU red is fine.

##### **Geohot** [[00:22:31](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1351)]
Yeah, if you don't already have tiny boxes, just DM me a public key. And I'll add you to a few.

##### **Hooved** [[00:22:37](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1357)]
Yeah, I have the ones from a few months ago and you change things around. So yeah, I'll follow up on what. Okay, cool. Thanks.

##### **Geohot** [[00:22:47](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1367)]
Yeah, so. This let we can move on to this.

##### **Qazalin** [[00:22:54](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1374)]
I worked on app holes tools this week. And a bunch of the programming post the picture on general. This is currently how this looks like in my branch. Is it the track in global counters of the device?

##### **Geohot** [[00:23:12](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1392)]
Cool. Is this funny? Sorry. What this is like, amnesty or something?

##### **Qazalin** [[00:23:23](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1403)]
Yeah, this is a bit of lambnist. The challenges are that these counters are public and they aren't documents at the only way that Apple exposes them is with X code. So I think I have to reverse engineer it this week.

##### **Geohot** [[00:23:42](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1422)]
Well, I'm a lot more interested in the AMD ones than the Apple ones.

##### **Geohot** [[00:23:52](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1432)]
I think they're pretty similar. Yeah, no, I mean, I don't think we should put a lot of Apple specific work in.

##### **Geohot** [[00:24:05](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1445)]
And then like there's a few main things that we basically want to know. We want to know for every kernel. Like pretty much, you know, this I'm looking at this and this looks like information overload to me. I kind of want to know three things. I want to know what percent of the DRAM bandwidth am I using? What percent of the SRAM bandwidth am I using and what percent of the ALU's am I using?

##### **Geohot** [[00:24:29](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1469)]
Because there anything else that a kernel could be limited on? It also puts the conditionals and branching in ALU.

##### **Qazalin** [[00:24:52](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1492)]
So they have to bring down of FB 30 to utilization FB 16 utilization for this metal example. I think the categories are not that.

##### **Chenyu** [[00:25:03](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1503)]
I mean, even if you even if you split it like group by by different D types, you can still answer, OK, is this kernel limited by ALU? It can be integer, it can be flow, it can be whatever, but is it limited by that?

##### **Geohot** [[00:25:24](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1524)]
Interesting. I've heard this about metal. I've heard that they actually have completely separate ALUs for 32 and 16. And it almost looks like you can use both if you know how to do it. I guess the integer thing is different too because I guess you could also be limited by indexing. But even if I just knew, even if I just had like those three numbers, like what's my RAM utilization, my SRAM, my DRAM and my ALUs. And then if for some reason like they're all low, that's an interesting question too. But my only point is like the goal with Viz here should not be to surface every piece of information possibly in the trace. Val, like I find that this is some of the problem with some of these GPU profilers, like they don't let me quickly answer the question of, OK, wait, why is my kernel slow? The Nvidia ones a lot better than the AMD one if you've used it. The Nvidia one will show you these. It will draw these like graphs for you that show you like the data flow. Have you seen them?

##### **Qazalin** [[00:26:33](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1593)]
OK, I have some pictures.

##### **Geohot** [[00:26:41](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1601)]
Yeah, I think the picture is a bit overkill. I don't think we need to picture, but just.

##### **Qazalin** [[00:26:45](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1605)]
No, remember what you're saying with the arrows that go into how much cash it's raised with that board and it shows you like what single bar jobs.

##### **Geohot** [[00:26:58](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1618)]
Yeah, like we should think about how best to canonicalize these things and then display them in a way that's useful for kernel tuning. Like the dream. OK, so the way to get performance out of these entire systems is like you think about every resource you have. You have ALUs, you have RAM, you have S RAM, you have network cards, you have hard drives, you have you have everything. The closer you can get all your utilization to 100% the better you are, the better you overlap all of your things. So yeah, that's like the kind of information I want this stuff to surface quickly. Whereas then I see something on here like I don't even know what FS occupancy means.

##### **Chenyu** [[00:27:47](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1667)]
I think something that would be useful is you can just write a benchmark that has like a big jam has a metrics to vector multiplication and when I just copy data from one to like another. Yeah, you would you can tell like in this three type of scenario what the profiler will look like and does it really surface like the limited point of that kernel. We will expect that three graph to look very different.

##### **Geohot** [[00:28:22](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1702)]
I think that's a good strategy.

##### **Geohot** [[00:28:28](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1708)]
I don't know, I mean also if it's just if it's just easy to like we start by servicing everything, then we write that then we write that task with the three things and then we say OK wait, so what do we how do we want to clean this up so it's actually like like usable for kernel tuning.

##### **Chenyu** [[00:28:45](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1725)]
I think I think a good part of this exercise is if you are looking to different profiler and the counters they expose and end up having a much better attraction for the thing one to track. I think that's also a win.

##### **Geohot** [[00:29:03](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1743)]
Yeah, great. Is this how much overhead is this ad?

##### **Qazalin** [[00:29:12](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1752)]
Basically zero runtime overhead.

##### **Geohot** [[00:29:15](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1755)]
Great.

##### **Qazalin** [[00:29:17](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1757)]
Start-up time is slow because I'm using subprocess calls. We could be faster.

##### **Geohot** [[00:29:26](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1766)]
Wait, what do you need subprocesses for?

##### **Qazalin** [[00:29:30](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1770)]
Because they don't expose it. They will be exported by a command-wide interface if the counters and reporting.

##### **Geohot** [[00:29:42](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1782)]
Huh? Is this not a pill? It's not public. It's not documented anywhere. I would access the counters for it.

##### **Hooved** [[00:29:56](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1796)]
Basically.

##### **Geohot** [[00:29:56](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1796)]
I see. So you're calling this XC trace export thing. I see. So it's just like you're saying this is like a file format we don't understand. And then it's outputting some XML.

##### **Qazalin** [[00:30:24](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1824)]
The file format would be easy to reverse. I think the harder one is the counters. The file format is easy to parse also. It's not a difficult thing. I've already made that fast.

##### **Geohot** [[00:30:36](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1836)]
I see.

##### **Qazalin** [[00:30:38](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1838)]
But the counters themselves like XC trace stopping the XC trace on beautiful msx4 seconds.

##### **Geohot** [[00:30:47](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1847)]
I see. Yeah. Yeah, we should just figure out what that. We should read the file. Is it some cost of format or like what is the metal that trace file?

##### **Qazalin** [[00:31:11](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1871)]
The trace what is a custom format yet, but it's a binary. You can reverse it. There's been attempts to reverse it. It's what the source. No, the problem isn't the trace format. It's the actual counters and accessing them. The hardware counters and reading those. There was basically no docs on that.

##### **Geohot** [[00:31:44](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1904)]
Wait, but it's not like XC trace is reading those. It's like this. It's like this. It's recording them. Oh. Oh, I see. Okay. You have two calls to XC trace. You have an XC trace record call here. Huh. Interesting.

##### **Geohot** [[00:32:13](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1933)]
Yeah, I don't know. I mean, we could also like for metal, we could the more the really important one here is is to get this working on the CDNA AMD. So we can start so we can start running llamas and we can start saying, okay, where are we not utilizing correctly?

##### **Geohot** [[00:32:36](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1956)]
So if this is how it is for metal, then I guess that's fine for now. I don't know. Maybe we should get it behind a. Get it behind a flag.

##### **Qazalin** [[00:32:50](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1970)]
Let's focus on the.

##### **Geohot** [[00:32:52](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1972)]
Yeah, no, let's get metal merged, but I wouldn't spend too much time reversing this format. I would be like, this is fine for now. Just get it behind something. We could use it sometimes. And then as we like get better at this, we can we can work on we can do that later.

##### **Geohot** [[00:33:09](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1989)]
Yeah, I mean, for AMD, we should already have all the like all the SKTT stuff is already in our stuff.

##### **Geohot** [[00:33:14](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=1994)]
So we shouldn't have to like call out to something.

##### **Qazalin** [[00:33:20](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2000)]
Yeah, so many run out of buffer errors.

##### **Geohot** [[00:33:27](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2007)]
Brand out of ran out of buffer.

##### **Qazalin** [[00:33:30](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2010)]
Yeah, the buffer size error. This get you just crashes. You think the word stops.

##### **Geohot** [[00:33:36](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2016)]
Oh, yeah, I mean, yeah, sure. It's not going to eat all your GPU RAM. If you've been on suggests disabling the instruction tracing, yeah, you can enable like different things in SKTT. And I think we can disable some of them.

##### **Geohot** [[00:33:50](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2030)]
Oh, that's move on to driver. Or I guess copy speed.

##### **Nimlgen** [[00:34:07](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2047)]
Yeah, so in working on their factors and the copies it. Yeah, so basically their factors to support several devices inside each secure graph. Because now we can like mix AMD and CPU. Man, which is also security device now like CPU in the end of the year. So yeah, I mean, the factor is almost like done like the final PR to get this speed is not ours yet. But yeah, it's about when it's cheated. It's about like on MI 300. It's 53 gigabytes a second cup and two gigabytes from the CPU to GPU. Nice. Yeah, so I'm going to finish this this week.

##### **Geohot** [[00:35:05](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2105)]
Yeah, then I think the next thing to work on is starting to actually offload the optimizer. Putting the optimizer on the CPU and. Yeah, running it there and being able I mean, we need to overlap the copy with the compute.

##### **Geohot** [[00:35:24](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2124)]
Yeah, I mean, theoretically we can do that already.

##### **Hooved** [[00:35:31](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2131)]
That's.

##### **Geohot** [[00:35:33](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2133)]
Yeah, okay.

##### **Nimlgen** [[00:35:34](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2134)]
I mean, that's depends on the schedule order we get. I'll take a look into this.

##### **Geohot** [[00:35:39](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2139)]
Yeah, I mean, I think we could write like a test that just creates a huge number of parameters and on the GPUs and does the does the stuff. It runs the optimizer basically. Kind of the end to end test does the HQ CPU stuff support any multi dreaded.

##### **Nimlgen** [[00:36:02](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2162)]
Not yet. I mean, yeah, I also thought about that. I mean, I've posted that basically they want the.

##### **Geohot** [[00:36:11](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2171)]
Threading thing, but I mean, currently like we can do this. I mean, the.

##### **Nimlgen** [[00:36:22](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2182)]
So yeah, I mean, the ideal way is to write like the pollers in and see like I mean in tiny grad and just compile them to see because overweist. I mean, we have like 64 CPUs and I think it will be pretty slow to. Dispatch all of them from Python. Because of the. I mean, we can do that as the first step. Yeah, I can do that.

##### **Geohot** [[00:36:51](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2211)]
I mean, I don't think we want the Python to create like we need we need these threads to be long running. We want basically 64 long running threads that sit and wait on a queue. And then they all pull on the queue or some some some non busy way on the queue. And then as soon as a kernel comes in, they all launch the kernel.

##### **Geohot** [[00:37:16](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2236)]
Yeah, I mean, yeah, I can do that.

##### **Nimlgen** [[00:37:18](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2238)]
But I think we will have some overhead because of the G. I mean, these threads, they won't execute in parallel in Python.

##### **Geohot** [[00:37:27](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2247)]
Well, no, but I mean, they will if you make them like if you call out to some some FFI thing, they'll totally execute in parallel. Yeah, I mean, I agree that you have to write this like waiting stub and see. I think the waiting stub can't be in Python. I agree with that.

##### **Geohot** [[00:37:46](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2266)]
Yeah, okay.

##### **Geohot** [[00:37:47](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2267)]
But you know, you can totally like launch the threads from Python. I don't think it should be a problem with that. As long as you're in some external call, I'm pretty sure Python releases the G.

##### **Nimlgen** [[00:37:59](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2279)]
Yeah, that's true. But yeah, actually it's interesting what we have to have like to dispatch 64 threads. Because we have a lot of course, CPUs. Oh, just to be honest.

##### **Geohot** [[00:38:11](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2291)]
Yeah, I don't know. Yeah, I don't know. Creating a thread is going to be slow. We can play with that. But yeah, no, it's these threads that are just these. Yeah, like the little bit of like waiting logic needs to be, or basically doing is like building a like a GPU dispatcher. And we can decide whether we want it to be like GPU style with the with the G, where they all run or whether it's just actually like it has to be exactly 64, or kind of like how we did it for DSP. Yeah, but I mean, this should this should unify with the DSP thing. Remember the DSP thing where we launched on the two course?

##### **Geohot** [[00:38:48](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2328)]
Yeah. Yeah, I think it might be.

##### **Nimlgen** [[00:39:00](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2340)]
I mean, the DSP would just like in C, we just, I mean, they started this thread from C, from C program. I think we don't want to do this, this way here.

##### **Geohot** [[00:39:13](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2353)]
Agreed. I think we want them to be long running threads that, yeah.

##### **Geohot** [[00:39:22](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2362)]
It seems like a progress.

##### **Geohot** [[00:39:24](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2364)]
Yeah, I mean, I think the thing to the thing to just write as soon as you feel you're ready is to just write the optimizer and get the optimizer running offloaded with overlapped copying compute.

##### **Wozeparrot** [[00:39:43](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2383)]
Just something quickly. I wrote the initial port to MI 350, but I think beam is still broken. If you want to look into that.

##### **Nimlgen** [[00:39:55](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2395)]
Yeah, sure.

##### **Geohot** [[00:39:56](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2396)]
Yeah, I'll take a quick. You mean, you mean it finds bad kernels to find scourgless crash GPU?

##### **Wozeparrot** [[00:40:01](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2401)]
No, it's the same thing. I don't know if it's finding bad kernels and crashing. It might be something with the driver.

##### **Geohot** [[00:40:07](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2407)]
Got it. I mean, the question is like, is beam crashing because like it just beams like doing a lot? Or is beam crashing because it occasionally finds a kernel that uses the locals wrong?

##### **Wozeparrot** [[00:40:16](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2416)]
Yeah, it's hard to tell.

##### **Geohot** [[00:40:17](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2417)]
Yeah, I mean, what you'd want to do is just save each kernel. If you can find one kernel that repeatedly crashes it.

##### **Wozeparrot** [[00:40:23](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2423)]
Oh, I have a kernel that repeated the crash.

##### **Geohot** [[00:40:24](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2424)]
You have one kernel.

##### **Wozeparrot** [[00:40:26](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2426)]
Well, I just beam, but...

##### **Geohot** [[00:40:28](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2428)]
Yeah, but what I'm saying is get the generated code, get the generated code from beam, and then make a... I would do this, I think it's worth your time. Make a minimum reproduction that's just like when I run this kernel like crashes, right? Cause that's what you got kind of got to do. It's likely to do like some like local configuration thing.

##### **Geohot** [[00:40:45](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2445)]
Probably. Yeah.

##### **Chenyu** [[00:40:48](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2448)]
Oh, also, I guess maybe semi related. I haven't checked for a while, but it looks like our ML Perth Chrome job has been failing for a week or so. It depends during the instance.

##### **Geohot** [[00:41:03](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2463)]
Oh. I don't know if it's related. Okay. Great.

##### **Chenyu** [[00:41:15](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2475)]
Anything else? Oh. Have you figured out the CIA issue?

##### **Nimlgen** [[00:41:24](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2484)]
Actually, not. I just try to add some debug in like the limit the size we allocate, like the total memory we allocate, but I know I need to make a second.

##### **Chenyu** [[00:41:39](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2499)]
I was checking if there's like an easy way to add a plugin for PyTask to show like some more information,

##### **Geohot** [[00:41:49](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2509)]
other than just the time. But it's not very helpful. Okay. Anything for cloud?

##### **Wozeparrot** [[00:42:07](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2527)]
I merged our remote schedule. I'm sorry that took so long. The next one should hopefully just land pretty soon. I looked over it initially and it looks okay. Cloud is blocked on hashing. So cac fails basically for any reasonable length input.

##### **Chenyu** [[00:42:27](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2547)]
Yeah, that's the test you're having PR right?

##### **Wozeparrot** [[00:42:29](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2549)]
I have a failing test for it. It always broken or did we break? Not sure. Basically like a 4 kilobyte input and you call cac on it, you can have a curgion error.

##### **Geohot** [[00:42:41](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2561)]
A curgion error?

##### **Wozeparrot** [[00:42:43](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2563)]
Yes.

##### **Geohot** [[00:42:44](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2564)]
Hmm.

##### **Wozeparrot** [[00:42:45](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2565)]
Not sure. If it broke or if it worked before. So I think something. Yeah. So I'm genuinely take a look and then I'm moving to MLPervStub. Great.

##### **Geohot** [[00:43:00](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2580)]
How's the benchmarking the new drives going?

##### **Wozeparrot** [[00:43:04](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2584)]
As our card is not in. Yeah, the crucial one sucks. And I think we're just going with the western digital ones.

##### **Geohot** [[00:43:10](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2590)]
Great.

##### **Hooved** [[00:43:13](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2593)]
Okay.

##### **Geohot** [[00:43:16](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2596)]
Anything for our next. I will merge low one eating. Oh, I didn't know it. I'm trying to. One one zero zero zero zero. Looks like a bunch of tension to the parser.

##### **Geohot** [[00:43:53](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2633)]
No, no, the test pass it probably just be merged.

##### **Chenyu** [[00:43:59](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2639)]
Yeah, did I come in anything? Maybe it's fine. Okay. Okay. I will reveal this in wrong event. I think things like this is. Why? I will let you know if I want like more separates. Exable version, but otherwise it.

##### **Geohot** [[00:44:22](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2662)]
Okay. Interesting to see TVM has four front ends. It's very similar to ours. It's interesting they call their NN of front end. I guess you could call our NN of front end toe. I mean, it's also relax.

##### **Wozeparrot** [[00:44:40](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2680)]
They have stable each other.

##### **Geohot** [[00:44:42](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2682)]
Relax is just their like scheduler. Yeah, they have stable HLO as well.

##### **Wozeparrot** [[00:44:47](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2687)]
Does it actually write stuff? That's what I look directly. Oh, yeah.

##### **Geohot** [[00:44:55](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2695)]
So yeah, stable HLO is just a jacks cannot put stable HLO. I don't think we need stable HLO.

##### **Chenyu** [[00:45:04](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2704)]
Okay. So I will reveal our next stuff and we can continue discussion in our next. Cano to see what's left before we can merge that to tiny repraper.

##### **Geohot** [[00:45:19](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2719)]
Okay. Let's look main stuff other boundaries. So I think as like also he doesn't have time to finish the const thing. We can unlock that.

##### **Chenyu** [[00:45:43](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2743)]
I don't know. I think I merged one one small refactor for our science door. I don't know what's the current status to that.

##### **Geohot** [[00:46:01](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2761)]
That was to weakness. Oh, it's been a test.

##### **Chenyu** [[00:46:05](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2765)]
The tiny bit of back end for Steve.

##### **Geohot** [[00:46:07](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2767)]
Oh, no. No, okay. Yeah, okay. I saw them done that. All right. To work. See for back end. It's so far down. I went through some PRs. I tried to close PRs. It's getting overwhelming. Everyone please close your PRs.

##### **Geohot** [[00:46:31](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2791)]
Yeah.

##### **Hooved** [[00:46:36](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2796)]
Okay.

##### **Geohot** [[00:46:37](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2797)]
I merged the failing test.

##### **Chenyu** [[00:46:41](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2801)]
Okay. What else do we have? Oh, we have the assembly back end for some progress on that.

##### **Geohot** [[00:46:53](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2813)]
That's guys the speed there. I don't know if the search here. Have some point he mentioned something. Damn, that's a lot of lines.

##### **Geohot** [[00:47:12](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2832)]
Yeah, no, I mean, if this is still 802A, this PR needs to be broken up into a lot of things. Like I see this change to symbolic and some of these changes to ops. Need to be their own. Need to be their own PR. I'm fine with things like comp GT. We should just really add all these. And we should separate the ones that can exist in the early graph. Versus the ones that are only existing to rewrite. But yeah, I mean, there's a ton of stuff in this PR that needs to be separated. Before we can merge anything. But then first, I also want to see some benchmarks showing that it's as fast as a one. But I see you, VNs, working on assembly stuff too. For the RDNA. We're getting there. We're getting to the point where you start to see what these things are and how register allocation and memory assignments and stuff are all the same problem. Oh, I also play with this thing called a model that does uses grobe for. For for for it makes it clear how at least. Like determining schedule order and determining memory layouts are intergeneral near programming. So if there's any dependencies that we should be adding to tiny grad, there are things like sat solvers and I don't piece all this.

##### **Chenyu** [[00:48:47](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2927)]
Great. You also have 16 PR open apparently. I know. I know. I can do your parts. I know.

##### **Geohot** [[00:49:00](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2940)]
I know. I looked at the one. I was like, oh, I want that one. I want that one. Uh, I don't know. It's probably fine. All right. You apps unique fixes, double gradient issue. Close out.

##### **Hooved** [[00:49:13](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2953)]
Okay.

##### **Chenyu** [[00:49:15](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2955)]
Uh, uh, yeah. I think that's pretty much it. Given that we post on Twitter. Or people in this chat. If you have any questions about tiny grads, how is your time you can pose it in general or just pose it in general.

##### **Geohot** [[00:49:39](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2979)]
I'm having a chance to do more work for tensor cat and loops splitting.

##### **Geohot** [[00:49:43](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=2983)]
Yeah. That stuff needs to kind of be rewritten. I mean, you can think about which of the. So, so like what TVM and halide have for their loops is they kind of just give you like a range variable. And then you can do things on that range variable, like split them or views them and stuff. Uh, so I think that that's more of the direction we'll go, right? Like you could imagine these optimizations being done after the lower where you can just split a range into two ranges.

##### **Geohot** [[00:50:17](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=3017)]
Um, all that stuff sure to kind of work. But it is going to be rewritten so. Uh, for the whisper web GPU bounty.

##### **Geohot** [[00:50:34](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=3034)]
Do we have, I mean, let's get it working. Right. Like let's claim the bounty and get it working. Is it good to merge? Is it working? Is it tested more than trying to like make anything faster or better? Like, as long as it's not wrong, let's get the bounty claim. And then we can see what's next.

##### **Geohot** [[00:50:49](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=3049)]
Um, before we start adding these optional things.

##### **Geohot** [[00:51:12](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=3072)]
So you say it has hallucinations and is generally unstable. Is that due to a bug or is that due to the model just not being good?

##### **Chenyu** [[00:51:24](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=3084)]
If you call us a model using other people's implementation and it gives you pretty much the same thing, then it's not. To the your implementation.

##### **Geohot** [[00:51:35](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=3095)]
Yeah, can you, I mean, can you run the bigger one?

##### **Geohot** [[00:51:43](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=3103)]
Well, the problem with saying that is there might also be bugs, right? Like it might not work when it's correct, but there might also be bugs. So I think we should figure out how to like whatever whisper model has been using it. We've been using to transcribe. Why can't we just run the big one?

##### **Geohot** [[00:51:56](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=3116)]
How big is the big one? Big one's not that big, right?

##### **Chenyu** [[00:52:02](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=3122)]
Also, it's between compare comparing or implementation to maybe a different backend in tiny grads. Then if you really want to, you can compare it to other people's implementation. It's just for sanity checking because maybe there's a box in other people's implementation.

##### **Geohot** [[00:52:19](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=3139)]
Yeah, I've been used to like their official open AI one.

##### **Geohot** [[00:52:24](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=3144)]
There's bugs in that there, the design. We know if comma people are happy with working on tiny breath stuff. No, they hate all the flags.

##### **Wozeparrot** [[00:52:44](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=3164)]
So comma intern. Is the bid cast thing fixed for that? Yeah, it's my passion.

##### **Geohot** [[00:52:53](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=3173)]
They don't know flags, what flags are they now?

##### **Wozeparrot** [[00:52:57](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=3177)]
They said it's slow and then I tell them, oh, did you try this flag? Which flag? Yeah, which flag they said about? They say beam takes too long. Well, yeah. You tell them the beam optimization flags you can do, like beam min progress.

##### **Geohot** [[00:53:14](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=3194)]
Wait, you might just not work because you're not a speaker.

##### **Geohot** [[00:53:16](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=3196)]
I'll make you a speaker. If you want to speak. If you want to speak, you have to exit the chat and rejoin. Now you have that role. I feel like my mic just doesn't work. There's some shoe works on here.

##### **Geohot** [[00:53:40](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=3220)]
Oh, okay. No, I'm still most passionate about the whole device thing that is from my biggest passion.

##### **Chenyu** [[00:53:48](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=3228)]
Yeah, I thought you were working on that.

##### **Geohot** [[00:53:51](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=3231)]
Yeah, whatever you want to hear, what does we decide? Dev equals. Oh, we decided I thought it was.

##### **Wozeparrot** [[00:53:59](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=3239)]
Devices so long to tie.

##### **Geohot** [[00:54:01](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=3241)]
I don't care. I whatever whatever you guys decide.

##### **Wozeparrot** [[00:54:07](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=3247)]
I'm fine with D equals. Flip the flag around. One equals.

##### **Geohot** [[00:54:15](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=3255)]
Yeah, it's just like instead of CPU, it was one. You just do one equals.

##### **Geohot** [[00:54:20](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=3260)]
At least it exposes the silliness of the other thing. Okay, so what? The equal. Okay, but you want me to write a similar margin. Yes, dev equals is good. Right test for that will merge it. Okay, sounds good. That's actually my only complaint. We have some other model that didn't compile. Wait, wait, wait.

##### **Chenyu** [[00:54:43](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=3283)]
If that's the only complaint, that's very different from we do hate flags.

##### **Geohot** [[00:54:47](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=3287)]
Yeah, that's well, that's after the flags we use. If you use it, it was one of the things that was for being it. LLM LVM LLVM opt. Why would I not want to optimize LVM? It sounds like a good idea. Did we remove that flag? We LLM opt just defaults the one now. Yeah. No action explicitly. Does it probably these flags just hang around? Even if we don't do anything.

##### **Geohot** [[00:55:11](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=3311)]
And the reason you don't, yeah, and you don't always know. Put the reason that you don't always want to optimize it is because you can see optimize your slow.

##### **Geohot** [[00:55:18](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=3318)]
Okay, fair enough. I guess that makes sense.

##### **Geohot** [[00:55:22](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=3322)]
Yeah.

##### **Geohot** [[00:55:23](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=3323)]
But no, dev equals sounds good. I have a thinking about that. Another model compilation issue, but I'll see if it's fixed. The latest 10 eGrid. Otherwise, I'll post about it again. Cool.

##### **Geohot** [[00:55:32](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=3332)]
Yeah, a lot of that stuff has to do with bitcast. I have like the right refactor for that. What we'll get to that after.

##### **Geohot** [[00:55:42](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=3342)]
Once we're back on schedule or stuff.

##### **Chenyu** [[00:55:46](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=3346)]
We will get. Yeah, postly issue if the compiles sales and we will cry out. Yeah. And unlike now, we can call it product perfas. Very important that opened policy using. ��q ossversion of anything.

##### **Geohot** [[00:56:00](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=3360)]
Um, yeah, that was a new model we want to merge. We've been on a latest version for a while, which is actually a really nice upgrade. Yes. That we want to keep that going forward. 느�ide Naj, that's been working. Sometimes we just have. New malls. And then I failed for weird reasons, but I guess one of those. It was just fixed so I think there's one more.

##### **Geohot** [[00:56:20](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=3380)]
that I'll check it again. Okay sounds good. Okay I think let's say it for a

##### **Chenyu** [[00:56:33](https://www.youtube.com/watch?v=ZH1wOuAvl3k&t=3393)]
listening. Thank you everyone. See you next week. Bye. Bye.
