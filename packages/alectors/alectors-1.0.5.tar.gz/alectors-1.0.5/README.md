
# alectors

*alectors* is a library providing transformer-based rl agents for nlp tasks, that is extremely customizable, but also comes with sane defaults.

>source code: [erga.apotheke.earth/aethrvmn/alectors](https://erga.apotheke.earth/aethrvmn/alectors)

> license: [Source First License 1.1](/license)  
> [learn more about sourcefirst here](https://sourcefirst.com)

## Why "alectors"?

The word lector has deep roots in language and learning. Derived from the Latin *legere* ("to read"), it originally referred to someone who reads aloud—whether to an audience, to students, or in religious ceremonies. Throughout history, lectors played a vital role as intermediaries between text and audience. In medieval times, a lector was a scholar who interpreted sacred or philosophical texts. In cigar factories of the 19th century, lectors read newspapers and novels aloud to entertain workers, bridging knowledge and communication. Even today, in languages like Greek (λέκτορας), English (lecturer), French (lecteur), and Polish (lektor), the term retains its connection to reading and narration.

In many ways, an NLP agent is a modern lector; processing, interpreting, and generating language to make text more accessible, structured, and meaningful. Just as historical lectors gave voice to the written word, these agents bring understanding and coherence to natural language.

However, adding the prefix a- changes the word's meaning entirely. *alector* (*ἀλέκτωρ*) means "cock" (rooster) in Greek. I find the juxtaposition funny, hence the name.

## Reasoning

Modern NLP solutions like GPTs and BERTs have made great strides in language processing and generation, however they come with serious limitations. As an example, even though a large language model can describe or make a game of chess, and even justify moves made, it is unable to play it, since there is no underlying mechanism for decision-making or reward incentives during training. Transformers rely on static token distributions without real-time feedback, limiting their capacity to actively learn.

*alectors* tries to address this gap by shifting the focus to active learning through reinforcement. An *alector* doesn’t just passively learn to generate language; it learns through interaction.

## Supported Architectures

The currently supported architecture is PPO.  Plans exist to include SAC, GRPO, and maybe DDQN.
