from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
)
from botbuilder.dialogs.prompts import (
    TextPrompt,
    NumberPrompt,
    ChoicePrompt,
    ConfirmPrompt,
    AttachmentPrompt,
    PromptOptions,
    PromptValidatorContext,
)
from botbuilder.dialogs.choices import Choice
from botbuilder.core import MessageFactory, UserState

from weather.data_models import PatientDemographics
from weather.infermedica import InfermedicaApi

class TriageDialog(ComponentDialog):
    def __init__(self, user_state: UserState):
        super(TriageDialog, self).__init__(TriageDialog.__name__)

        self.patient_demographics_accessor = user_state.create_property("PatientDemographics")

        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.patient_route_step,
                    self.patient_age_step,
                    self.patient_gender_step,
                    self.initial_symptom_step,
                    self.more_symptoms_step,
                    self.risk_factors_step,
                    """self.related_symptoms_step,
                    self.red_flags_step,
                    self.interview_step,
                    self.summary_step,
                    self.call_to_action_step, """
                ] 
            )
        )

        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(
                NumberPrompt(NumberPrompt.__name__, TriageDialog.age_prompt_validator)
            )
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.initial_dialog_id = WaterfallDialog.__name__

    async def patient_route_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        return await step_context.prompt(
            ChoicePrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text("Please select what you would like to do today."),
                choices=[Choice("Book Appointment"), Choice("Check Symptoms")],
            )
        )

    async def patient_age_step(self, step_context:WaterfallStepContext) -> DialogTurnResult:
        if step_context.result.value == "Check Symptoms":
            return await step_context.prompt(
                NumberPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("Please enter your age "),
                    retry_prompt=MessageFactory.text("The value must be greater than 0 and less than 120."
                    ),
                ),
            )
        else:
             return await step_context.prompt(
                NumberPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("Book appointment ")
                ),
            )

    async def patient_gender_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        age = step_context.result
        step_context.values["age"] = age
        msg = (
                "No age given."
                if step_context.result == -1
                else f"Got it!  You are {age} years old."
            )

        await step_context.context.send_activity(MessageFactory.text(msg))
        return await step_context.prompt(
            ChoicePrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text("Please select your gender assigned at birth."),
                choices=[Choice("Female"), Choice("Male")],
            )
        )

    async def initial_symptom_step(
        self, step_context: WaterfallStepContext
     ) -> DialogTurnResult:
        gender = step_context.result.value
        step_context.values["gender"] = gender
        msg = (
                "No age given."
                if step_context.result == -1
                else f"OK.  We will use {gender} for the interview."
            )

        await step_context.context.send_activity(MessageFactory.text(msg))
        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text("Please enter the symptoms that are bothering you the most, for example, 'I have a sore through and a cough'."),
            )
        )

    async def more_symptoms_step(
        self, step_context: WaterfallStepContext

    ) -> DialogTurnResult:
        utterance = step_context.result
        step_context.values["initial_symptoms"] = utterance

        age =  int(step_context.values["age"])
        gender =  step_context.values["gender"]

        result = await InfermedicaApi.parse(age, gender, utterance)
        symptom = result["mentions"][0]["common_name"]

        msg = (
                 f"OK.  I understood {symptom}. Is there anything else bothering you?"
            )

        await step_context.context.send_activity(MessageFactory.text(msg))
        return await step_context.prompt(
            ChoicePrompt.__name__,
           PromptOptions(
                prompt=MessageFactory.text("Is there anything else bothering you?"),
                choices=[Choice("Yes"), Choice("No")],
            )
        )

    async def risk_factors_step(
        self, step_context: WaterfallStepContext

    ) -> DialogTurnResult:
        age =  step_context.values["age"]
        gender =  step_context.values["gender"]
        result = await InfermedicaApi.get_risk_factors(age, gender)
       
        await step_context.context.send_activity(MessageFactory.text(result))
        return await step_context.prompt(
            ChoicePrompt.__name__,
           PromptOptions(
                prompt=MessageFactory.text("Is there anything else bothering you?"),
                choices=[Choice("Female"), Choice("Male")],
            )
        )


    @staticmethod
    async def age_prompt_validator(prompt_context: PromptValidatorContext) -> bool:
        return (
            prompt_context.recognized.succeeded
            and 0 < prompt_context.recognized.value < 120
        ) 