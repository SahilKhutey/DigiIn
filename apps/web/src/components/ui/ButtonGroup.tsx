import React from "react";

export interface ButtonGroupProps extends React.HTMLAttributes<HTMLDivElement> {
  attached?: boolean;
}

export const ButtonGroup: React.FC<ButtonGroupProps> = ({
  children,
  attached = false,
  className = "",
  ...props
}) => {
  return (
    <div
      role="group"
      className={`inline-flex flex-wrap items-center ${
        attached ? "divide-x divide-[#CBD5E1] rounded-lg shadow-xs overflow-hidden" : "gap-2"
      } ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};
