import { forwardRef, InputHTMLAttributes } from "react";

import { cn } from "@/lib/utils";

export const Input = forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement>>(function Input(
  props,
  ref
) {
  return (
    <input
      ref={ref}
      {...props}
      className={cn(
        "w-full rounded-xl border border-white/15 bg-white/5 px-3 py-2 text-sm text-noir-text placeholder:text-white/45",
        props.className
      )}
    />
  );
});
