
### Function Naming Convention

#### `gfun_{dashboard_class}_{resource_type}_main`

- **Purpose**: This function serves as the main entry point for creating a dashboard.
- **Input**: Receives a configuration file.
- **Functionality**:
  - Parses the configuration file according to the specified requirements.
  - Constructs the dashboard based on the parsed configuration.
  - Allows customization of the dashboard layout and components.

#### `gfun_{dashboard_class}_{resource_type}_{metric}`

- **Purpose**: This function is responsible for creating individual graphic panels for each metric defined in the configuration file.
- **Input**: Metric specifications from the configuration file.
- **Functionality**:
  - Each metric defined in the configuration file should have a corresponding function.
  - Constructs a graphic panel tailored to the specific metric.
  - Ensures that the graphic accurately represents the data associated with the metric.

---

### Key Improvements

- **Clarity**: The purpose and functionality of each function are clearly stated.
- **Structure**: The documentation is structured with headings and bullet points for better readability.
- **Consistency**: Consistent use of terms and formatting for ease of understanding.

