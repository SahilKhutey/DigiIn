import React from "react";

export interface AvatarProps {
  name?: string;
  src?: string;
  size?: "sm" | "md" | "lg" | "xl";
  status?: "online" | "offline" | "busy";
  className?: string;
}

export const Avatar: React.FC<AvatarProps> = ({
  name = "User",
  src,
  size = "md",
  status,
  className = "",
}) => {
  const sizeClasses = {
    sm: "h-8 w-8 text-xs",
    md: "h-10 w-10 text-sm",
    lg: "h-12 w-12 text-base",
    xl: "h-16 w-16 text-xl",
  };

  const getInitials = (n: string) => {
    const parts = n.trim().split(" ");
    if (parts.length >= 2) return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
    return (n[0] || "U").toUpperCase();
  };

  return (
    <div className={`relative inline-flex items-center justify-center shrink-0 ${className}`}>
      {src ? (
        <img
          src={src}
          alt={name}
          className={`${sizeClasses[size]} rounded-full object-cover border border-slate-200`}
        />
      ) : (
        <div
          className={`${sizeClasses[size]} rounded-full bg-[#0B5D9B] text-white font-bold flex items-center justify-center border border-[#092F4F] shadow-xs`}
          aria-label={name}
        >
          {getInitials(name)}
        </div>
      )}
      {status && (
        <span
          className={`absolute bottom-0 right-0 block h-2.5 w-2.5 rounded-full ring-2 ring-white ${
            status === "online" ? "bg-emerald-500" : status === "busy" ? "bg-amber-500" : "bg-slate-400"
          }`}
        />
      )}
    </div>
  );
};
