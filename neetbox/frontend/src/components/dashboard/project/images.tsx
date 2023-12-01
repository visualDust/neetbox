import { memo } from "react";
import { useCurrentProject, useProjectImages } from "../../../hooks/useProject";

export const Images = memo(() => {
  const { projectId } = useCurrentProject()!;
  const images = useProjectImages(projectId);
  return (
    <div>
      {images.map((img) => (
        <div>
          <img src={"/web/image/" + projectId + "/" + img.imageId} />
          {JSON.stringify(img.metadata)}
        </div>
      ))}
    </div>
  );
});
