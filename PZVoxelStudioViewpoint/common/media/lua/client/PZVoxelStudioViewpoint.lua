-- Registers the Voxel Studio model pack with Project Viewpoint (see Viewpoint's MODEL-PACK-GUIDE).
local manifests={"media/voxel-studio/package.properties","media/voxel-studio/package-2.properties","media/voxel-studio/package-3.properties","media/voxel-studio/package-4.properties","media/voxel-studio/package-5.properties","media/voxel-studio/package-6.properties","media/voxel-studio/package-7.properties","media/voxel-studio/package-8.properties","media/voxel-studio/package-9.properties","media/voxel-studio/package-10.properties","media/voxel-studio/package-11.properties","media/voxel-studio/package-12.properties","media/voxel-studio/package-13.properties","media/voxel-studio/package-14.properties","media/voxel-studio/package-15.properties","media/voxel-studio/package-vp-extra.properties","media/voxel-studio/package-houses.properties","media/voxel-studio/package-generated-1.properties","media/voxel-studio/package-generated-2.properties","media/voxel-studio/package-generated-3.properties","media/voxel-studio/package-generated-4.properties","media/voxel-studio/package-generated-5.properties","media/voxel-studio/package-generated-6.properties","media/voxel-studio/package-generated-7.properties","media/voxel-studio/package-generated-8.properties"}
local done={}
local function register()
    if not Viewpoint or not Viewpoint.ModelPacks then return end
    for _,manifest in ipairs(manifests) do
        if not done[manifest] then
            local ok,res=pcall(Viewpoint.ModelPacks.register,"PZVoxelStudioViewpoint",manifest)
            if ok and res then done[manifest]=true elseif not ok then print("[Voxel Studio for Viewpoint] "..manifest..": "..tostring(res)) end
        end
    end
end
Events.OnGameBoot.Add(register)
Events.OnGameStart.Add(register)
register()
