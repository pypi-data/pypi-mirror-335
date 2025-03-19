"""Text classifiers for drug and stigma detection."""

import time
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class BaseClassifier(ABC):
    """Abstract base class for text classifiers."""
    
    def __init__(self, client: Any):
        """Initialize classifier with an LLM client.
        
        Args:
            client: LLM client instance
        """
        self.client = client
        self.retry_wait_time = 5  # seconds between retries
        
    @abstractmethod
    def classify(self, text: str, model: Optional[str] = None, retries: int = 2) -> str:
        """Classify the provided text.
        
        Args:
            text: Text to classify
            model: Model to use for classification
            retries: Number of retries on failure
            
        Returns:
            str: Classification result
        """
        pass


class DrugClassifier(BaseClassifier):
    """Classifier for drug-related content."""
    
    def classify(self, text: str, model: Optional[str] = None, retries: int = 2) -> str:
        """Classify if text contains drug-related content.
        
        Args:
            text: Text to classify
            model: Model to use
            retries: Number of retries on failure
            
        Returns:
            str: 'D' for drug-related, 'ND' for non-drug-related, 'skipped' on error
        """
        prompt = """
        *Instructions for Labeling Drug References in Social Media Posts*

        1. **Objective**: Identify references to drugs or people who use drugs in each post.

        2. **Include**:
        - Illicit Drugs: All controlled substances with no legal usage (e.g. cannabis, heroin, cocaine, methamphetamine)
        - Prescription Drugs: drugs that are often abused even if they have legitimate medical uses (e.g., opioids, benzodiazepines).
        - Other Drugs: drugs that are non-prescription and known to be abused (e.g., inhalants, k2, bath salts).
        - Explicit mentions of drug use, abuse, or addiction related terms (e.g., "getting high", "stoned").

        3. **Exclude**:
        - Tobacco, nicotine, or alcohol unless explicitly linked to drug use.
        - Do not include medical or psychological discussions unless there is a direct and clear mention of drug use or abuse.

        4. **Clarifications**:
        - Mental health discussions should not be labeled as 'D' unless there is an explicit mention of drugs as defined above.
        - Use 'ND' for posts that discuss health or psychological issues without specific drug references.

        5. **Language Cues**:
        - Focus on clear drug-related terminology (e.g., "junkie", "addict") and slang.
        - If a post is ambiguous and does not clearly fit the drug reference criteria, label as 'ND'.

        6. **Response Requirement**:
        - Respond with either 'D' (Drug) or 'ND' (Non-Drug) based on these guidelines. No additional commentary is needed.
        """

        # Examples for few-shot learning
        examples = [
            ("I'm so high right now, I can't even feel my face. This is the best weed I've ever smoked.", "D"),
            ("I hope my junkie sister OD's or disappears out of our lives My sister is an alcoholic junkie who has 2 DUIs under her belt as well as loves taking Xanax and alcohol together and wreaking havoc for our family and even strangers.", "D"),
            ("My mom is going to kick me out. She graciously gave me the choice of getting dropped off in a shelter in either San Diego or the desert area (Palm Springs and surrounding areas). I would choose the desert because that is one of my old stomping grounds. The dope is phenomenal and cheap (3g's for $100) and the homeless population is a majority young people. I can also hustle up $350 and rent a room at a buddy's place. I have a few options that I can look at but I have to figure it out soon.", "D"),
            ("I cut tonight I cut myself tonight after I've been clean for a few months now and I'm honestly just broken inside. I had a huge fight with my girlfriend, I'm worried we might break up. I just kinda lost control, grabbed my razorblade and cut. I feel like crap and am honestly just lost right now.", "ND"),
            ("My drinking problem is way worse than anyone knows. I'm an alcoholic and the people around me know that, because I told them. But if I hadn't, they wouldn't have guessed, judging by their reactions of shock and disbelief and the actual ‚are you sure you're not exaggerating, that I got when I came clean a couple years ago.", "ND"),
            ("My mother died two years ago from cancer of basically all of her internal organs starting in the colon and then liver and spleen and just everywhere. I hadn't seen her in years because she struggled with drug addiction since I was about four or five. We had years together but not enough. I was there the day she died and I wouldn't wish anyone to go through what she did or what our family did when we saw her in that state. My father also had an addiction to pain pills and alcohol. My last few years of high school were ruined because of that. I watched him overdoes on thanksgiving. I watched him try to kill himself with his own hand gun more than once. I watched him aim it at my stepmom when she tried to take it from him. I heard him yell at me while he kicked me and told me that he didn't want me anymore and tried to drag me up the stairs. Maybe these are some of the reasons I drink. Maybe because I barely have a relationship with my dad now and he still hasn't said anything to me today.", "D"),
            ("Hate my new job I just got hired at Taco Bell a few weeks ago and I really hate it. The only thing that's gets me through it is smoking weed. I wonder if i should just quit or no call no show?", "D"),
            ("I'm trying not to get emotionally invested again in you because I know all to well how you are. You're an alcoholic and I know there is nothing I can do to save you. It kills me to see you drink like you do but I know how it is, you have to want to stop. As much as I love fucking you and being around you, It's not a good idea to continue being around you. ", "ND"),
            ("Recently I took a psychological exam for work. To know if I'm fit to work.The doctor looked at my paper and asked 'Do your have urges to hurt/killpeople?' I laughed in my head and lied..", "ND"),
        ]

        # Build messages for few-shot learning
        messages = [{"role": "system", "content": prompt}]
        for example, answer in examples:
            messages.append({"role": "user", "content": example})
            messages.append({"role": "system", "content": answer})
        
        messages.append({"role": "user", "content": text})

        while retries > 0:
            try:
                result = self.client.create_completion(
                    messages=messages,
                    model=model
                )
                return result.lower().strip()
            except Exception as e:
                print(f"An error occurred: {e}. Retrying...")
                retries -= 1
                time.sleep(self.retry_wait_time)

        return "skipped"


class StigmaClassifier(BaseClassifier):
    """Classifier for stigmatizing language related to drug use."""
    
    def classify(self, text: str, model: Optional[str] = None, retries: int = 2) -> str:
        """Classify if text contains stigmatizing language.
        
        Args:
            text: Text to classify
            model: Model to use
            retries: Number of retries on failure
            
        Returns:
            str: Classification result with explanation if stigmatizing
        """
        prompt = """
        **Instructions:**
        You are an expert in identifying stigma related to drug use and addiction in social media posts. Your task is to analyze each post and determine if it contains stigmatizing language. 

        1. **Label:**
            * If the post contains stigmatizing language, label it as **"S" (Stigma)**.
            * If the post does not contain stigmatizing language, label it as **"NS" (Non-Stigma)**.

        2. **Explanation:**
            * **For "S" (Stigma) labels:**
                * If the post demonstrates **stigmatizing language (directed at others)**, analyze it based on the following four attributes and provide an explanation for each attribute:
                    * **Labeling:** Does the post use derogatory or othering language related to drug use/addiction?
                    * **Stereotyping:** Does the post reinforce negative generalizations about people who use drugs?
                    * **Separation:** Does the post create a divide between people who use drugs and those who don't?
                    * **Discrimination:** Does the post imply or suggest unfair treatment based on drug use?
                * If the post demonstrates **self-stigma or structural stigma**, provide a brief, one-sentence explanation of the type of stigma present.

            * **For "NS" (Non-Stigma) labels:** No explanation is needed.

        **Definitions:**

        * **Stigma:** Negative attitudes or beliefs directed at individuals based on their drug use.
        * **Self-Stigma:** Internalization of negative societal attitudes about drug use.
        * **Structural Stigma:** Societal systems, policies, or practices that disadvantage people who use drugs.

        **Additional Considerations:**

        * Consider the context of the post and the author's intent.
        * Focus on language that is harmful, discriminatory, or perpetuates negative stereotypes.

        **Task:**
        Read the following post, label it as "S" or "NS", and provide the appropriate explanation:
        """
        
        # Examples for few-shot learning
        examples = [
            ("Once an addict, always an addict. They'll never change.", "S, Labeling: 'addict', Stereotyping: Assumes that people with addiction are incapable of recovery or personal growth, Separation: Creates a sense of hopelessness and perpetuates the idea that people with addiction are fundamentally different, Discrimination: Discourages offering support or opportunities to individuals in recovery due to a belief they'll relapse."),
            ("He's just a junkie looking for his next fix.", "S, Labeling: 'junkie', a derogatory term, Stereotyping: Reduces the person's identity to their substance use, ignoring other aspects of their life, Separation: Creates a distance between 'us' (non-users) and 'them' (people who use substances), Discrimination: Implies the person is solely motivated by drug use and lacks other values or goals."),
            ("She's constantly nodding off at work. Probably using again.", "S, Labeling: Implies the person has a substance use disorder by suggesting they are 'using again,' Stereotyping: Generalizes that the person's behavior (nodding off) is solely due to drug use, Separation: Creates a distinction between the person and their colleagues, implying they are unreliable or irresponsible due to assumed substance use, Discrimination: Could lead to unfair treatment at work based on an assumption of relapse."),
            ("If you hang out with those druggies, you'll end up like them.", "S, Labeling: 'druggies', Stereotyping: Generalizes that all people who use drugs are bad influences and will lead others to the same behavior, Separation: Creates a clear division between 'us' (those who don't use drugs) and 'them' (those who do), Discrimination: Promotes exclusion and fear of people who use drugs, potentially leading to social isolation."),
            ("My friend is in recovery from opioid use disorder and is doing incredibly well.", "NS"),
            ("Addiction is a complex disease, but with the right support, people can and do recover.", "NS"),
            ("I'm concerned about my brother's substance use. I'm learning about available resources to help him.", "NS"),
            ("I always hide my medication because I feel ashamed of my condition. I'm just an addict, and that's all people will see if they know.", "S, The author internalizes the negative stereotype associated with addiction, labeling themselves pejoratively as 'just an addict.'"),
            ("Our town's only rehab facility refuses to accept people who have been arrested for drug offenses. They say it's a policy to maintain safety, but it just prevents those who need help the most from getting it.", "S, This post describes a systemic policy that discriminates against individuals with drug offenses, reinforcing stereotypes that they are dangerous. The policy creates a separation by denying these individuals access to rehabilitation."),
            ("Crack is a better alternative to coffee All coffee does is make you feel less drowsy. When I smoke a bowl of crack in the morning, shit gets me gooooinn, makes me go absolutely bonkers, crazy ridiculous out of the world bonkers ! I'm getting the jitters just thinkin about it", "NS"),
        ]
        
        # Build messages for few-shot learning
        messages = [{"role": "system", "content": prompt}]
        for example, answer in examples:
            messages.append({"role": "user", "content": example})
            messages.append({"role": "system", "content": answer})
        
        messages.append({"role": "user", "content": text})

        while retries > 0:
            try:
                result = self.client.create_completion(
                    messages=messages,
                    model=model
                )
                return result.lower().strip()
            except Exception as e:
                print(f"An error occurred: {e}. Retrying...")
                retries -= 1
                time.sleep(self.retry_wait_time)
                
        return "skipped"
