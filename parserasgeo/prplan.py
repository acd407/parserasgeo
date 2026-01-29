class ParseRASPlan(object):
    def __init__(self, plan_filename):
        self.plan_filename = plan_filename
        self.plan_title = None   # Full plan name
        self.plan_id = None      # Short id
        self.geo_file = None     # geometry file extension: g01, g02, ..
        self.plan_file = None    # flow file extension: f01, f02, ..
        self.other_lines = []

        with open(plan_filename, 'rt') as plan_file:
            for line in plan_file:
                stripped = line.rstrip('\n')
                fields = stripped.split('=')

                if len(fields) == 1:
                    self.other_lines.append(stripped)
                    continue

                var, value = fields[0], fields[1]

                if var == 'Geom File':
                    self.geo_file = value
                elif var == 'Flow File':
                    self.plan_file = value
                elif var == 'Plan Title':
                    self.plan_title = value
                elif var == 'Short Identifier':
                    self.plan_id = value
                else:
                    self.other_lines.append(stripped)
                    
    def update_description(self, context: str):
        """
        Replace the description block between 'BEGIN DESCRIPTION:' and 'END DESCRIPTION:'.
        If no block exists, a new block is appended at the end of the file.

        Parameters
        ----------
        context : str
            The exact text to place as the description content. May include
            newlines; each line becomes one line in the p?? file between the
            BEGIN/END markers.
        """
        # Ensure container exists
        if not hasattr(self, "other_lines") or self.other_lines is None:
            self.other_lines = []

        begin_token = "BEGIN DESCRIPTION:"
        end_token = "END DESCRIPTION:"

        # Find markers
        try:
            begin_idx = next(
                i for i, ln in enumerate(self.other_lines) if ln.strip() == begin_token
            )
        except StopIteration:
            begin_idx = -1

        try:
            end_idx = next(
                i for i, ln in enumerate(self.other_lines)
                if ln.strip() == end_token and (begin_idx == -1 or i > begin_idx)
            )
        except StopIteration:
            end_idx = -1

        # Normalize new content to a list of lines (no trailing newlines)
        new_lines = context.splitlines()

        if begin_idx != -1 and end_idx != -1 and end_idx > begin_idx:
            # Replace everything strictly between the markers
            # If context is empty, keep a single blank line inside the block
            self.other_lines[begin_idx + 1:end_idx] = new_lines if new_lines else [""]
        else:
            # No existing block — append a new one at the end
            if self.other_lines and self.other_lines[-1] != "":
                self.other_lines.append("")  # keep a spacing line before block
            self.other_lines.append(begin_token)
            if new_lines:
                self.other_lines.extend(new_lines)
            else:
                self.other_lines.append("")  # empty content -> leave a blank line
            self.other_lines.append(end_token)

    def __str__(self):
        s = f'Plan Title={self.plan_title}\n'
        s += f'Short Identifier={self.plan_id}\n'
        s += f'Geom File={self.geo_file}\n'
        s += f'Flow File={self.plan_file}\n'
        for line in self.other_lines:
            s += line + '\n'
        return s

    def write(self, output_filename=None):
        if output_filename is None:
            output_filename = self.plan_filename
        with open(output_filename, 'w') as f:
            f.write(str(self))
