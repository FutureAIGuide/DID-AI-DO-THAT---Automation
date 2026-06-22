# Anthropic Frontier Model Shutdown - Research Packet

Prepared: 2026-06-22

## Executive Summary

On June 12, 2026, Anthropic said the U.S. government issued an export-control directive requiring it to suspend access to Claude Fable 5 and Claude Mythos 5 for every foreign national, including foreign-national employees inside the United States. Anthropic disabled both models for all customers because, it said, that was necessary to comply. The directive arrived three days after Anthropic launched the models and ten days after it announced an expansion of Project Glasswing, a government-collaborative effort providing powerful cyber models to critical-infrastructure defenders in more than 15 countries.

The public evidence establishes the shutdown, its timing, Anthropic's description of the order, the models' dual-use capabilities, and the administration's broader frontier-AI policies. It does not establish the full contents of the directive, the issuing agency with documentary certainty, the classified or technical evidence behind it, or whether political conflict with Anthropic influenced the decision.

The strongest investigation is therefore not a claim that the government acted improperly. It is an examination of an opaque and apparently unprecedented intervention whose stated target was foreign-national access but whose practical consequence was worldwide withdrawal of two frontier models. The reporting must test both propositions: that the models posed an exceptional national-security risk and that removing them from vetted defenders may have created a different security risk.

## Core Claim

The U.S. government used undisclosed national-security authority to restrict foreign-national access to Anthropic's newest frontier models. The order's breadth and Anthropic's implementation caused a global shutdown, while the public record remains insufficient to judge whether that response was proportionate to the underlying technical threat.

## Why This Matters

- The action appears to be a novel use of export-control authority against access to a live, commercially deployed AI model.
- The restriction covered nationality rather than only location, including foreign-national workers inside the United States.
- Fable 5 and Mythos 5 were designed for high-value software and cybersecurity work. Mythos 5 offered fewer cyber safeguards only to vetted organizations.
- The same administration had just ordered agencies to expand access to frontier models for cyber defense and accelerate AI adoption in national security.
- The incident may establish a precedent for secret, model-specific restrictions without a public technical standard or review process.
- It exposes a governance gap when a model developer and the government disagree about the severity of a frontier-model risk.

## What Is Verified

1. Anthropic published a statement dated June 12, 2026 saying it had received a U.S. government export-control directive at 5:21 p.m. ET that day.
2. Anthropic said the directive covered access by all foreign nationals, inside or outside the United States, including its own foreign-national employees.
3. Anthropic disabled Fable 5 and Mythos 5 for all customers while leaving other Claude models available.
4. Anthropic launched Fable 5 and Mythos 5 on June 9, 2026.
5. Fable 5 and Mythos 5 were the same underlying model differentiated by safeguards and access.
6. Fable 5 was generally available with classifiers intended to redirect risky cyber, biology, chemistry, and model-distillation requests to Opus 4.8.
7. Mythos 5 was restricted to vetted Project Glasswing partners with some cyber safeguards lifted.
8. Anthropic publicly acknowledged that Mythos-class models presented substantial dual-use risks and could make serious cyberattacks easier.
9. Anthropic said it had not been given specific details of the national-security concern and understood that a narrow jailbreak demonstration was involved.
10. Anthropic disputed the apparent severity of that demonstration, saying the identified vulnerabilities were previously known, minor, and discoverable by other public models.
11. The White House's June 2 executive order called for federal access to covered frontier models for cyber defense, a vulnerability-clearinghouse, classified capability benchmarks, and a voluntary pre-release collaboration framework.
12. NSPM-11, dated June 5, directed rapid frontier-model adoption across national-security work while requiring reliability, availability, and government control over mission systems.
13. Anthropic expanded Project Glasswing on June 2 to approximately 150 additional organizations in more than 15 countries.
14. Cybersecurity executives and researchers published an open letter asking the government to reverse the restriction and create a transparent risk-assessment process.
15. Anthropic and the U.S. defense establishment were already in a public legal dispute over military usage restrictions and a supply-chain-risk designation.

## What Is Unverified

- The complete language of the June 12 directive.
- The issuing official and agency, except as described by media reports and legal analysis.
- The precise statutory subsection used.
- Whether the government possessed evidence beyond the jailbreak report Anthropic reviewed.
- Who produced the jailbreak report and under what testing conditions.
- Whether the technique enabled materially greater cyber harm than public alternatives.
- Whether the shutdown measurably impaired active defensive operations.
- Whether political or military-use disputes influenced the export-control decision.
- Whether Anthropic lacked any technically feasible narrower compliance option.
- Whether the directive was temporary, conditional, or part of a broader planned model-control regime.

## Timeline

- **April 7, 2026:** Anthropic launches Mythos Preview and Project Glasswing, saying the model could identify and exploit sophisticated vulnerabilities.
- **May 2026:** Anthropic reports more than 10,000 high- or critical-severity vulnerabilities found across Project Glasswing work, while warning that most remain unpatched.
- **June 2:** Anthropic announces Glasswing expansion to roughly 150 additional organizations in more than 15 countries.
- **June 2:** The White House signs an AI-security executive order directing federal cyber-defense expansion, frontier-model benchmarking, and voluntary pre-release collaboration.
- **June 5:** The White House issues NSPM-11 to accelerate AI across intelligence and warfighting.
- **June 9:** Anthropic launches Fable 5 generally and Mythos 5 for vetted partners.
- **June 12, 5:21 p.m. ET:** Anthropic says it receives the export-control directive.
- **June 12:** Anthropic announces global suspension of both models.
- **June 14:** Cybersecurity leaders publish an open letter seeking reversal and transparent technical review.
- **June 15:** Former national-security lawyer Brian Egan publishes an analysis identifying the Export Control Reform Act as a likely authority while emphasizing that the directive is not public.
- **June 16:** Reporting documents wider cybersecurity-industry opposition and government negotiations.
- **June 22:** Reporting on an allied cyber warning reinforces the larger concern about frontier-model offense and defense.

## Key Players

### Organizations

- Anthropic PBC
- U.S. Department of Commerce and Bureau of Industry and Security, as the reported and legally inferred export-control authorities
- White House
- Department of War
- National Security Agency
- Cybersecurity and Infrastructure Security Agency
- Office of the National Cyber Director
- Project Glasswing partners
- UK AI Security Institute

### Individuals

- Dario Amodei, Anthropic CEO
- Howard Lutnick, Secretary of Commerce, identified in reporting and the open letter
- Alex Stamos and other cybersecurity signatories opposing the restriction
- Brian Egan, former National Security Council and State Department legal adviser

## Primary Sources

1. [Anthropic: Statement on the U.S. government directive](https://www.anthropic.com/news/fable-mythos-access)
2. [Anthropic: Claude Fable 5 and Claude Mythos 5 launch](https://www.anthropic.com/news/claude-fable-5-mythos-5)
3. [Anthropic: Fable 5 and Mythos 5 system card](https://www-cdn.anthropic.com/d00db56fa754a1b115b6dd7cb2e3c342ee809620.pdf)
4. [Anthropic: Expanding Project Glasswing](https://www.anthropic.com/news/expanding-project-glasswing)
5. [Anthropic: Project Glasswing initial update](https://www.anthropic.com/research/glasswing-initial-update)
6. [Anthropic: Technical assessment of Mythos Preview](https://red.anthropic.com/2026/mythos-preview/)
7. [White House: AI innovation and security executive order](https://www.whitehouse.gov/presidential-actions/2026/06/promoting-advanced-artificial-intelligence-innovation-and-security/)
8. [White House: NSPM-11](https://www.whitehouse.gov/presidential-actions/2026/06/national-security-presidential-memorandum-nspm-11/)
9. [Open letter on transparent AI cyber protections](https://freefable.org/)
10. [Anthropic: Where things stand with the Department of War](https://www.anthropic.com/news/where-stand-department-war)
11. [Federal docket: Anthropic PBC v. U.S. Department of War](https://www.courtlistener.com/docket/72379655/anthropic-pbc-v-us-department-of-war/)

## Secondary Sources

1. [Just Security: Legal considerations related to the directive](https://www.justsecurity.org/142745/law-anthropic-export-controls/)
2. [The Verge: Inside the fight over Claude Mythos 5](https://www.theverge.com/ai-artificial-intelligence/950412/anthropic-trump-adminstration-claude-mythos-fable-5-export-controls)
3. [Axios: Anthropic crackdown rattles cyber defenders](https://www.axios.com/2026/06/16/anthropic-fable-trump-white-house-cybersecurity)
4. [TechCrunch: Cybersecurity veterans protest the restriction](https://techcrunch.com/2026/06/15/cybersecurity-vets-protest-dangerous-us-government-ban-on-anthropics-most-powerful-models/)
5. [Fortune: Anthropic disables the models](https://fortune.com/2026/06/13/anthropic-disables-fable-mythos-export-controls-national-security-threat/)
6. [Guardian: Frontier AI cyber warning](https://www.theguardian.com/technology/2026/jun/22/anthropic-claude-fable-ai-model-artificial-intelligence-national-security)

## Supporting Evidence

- Anthropic's June 12 account is specific about timing and practical effect.
- The launch documentation independently establishes that the models existed, were released, and had unusually strong cyber capability.
- Project Glasswing documentation establishes international distribution to vetted defenders before the shutdown.
- The White House orders establish a simultaneous policy preference for rapid frontier-model cyber-defense use.
- Independent legal analysis identifies a plausible legal mechanism but calls the directive's breadth unprecedented.
- The open letter demonstrates organized opposition from identifiable cybersecurity professionals.

## Contradicting Evidence And Alternative Explanations

- Anthropic itself described Mythos-class capabilities as capable of serious harm and said no developer had perfect safeguards. That supports government caution.
- Anthropic said UK AISI testing had made progress toward a universal jailbreak, although none had been completed at launch.
- The government may possess classified evidence that cannot be released without exposing intelligence sources or exploit methods.
- A model need not outperform all alternatives to create unacceptable marginal risk when used at scale.
- Anthropic's global shutdown was its compliance decision; the public record does not prove the directive explicitly ordered universal withdrawal.
- Broad access to defensive capability can also broaden offensive access, especially when nationality and organizational identity are difficult to verify.

## Risks

- Defamation or false-light risk from presenting political retaliation as fact.
- National-security risk from publishing exploit details.
- Circular sourcing because much reporting traces back to Anthropic's statement.
- Overreliance on company benchmarks and unverified vulnerability counts.
- False equivalence between Fable's guarded public version and Mythos's trusted-access version.
- Conflating export controls, procurement sanctions, and military AI usage disputes.
- Treating a lack of public evidence as proof that no evidence exists.

## Open Questions

1. Can the directive or a redacted version be obtained?
2. Which official signed it?
3. Which ECRA authority or regulation was invoked?
4. Was Anthropic offered a license, mitigation plan, or compliance period?
5. Why did the order cover foreign nationals in allied countries and inside the United States?
6. Could identity verification, geofencing, customer vetting, or isolated deployment have provided narrower compliance?
7. Did the government test competing models under the same standard?
8. What operational work did Glasswing partners lose?
9. What evidence would justify restoration?
10. Will the government publish a generally applicable frontier-model threshold?

## Investigation Opportunities

- Compare the directive with traditional BIS "is-informed" letters.
- Map the conflict between voluntary frontier-model cooperation and secret compulsory intervention.
- Interview affected allied cyber defenders and foreign-national Anthropic staff.
- Examine how nationality-based controls work in cloud services.
- Compare Anthropic's safeguard claims with independent red-team evidence.

## Documentary Angles

- A three-day model life cycle: launch, government alarm, shutdown.
- The hidden letter that changed global AI access.
- The race between finding vulnerabilities and patching them.
- A company-government feud moving from military contracts into export controls.

## Viral And Short-Video Angles

- "The U.S. banned an AI model for foreign nationals, so it vanished for everyone."
- "The model existed publicly for three days."
- "The government wants frontier AI for cyber defense while restricting the same capability."
- "What is a jailbreak, and why can a narrow bypass trigger a global shutdown?"

## Newsletter Angles

- The precedent hiding inside one secret directive.
- Why nationality is difficult to enforce in a global cloud product.
- The unsolved problem of independent frontier-AI risk assessment.

## Follow-Up Stories

1. The legal architecture for controlling access to frontier models.
2. What Project Glasswing partners found and fixed.
3. The Anthropic-Pentagon dispute and commercial AI independence.
4. Whether allied cyber defenders can depend on U.S. frontier models.
5. How governments should disclose risk without publishing exploit instructions.
