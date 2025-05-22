import re
from termcolor import colored
import spacy
from collections import Counter

nlp = spacy.load('en_core_web_sm')

def kwic(text, target, window=5, search_type='token', color='cyan', attrs=None, sort_mode='sequential'):
    if attrs is None:
        attrs = ['bold']

    doc = nlp(text)
    tokens = [tok.text for tok in doc]
    matches = []
    output_data = []

    if search_type == 'token':
        target_words = target.split()
        n = len(target_words)
        lowered = [t.lower() for t in tokens]
        for i in range(len(tokens) - n + 1):
            if lowered[i:i+n] == [w.lower() for w in target_words]:
                matches.append((i, n))

    elif search_type == 'pos':
        target_tags = target.split()
        n = len(target_tags)
        pos_list = [tok.pos_ for tok in doc]
        for i in range(len(pos_list) - n + 1):
            if pos_list[i:i+n] == target_tags:
                matches.append((i, n))

    elif search_type == 'entity':
        ent_type = target.upper()
        for ent in doc.ents:
            if ent.label_ == ent_type and ent.text != "NLP":
                matches.append((ent.start, ent.end - ent.start))

    else:
        raise ValueError("search_type must be one of: 'token', 'pos', 'entity'")

    for idx, length in matches:
        for sent in doc.sents:
            if sent.start <= idx < sent.end:
                sent_tokens = [tok.text_with_ws for tok in sent]
                sent_doc = list(sent)
                local_idx = idx - sent.start
                left = sent_tokens[max(0, local_idx - window): local_idx]
                mid = sent_tokens[local_idx: local_idx + length]
                right = sent_tokens[local_idx + length: local_idx + length + window]
                mid_str = ''.join(mid).strip()
                highlighted = colored(mid_str, color, attrs=attrs)
                display = ''.join(left).strip() + ' ' + highlighted + ' ' + ''.join(right).strip()
                next_token = sent_doc[local_idx + length].text if local_idx + length < len(sent_doc) else ''
                next_pos = sent_doc[local_idx + length].pos_ if local_idx + length < len(sent_doc) else ''
                output_data.append((display, next_token, next_pos))
                break

    if sort_mode == 'sequential':
        sorted_output = output_data
    elif sort_mode == 'token_freq':
        freq = Counter([item[1] for item in output_data])
        sorted_output = sorted(output_data, key=lambda x: (-freq[x[1]], x[1]))
    elif sort_mode == 'pos_freq':
        freq = Counter([item[2] for item in output_data])
        sorted_output = sorted(output_data, key=lambda x: (-freq[x[2]], x[2]))
    else:
        print("Invalid sort_mode. Defaulting to sequential.")
        sorted_output = output_data

    for display, _, _ in sorted_output:
        print(display)

if __name__ == '__main__':
    text = """
    Natural language processing (NLP) has undergone significant transformation over the past few decades.
    Techniques have evolved from simple rule-based systems to sophisticated neural models,
    enabling tasks such as machine translation, sentiment analysis, and question answering.
    Language models like BERT, GPT, and RoBERTa have transformed the way machines understand text.
    With advancements in attention mechanisms and transformer architectures,
    these systems achieve state-of-the-art results across multiple benchmarks.
    Researchers are now focusing on multilingual capabilities, model interpretability, and ethical considerations.
    Tools like spaCy and HuggingFace Transformers have democratized access to powerful NLP models.
    Applications include chatbots, summarization, translation, and sentiment detection.
    As computing power grows, so does the potential for real-time, context-aware NLP applications.
    However, issues such as bias, hallucination, and data privacy still pose challenges.
    The future of NLP lies in responsible innovation, interdisciplinary collaboration,
    and a deeper integration with human communication needs.
    Barack Obama was born in Hawaii and served as the 44th President of the United States.
    He delivered a keynote speech in New York City on climate change policy.
    The event was hosted by the United Nations and attended by representatives from Google and Microsoft.
    On January 1, 2020, the organization pledged $1,000,000 to support renewable energy projects.
    Meetings are scheduled daily at 10:00 AM in GeAneva, Switzerland to evaluate the progress.
    The train departs at 6:45 PM from platform 3 and arrives by 9:30 PM.
    A banana is an elongated, edible fruit – botanically a berry – produced by several kinds of large treelike herbaceous flowering plants in the genus Musa. In some countries, cooking bananas are called plantains, distinguishing them from dessert bananas. The fruit is variable in size, color and firmness, but is usually elongated and curved, with soft flesh rich in starch covered with a peel, which may have a variety of colors when ripe. It grows upward in clusters near the top of the plant. Almost all modern edible seedless (parthenocarp) cultivated bananas come from two wild species – Musa acuminata and Musa balbisiana, or hybrids of them.
Musa species are native to tropical Indomalaya and Australia; they were probably domesticated in New Guinea. They are grown in 135 countries, primarily for their fruit, and to a lesser extent to make banana paper and textiles, while some are grown as ornamental plants. The world's largest producers of bananas in 2022 were India and China, which together accounted for approximately 26% of total production. Bananas are eaten raw or cooked in recipes varying from curries to banana chips, fritters, fruit preserves, or simply baked or steamed.
Worldwide, there is no sharp distinction between dessert "bananas" and cooking "plantains": this distinction works well enough in the Americas and Europe, but it breaks down in Southeast Asia where many more kinds of bananas are grown and eaten. The term "banana" is applied also to other members of the genus Musa, such as the scarlet banana (Musa coccinea), the pink banana (Musa velutina), and the Fe'i bananas. Members of the genus Ensete, such as the snow banana (Ensete glaucum) and the economically important false banana (Ensete ventricosum) of Africa are sometimes included. Both genera are in the banana family, Musaceae.
Banana plantations are subject to damage by parasitic nematodes and insect pests, and to fungal and bacterial diseases, one of the most serious being Panama disease which is caused by a Fusarium fungus. This and black sigatoka threaten the production of Cavendish bananas, the main kind eaten in the Western world, which is a triploid Musa acuminata. Plant breeders are seeking new varieties, but these are difficult to breed given that commercial varieties are seedless. To enable future breeding, banana germplasm is conserved in multiple gene banks around the world.
The banana plant is the largest herbaceous flowering plant. All the above-ground parts of a banana plant grow from a structure called a corm. Plants are normally tall and fairly sturdy with a treelike appearance, but what appears to be a trunk is actually a pseudostem composed of multiple leaf-stalks (petioles). Bananas grow in a wide variety of soils, as long as it is at least 60 centimetres deep, has good drainage and is not compacted. They are fast-growing plants, with a growth rate of up to 1.6 metres per day.
The leaves of banana plants are composed of a stalk (petiole) and a blade (lamina). The base of the petiole widens to form a sheath; the tightly packed sheaths make up the pseudostem, which is all that supports the plant. The edges of the sheath meet when it is first produced, making it tubular. As new growth occurs in the centre of the pseudostem, the edges are forced apart. Cultivated banana plants vary in height depending on the variety and growing conditions. Most are around 5 m tall, with a range from 'Dwarf Cavendish' plants at around 3 m to 'Gros Michel' at 7 m or more. Leaves are spirally arranged and may grow 2.7 metres long and 60 cm wide. When a banana plant is mature, the corm stops producing new leaves and begins to form a flower spike or inflorescence. A stem develops which grows up inside the pseudostem, carrying the immature inflorescence until eventually it emerges at the top. Each pseudostem normally produces a single inflorescence, also known as the "banana heart". After fruiting, the pseudostem dies, but offshoots will normally have developed from the base, so that the plant as a whole is perennial. The inflorescence contains many petal-like bracts between rows of flowers. The female flowers (which can develop into fruit) appear in rows further up the stem (closer to the leaves) from the rows of male flowers. The ovary is inferior, meaning that the tiny petals and other flower parts appear at the tip of the ovary.
The banana fruits develop from the banana heart, in a large hanging cluster called a bunch, made up of around nine tiers called hands, with up to 20 fruits to a hand. A bunch can weigh 22–65 kilograms. The stalk ends of the fruits connect up to the rachis part of the inflorescence. Opposite the stalk end, is the blossom end, where the remnants of the flower deviate the texture from the rest of the flesh inside the peel.
The fruit has been described as a "leathery berry". There is a protective outer layer (a peel or skin) with numerous long, thin strings (vascular bundles), which run lengthwise between the skin and the edible inner white flesh. The peel is less palatable and usually discarded after peeling the fruit, optimally done from the blossom end, but often started from the stalk end. The inner part of the common yellow dessert variety can be split lengthwise into three sections that correspond to the inner portions of the three carpels by manually deforming the unopened fruit. In cultivated varieties, fertile seeds are usually absent.
A 2011 phylogenomic analysis using nuclear genes indicates the phylogeny of some representatives of the Musaceae family. Major edible kinds of banana are shown in boldface.
The genus Musa was created by Carl Linnaeus in 1753. The name may be derived from Antonius Musa, physician to the Emperor Augustus, or Linnaeus may have adapted the Arabic word for banana, mauz. The ultimate origin of musa may be in the Trans–New Guinea languages, which have words similar to "#muku"; from there the name was borrowed into the Austronesian languages and across Asia, accompanying the cultivation of the banana as it was brought to new areas, via the Dravidian languages of India, into Arabic as a Wanderwort. The word "banana" is thought to be of West African origin, possibly from the Wolof word banaana, and passed into English via Spanish or Portuguese.
Musa is the type genus in the family Musaceae. The APG III system assigns Musaceae to the order Zingiberales, part of the commelinid clade of the monocotyledonous flowering plants. Some 70 species of Musa were recognized by the World Checklist of Selected Plant Families as of January 2013; several produce edible fruit, while others are cultivated as ornamentals.
The classification of cultivated bananas has long been a problematic issue for taxonomists. Linnaeus originally placed bananas into two species based only on their uses as food: Musa sapientum for dessert bananas and Musa paradisiaca for plantains. More species names were added, but this approach proved to be inadequate for the number of cultivars in the primary center of diversity of the genus, Southeast Asia. Many of these cultivars were given names that were later discovered to be synonyms.
In a series of papers published from 1947 onward, Ernest Cheesman showed that Linnaeus's Musa sapientum and Musa paradisiaca were cultivars and descendants of two wild seed-producing species, Musa acuminata and Musa balbisiana, both first described by Luigi Aloysius Colla. Cheesman recommended the abolition of Linnaeus's species in favor of reclassifying bananas according to three morphologically distinct groups of cultivars – those primarily exhibiting the botanical characteristics of Musa balbisiana, those primarily exhibiting the botanical characteristics of Musa acuminata, and those with characteristics of both. Researchers Norman Simmonds and Ken Shepherd proposed a genome-based nomenclature system in 1955. This system eliminated almost all the difficulties and inconsistencies of the earlier classification of bananas based on assigning scientific names to cultivated varieties. Despite this, the original names are still recognized by some authorities, leading to confusion.
The accepted scientific names for most groups of cultivated bananas are Musa acuminata Colla and Musa balbisiana Colla for the ancestral species, and Musa × paradisiaca L. for the hybrid of the two.
An unusual feature of the genetics of the banana is that chloroplast DNA is inherited maternally, while mitochondrial DNA is inherited paternally. This facilitates taxonomic study of species and subspecies relationships.
In regions such as North America and Europe, Musa fruits offered for sale can be divided into small sweet "bananas" eaten raw when ripe as a dessert, and large starchy "plantains" or cooking bananas, which do not have to be ripe. Linnaeus made this distinction when naming two "species" of Musa. Members of the "plantain subgroup" of banana cultivars, most important as food in West Africa and Latin America, correspond to this description, having long pointed fruit. They are described by Ploetz et al. as "true" plantains, distinct from other cooking bananas.
The cooking bananas of East Africa belong to a different group, the East African Highland bananas. Further, small farmers in Colombia grow a much wider range of cultivars than large commercial plantations do, and in Southeast Asia—the center of diversity for bananas, both wild and cultivated—the distinction between "bananas" and "plantains" does not work. Many bananas are used both raw and cooked. There are starchy cooking bananas which are smaller than those eaten raw. The range of colors, sizes and shapes is far wider than in those grown or sold in Africa, Europe or the Americas. Southeast Asian languages do not make the distinction between "bananas" and "plantains" that is made in English. Thus both Cavendish dessert bananas and Saba cooking bananas are called pisang in Malaysia and Indonesia, kluai in Thailand and chuối in Vietnam. Fe'i bananas, grown and eaten in the islands of the Pacific, are derived from a different wild species. Most Fe'i bananas are cooked, but Karat bananas, which are short and squat with bright red skins, are eaten raw.
The earliest domestication of bananas (Musa spp.) was from naturally occurring parthenocarpic (seedless) individuals of Musa banksii in New Guinea. These were cultivated by Papuans before the arrival of Austronesian-speakers. Numerous phytoliths of bananas have been recovered from the Kuk Swamp archaeological site and dated to around 10,000 to 6,500 BP. Foraging humans in this area began domestication in the late Pleistocene using transplantation and early cultivation methods. By the early to middle of the Holocene the process was complete. From New Guinea, cultivated bananas spread westward into Island Southeast Asia. They hybridized with other (possibly independently domesticated) subspecies of Musa acuminata as well as M. balbisiana in the Philippines, northern New Guinea, and possibly Halmahera. These hybridization events produced the triploid cultivars of bananas commonly grown today. The banana was one of the key crops that enabled farming to begin in Papua New Guinea.
From Island Southeast Asia, bananas became part of the staple domesticated crops of Austronesian peoples.
These ancient introductions resulted in the banana subgroup now known as the true plantains, which include the East African Highland bananas and the Pacific plantains (the Iholena and Maoli-Popo'ulu subgroups). East African Highland bananas originated from banana populations introduced to Madagascar probably from the region between Java, Borneo, and New Guinea; while Pacific plantains were introduced to the Pacific Islands from either eastern New Guinea or the Bismarck Archipelago.
21st century discoveries of phytoliths in Cameroon dating to the first millennium BCE triggered a debate about the date of first cultivation in Africa. There is linguistic evidence that bananas were known in East Africa or Madagascar around that time. The earliest prior evidence indicates that cultivation dates to no earlier than the late 6th century AD. Malagasy people colonized Madagascar from South East Asia around 600 AD onwards. Glucanase and two other proteins specific to bananas were found in dental calculus from the early Iron Age (12th century BCE) Philistines in Tel Erani in the southern Levant.
Another wave of introductions later spread bananas to other parts of tropical Asia, particularly Indochina and the Indian subcontinent. Some evidence suggests bananas were known to the Indus Valley civilisation from phytoliths recovered from the Kot Diji archaeological site in Pakistan. Southeast Asia remains the region of primary diversity of the banana. Areas of secondary diversity are found in Africa, indicating a long history of banana cultivation there.
The banana may have been present in isolated locations elsewhere in the Middle East on the eve of Islam. The spread of Islam was followed by far-reaching diffusion. There are numerous references to it in Islamic texts (such as poems and hadiths) beginning in the 9th century. By the 10th century, the banana appeared in texts from Palestine and Egypt. From there it diffused into North Africa and Muslim Iberia during the Arab Agricultural Revolution. An article on banana tree cultivation is included in Ibn al-'Awwam's 12th-century agricultural work, Kitāb al-Filāḥa (Book on Agriculture). During the Middle Ages, bananas from Granada were considered among the best in the Arab world. Bananas were certainly grown in the Christian Kingdom of Cyprus by the late medieval period. Writing in 1458, the Italian traveller and writer Gabriele Capodilista wrote favourably of the extensive farm produce of the estates at Episkopi, near modern-day Limassol, including the region's banana plantations.
In the 15th and 16th centuries, Portuguese colonists started banana plantations in the Atlantic Islands, Brazil, and western Africa. North Americans began consuming bananas on a small scale at very high prices shortly after the Civil War, though it was only in the 1880s that the food became more widespread. As late as the Victorian Era, bananas were not widely known in Europe, although they were available.
The earliest modern plantations originated in Jamaica and the related Western Caribbean Zone, including most of Central America. Plantation cultivation involved the combination of modern transportation networks of steamships and railroads with the development of refrigeration that allowed more time between harvesting and ripening. North American shippers like Lorenzo Dow Baker and Andrew Preston, the founders of the Boston Fruit Company started this process in the 1870s, with the participation of railroad builders like Minor C. Keith. Development led to the multi-national giant corporations like Chiquita and Dole. These companies were monopolistic, vertically integrated (controlling growing, processing, shipping and marketing) and usually used political manipulation to build enclave economies (internally self-sufficient, virtually tax exempt, and export-oriented, contributing little to the host economy). Their political maneuvers, which gave rise to the term banana republic for states such as Honduras and Guatemala, included working with local elites and their rivalries to influence politics or playing the international interests of the United States, especially during the Cold War, to keep the political climate favorable to their interests.
The vast majority of the world's bananas are cultivated for family consumption or for sale on local markets. They are grown in large quantities in India, while many other Asian and African countries host numerous small-scale banana growers who sell at least some of their crop. Peasants with smallholdings of 1 to 2 acres in the Caribbean produce bananas for the world market, often alongside other crops. In many tropical countries, the main cultivars produce green (unripe) bananas used for cooking. Because bananas and plantains produce fruit year-round, they provide a valuable food source during the hunger season between harvests of other crops, and are thus important for global food security.
Bananas are propagated asexually from offshoots. The plant is allowed to produce two shoots at a time; a larger one for immediate fruiting and a smaller "sucker" or "follower" to produce fruit in 6–8 months. As a non-seasonal crop, bananas are available fresh year-round. They are grown in some 135 countries.
Cultivars in the Cavendish group dominate the world market. In global commerce in 2009, by far the most important cultivars belonged to the triploid Musa acuminata AAA group of Cavendish group bananas. Disease is threatening the production of the Cavendish banana worldwide. It is unclear if any existing cultivar can replace Cavendish bananas, so various hybridisation and genetic engineering programs are attempting to create a disease-resistant, mass-market banana. One such strain that has emerged is the Taiwanese Cavendish or Formosana.
Export bananas are picked green, and ripened in special rooms upon arrival in the destination country. These rooms are air-tight and filled with ethylene gas to induce ripening. This mimics the normal production of this gas as a ripening hormone. Ethylene stimulates the formation of amylase, an enzyme that breaks down starch into sugar, influencing the taste. Ethylene signals the production of pectinase, a different enzyme which breaks down the pectin between the cells of the banana, causing the banana to soften as it ripens. The vivid yellow color many consumers in temperate climates associate with bananas is caused by ripening around 18 °C, and does not occur in Cavendish bananas ripened in tropical temperatures (over 27 °C), which leaves them green.
Bananas are transported over long distances from the tropics to world markets. To obtain maximum shelf life, harvest comes before the fruit is mature. The fruit requires careful handling, rapid transport to ports, cooling, and refrigerated shipping. The goal is to prevent the bananas from producing their natural ripening agent, ethylene. This technology allows storage and transport for 3–4 weeks at 13 °C. On arrival, bananas are held at about 17 °C and treated with a low concentration of ethylene. After a few days, the fruit begins to ripen and is distributed for final sale. Ripe bananas can be held for a few days at home. If bananas are too green, they can be put in a brown paper bag with an apple or tomato overnight to speed up the ripening process.
The excessive use of fertilizers contributes greatly to eutrophication in streams and lakes, harming aquatic life, while expanding banana production has led to deforestation. As soil nutrients are depleted, more forest is cleared for plantations. This causes soil erosion and increases the frequency of flooding.
Voluntary sustainability standards such as Rainforest Alliance and Fairtrade are being used to address some of these issues. Banana production certified in this way grew rapidly at the start of the 21st century to represent 36% of banana exports by 2016. However, such standards are applied mainly in countries which focus on the export market, such as Colombia, Costa Rica, Ecuador, and Guatemala; worldwide they cover only 8–10% of production.
Mutation breeding can be used in this crop. Aneuploidy is a source of significant variation in allotriploid varieties. For one example, it can be a source of TR4 resistance. Lab protocols have been devised to screen for such aberrations and for possible resulting disease resistances. Wild Musa spp. provide useful resistance genetics, and are vital to breeding for TR4 resistance
    """

    st = input("Select search mode (token / pos / entity, default is token): ").strip().lower()
    search_type = st if st in {'token', 'pos', 'entity'} else 'token'

    if search_type == 'pos':
        print("Available POS tags: NOUN, VERB, ADJ, ADV, PROPN, DET, ADP, AUX")
    elif search_type == 'entity':
        print("Available entity labels: PERSON, ORG, GPE, DATE, MONEY, TIME")

    target = input(f"Enter target for {search_type} search: ")

    w_in = input("Enter window size (number of words left/right, default is 5): ").strip()
    window = int(w_in) if w_in.isdigit() and int(w_in) > 0 else 5

    color_in = input("Enter highlight color (grey, red, green, yellow, blue, magenta, cyan, white; default is cyan): ").strip().lower()
    colors = {'grey', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white'}
    color = color_in if color_in in colors else 'cyan'

    attrs_in = input("Enter attributes (comma-separated: bold, underline, blink, reverse, concealed; default is bold): ").strip().lower()
    valid_attrs = {'bold', 'underline', 'blink', 'reverse', 'concealed'}
    if attrs_in:
        attrs = [a.strip() for a in attrs_in.split(',') if a.strip() in valid_attrs]
        attrs = attrs or ['bold']
    else:
        attrs = ['bold']

    sort_mode = input("Select display mode (sequential / token_freq / pos_freq, default is sequential): ").strip().lower()
    sort_mode = sort_mode if sort_mode in {'sequential', 'token_freq', 'pos_freq'} else 'sequential'

    print(f"\n=== KWIC (mode={search_type}, window={window}, color={color}, attrs={attrs}, sort={sort_mode}) ===\n")
    kwic(text, target, window=window, search_type=search_type, color=color, attrs=attrs, sort_mode=sort_mode)
