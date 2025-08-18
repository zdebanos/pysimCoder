enum pysim_model_state
{
    NOT_RUNNING,
    INIT,
    RUNNING,
    END
};

struct pysim_model
{
  const char *name;
  enum pysim_model_state state;
  double sampling_period;
};

/* Definitions of routines below must be provided by the respective platform */

/**
 * @brief Get model's runtime in seconds
 *
 * @return double
 */
double pysim_model_runtime(struct pysim_model *m);

/**
 * @brief Get the priority for the communication task
 * 
 * @return int 
 */
int pysim_model_compriority(struct pysim_model *m);

/**
 * @brief Pause the model's execution and deinits the model
 * 
 */
void pysim_model_pausectrl(struct pysim_model *m);

/**
 * @brief Resume the model's execution: inits the model again
 * 
 */
void pysim_model_resumectrl(struct pysim_model *m);
