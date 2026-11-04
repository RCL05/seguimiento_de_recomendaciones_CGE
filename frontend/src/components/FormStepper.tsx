type FormStep = {
  label: string;
  description: string;
};

type FormStepperProps = {
  steps: FormStep[];
  currentStep: number;
};

export function FormStepper({ steps, currentStep }: FormStepperProps) {
  return (
    <ol className="form-stepper" aria-label="Progreso del formulario">
      {steps.map((step, index) => {
        const stepNumber = index + 1;
        const status =
          stepNumber < currentStep ? "complete" : stepNumber === currentStep ? "current" : "upcoming";

        return (
          <li key={step.label} className={`form-step ${status}`}>
            <span className="step-number" aria-hidden="true">
              {stepNumber}
            </span>
            <span>
              <strong>{`Paso ${stepNumber}: ${step.label}`}</strong>
              <small>{step.description}</small>
            </span>
          </li>
        );
      })}
    </ol>
  );
}
